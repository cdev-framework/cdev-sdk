import symtable
import os




def get_global_function_symbols(src, file_loc):
    if not os.path.isfile(file_loc):
        return False


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

def get_global_module_symbols(src, file_loc):
    if not os.path.isfile(file_loc):
        return False


    symbol_table = symtable.symtable(src, file_loc, 'exec')


    symbols = symbol_table.get_symbols()

    for sym in symbols:
        print(f"{sym.get_name()}: {sym.is_imported()}; {sym.is_namespace()}; {sym.is_global()}")

    print(symbol_table.get_namespaces())
