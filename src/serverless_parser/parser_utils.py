import ast
import os
from sys import modules, version_info

from typing import List
from pydantic.types import DirectoryPath, FilePath

import tokenize 

from .parser_objects import *
from .parser_exceptions import InvalidParamError, CouldNotParseFileError, CdevFileNotFoundError, InvalidDataError

EXCLUDED_SYMBOLS = set([ "print", "sss"])


def _get_global_variables_in_symboltable(table):
    if not isinstance(table, symtable.SymbolTable):
        raise InvalidParamError(f"Invalid Param in _get_functions_in_symboltable: Expected symtable.SymbolTable got {type(table)}")

    symbols = table.get_symbols()

    rv_variables = set()

    for sym in symbols:
        # Check all symbols to see if they are not a namespace. Check if the symbol is a global.
        if not sym.is_namespace():
            if sym.is_global():
                rv_variables.add(sym.get_name())

    return rv_variables


def _get_imported_variables_in_symboltable(table):
    # TODO Change error that is raised
    if not isinstance(table, symtable.SymbolTable):
        raise InvalidParamError(f"Invalid Param in _get_functions_in_symboltable: Expected symtable.SymbolTable got {type(table)}")

    symbols = table.get_symbols()

    rv_variables = set()

    for sym in symbols:
        # Check all symbols to see if they are not a namespace. If not then they are a normal symbols for this symboltable.
        if not sym.is_namespace():
            if sym.is_imported():
                rv_variables.add(sym.get_name())

    return rv_variables


def _get_local_variables_in_symboltable(table):
    if not isinstance(table, symtable.SymbolTable):
        raise InvalidParamError(f"Invalid Param in _get_functions_in_symboltable: Expected symtable.SymbolTable got {type(table)}")

    symbols = table.get_symbols()

    rv_variables = set()

    for sym in symbols:
        # Check all symbols to see if they are not a namespace. If not then they are a normal gloabl variable for this symboltable.
        if not sym.is_namespace():
            if not sym.is_imported() and not sym.is_free(
            ) and not sym.is_global():
                rv_variables.add(sym.get_name())

    return rv_variables


def _get_functions_in_symboltable(table):
    if not isinstance(table, symtable.SymbolTable):
        raise InvalidParamError(f"Invalid Param in _get_functions_in_symboltable: Expected symtable.SymbolTable got {type(table)}")

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


def _get_global_class_definitions_in_symboltable(table):
    if not isinstance(table, symtable.SymbolTable):
        raise InvalidParamError(f"Invalid Param in _get_functions_in_symboltable: Expected symtable.SymbolTable got {type(table)}")

    symbols = table.get_symbols()

    rv_class_defs = set()

    for sym in symbols:
        # Check all symbols to see if they are a namespace (only functions and classes are namespaces)
        if sym.is_namespace():
            for ns in sym.get_namespaces():
                # A symbol can have multiple bindings so we need to see if any of them are functions
                if isinstance(ns, symtable.Class):
                    rv_class_defs.add(sym.get_name())
                    continue

    return rv_class_defs


def _generate_global_statement(file_info_obj, node, line_info):
    # This function is used to determine the type of global statement the node is and create the corresponding global statement obj
    ast_node = node
    # Need to adjust the starting line if using python3.8 or greater

    #start_line = line_info[0] if  version_info < (3,8) else line_info[0]-1
    start_line = line_info[0]

    if isinstance(ast_node, ast.FunctionDef):
        if ast_node.decorator_list:
            start_line = line_info[0] if  version_info < (3,8) else line_info[0]-1
    

    
    last_line = line_info[1]

    manual_include = False
    manual_include_sym = ""

    # Look one line above the start for a manual include
    for k in file_info_obj.include_overrides_lineno:
        if file_info_obj.include_overrides_lineno.get(k) == start_line-1:
            manual_include = True
            manual_include_sym = k
            break

    tmp_src_code = file_info_obj.get_lines_of_source_code(
        start_line, last_line)

    tmp_symbol_table = symtable.symtable(tmp_src_code,
                                         file_info_obj.file_location, 'exec')

    symbol_table = tmp_symbol_table

    # If the symbol table is a function then it will appear as a single symbol that is a namespace
    # But when using an annotation it will have more than 1 symbol 
    need_to_check_function = len(tmp_symbol_table.get_symbols()) == 1

    need_to_check_class_def = False

    for sym in tmp_symbol_table.get_symbols():
        if sym.is_namespace():
            if isinstance(sym.get_namespaces()[0], symtable.Function):
                need_to_check_function = True
            elif isinstance(sym.get_namespaces()[0], symtable.Class):
                need_to_check_class_def = True
        

    if need_to_check_function:
        single_symbol = tmp_symbol_table.get_symbols()[0]
        if single_symbol.is_namespace():
            if isinstance(single_symbol.get_namespaces()[0],
                          symtable.Function):
                name = single_symbol.get_name()
                fs = FunctionStatement(ast_node, [start_line, last_line],
                                       single_symbol.get_namespaces()[0], name)
                file_info_obj.add_global_function(name, fs)

                if manual_include:
                    file_info_obj.include_overrides_glob[manual_include_sym] = fs

                return

    if need_to_check_class_def:

        class_def_table = symbol_table.get_children()[0]

        class_def = ClassDefinitionStatement(ast_node, [start_line, last_line], class_def_table , class_def_table.get_name())
        file_info_obj.add_class_definition(class_def_table.get_name(), class_def)
        return 

    ts = {s.get_name() for s in tmp_symbol_table.get_symbols()}

    used_imported_symbols = file_info_obj.imported_symbols.intersection(ts)
    if len(used_imported_symbols) > 0:
        # This statement uses an imported symbol so we need to check it to see if it is the import statement
        for n in ast.walk(ast_node):
            #print(n)
            if isinstance(n, ast.Import):
                #print(f"IMPORT: {n}")
                #print(f"FIELDS { [(cn.name, cn.asname)  for cn in n.names] }")
                for imprt in n.names:
                    #print(f"FIELDS: {imprt.name}; {imprt.asname}")
                    if not imprt.asname:
                        asname = imprt.name
                    else:
                        asname = imprt.asname

                    imp_statement = ImportStatement(ast_node,
                                                    [start_line, last_line],
                                                    symbol_table, asname,
                                                    imprt.name)

                    #print(f"{ast.dump(n)} -> {asname}?{imprt.name}")
                    file_info_obj.add_global_import(imp_statement)
                    continue

            if isinstance(n, ast.ImportFrom):
                for imprt in n.names:
                    if not imprt.asname:
                        asname = imprt.name
                    else:
                        asname = imprt.asname
                    

                    if n.level > 0:
                        if not n.module:
                            asmodule = f"{'.' * n.level}{asname}"
                        else:
                            asmodule = f"{'.' * n.level}{n.module}"
                            

                    else:
                        asmodule =  n.module

                    #print(f"{ast.dump(n)} -> {asname}?{asmodule}")
                    imp_statement = ImportStatement(ast_node,
                                                    [start_line, last_line],
                                                    symbol_table, asname,
                                                    asmodule)

                    file_info_obj.add_global_import(imp_statement)
                continue

    global_statement_obj = GlobalStatement(ast_node, [start_line, last_line],
                                           symbol_table)


    
    file_info_obj.add_global_statement(global_statement_obj)

    if manual_include:
        file_info_obj.include_overrides_glob[manual_include_sym] = global_statement_obj


def _validate_param_function_manual_includes(param):
    # Validate that the function manual includes param is:
    # - dict<str,[str]>

    if not isinstance(param, dict):
        raise InvalidParamError(
            f"cdev_parser.get_file_information: function_manual_includes value not dict")

    for key in param:
        if not isinstance(param.get(key), list):
            raise InvalidParamError(
                f"cdev_parser.get_file_information: function_manual_includes param: key '{key}' has non-list value")    

        for val in param.get(key):
            if not isinstance(val, str):
                raise InvalidParamError(
                f"cdev_parser.get_file_information: function_manual_includes param: value '{val}' in '{key}' is a non string ({type(val)})")


def _validate_param_global_manual_includes(param):
    # Validate that the function manual includes param is:
    # - list[str]

    if not isinstance(param, list):
        raise InvalidParamError(
            f"cdev_parser.get_file_information: global_manual_includes value not list")

    for val in param:
        if not isinstance(val, str):
            raise InvalidParamError(
            f"cdev_parser.get_file_information: global_manual_includes param: value '{val}' in param is a non string ({type(val)})")


def _validate_param_include_functions(param):
    # Validate that the function manual includes param is:
    # - list[str]

    if not isinstance(param, list):
        raise InvalidParamError(
            f"cdev_parser.get_file_information: include_functions value not list")

    for val in param:
        if not isinstance(val, str):
            raise InvalidParamError(
            f"cdev_parser.get_file_information: include_functions param: value '{val}' in param is a non string ({type(val)})")


def get_file_information(file_path, include_functions=[], function_manual_includes={}, global_manual_includes=[], remove_top_annotation=False):
    if not os.path.isfile(file_path):
        raise CouldNotParseFileError(CdevFileNotFoundError(
            f"cdev_parser: could not find file at -> {file_path}"))

    try:
        _validate_param_include_functions(include_functions)
        _validate_param_function_manual_includes(function_manual_includes)
        _validate_param_global_manual_includes(global_manual_includes)
    except InvalidParamError as e:
        raise CouldNotParseFileError(e)
        return

    file_info_obj = file_information(file_path)

    symbol_table = file_info_obj.get_symbol_table()

    # Need to get some basic information about the global namespace in the file. This includes:
    # - all defined functions (_get_functions_in_symboltable)
    # - variables defined in the global namespace (_get_local_variables_in_symboltable)
    # - imported symbols (_get_imported_variables_in_symboltable)
    # - global variables (_get_global_variables_in_symboltable)

    try:
        functions = _get_functions_in_symboltable(symbol_table)

        file_info_obj.function_names = functions

        local_variables = _get_local_variables_in_symboltable(symbol_table)

        imported_symbols = _get_imported_variables_in_symboltable(symbol_table)

        global_symbols = _get_global_variables_in_symboltable(symbol_table)

        class_definitions = _get_global_class_definitions_in_symboltable(symbol_table)
    except InvalidParamError as e:
        raise CouldNotParseFileError(e)
        return

    for item in functions.union(local_variables).union(imported_symbols).union(
            global_symbols).union(class_definitions):
        file_info_obj.symbol_to_statement[item] = set()

    file_info_obj.set_imported_symbols(imported_symbols)

    # Need to get the line range of each global statement, but this requires looping over all the global nodes in the ast
    # in the top level of the file. 
    # 
    # Python3.8 introduced node.end_lineno to ast nodes, which makes it easier to get the ending line info
    # 
    # To support earlier versions of python (<3.7) we must use the starting line of
    # the next statement as the last line of previous node. We are going to store this info in a tmp dict then
    # once we have all the information create the objects

    file_ast = file_info_obj.get_ast()

    # dict<ast.node, [line1,line2]>
    _tmp_global_information = {}

    # sys.version_info
    if version_info < (3,8):
        previous_node = None
        for node in file_ast.body:
            #_tmp_global_information[node] = [node.lineno, node.end_lineno]
            if previous_node:
                prev_vals = _tmp_global_information.get(previous_node)
                prev_vals.append(node.lineno-1)
                _tmp_global_information[previous_node] = prev_vals

            _tmp_global_information[node] = [node.lineno]

            previous_node = node

        # Set the last line of the last global statement to the last line of the file
        prev_vals = _tmp_global_information.get(previous_node)
        prev_vals.append(file_info_obj.get_file_length() + 1)
        _tmp_global_information[previous_node] = prev_vals
    else:
        for node in file_ast.body:
            _tmp_global_information[node] = [node.lineno, node.end_lineno]


    # Now that the information has been collected for the global statements, we can create the actual objs and add
    # them to the file_info_obj
    for k in _tmp_global_information:
        _generate_global_statement(file_info_obj,
                                   k, _tmp_global_information.get(k))


    # Build a two-way binding of a symbol to statement and a statement to a symbol.
    # This information is needed to get all dependencies of symbols, which is needed
    # to reconstruct just the nessecary lines
    for i in file_info_obj.get_global_statements():
        syms = i.get_symbols()
        for sym in syms:
            if not sym.get_name() in file_info_obj.symbol_to_statement:
                continue

            # Some symbols do no create a dependency so they should not be added
            if sym.get_name() in EXCLUDED_SYMBOLS:
                continue

            # Add all the symbols in the statement to the list for this global statement. This means when this global object
            # is used we need to include all of these symbols
            if i in file_info_obj.statement_to_symbol:
                tmp = file_info_obj.statement_to_symbol.get(i)
                tmp.add(sym.get_name())
                file_info_obj.statement_to_symbol[i] = tmp

            # Since this global statement is a top level function... the code that effects this symbol within it will only execute if the
            # function itself is called. Therefor, other functions can use this symbol without depending on this function.
            if i.get_type() == GlobalStatementType.FUNCTION:
                continue

            tmp = file_info_obj.symbol_to_statement.get(sym.get_name())
            tmp.add(i)
            file_info_obj.symbol_to_statement[sym.get_name()] = tmp


        # if this global object is a function then we need to add the global object to its own symbol name dependency list. That way
        # if another global statement calls this function we include this global statement (which is the definition of the function) 
        if i.get_type() == GlobalStatementType.FUNCTION:
            tmp = file_info_obj.symbol_to_statement.get(i.get_function_name())
            tmp.add(i)
            file_info_obj.symbol_to_statement[i.get_function_name()] = tmp

        if i.get_type() == GlobalStatementType.CLASS_DEF:
            tmp = file_info_obj.symbol_to_statement.get(i.get_class_name())
            tmp.add(i)
            file_info_obj.symbol_to_statement[i.get_class_name()] = tmp


    # If a list of functions was not included then parse all top level functions
    if not include_functions:
        include_functions = file_info_obj.global_functions.keys()


    # manual includes is a dictionary from function name to global statement
    for function_name in include_functions:
        # Create new parsed function obj
        p_function = parsed_function(function_name)

        # Start with a set that already includes the symbol for itself
        already_included_symbols = set([function_name])

        # All functions will need to start by including the actual function body
        # Some functions will also need to include the manually added statements
        needed_global_objects = set([file_info_obj.global_functions.get(function_name)])

        if remove_top_annotation:
            # IF we need to remove the annotation marking this function as a handler then we 
            # need to remove the first line for the function
            for item in needed_global_objects:
                item.decrement_line_number()

        # if the function has any manual statement includes
        # function_manual_includes is the dict from function name to the name of the manual include
        if function_name in function_manual_includes:
            for include in function_manual_includes.get(function_name):
                if not include in file_info_obj.include_overrides_glob:
                    raise InvalidDataError(f"""function_manual_includes param data issue: Trying to manually include '{include}' for function '{function_name} but '{include}' is not present in file""")
                    continue

                needed_global_objects.add(file_info_obj.include_overrides_glob.get(include))
        
        # global_manual_includes is a list of the names of manual includes that need to be added to every function
        for include in global_manual_includes:
            if not include in file_info_obj.include_overrides_glob:
                raise InvalidDataError(f"""function_manual_includes param data issue: Trying to manually include '{include}' as a global manual include but '{include}' is not present in file""")
                continue

            needed_global_objects.add(file_info_obj.include_overrides_glob.get(include))

        
        next_symbols = set()
        already_included_global_obj = set()

        
        for global_object in needed_global_objects:
            # Add the functions lines to the parsed function
            p_function.add_line_numbers(global_object.get_line_no())

            # Start with a set that already includes the global statement for itself
            already_included_global_obj.add(global_object)

            # next symbols is the set of symbols that need their dependant global statements
            next_symbols = next_symbols.union(file_info_obj.statement_to_symbol.get(global_object))

            # Some symbols won't be included in the mapping because they are excluded, but they need to be kept track of to look at imports
            all_used_symbols = set(
                [g.get_name() for g in global_object.get_symbols()])

        keep_looping = True
        remaining_symbols = set()

        while keep_looping:
            # If there are no more symbols than break the loop
            


            # Add the previous iterations symbols as already seen so they are not readded
            already_included_symbols = already_included_symbols.union(
                remaining_symbols)
            remaining_symbols = next_symbols

            if not next_symbols:
                break

            next_symbols = set()

            for sym in remaining_symbols:
                if sym in already_included_symbols:
                    # If we have already added this symbol than we have all of its dependencies
                    continue

                # Add all dependant global statements to this symbol needs to the need lines for the function
                for glob_obj in file_info_obj.symbol_to_statement.get(sym):
                    if glob_obj in already_included_global_obj:
                        #IF this global statement has already been added continue
                        continue

                    # Add the lines numbers and place it in the already included set
                    p_function.add_line_numbers(glob_obj.get_line_no())
                    already_included_global_obj.add(glob_obj)

                    # include this statements
                    all_used_symbols = all_used_symbols.union(
                        set(g.get_name() for g in glob_obj.get_symbols()))

                    # Get the set of symbols that this statement depends on
                    set_symbols = file_info_obj.statement_to_symbol.get(
                        glob_obj)
                    # Remove the symbols that have already been included
                    new_needed_symbols = set_symbols.difference(
                        already_included_symbols)
                    actual_new_needed_symbols = new_needed_symbols.difference(
                        remaining_symbols)

                    # Add the actually needed new symbols to the set of symbols to be looped over next
                    next_symbols = next_symbols.union(
                        actual_new_needed_symbols)

        #print(f"all pkg in file -> {file_info_obj.imported_symbol_to_global_statement}")
        for symbol in all_used_symbols:
            if symbol in file_info_obj.imported_symbol_to_global_statement and not symbol in EXCLUDED_SYMBOLS:
                p_function.add_import(
                    file_info_obj.imported_symbol_to_global_statement.get(symbol)
                )

        
        
        #finally add the parsed function object to the file info
        file_info_obj.add_parsed_functions(p_function)

    return file_info_obj


_individual_file_cache = {}
def _get_individual_files_imported_symbols(file_location):
    if file_location in _individual_file_cache:
        return _individual_file_cache.get(file_location)

    rv = set()
    
    with open(file_location, 'r') as fh:
        src_code = fh.readlines()
        fh.seek(0)

    ast_rep = ast.parse("".join(src_code))

    

    for node in ast.walk(ast_rep):
        
        if isinstance(node, ast.Import):
            for pkg_name in node.names:
                if not pkg_name.asname:
                    asname = pkg_name.name
                else:
                    asname = pkg_name.asname
                rv.add((asname, None))
    
        elif isinstance(node, ast.ImportFrom):
            # if the import has levels > 0 and no module it is a local referenced package and will already be included
            # if not then it is a package on the PYTHONPATH and we need to add it as a dependency
            
            
            for pkg_name in node.names:
                
                if node.level > 0:
                    if not node.module:
                        asmodule = f"{'.' * node.level}{pkg_name.name}"
                    else:
                        asmodule = f"{'.' * node.level}{node.module}"

                    rv.add((asmodule, file_location))

                else:
                    asmodule =  node.module
                    rv.add((asmodule, None))

    _individual_file_cache[file_location] = rv
                
    return rv




def get_file_imported_symbols(file_loc: FilePath):
    # Walk the whole dir/children importing all python files and then searching their symbol tree to find import statements
    rv = _get_individual_files_imported_symbols(file_loc)

    return rv


