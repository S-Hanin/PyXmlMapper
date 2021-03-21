class Default:
    def __init__(self, default=None):
        self.value = default

    def __getattr__(self, item):
        return self.value

    def __bool__(self):
        return False

    def __eq__(self, other):
        if not isinstance(other, Default):
            return False
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)