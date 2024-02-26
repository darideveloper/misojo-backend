def get_clean_file_name(name: str) -> str:
    """ Clean file name """
    
    # Remove special chars from pdf file path
    clean_chars = [
        "-",
        " ",
        "/",
        "\\",
        "?",
        "!",
        "'",
        '"',
        "(",
        ")",
        ";"
    ]
    name = name.replace(".pdf", "").strip().lower()
    for char in clean_chars:
        name = name.replace(char, "_")
        
    name = name.replace("__", "_")
    
    return name