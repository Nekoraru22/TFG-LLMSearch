import mimetypes
import os

IMAGE_PREFIX = 'image/'
TEXT_PREFIXES = ('text/', 'application/pdf')

def get_mime_type(path):
    """
    Guess the MIME type based on file extension.
    Returns something like 'image/jpeg', 'text/plain', 'application/pdf', or None.
    """
    mime_type, encoding = mimetypes.guess_type(path)
    return mime_type

def classify_file(path):
    """
    Return 'image', 'text', or 'unknown' depending on the guessed mime type.
    Treat PDFs as 'text'.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such file: {path!r}")
    mime = get_mime_type(path)
    if mime is None:
        return 'unknown'
    if mime.startswith(IMAGE_PREFIX):
        return 'image'
    if any(mime.startswith(pref) for pref in TEXT_PREFIXES):
        return 'text'
    return 'unknown'

# Example usage:
if __name__ == '__main__':
    for fname in ['filesystem/gato_prueba.jpeg', 'filesystem/Notificacion_1742000847864.pdf', 'filesystem/meowtext.txt', 'filesystem/gato_prueba.rar']:
        kind = classify_file(fname)
        print(f"{fname}: {kind}")
