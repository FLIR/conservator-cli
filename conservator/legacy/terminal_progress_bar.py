import os


# Wraps a File so we can print the progress as requests uploads the file
class ProgressFileWrapper:
    def __init__(self, filename, mode,
                 cb_args=(),
                 cb_kwargs={}):
        file = open(filename, mode)
        size = os.path.getsize(filename)
        self._cb_args = cb_args
        self._cb_kwargs = cb_kwargs
        self._progress = 0
        self._len = size
        self._file = file
        self.mode = file.mode
        # io.BytesIO.__init__(self, buf)

    def __len__(self):
        return self._len

    def __iter__(self):
        return self

    def tell(self):
        return self._file.tell()

    def seek(self, offset, whence=0):
        return self._file.seek(offset, whence)

    def read(self, size=-1):
        data = self._file.read(size)
        num_bytes_read = len(data)
        if num_bytes_read:
            self._progress += num_bytes_read
        printProgressBar(self._progress, self._len, "Upload Progress:", "Complete", 1, 50)
        return data

