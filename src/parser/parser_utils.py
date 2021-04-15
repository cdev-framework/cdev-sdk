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


def get_global_information(file_info_obj):
    if not isinstance(file_info_obj, file_information):
        raise Error

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
        file_info_obj.symbol_to_statement[item] = []

    file_ast = file_info_obj.get_ast()

    previous_node = None

    for node in file_ast.body:
        if previous_node:
            previous_node.set_last_line(node.lineno-1)
        
        current_node = global_statement(file_info_obj)
        current_node.set_start_line(node.lineno)

        file_info_obj.add_global_statement(current_node)

        previous_node = current_node

    # Set the last line of the last global statement to the last line of the file
    file_info_obj.get_global_statements()[-1].set_last_line(file_info_obj.get_file_length()+1)


    for i in file_info_obj.get_global_statements():
        i.create_symbol_table()

        syms = i.get_symbol_table().get_symbols()

        for sym in syms:
            if not file_info_obj.symbol_to_statement.get(sym.get_name()) is None:
                tmp = file_info_obj.symbol_to_statement.get(sym.get_name())
                tmp.append(i)
                file_info_obj.symbol_to_statement[sym.get_name()] = tmp

    
    for func in file_info_obj.function_names:
        print(f">>>>{func}")
        print(file_info_obj.symbol_to_statement.get(func))
        for s in file_info_obj.symbol_to_statement.get(func)[0].get_symbol_table().get_symbols():
            print(f"    {s}; {s.get_namespaces()[0].get_symbols()}")