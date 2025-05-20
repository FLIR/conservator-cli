from git import RemoteProgress

class SimpleProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
        print(self._cur_line)
