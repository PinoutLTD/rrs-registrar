def read_file(file_path: str) -> bytes:
    """Read file and return its content

    :param file_path: Path to the file to read
    :return: File's content in bytes
    """

    with open(file_path, "rb") as f:
        data = f.read()
    return data
