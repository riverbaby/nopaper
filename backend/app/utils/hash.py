"""Hash utilities"""
import hashlib
from pathlib import Path


def sha256_file(file_path: str | Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Calculate SHA256 hash of bytes"""
    return hashlib.sha256(data).hexdigest()
