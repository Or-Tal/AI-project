import os
from enum import Enum
from operator import itemgetter
from random import shuffle

from tspvisual.tsplib import TSPLib, TSPLibTour


class TSP:
    """Internal representation of a Travelling Salesman Problem instance.

    Contains a few properties (name, type, comment, dimension), coordinates
    of cities and distance matrix.
    """

    def __init__(self, file=None):
        self._tsplib = None
        self.specification = {}
        self.coords = []
        self.distances = []
        self.display = []
        self.opt_tour = None
        self.opt_path = None

        if file is not None:
            self.load(file)

    def load(self, file):
        """Load TSPLIB file and read necessary data.

        :param string file: File to load.
        """

        self._tsplib = TSPLib(file)

        if self._tsplib.specification['TYPE'] not in ['TSP', 'ATSP']:
            raise TypeError('Unsupported problem. Only TSP and ATSP instances '
                            'are supported.')

        self.specification = self._tsplib.specification
        self.coords = self._tsplib.coords
        self.display = (self._tsplib.display if self._tsplib.display
                        else self.coords if self.coords else None)

        self._calc_distances()

        if self.display:
            self._norm_display()

        del self._tsplib

        self._load_opt_tour(file)

    @property
    def name(self):
        """Returns this instance' name from the specification.
        """

        return (self.specification['NAME'] if 'NAME' in self.specification
                else None)

    @property
    def dimension(self):
        """Returns this instance' dimension from the specification.
        """

        return (self.specification['DIMENSION'] if 'DIMENSION' in
                self.specification else None)

    def _calc_distances(self):
        """Calculate distance matrix using TSPLib weight function.
        """

        for i in range(self.dimension):
            row = []
            for j in range(self.dimension):
                row.append(self._tsplib.weight(i, j))
            self.distances.append(row)

    def _norm_display(self):
        """Translates and normalizes display coordinats for easier drawing.
        """

        # Find lowest X and Y values
        min_x = min(self.display, key=itemgetter(0))[0]
        min_y = min(self.display, key=itemgetter(1))[1]
        # Translate points to the (0, 0)
        self.display = [(c[0] - min_x, c[1] - min_y) for c in self.display]
        # Find maximum and normalize to [0, 1] values
        maximum = max(map(max, self.display))
        self.display = [(c[0] / maximum, c[1] / maximum) for c in self.display]

    def _load_opt_tour(self, file):
        """Loads optimal tour file (.opt.tour) if it's in the same directory as
        the instance.

        Also converts the TSPLibTour object to Path for easier use.
        """

        tour_filename = os.path.splitext(file)[0] + '.opt.tour'
        if os.path.isfile(tour_filename):
            self.opt_tour = TSPLibTour(tour_filename)
            self.opt_path = Path.from_tour(self.opt_tour)
            self.opt_path.distance = self.path_dist(self.opt_path)

    def dist(self, i, j):
        """Returns the distance between two cities.

        :param int i: Index of the first city.
        :param int j: Index of the second city.
        :return: The distance.
        :rtype: int
        """

        return self.distances[i][j]

    def path_dist(self, path):
        """Calculates total distance of a given path.

        :param Path path: Path to calculate distance of.
        :return: The distance of a path.
        :rtype: int
        """

        total = 0

        for i in range(path.length - 1):
            total += self.dist(path[i], path[i + 1])

        return total


# Available path neighbourhood types
Neighbourhood = Enum('Neighbourhood', 'SWAP INSERT INVERT')


class Path:
    """Representation of a path in TSP.

    Contains length of the path (number of visited cities), list of
    a consecutive city numbers and optionally path distance.

    Cities at specified stops can be accessed like in list since __setitem__
    and __getitem__ are implemented.
    """

    def __init__(self, length=0, path=None):
        self._path = [-1] * length if path is None else path
        self.length = length if path is None else len(path)
        self.distance = -1

    @classmethod
    def from_tour(cls, tour):
        """Creates Path from TSPLibTour object.
        """

        # TSPLIB starts indexing cities from 1, we start from 0
        path = [s - 1 for s in tour.tour]

        # TSPLIB doesn't store explicit return to the start, but we check just
        # in case before adding it
        if path[0] != path[-1]:
            path.append(path[0])

        return cls(path=path)

    @property
    def path(self):
        """Sequence of numbers representing consecutive cities visited in path.
        """

        return self._path

    @path.setter
    def path(self, path):
        """Sets the entire path to given sequence.

        :param list path: List of consecutive stops.
        """

        if len(path) != self.length:
            raise ValueError('Incorrect path length.')

        self._path = path

    def shuffle(self, i, j):
        """Shuffles specified slice of the path.

        :param int i: Index of the first stop in the slice.
        :param int j: Index of the last stop in the slice.
        """

        part = self._path[i:j]
        shuffle(part)
        self._path[i:j] = part

    def in_path(self, city, limit=None):
        """Checks whether specified city is in the first n elements of the path.

        :param int city: City to look for.
        :param int limit: Number of path stops to search.
        :return: True if the city was found.
        :rtype: bool
        """

        return city in self._path[:limit]

    def swap(self, i, j):
        """Swaps cities at a specified path stops.

        :param int i: Index of the first stop.
        :param int j: Index of the second stop.
        """

        self._path[i], self._path[j] = self._path[j], self._path[i]

    def insert(self, i, j):
        """Inserts one stop in the place of the other, shifts other stops.

        :param int i: Index of the first stop.
        :param int j: Index of the second stop.
        """

        new_j = self._path[i]

        while i > j:
            self._path[i] = self._path[i - 1]
            i = i - 1

        while i < j:
            self._path[i] = self._path[i + 1]
            i = i + 1

        self._path[j] = new_j

    def invert(self, i, j):
        """Reverses order of stops of specified slice of the path.

        :param int i: Index of the first stop.
        :param int j: Index of the second stop.
        """

        if i > j:
            i, j = j, i

        while i < j:
            self.swap(i, j)
            i = i + 1
            j = j - 1

    def move(self, neigh, i, j):
        """Performs move specified by a given neighbourhood type on i, j stops
        in this path.

        :param Neighbourhood neigh: Neighbourhood type.
        :param int i: Index of the first stop.
        :param int j: Index of the second stop.
        """

        moves = {
            Neighbourhood.SWAP: self.swap,
            Neighbourhood.INSERT: self.insert,
            Neighbourhood.INVERT: self.invert
        }

        moves[neigh](i, j)

    def __setitem__(self, stop, city):
        """Sets specified stop in path to given city.
        """

        self._path[stop] = city

    def __getitem__(self, stop):
        """Returns city at a specified stop in path.
        """

        return self._path[stop]

    def __len__(self):
        """Returns path's length.
        """

        return self.length

    def __str__(self):
        """Returns human-readable representation of the path.
        """

        string = ''
        for stop in self._path:
            string += f'{stop}, '

        string = string[:-2] + f' ({self.distance})'

        return string
