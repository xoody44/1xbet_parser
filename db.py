from os.path import abspath
from shlex import quote


def trim_db(max_lines: int = 300, trim_lines: int = 280):
    db_path = quote(abspath("db.txt")).replace("'", "")
    with open(db_path, 'r') as file:
        lines = file.readlines()

    if len(lines) > max_lines:
        remaining_lines = lines[trim_lines:]

        with open(db_path, 'w') as file:
            file.writelines(remaining_lines)
            