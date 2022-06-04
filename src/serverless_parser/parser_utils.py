import ast
import os
from sys import modules, version_info

from typing import Dict, List, Set, Tuple, Union
from pydantic.types import FilePath


from .parser_objects import *
from .parser_exceptions import (
    InvalidParamError,
    CouldNotParseFileError,
    CdevFileNotFoundError,
    InvalidDataError,
)

EXCLUDED_SYMBOLS = set(["print"])

line_type = Union[ast.stmt, ast.expr]


def parse_line_numbers(
    objs: List[line_type], final_line: int
) -> List[Tuple[line_type, Tuple[int, int]]]:
    rv = []
    previous_info = None
    for node in objs:
        # _tmp_global_information[node] = [node.lineno, node.end_lineno]
        if previous_info:
            previous_name, previous_start_line = previous_info
            line_nos = (previous_start_line, node.lineno - 1)
            rv.append((previous_name, line_nos))

        previous_info = (node, node.lineno)

    # Set the last line of the last global statement to the last line of the file
    previous_name, previous_start_line = previous_info
    line_nos = (previous_start_line, final_line)
    rv.append((previous_name, line_nos))

    return rv


def find_ending_line(
    file_info_obj: file_information,
    start_line: int,
    end_line: int,
    line_start_match: str,
) -> int:
    for i in range(start_line + 1, end_line):
        tmp = file_info_obj.get_lines_of_source_code(i, i)

        if tmp.startswith(line_start_match):
            return i

    raise Exception("Should not end loop without returning")


def _get_global_variables_in_symboltable(table) -> Set:
    if not isinstance(table, symtable.SymbolTable):
        raise InvalidParamError(
            f"Invalid Param in _get_functions_in_symboltable: Expected symtable.SymbolTable got {type(table)}"
        )

    symbols = table.get_symbols()

    rv_variables = set()

    for sym in symbols:
        # Check all symbols to see if they are not a namespace. Check if the symbol is a global.
        if not sym.is_namespace():
            if sym.is_global():
                rv_variables.add(sym.get_name())

    return rv_variables


def _get_imported_variables_in_symboltable(table) -> Set:
    # TODO Change error that is raised
    if not isinstance(table, symtable.SymbolTable):
        raise InvalidParamError(
            f"Invalid Param in _get_functions_in_symboltable: Expected symtable.SymbolTable got {type(table)}"
        )

    symbols = table.get_symbols()

    rv_variables = set()

    for sym in symbols:
        # Check all symbols to see if they are not a namespace. If not then they are a normal symbols for this symboltable.
        if not sym.is_namespace():
            if sym.is_imported():
                rv_variables.add(sym.get_name())

    return rv_variables


def _get_local_variables_in_symboltable(table) -> Set:
    if not isinstance(table, symtable.SymbolTable):
        raise InvalidParamError(
            f"Invalid Param in _get_functions_in_symboltable: Expected symtable.SymbolTable got {type(table)}"
        )

    symbols = table.get_symbols()

    rv_variables = set()

    for sym in symbols:
        # Check all symbols to see if they are not a namespace. If not then they are a normal gloabl variable for this symboltable.
        if not sym.is_namespace():
            if not sym.is_imported() and not sym.is_free() and not sym.is_global():
                rv_variables.add(sym.get_name())

    return rv_variables


def _get_functions_in_symboltable(table) -> Set:
    if not isinstance(table, symtable.SymbolTable):
        raise InvalidParamError(
            f"Invalid Param in _get_functions_in_symboltable: Expected symtable.SymbolTable got {type(table)}"
        )

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


def _get_global_class_definitions_in_symboltable(table) -> Set:
    if not isinstance(table, symtable.SymbolTable):
        raise InvalidParamError(
            f"Invalid Param in _get_functions_in_symboltable: Expected symtable.SymbolTable got {type(table)}"
        )

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


def _generate_global_statement(
    file_info_obj: file_information,
    ast_node: ast.NodeVisitor,
    line_info: List[str],
    remove_annotation_functions: Set[str] = set(),
) -> None:
    # This function is used to determine the type of global statement the node is and create the corresponding global statement obj

    last_line = line_info[1]

    manual_include = False
    manual_include_sym = ""

    # Need to adjust the starting line if using python3.8 or greater
    start_line = line_info[0]

    if isinstance(ast_node, ast.FunctionDef) and ast_node.decorator_list:
        # Since python < 3.8 does not include the end_line info on an ast.node, we need to handle removing the top annotation differently
        if version_info < (3, 8):
            if not ast_node.name in remove_annotation_functions:
                start_line = ast_node.decorator_list[0].lineno

            else:
                # Since we have no way of know when the first decorator ends because there is not end_lineno property,
                # we have to check each line below it to see if it is either the function declaration ('def ') or
                # the next annotation definition ('@')
                match_line = "def " if len(ast_node.decorator_list) == 1 else "@"

                # search for the next definition based on the match_line and search at longest til you get to the first line of the body of the function
                start_line = find_ending_line(
                    file_info_obj,
                    ast_node.decorator_list[0].lineno,
                    ast_node.body[0].lineno,
                    match_line,
                )
        else:
            # for python>=3.8
            start_line = (
                ast_node.decorator_list[0].end_lineno + 1
                if ast_node.name in remove_annotation_functions
                else ast_node.decorator_list[0].lineno
            )

    # Look one line above the start for a manual include
    for k in file_info_obj.include_overrides_lineno:
        if file_info_obj.include_overrides_lineno.get(k) == start_line - 1:
            manual_include = True
            manual_include_sym = k
            break

    tmp_src_code = file_info_obj.get_lines_of_source_code(start_line, last_line)

    tmp_symbol_table = symtable.symtable(
        tmp_src_code, file_info_obj.file_location, "exec"
    )

    need_to_check_function = False
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
            if isinstance(single_symbol.get_namespaces()[0], symtable.Function):

                name = single_symbol.get_name()

                function_symbols = set(
                    [
                        x.get_name()
                        for x in single_symbol.get_namespaces()[0].get_symbols()
                    ]
                )

                function_symbols.update(
                    set([x.get_name() for x in tmp_symbol_table.get_symbols()])
                )

                fs = FunctionStatement(
                    ast_node, [start_line, last_line], list(function_symbols), name
                )
                file_info_obj.add_global_function(name, fs)

                if manual_include:
                    file_info_obj.include_overrides_glob[manual_include_sym] = fs

                return

    if need_to_check_class_def:

        class_def_table = tmp_symbol_table.get_children()[0]

        class_def = ClassDefinitionStatement(
            ast_node,
            [start_line, last_line],
            [x.get_name() for x in class_def_table.get_symbols()],
            class_def_table.get_name(),
        )
        file_info_obj.add_class_definition(class_def_table.get_name(), class_def)
        return

    ts = {s.get_name() for s in tmp_symbol_table.get_symbols()}

    used_imported_symbols = file_info_obj.imported_symbols.intersection(ts)
    if len(used_imported_symbols) > 0:
        # This statement uses an imported symbol so we need to check it to see if it is the import statement
        for n in ast.walk(ast_node):
            # print(n)
            if isinstance(n, ast.Import):
                # print(f"IMPORT: {n}")
                # print(f"FIELDS { [(cn.name, cn.asname)  for cn in n.names] }")
                for imprt in n.names:
                    # print(f"FIELDS: {imprt.name}; {imprt.asname}")
                    if not imprt.asname:
                        asname = imprt.name
                    else:
                        asname = imprt.asname

                    imp_statement = ImportStatement(
                        ast_node,
                        [start_line, last_line],
                        [x.get_name() for x in tmp_symbol_table.get_symbols()],
                        asname,
                        imprt.name,
                    )

                    # print(f"{ast.dump(n)} -> {asname}?{imprt.name}")
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
                        asmodule = n.module

                    # print(f"{ast.dump(n)} -> {asname}?{asmodule}")
                    imp_statement = ImportStatement(
                        ast_node,
                        [start_line, last_line],
                        [x.get_name() for x in tmp_symbol_table.get_symbols()],
                        asname,
                        asmodule,
                    )

                    file_info_obj.add_global_import(imp_statement)
                continue

    global_statement_obj = GlobalStatement(
        ast_node,
        [start_line, last_line],
        [x.get_name() for x in tmp_symbol_table.get_symbols()],
    )

    file_info_obj.add_global_statement(global_statement_obj)

    if manual_include:
        file_info_obj.include_overrides_glob[manual_include_sym] = global_statement_obj


def get_file_information(
    file_path: str,
    include_functions: List[str] = [],
    function_manual_includes: Dict[str, str] = {},
    global_manual_includes: List[str] = [],
    remove_top_annotation: bool = False,
) -> file_information:
    if not os.path.isfile(file_path):
        raise CouldNotParseFileError(
            CdevFileNotFoundError(f"cdev_parser: could not find file at -> {file_path}")
        )

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

    for item in (
        functions.union(local_variables)
        .union(imported_symbols)
        .union(global_symbols)
        .union(class_definitions)
    ):
        file_info_obj.symbol_to_statement[item] = set()

    file_info_obj.set_imported_symbols(imported_symbols)

    # Need to get the line range of each global statement, but this requires looping over all the global nodes in the ast
    # in the top level of the file.
    #
    # Python3.8 introduced node.end_lineno to ast nodes, which makes it easier to get the ending line info
    #
    # To support earlier versions of python (<3.8) we must use the starting line of
    # the next statement as the last line of previous node. We are going to store this info in a tmp dict then
    # once we have all the information create the objects

    file_ast = file_info_obj.get_ast()

    # dict<ast.node, [line1,line2]>
    _tmp_global_information = {}

    # sys.version_info
    if version_info < (3, 8):
        _tmp_global_information = dict(
            parse_line_numbers(file_ast.body, file_info_obj.get_file_length() + 1)
        )
    else:
        for node in file_ast.body:
            _tmp_global_information[node] = [node.lineno, node.end_lineno]

    remove_function_annotations = (
        set(include_functions) if remove_top_annotation else set()
    )
    # Now that the information has been collected for the global statements, we can create the actual objs and add
    # them to the file_info_obj
    for node, line_info in _tmp_global_information.items():
        _generate_global_statement(
            file_info_obj, node, line_info, remove_function_annotations
        )

    # Build a two-way binding of a symbol to statement and a statement to a symbol.
    # This information is needed to get all dependencies of symbols, which is needed
    # to reconstruct just the necessary lines
    for i in file_info_obj.get_global_statements():
        syms = i.get_symbols()

        for sym in syms:
            if not sym in file_info_obj.symbol_to_statement:
                continue

            # Some symbols do no create a dependency so they should not be added
            if sym in EXCLUDED_SYMBOLS:
                continue

            # Add all the symbols in the statement to the list for this global statement. This means when this global object
            # is used we need to include all of these symbols
            if i in file_info_obj.statement_to_symbol:
                tmp = file_info_obj.statement_to_symbol.get(i)
                tmp.add(sym)
                file_info_obj.statement_to_symbol[i] = tmp

            # Since this global statement is a top level function... the code that effects this symbol within it will only execute if the
            # function itself is called. Therefor, other functions can use this symbol without depending on this function.
            if i.get_type() == GlobalStatementType.FUNCTION:
                continue

            tmp = file_info_obj.symbol_to_statement.get(sym)
            tmp.add(i)
            file_info_obj.symbol_to_statement[sym] = tmp

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

        # if the function has any manual statement includes
        # function_manual_includes is the dict from function name to the name of the manual include
        if function_name in function_manual_includes:
            for include in function_manual_includes.get(function_name):
                if not include in file_info_obj.include_overrides_glob:
                    raise InvalidDataError(
                        f"""function_manual_includes param data issue: Trying to manually include '{include}' for function '{function_name} but '{include}' is not present in file"""
                    )

                needed_global_objects.add(
                    file_info_obj.include_overrides_glob.get(include)
                )

        # global_manual_includes is a list of the names of manual includes that need to be added to every function
        for include in global_manual_includes:
            if not include in file_info_obj.include_overrides_glob:
                raise InvalidDataError(
                    f"""function_manual_includes param data issue: Trying to manually include '{include}' as a global manual include but '{include}' is not present in file"""
                )

            needed_global_objects.add(file_info_obj.include_overrides_glob.get(include))

        next_symbols = set()
        already_included_global_obj = set()

        for global_object in needed_global_objects:
            # Add the functions lines to the parsed function
            p_function.add_line_numbers(global_object.get_line_no())

            # Start with a set that already includes the global statement for itself
            already_included_global_obj.add(global_object)

            # next symbols is the set of symbols that need their dependant global statements
            next_symbols = next_symbols.union(
                file_info_obj.statement_to_symbol.get(global_object)
            )

            # Some symbols won't be included in the mapping because they are excluded, but they need to be kept track of to look at imports
            all_used_symbols = set(global_object.get_symbols())

        keep_looping = True
        remaining_symbols = set()

        while keep_looping:
            # If there are no more symbols than break the loop

            # Add the previous iterations symbols as already seen so they are not readded
            already_included_symbols = already_included_symbols.union(remaining_symbols)
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
                        # IF this global statement has already been added continue
                        continue

                    # Add the lines numbers and place it in the already included set
                    p_function.add_line_numbers(glob_obj.get_line_no())
                    already_included_global_obj.add(glob_obj)

                    # include this statements
                    all_used_symbols = all_used_symbols.union(
                        set(glob_obj.get_symbols())
                    )

                    # Get the set of symbols that this statement depends on
                    set_symbols = file_info_obj.statement_to_symbol.get(glob_obj)
                    # Remove the symbols that have already been included
                    new_needed_symbols = set_symbols.difference(
                        already_included_symbols
                    )
                    actual_new_needed_symbols = new_needed_symbols.difference(
                        remaining_symbols
                    )

                    # Add the actually needed new symbols to the set of symbols to be looped over next
                    next_symbols = next_symbols.union(actual_new_needed_symbols)

        # print(f"all pkg in file -> {file_info_obj.imported_symbol_to_global_statement}")
        for symbol in all_used_symbols:
            if (
                symbol in file_info_obj.imported_symbol_to_global_statement
                and not symbol in EXCLUDED_SYMBOLS
            ):
                p_function.add_import(
                    file_info_obj.imported_symbol_to_global_statement.get(symbol)
                )

        # finally add the parsed function object to the file info
        file_info_obj.add_parsed_functions(p_function)

    return file_info_obj


_individual_file_cache = {}


def _get_individual_files_imported_symbols(file_location) -> Set:
    if file_location in _individual_file_cache:
        return _individual_file_cache.get(file_location)

    rv = set()

    with open(file_location, "r") as fh:
        src_code = fh.readlines()
        fh.seek(0)

    ast_rep = ast.parse("".join(src_code))

    for node in ast.walk(ast_rep):

        if isinstance(node, ast.Import):
            for pkg_name in node.names:

                asname = (
                    pkg_name.name.split(".")[0]
                    if not pkg_name.name.startswith(".")
                    else pkg_name.name
                )

                rv.add(asname)

        elif isinstance(node, ast.ImportFrom):
            # IF the import has a named module then it can either be a relative or absolute import
            # If the import does not have a named module, it must be a relative import

            if node.module:
                asname = (
                    node.module.split(".")[0]
                    if node.level == 0
                    else f"{node.level * '.'}{node.module}"
                )
                rv.add(asname)

            else:
                [rv.add(f"{node.level * '.'}{x.name}") for x in node.names]

    _individual_file_cache[file_location] = rv

    return rv


def get_file_imported_symbols(file_loc: FilePath) -> Set:
    # Walk the whole dir/children importing all python files and then searching their symbol tree to find import statements
    rv = _get_individual_files_imported_symbols(file_loc)

    return rv
