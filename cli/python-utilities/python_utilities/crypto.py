import hashlib
import random
import string


def random_string(chars=string.ascii_uppercase + string.digits, n=10):
    return "".join(random.choice(chars) for _ in range(n))


FILE_READ_BUFFER_SIZE = 65536


def generate_checksum_from_file(file_path):
    """Calculates the checksum of a file"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(FILE_READ_BUFFER_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def generate_checksum_from_chunks(file_chunks):
    """Calculates the checksum of file chunks"""
    sha256 = hashlib.sha256()
    for chunk in file_chunks:
        sha256.update(chunk)
    return sha256.hexdigest()
