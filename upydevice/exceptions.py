

class DeviceException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return '[DeviceError]:\n{0} '.format(self.message)
        else:
            return 'DeviceError has been raised'


class DeviceNotFound(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return '[DeviceNotFound]:\n{0} '.format(self.message)
        else:
            return 'DeviceNotFound has been raised'
