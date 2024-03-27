from collections.abc import Sequence


class LazySequence(Sequence):
    def __init__(self, sequence):
        self._sequence = sequence

    def __getitem__(self, i):
        value = self._sequence[i]
        if callable(value):
            return value()
        return value

    def __len__(self):
        return len(self._sequence)
