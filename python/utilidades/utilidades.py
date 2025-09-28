import re

import pycurl
from io import BytesIO

# Expresión regular para validar email (básica pero efectiva)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def descargar_imagen_con_curl(url):
    """
    Descarga una imagen usando pycurl y devuelve el contenido binario.
    """
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(c.TIMEOUT, 30)
    c.setopt(c.SSL_VERIFYPEER, False)
    c.setopt(c.SSL_VERIFYHOST, False)
    try:
        c.perform()
        http_code = c.getinfo(c.RESPONSE_CODE)
        c.close()
        if http_code == 200:
            return buffer.getvalue()
        else:
            raise Exception(f"Error al descargar la imagen (HTTP {http_code})")
    except Exception as e:
        c.close()
        raise Exception(f"Error al descargar la imagen: {str(e)}")