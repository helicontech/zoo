# -*- coding: utf-8 -*-


class OutputDecoder(object):
    """Decode bytes from stdout of process to string. Uses in install worker process and web console."""

    def __init__(self, encoding_names=None):
        # Order encodings to try
        self.encoding_names = encoding_names or ['utf-8', 'cp866']

    def try_decode(self, b: bytes) -> str:
        """
        Tries decode bytes with encodings and returns string.
        :param b: bytes to decode
        :return: decoded string
        """
        for encoding in self.encoding_names:
            try:
                return b.decode(encoding)
            except:
                pass
        return b.decode(self.encoding_names[0], errors='replace')
