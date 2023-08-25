import hashlib
import random
import string


def random_string(chars=string.ascii_uppercase + string.digits, n=10):
    return "".join(random.choice(chars) for _ in range(n))


CHECKSUM_BUFFER_SIZE = 65536


def generate_checksum(file_path):
    """Calculates the checksum of the own file"""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(CHECKSUM_BUFFER_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()
