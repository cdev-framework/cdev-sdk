import ast
import os
import symtable
import math
from enum import Enum

from sortedcontainers import SortedList


class parsed_function():
    """
        This class represents the information for a parsed function. It mostly is used to house a function that can keep track of the line numbers.
    """
    # A sorted list of (int,int) that represents lines that need to be parsed out of the file for this function
    needed_line_numbers = []

    # str: name of function
    name = ""

    def __init__(self, name):
        self.name = name
        self.needed_line_numbers = SortedList()

    def __eq__(self):
        return self.name == self.name

    def add_line_numbers(self, line_no):
        # Use a sorted list
        self.needed_line_numbers.add(line_no)

    def get_line_numbers(self):
        return self.needed_line_numbers


class GlobalStatementType(Enum):
    STANDARD = 1
    FUNCTION = 2
    IMPORT = 3
    CLASS = 4

    
        
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

        for i in range(self.line_no[0], self.line_no[1]+2):
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

    def __init__(self, node, line_no, symbol_table, name):
        super().__init__(node, line_no, symbol_table)
        self.func_name = name
    

    def get_type(self):
        return GlobalStatementType.FUNCTION


    def get_function_name(self):
        return self.func_name




class file_information():
    """
        This class represents a file that needs to have functions parsed out of it. 
    """

    # Dict<name,symbol_information_obj> 
    parsed_functions = {}

    # Path to the file
    file_location = ""

    # Source code
    src_code = []

    # list[global_statements]
    top_level_statements = []

    # symbol table for the file
    symbol_table = ""

    # abstract syntax tree for the file
    ast = ""

    # dict<str, list(statement)>: dictionary from string name of symbol to global statement
    symbol_to_statement = {}

    # dict<statement, list(str)>: fuction from statement to symbols
    statement_to_symbol = {}

    # dict<str, global_statement>: function name to its global statement
    global_functions = {}

    parsed_functions = []

    # Set of the symbol names 
    imported_symbols = set()

    # dict<str, global_statement>: imported symbol name to global statement
    imported_symbol_to_global_statement = {}

    # init method or constructor   
    def __init__(self, location):  
        if not os.path.isfile(location):
            raise FileNotFoundError(
                f"parser_utils: could not find file at -> {location}")

        self.file_location = location  
        self.imported_symbol_to_global_statement = {}

        with open(location, 'r') as fh:
            self.src_code = fh.readlines()

        try:
            self.symbol_table = symtable.symtable("".join(self.src_code), location, 'exec')
        except SyntaxError as e:
            print(e)

        try:
            self.ast = ast.parse("".join(self.src_code))
        except Exception as e:
            print(e)

    def get_source_code(self):
        return "".join(self.src_code)

    def get_lines_of_source_code(self, start_line, end_line):
        return "".join(self.src_code[(start_line-1):(end_line)])

    def get_symbol_table(self):
        return self.symbol_table

    def get_ast(self):
        return self.ast

    def add_global_statement(self, global_statement):
        print(global_statement)
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
        self.imported_symbol_to_global_statement[global_obj.as_symbol] = global_obj
        self.add_global_statement(global_obj)

    def add_parsed_functions(self, func):
        self.parsed_functions.append(func)

    def set_imported_symbols(self, symbols):
        self.imported_symbols = symbols
