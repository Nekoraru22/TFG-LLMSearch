import mimetypes
import hashlib


IMAGE_PREFIX = 'image/'
TEXT_PREFIX = 'text/'
PDF_MIME = 'application/pdf'

def get_mime_type(path: str) -> str | None:
    """
    Guess the MIME type based on file extension.
    Returns something like 'image/jpeg', 'text/plain', 'application/pdf', or None.
    """
    mime_type, _ = mimetypes.guess_type(path)
    return mime_type


def get_file_hash(path: str) -> str:
    """
    Calcula el hash MD5 del archivo en 'path'.

    Args:
        path: Ruta del archivo a calcular el hash.
    """
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
