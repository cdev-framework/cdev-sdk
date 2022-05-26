import ast
import os
import symtable
from enum import Enum
import tokenize
import re
import hashlib
from typing import List

from sortedcontainers import SortedList

INCLUDE_REGEX = "^#include <(\w+)>$"


def _hash_line_numbers(line_no_1: int, line_no_2: int) -> str:
    s_numbers = f"{line_no_1}:{line_no_2}"
    return int.from_bytes(hashlib.md5(s_numbers.encode()).digest(), byteorder="big")


class parsed_function:
    """
    This class represents the information for a parsed function. It mostly is used to house a function that can keep track of the line numbers.
    """

    def __init__(self, name):
        self.name: str = name
        self.needed_line_numbers = SortedList(key=lambda x: x[0])

        # set of imported packages
        self.imported_packages: str = set()

        # some packages come with the lambda runtime so they do not need to be packaged into a layer so we need to make a new set with
        # just packages we need to actually package into layers
        # EX: 'os' does not need to be packaged into a layer
        self.needed_imports = set()

        self.needed_imports_hash = ""

    def __eq__(self) -> bool:
        return self.name == self.name

    def add_line_numbers(self, line_no) -> None:
        # Use a sorted list
        self.needed_line_numbers.add(line_no)

    def get_line_numbers(self) -> SortedList:
        return self.needed_line_numbers

    def get_line_numbers_serializeable(self) -> List:
        return list(self.needed_line_numbers)

    def add_import(self, global_import_obj) -> None:
        # self.add_line_numbers(global_import_obj.get_line_no())
        # original package will be how it is denoted in the import statement
        # for absolute packages we only want the top level name (absolutes don't start with '.')
        # for relative packages we want the entire name (relatives start with '.')
        top_level_package_name = (
            global_import_obj.original_package.split(".")[0]
            if not global_import_obj.original_package.startswith(".")
            else global_import_obj.original_package
        )
        self.imported_packages.add(top_level_package_name)


class GlobalStatementType(Enum):
    STANDARD = 1
    FUNCTION = 2
    IMPORT = 3
    CLASS_DEF = 4


class GlobalStatement:
    """
    This class represents the extra information for the global statements of a file. A global statement are the first children in the
    ast for a file.
    """

    def __init__(self, node, line_no, symbols) -> None:
        self.line_no = line_no

        self.set_symbols(symbols)

        self.node = node

        self.hashed = _hash_line_numbers(self.line_no[0], self.line_no[1])

        # The type of statement
        self.statement_type = GlobalStatementType.STANDARD

    def __hash__(self):
        return self.hashed

    def __eq__(self, other) -> bool:
        return self.hashed == other.hashed

    def __repr__(self):
        return f"<statement at {self.line_no[0]} thru {self.line_no[1]}>"

    def set_symbols(self, symbols: List[str]) -> None:
        self.symbols = symbols

    def get_symbols(self) -> List[str]:
        return self.symbols

    def get_line_no(self):
        return self.line_no

    def get_type(self):
        return self.statement_type


class ImportStatement(GlobalStatement):
    # The original package that the package is from
    # ex: import pandas as pd... original_package = 'pandas'
    original_package = ""

    # The actual symbol the package is import as
    # ex: import pandas as pd... as_symbol = 'pd'
    as_symbol = ""

    # Is local file or pkg
    is_local = False

    def __init__(self, node, line_no, symbol_table, asname, pkgname):
        super().__init__(node, line_no, symbol_table)
        self.as_symbol = asname
        self.original_package = pkgname

    def get_type(self):
        return GlobalStatementType.IMPORT


class FunctionStatement(GlobalStatement):

    # function name is a func
    func_name: str = ""

    has_decremented: bool = False

    def __init__(self, node, line_no, symbol_table, name) -> None:
        super().__init__(node, line_no, symbol_table)
        self.func_name = name
        self.has_decremented = False

    def get_type(self):
        return GlobalStatementType.FUNCTION

    def get_function_name(self) -> str:
        return self.func_name

    def decrement_line_number(self) -> None:
        if self.has_decremented:
            return

        old_lineno = self.line_no
        self.line_no = [old_lineno[0] + 1, old_lineno[1]]
        self.has_decremented = True


class ClassDefinitionStatement(GlobalStatement):
    def __init__(self, node, line_no, symbol_table, name):
        super().__init__(node, line_no, symbol_table)
        self.class_name = name

    def get_type(self):
        return GlobalStatementType.CLASS_DEF

    def get_class_name(self) -> str:
        return self.class_name


class file_information:
    """
    This class represents a file that needs to have functions parsed out of it.
    """

    # init method or constructor
    def __init__(self, location) -> None:
        if not os.path.isfile(location):
            raise FileNotFoundError(
                f"parser_utils: could not find file at -> {location}"
            )

        # Path to the file
        self.file_location = location

        # Source code
        self.src_code = []

        # dict<str, global_statement>: imported symbol name to global statement
        self.imported_symbol_to_global_statement = {}

        # Set of the symbol names
        self.imported_symbols = set()

        # List of parsed function objects
        self.parsed_functions: List[parsed_function] = []

        # dict<str, global_statement>: function name to its global statement
        self.global_functions = {}

        # dict<statement, list(str)>: function from statement to symbols
        self.statement_to_symbol = {}

        # dict<str, list(statement)>: dictionary from string name of symbol to global statement
        self.symbol_to_statement = {}

        # list[global_statements]
        self.top_level_statements = []

        # dict<str, int>: dict from label for manual override to the line number of the comment
        self.include_overrides_lineno = {}

        # dict<str, globalobj>: dict from label for manual override to the line number of the comment
        self.include_overrides_glob = {}

        # symbol table for the file
        self.symbol_table = None

        # abstract syntax tree for the file
        self.ast = ""

        with open(location, "r") as fh:
            self.src_code = fh.readlines()
            fh.seek(0)

            for toktype, tok, start, end, line in tokenize.generate_tokens(fh.readline):
                # we can also use token.tok_name[toktype] instead of 'COMMENT'
                # from the token module
                if toktype == tokenize.COMMENT:
                    self._evaluate_comment(line, start)

        try:
            self.symbol_table = symtable.symtable(
                "".join(self.src_code), location, "exec"
            )
        except SyntaxError as e:
            print(e)

        try:
            self.ast = ast.parse("".join(self.src_code))
        except Exception as e:
            print(e)

    def _evaluate_comment(self, line, start):
        # print(f"COMMENT {start} {line}")

        match_obj = re.match(INCLUDE_REGEX, line)

        if match_obj:
            if len(match_obj.groups()) == 1:
                self.include_overrides_lineno[match_obj.groups()[0]] = start[0]

    def get_source_code(self) -> str:
        return "".join(self.src_code)

    def get_lines_of_source_code(self, start_line, end_line) -> str:
        return "".join(self.src_code[(start_line - 1) : (end_line)])

    def get_symbol_table(self):
        return self.symbol_table

    def get_ast(self):
        return self.ast

    def add_global_statement(self, global_statement) -> None:
        self.top_level_statements.append(global_statement)
        self.statement_to_symbol[global_statement] = set()

    def get_global_statements(self) -> List[GlobalStatement]:
        return self.top_level_statements

    def get_file_length(self) -> int:
        return len(self.src_code)

    def add_global_function(self, name, global_obj) -> None:
        self.global_functions[name] = global_obj
        self.add_global_statement(global_obj)

    def add_global_import(self, global_obj) -> None:
        self.imported_symbol_to_global_statement[global_obj.as_symbol] = global_obj

        self.add_global_statement(global_obj)

    def add_class_definition(self, name, global_obj) -> None:
        self.global_functions[name] = global_obj
        self.add_global_statement(global_obj)

    def add_parsed_functions(self, func) -> None:
        self.parsed_functions.append(func)

    def set_imported_symbols(self, symbols) -> None:
        self.imported_symbols = symbols
