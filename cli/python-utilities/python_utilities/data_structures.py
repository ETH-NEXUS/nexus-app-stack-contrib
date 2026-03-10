from collections import OrderedDict


class LazyDict(dict):
    def __init__(self, factory):
        super().__init__()
        assert hasattr(self, "_factory") is False
        self._factory = factory
        assert hasattr(self, "_loaded") is False
        self._loaded = False
        assert hasattr(super(), "_load") is False

    def _load(self):
        if not self._loaded:
            self.update(self._factory())
            self._loaded = True

    def __getitem__(self, key):
        self._load()
        return super().__getitem__(key)

    def get(self, key, default=None):
        self._load()
        return super().get(key, default)

    def __contains__(self, key):
        self._load()
        return super().__contains__(key)


class AssertNoOverwriteOrderedDict(OrderedDict):

    def __init__(self, assert_error_message="Key already exists", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assert_error_message = assert_error_message

    def __setitem__(self, key, value):
        assert key not in self, f"{self.assert_error_message}: {key}"
        super().__setitem__(key, value)
