# -*- coding: utf-8 -*-

from queue import Queue, Empty
from threading import Thread

from core.helpers.decode import OutputDecoder

"""
Helper classes to manage streams
"""


class OutputReader(object):
    """
    Non-blocking stream reader.
    Uses in WebConsole.
    """

    def __init__(self, stream):
        """
        Creates thread which wait data from stream and put they in inter-thread queue
        :param stream: stream to read
        """
        # input stream to read
        self.stream = stream
        # inter-thread queue to pass data from stream
        self.queue = Queue()
        # stream-read thread
        self.thread = Thread(target=self.wait_output)
        self.thread.daemon = True
        self.thread.start()
        self.decoder = OutputDecoder()

    def wait_output(self):
        """
        Reading thread entry point
        """
        for line in iter(self.stream.readline, b''):
            self.queue.put(line)
        self.stream.close()

    def read_nowait(self):
        """
        Non-blocking read from stream.
        :return: string from stream
        """
        result = []
        try:
            for i in range(0, 100):
                # get bytes from inter-thread queue
                b = self.queue.get_nowait()
                if b:
                    # decode bytes to string
                    s = self.decoder.try_decode(b)
                    s = s.rstrip()
                    result.append(s)
        except Empty:
            pass
        # add empty line to add \n at the end of result
        result.append('')
        # join result list of string to string
        return '\n'.join(result)


