
class parsed_function():
    """
        This class represents the information for a parsed function, and it can be used to create an intermediate file with just
        that function.
    """

    original_file_location = ""
    
    need_line_numbers = set()

    import_statements = set()
