from collections import OrderedDict


class AssertNoOverwriteOrderedDict(OrderedDict):

    def __init__(self, assert_error_message="Key already exists", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assert_error_message = assert_error_message

    def __setitem__(self, key, value):
        assert key not in self, f"{self.assert_error_message}: {key}"
        super().__setitem__(key, value)
