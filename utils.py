import logging
import base64
import re
import validators


def setup_logger():
    logging.basicConfig(format='%(levelname)s (%(asctime)s): %(message)s',
                        datefmt='%d/%m/%y %H:%M:%S',
                        level=logging.DEBUG)
    logger = logging.getLogger("httpx").setLevel(logging.WARNING)
    return logger


# Function to go around readdressing
def decode_url(encoded_url):
    start_index = encoded_url.find("articles/") + len("articles/")
    end_index = encoded_url.find("?", start_index)
    encoded_url = encoded_url[start_index:end_index]

    padding = len(encoded_url) % 4
    if padding:
        encoded_url += '=' * (4 - padding)

    decoded_bytes = base64.b64decode(encoded_url)
    decoded_url = decoded_bytes.decode('latin-1')
    pattern = r'[A-Za-z0-9:/._-]'
    cleaned_string = ''.join(re.findall(pattern, decoded_url))

    start = cleaned_string.find('http')
    target_url = str(cleaned_string[start:])
    logging.info(f'Decoded url : {target_url}')
    return target_url


def valid_url(url):
    if not url.startswith('http://'): url = 'http://' + url
    return True if validators.url(url) else False

