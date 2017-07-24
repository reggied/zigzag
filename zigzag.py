# zigzag engine as I understand it after an explanation by Ted Nelson

from collections import defaultdict
from enum import Enum, auto


class ConnectionError(Exception):
    pass


class Direction(Enum):
    POS = auto()
    NEG = auto()

    @property
    def other(self):
        return self.POS if self.value == self.NEG.value else self.NEG


class Tissue(dict):
    def __init__(self):
        self.key = 0

    def next_key(self):
        key = self.key
        self.key += 1
        return key

    def start(self, value):
        key = self.next_key()
        self[key] = cell = Cell(key, value)
        return cell

    def delete(self, cell):
        self.pop(cell.key).cross_connect()

    def add(self, cell, dimension, value, direction=Direction.POS):
        key = self.next_key()
        self[key] = cell = self[cell.key].add(key, value, dimension, direction)
        return cell


class Cell:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.connectors = defaultdict(lambda: dict((d, None)
                                                   for d in Direction))

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

    def connect(self, cell, dimension, direction, new=True):
        my_connectors = self.connectors[dimension]
        step_fwd = my_connectors[direction]
        other_connectors = cell.connectors[dimension]
        step_back = other_connectors[direction.other]

        # Make sure to keep consistency if a connection is being replaced
        if step_fwd not in (None, cell):
            if new:
                raise ConnectionError(f'Connection already exists: {step_fwd}')
            else:
                step_fwd.connectors[dimension][direction.other] = None
        if step_back not in (None, self):
            if new:
                raise ConnectionError(
                    f'Connection already exists: {step_back}'
                )
            else:
                step_back.connectors[dimension][direction] = None

        my_connectors[direction] = cell
        other_connectors[direction.other] = self

    def add(self, key, value, dimension, direction=Direction.POS):
        new_cell = Cell(key, value)
        self.connect(new_cell, dimension, direction)
        return new_cell

    def cross_connect(self):
        for dimension, connectors in self.connectors.items():
            neg = connectors[Direction.NEG]
            positive = Direction.POS
            neg.connect(connectors[positive], dimension, positive, new=False)

    def next_step(self, dimension, direction=Direction.POS):
        return self.connectors[dimension].get(direction)


if __name__ == '__main__':
    geneology = Tissue()
    liz = geneology.start('Elizabeth II')
    charles = geneology.add(liz, 'generation', 'Charles')
    ann = geneology.add(charles, 'sibling', 'Ann')
    ann.connect(liz, 'generation', Direction.NEG, new=False)
    andrew = geneology.add(ann, 'sibling', 'Andrew')
    geneology.add(andrew, 'sibling', 'Edward')
    george = geneology.add(liz, 'generation', 'George VI', Direction.NEG)
    geneology.add(george, 'generation', 'Victoria', Direction.NEG)
    geneology.delete(andrew)
