import ast
import os
import symtable


class parsed_function():
    """
        This class represents the information for a parsed function. It mostly is used to house a function that can keep track of the line numbers.
    """
    # A list of (int,int) that represents lines that need to be parsed out of the file for this function
    needed_line_numbers = []

    # str: name of function
    name = ""

    def __init__(self, name):
        self.name = name


    def add_line_numbers(self, line_no):
        self.needed_line_numbers.append(line_no)

    def get_line_numbers(self):
        return self.needed_line_numbers
    
        
class global_statement():
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

    # boolean that states if this global statement is a function
    is_function = False

    # ast node for this global statement
    node = None

    def __init__(self, file_info_obj, node, line_no):
        self.src_file_info = file_info_obj

        self.line_no = line_no

        self.create_symbol_table()

        self.node = node


    def create_symbol_table(self):
        tmp_src_code = self.src_file_info.get_lines_of_source_code(self.line_no[0], self.line_no[1])

        tmp_symbol_table = symtable.symtable(tmp_src_code, self.src_file_info.file_location, 'exec')

        self.symbol_table = tmp_symbol_table   

        print(f"{self.line_no}; {self.symbol_table.get_symbols()}")

        # if the symbol table is a function then it will appear as a single symbol that is a namespace 
        if len(tmp_symbol_table.get_symbols()) == 1:
            single_symbol = tmp_symbol_table.get_symbols()[0]
            if single_symbol.is_namespace():
                if isinstance(single_symbol.get_namespaces()[0], symtable.Function):
                    self.symbol_table = single_symbol.get_namespaces()[0]
                    self.is_function = True

                    self.src_file_info.add_global_function(single_symbol.get_name(), self)
                
    def get_symbol_table(self):
        return self.symbol_table

    def get_is_function(self):
        return self.function

    def get_line_no(self):
        return self.line_no



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

    # init method or constructor   
    def __init__(self, location):  
        if not os.path.isfile(location):
            raise FileNotFoundError(
                f"parser_utils: could not find file at -> {location}")

        self.file_location = location  

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
        self.top_level_statements.append(global_statement)

    def get_global_statements(self):
        return self.top_level_statements

    def get_file_length(self):
        return len(self.src_code)
        
    def add_global_function(self, name, global_obj):
        self.global_functions[name] = global_obj
