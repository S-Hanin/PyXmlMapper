class Default:
    def __init__(self, default=None):
        self.default = default

    def __getattr__(self, item):
        return self.default

    def __bool__(self):
        return False
