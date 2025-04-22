import mimetypes

IMAGE_PREFIX = 'image/'
TEXT_PREFIX = 'text/'
PDF_MIME = 'application/pdf'

def get_mime_type(path):
    """
    Guess the MIME type based on file extension.
    Returns something like 'image/jpeg', 'text/plain', 'application/pdf', or None.
    """
    mime_type, encoding = mimetypes.guess_type(path)
    return mime_type
