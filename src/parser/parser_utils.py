import symtable
import os


def get_global_function_symbols(src, file_loc):
    if not os.path.isfile(file_loc):
        raise FileNotFoundError(f"parser_utils: could not find file at -> {file_loc}")


    symbol_table = symtable.symtable(src, file_loc, 'exec').get_children()[0]
    print(type(symbol_table))
    symbols = symbol_table.get_symbols()

    _all_symbols_dict = {}
    for sym in symbol_table.get_symbols():
        _all_symbols_dict[sym.get_name()] = sym

    _local_symbols_dict = {}
    for sym in symbol_table.get_locals():
        _local_symbols_dict[sym] = sym
    

    _globals = { k : _all_symbols_dict[k] for k in set(_all_symbols_dict) - set(_local_symbols_dict) }


    return _globals

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
            print(f"{sym.get_name()}: {sym.is_imported()}; {sym.is_free()}; {sym.is_global()}; {sym.is_local()}")
            if not sym.is_imported() and not sym.is_free() and not sym.is_global():
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


def get_global_information(src, file_loc):
    if not os.path.isfile(file_loc):
        raise FileNotFoundError(f"parser_utils: could not find file at -> {file_loc}")

    symbol_table = symtable.symtable(src, file_loc, 'exec')

    try: 
        functions = _get_functions_in_symboltable(symbol_table)

        local_variables = _get_local_variables_in_symboltable(symbol_table)

        imported_symbols = _get_imported_variables_in_symboltable(symbol_table)
    except FileNotFoundError as e:
        print(e)

    print((functions, local_variables, imported_symbols))