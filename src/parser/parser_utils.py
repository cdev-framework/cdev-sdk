import os

from src.parser.parser_objects import *
from src.parser.cdev_parser_exceptions import *

def _get_global_variables_in_symboltable(table):
    # TODO Change error that is raised
    if not isinstance(table, symtable.SymbolTable):
        raise FileNotFoundError("tmp")

    symbols = table.get_symbols()

    rv_variables = set()

    for sym in symbols:
        # Check all symbols to see if they are not a namespace. If not then they are a normal symbols for this symboltable.
        if not sym.is_namespace():
            if sym.is_global():
                rv_variables.add(sym.get_name())

    return rv_variables

def _get_imported_variables_in_symboltable(table):
    # TODO Change error that is raised
    if not isinstance(table, symtable.SymbolTable):
        raise FileNotFoundError("tmp")

    symbols = table.get_symbols()

    rv_variables = set()

    for sym in symbols:
        # Check all symbols to see if they are not a namespace. If not then they are a normal symbols for this symboltable.
        if not sym.is_namespace():
            if sym.is_imported():
                rv_variables.add(sym.get_name())

    return rv_variables


def _get_local_variables_in_symboltable(table):
    # TODO Change error that is raised
    if not isinstance(table, symtable.SymbolTable):
        raise FileNotFoundError("tmp")

    symbols = table.get_symbols()

    rv_variables = set()

    for sym in symbols:
        # Check all symbols to see if they are not a namespace. If not then they are a normal gloabl variable for this symboltable.
        if not sym.is_namespace():
            #print(
            #    f"{sym.get_name()}: {sym.is_imported()}; {sym.is_free()}; {sym.is_global()}; {sym.is_local()}"
            #)
            if not sym.is_imported() and not sym.is_free(
            ) and not sym.is_global():
                rv_variables.add(sym.get_name())

    return rv_variables


def _get_functions_in_symboltable(table):
    # TODO Change error that is raised
    if not isinstance(table, symtable.SymbolTable):
        raise FileNotFoundError("tmp")

    symbols = table.get_symbols()

    rv_functions = set()

    for sym in symbols:
        # Check all symbols to see if they are a namespace (only functions and classes are namespaces)
        if sym.is_namespace():
            for ns in sym.get_namespaces():
                # A symbol can have multiple bindings so we need to see if any of them are functions
                if isinstance(ns, symtable.Function):
                    rv_functions.add(sym.get_name())
                    continue

    return rv_functions


def get_file_information(file_path, include_functions=[]):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"cdev_parser: could not find file at -> {file_path}")

    file_info_obj = file_information(file_path)

    symbol_table = file_info_obj.get_symbol_table()

    try:
        functions = _get_functions_in_symboltable(symbol_table)
        file_info_obj.function_names = functions

        local_variables = _get_local_variables_in_symboltable(symbol_table)

        imported_symbols = _get_imported_variables_in_symboltable(symbol_table)
    
        global_symbols = _get_global_variables_in_symboltable(symbol_table)
    except FileNotFoundError as e:
        print(e)

    for item in functions.union(local_variables).union(imported_symbols).union(global_symbols):
        file_info_obj.symbol_to_statement[item] = set()

    
    # Need to get the line range of each global statement, but this requires looping over all the global nodes in the ast
    # in the top level of the file. To support earlier versions of python <3.7 we must use the starting line of 
    # the next statement as the last line of previous node. We are going to store this info in a tmp dict then
    # once we have all the information create the objects

    file_ast = file_info_obj.get_ast()

    # dict<ast.node, [line1,line2]>
    _tmp_global_information = {}

    previous_node = None
    for node in file_ast.body:
        if previous_node:
            prev_vals = _tmp_global_information.get(previous_node)
            prev_vals.append(node.lineno-1)
            _tmp_global_information[previous_node]

        _tmp_global_information[node] = [node,node.lineno]

        previous_node = node

    # Set the last line of the last global statement to the last line of the file
    prev_vals = _tmp_global_information.get(previous_node)
    prev_vals.append(file_info_obj.get_file_length()+1)
    _tmp_global_information[previous_node]

    #print(_tmp_global_information)

    # Now that the information has been collected for the global statements, we can create the actual objs and add
    # them to the file_info_obj 
    for k in _tmp_global_information:
        glob_obj = global_statement(file_info_obj, _tmp_global_information.get(k)[0], _tmp_global_information.get(k)[1:3])
        file_info_obj.add_global_statement(glob_obj)
        file_info_obj.statement_to_symbol[glob_obj] = set()


    EXCLUDED_SYMBOLS = set(["os", "print"])
    #print(file_info_obj.statement_to_symbol)

    # Build a two-way binding of a symbol to statement and a statement to a symbol.
    # This information is needed to get all dependencies of symbols, which is needed
    # to reconstruct just the nessecary lines
    for i in file_info_obj.get_global_statements():
        syms = i.get_symbols()
        for sym in syms:
            if not sym.get_name() in file_info_obj.symbol_to_statement:
                continue

            if sym.get_name() in EXCLUDED_SYMBOLS:
                continue

            # Add all the symbols in the statement to the list of this global statement
            if i in file_info_obj.statement_to_symbol:
                tmp = file_info_obj.statement_to_symbol.get(i)
                tmp.add(sym.get_name())
                file_info_obj.statement_to_symbol[i] = tmp

            # Since this global statement is a top level function... the code that effects this symbol within it will only execute if the 
            # function itself is called. Therefor, other functions can use this symbol without depending on that actual function it is in. 
            if i.is_function:
                continue

            tmp = file_info_obj.symbol_to_statement.get(sym.get_name())
            tmp.add(i)
            file_info_obj.symbol_to_statement[sym.get_name()] = tmp

        if i.is_function:
            tmp = file_info_obj.symbol_to_statement.get(i.get_function_name())
            tmp.add(i)
            file_info_obj.symbol_to_statement[i.get_function_name()] = tmp

    #print(file_info_obj.statement_to_symbol)
    #print("--------")
    #for s in file_info_obj.symbol_to_statement:
    #    print(f"-----{s}")
    #    print(f"----->>>>>{file_info_obj.symbol_to_statement.get(s)}")

    # If a list of functions was not included then parse all top level functions
    if not include_functions:
        include_functions = file_info_obj.global_functions.keys()


    for function_name in include_functions:
        # Create new parsed function obj
        p_function = parsed_function(function_name)

        # Get the Global obj associated with the current function
        func_glob_obj = file_info_obj.global_functions.get(function_name)

        # Add the functions lines to the parsed function
        p_function.add_line_numbers(func_glob_obj.get_line_no())

        # Start with a set that already includes the global statement for itself
        already_included_global_obj = set([func_glob_obj])

        # Start with a set that already includes the symbol for itself
        already_included_symbols = set([function_name])

        # next symbols is the set of symbols that need their dependant global statements
        next_symbols =  file_info_obj.statement_to_symbol.get(func_glob_obj)

        keep_looping = True
        remaining_symbols = set()

        while keep_looping:
            # If there are no more symbols than break the loop
            if not next_symbols:
                break 
            
            # Add the previous iterations symbols as already seen so they are not readded
            already_included_symbols = already_included_symbols.union(remaining_symbols)
            remaining_symbols = next_symbols
            next_symbols = set()

            #print(f"{function_name} already include objects: {already_included_global_obj}")
            #print(f"{function_name} already include symbols: {already_included_symbols}")
            for sym in remaining_symbols:
                if sym in already_included_symbols:
                    # If we have already added this symbol than we have all of its dependencies
                    continue

                #print(f"-----{sym}")

                # Add all dependant global statements to this symbol needs to the need lines for the function
                for glob_obj in file_info_obj.symbol_to_statement.get(sym):
                    
                    if glob_obj in already_included_global_obj:
                        #IF this global statement has already been added continue
                        #print(f"----------{glob_obj} CONTINUE")
                        #print(f"{function_name} already include objects: {already_included_global_obj}")
                        continue

                    #print(f"----------{glob_obj}")

                    # Add the lines numbers and place it in the already included set
                    p_function.add_line_numbers(glob_obj.get_line_no())
                    already_included_global_obj.add(glob_obj)

                    # Get the set of symbols that this statement depends on
                    set_symbols = file_info_obj.statement_to_symbol.get(glob_obj)
                    # Remove the symbols that have already been included
                    new_needed_symbols = set_symbols.difference(already_included_symbols) 
                    actual_new_needed_symbols = new_needed_symbols.difference(remaining_symbols)
                    #print(f"------------------{actual_new_needed_symbols}")
                    # Add the actually needed new symbols to the set of symbols to be looped over next
                    next_symbols = next_symbols.union(actual_new_needed_symbols)

        #finally add the parsed function object to the file info
        file_info_obj.add_parsed_functions(p_function)
                   

    for f in file_info_obj.parsed_functions:
        print(f"{f.needed_line_numbers}")


    return file_info_obj