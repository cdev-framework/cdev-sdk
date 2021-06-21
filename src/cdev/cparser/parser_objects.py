import ast
import os
import symtable
import math
from enum import Enum
import tokenize
import re

from sortedcontainers import SortedList

INCLUDE_REGEX = '^#include <(\w+)>$'


class parsed_function():
    """
        This class represents the information for a parsed function. It mostly is used to house a function that can keep track of the line numbers.
    """
    # A sorted list of (int,int) that represents lines that need to be parsed out of the file for this function
    needed_line_numbers = []

    # str: name of function
    name = ""

    imported_packages = set()

    def __init__(self, name):
        self.name = name
        self.needed_line_numbers = SortedList()
        self.imported_packages = set()

    def __eq__(self):
        return self.name == self.name

    def add_line_numbers(self, line_no):
        # Use a sorted list
        self.needed_line_numbers.add(line_no)

    def get_line_numbers(self):
        return self.needed_line_numbers

    def add_import(self, global_import_obj):
        self.add_line_numbers(global_import_obj.get_line_no())
        self.imported_packages.add(global_import_obj.orginal_package)


class GlobalStatementType(Enum):
    STANDARD = 1
    FUNCTION = 2
    IMPORT = 3
    CLASS_DEF = 4


class GlobalStatement():
    """
        This class represents the extra information for the global statements of a file. A global statement are the first children in the 
        ast for a file. 
    """

    # Tuple that represents the line numbers the statement spans
    line_no = []

    # File information object for the source file
    src_file_info = ""

    # symbols
    used_symbols = ""

    # symbol table
    symbol_table = ""

    # ast node for this global statement
    node = None

    # hash
    hashed = 0

    # The type of statement
    statement_type = GlobalStatementType.STANDARD

    def __init__(self, node, line_no, symbol_table):
        self.line_no = line_no

        self.set_symbol_table(symbol_table)

        self.node = node

        self.hashed = 0

        for i in range(self.line_no[0], self.line_no[1] + 2):
            self.hashed = self.hashed + i

    def __hash__(self):
        return self.hashed

    def __eq__(self, other):
        return self.hashed == other.hashed

    def __repr__(self):
        return f"<statement at {self.line_no[0]} thru {self.line_no[1]}>"

    def set_symbol_table(self, symbol_table):
        self.symbol_table = symbol_table

    def get_symbol_table(self):
        return self.symbol_table

    def get_symbols(self):
        return self.symbol_table.get_symbols()

    def get_line_no(self):
        return self.line_no

    def get_type(self):
        return self.statement_type


class ImportStatement(GlobalStatement):
    # The original package that the package is from
    # ex: import pandas as pd... original_package = 'pandas'
    orginal_package = ""

    # The actual symbol the package is import as
    # ex: import pandas as pd... as_symbol = 'pd'
    as_symbol = ""

    # Is local file or pkg
    is_local = False

    def __init__(self, node, line_no, symbol_table, asname, pkgname):
        super().__init__(node, line_no, symbol_table)
        self.as_symbol = asname
        self.orginal_package = pkgname

    def get_type(self):
        return GlobalStatementType.IMPORT


class FunctionStatement(GlobalStatement):

    # function name is a func
    func_name = ""

    has_decremented = False

    def __init__(self, node, line_no, symbol_table, name):
        super().__init__(node, line_no, symbol_table)
        self.func_name = name
        self.has_decremented = False

    def get_type(self):
        return GlobalStatementType.FUNCTION

    def get_function_name(self):
        return self.func_name

    def decrement_line_number(self):
        if self.has_decremented:
            return
        
        
        old_lineno = self.line_no
        self.line_no = [old_lineno[0]+1, old_lineno[1]]
        self.has_decremented = True


class ClassDefinitionStatement(GlobalStatement):

    def __init__(self, node, line_no, symbol_table, name):
        super().__init__(node, line_no, symbol_table)
        self.class_name = name

    def get_type(self):
        return GlobalStatementType.CLASS_DEF

    def get_class_name(self):
        return self.class_name
    



class file_information():
    """
        This class represents a file that needs to have functions parsed out of it. 
    """

    # init method or constructor
    def __init__(self, location):
        if not os.path.isfile(location):
            raise FileNotFoundError(
                f"parser_utils: could not find file at -> {location}")
        
        # Path to the file
        self.file_location = location

        # Source code
        self.src_code = []

        # dict<str, global_statement>: imported symbol name to global statement
        self.imported_symbol_to_global_statement = {}

        # Set of the symbol names
        self.imported_symbols = set()

        # List of parsed function objects
        self.parsed_functions = []

        # dict<str, global_statement>: function name to its global statement
        self.global_functions = {}

        
        # dict<statement, list(str)>: fuction from statement to symbols
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
        self.symbol_table = ""

        
        # abstract syntax tree for the file
        self.ast = ""

        with open(location, 'r') as fh:
            self.src_code = fh.readlines()
            fh.seek(0)

            for toktype, tok, start, end, line in tokenize.generate_tokens(fh.readline):
                # we can also use token.tok_name[toktype] instead of 'COMMENT'
                # from the token module 
                if toktype == tokenize.COMMENT:
                    self._evaluate_comment(line, start)

        try:
            self.symbol_table = symtable.symtable("".join(self.src_code),
                                                  location, 'exec')
        except SyntaxError as e:
            print(e)

        try:
            self.ast = ast.parse("".join(self.src_code))
        except Exception as e:
            print(e)

    def _evaluate_comment(self, line, start):
        #print(f"COMMENT {start} {line}")

        match_obj = re.match(INCLUDE_REGEX, line)

        if match_obj:
            if len(match_obj.groups()) == 1:
                self.include_overrides_lineno[match_obj.groups()[0]] = start[0]


    def get_source_code(self):
        return "".join(self.src_code)

    def get_lines_of_source_code(self, start_line, end_line):
        return "".join(self.src_code[(start_line - 1):(end_line)])

    def get_symbol_table(self):
        return self.symbol_table

    def get_ast(self):
        return self.ast

    def add_global_statement(self, global_statement):
        self.top_level_statements.append(global_statement)
        self.statement_to_symbol[global_statement] = set()

    def get_global_statements(self):
        return self.top_level_statements

    def get_file_length(self):
        return len(self.src_code)

    def add_global_function(self, name, global_obj):
        self.global_functions[name] = global_obj
        self.add_global_statement(global_obj)

    def add_global_import(self, global_obj):
        self.imported_symbol_to_global_statement[
            global_obj.as_symbol] = global_obj
        self.add_global_statement(global_obj)

    def add_class_definition(self, name, global_obj):
        self.global_functions[name] = global_obj
        self.add_global_statement(global_obj)

    def add_parsed_functions(self, func):
        self.parsed_functions.append(func)

    def set_imported_symbols(self, symbols):
        self.imported_symbols = symbols
