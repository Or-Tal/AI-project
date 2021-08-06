from math import sqrt


class Lines:
    """Iterable wrapper allowing to access current item.
    """

    def __init__(self, lines):
        self.lines = iter(lines)
        self.current = next(self.lines)

    def __iter__(self):
        return self

    def __next__(self):
        self.current = next(self.lines)
        return self.current


class TSPLib:
    """Simple parser for TSPLIB files.
    """

    # Names of properties of integer type (all others are strings)
    _INT_PROPERTIES = ['DIMENSION']

    def __init__(self, file=None):
        self._lines = None
        self.specification = {}
        self.coords = []
        self.weights = None
        self.display = []

        if file:
            self.load(file)

    def load(self, file):
        """Loads lines from file, creates Lines iterable and starts parsing.

        :param string file: File to load.
        """

        with open(file, 'r') as f:
            self._lines = Lines(f.read().splitlines())

        self._parse()

    def _parse(self):
        """Iterates over lines and calls appropriate parses for each section
        of the file.
        """

        self.specification = {}

        while True:
            try:
                line = self._lines.current
                if ':' in line:
                    self.specification.update(self._parse_spec())
                elif line.startswith('NODE_COORD_SECTION'):
                    next(self._lines)
                    self.coords = self._parse_coords()
                elif line.startswith('EDGE_WEIGHT_SECTION'):
                    next(self._lines)
                    self.weights = self._parse_weights()
                elif line.startswith('DISPLAY_DATA_SECTION'):
                    next(self._lines)
                    self.display = self._parse_coords()
                else:
                    break
            except StopIteration:
                break

        del self._lines

    def _parse_spec(self):
        """Parses single line containing instance specification.

        :return: Single parsed specification.
        :rtype: dict
        """

        key, value = self._lines.current.split(':', 1)
        key, value = key.strip(), value.strip()
        value = int(value) if key in self._INT_PROPERTIES else value

        try:
            next(self._lines)
        except StopIteration:
            pass

        return {key: value}

    def _parse_coords(self):
        """Parses contents of NODE_COORD_SECTION or DISPLAY_DATA_SECTION.

        :return: Parsed coordinates.
        :rtype: list
        """

        coords = []

        while True:
            try:
                _, x, y = self._lines.current.split()
                coords.append((float(x), float(y)))
            except ValueError:
                break

            try:
                next(self._lines)
            except StopIteration:
                break

        return coords

    def _parse_weights(self):
        """Parses contents of EDGE_WEIGHT_SECTION.

        :return: Parsed weights.
        :rtype: list
        """

        # Initialize weights matrix
        weights = [[-1 for _ in range(self.specification['DIMENSION'])]
                   for _ in range(self.specification['DIMENSION'])]

        # Cell coordinates iterator
        cells = self._cells()

        while True:
            for value in self._lines.current.split():
                try:
                    weight = int(value)
                    row, col = next(cells)
                    weights[row][col] = weight
                except (ValueError, StopIteration):
                    return weights

            try:
                next(self._lines)
            except StopIteration:
                break

        return weights

    def _cells(self):
        """Generates consecutive matrix cells coordinates.
        """

        # Matrix size
        size = self.specification['DIMENSION']
        # Edge weight format
        edge_format = self.specification['EDGE_WEIGHT_FORMAT'].split('_')
        # Matrix type: FULL, UPPER, LOWER
        matrix = edge_format[0]

        # Data direction: ROW, COL; diagonal offset
        offset = 0
        if matrix != 'FULL':
            if edge_format[1] in ['ROW', 'COL']:
                direction = edge_format[1]
                # No diagonal entries, matrix needs to be offseted by 1
                offset = 1
            else:
                direction = edge_format[2]

        # Initial position in the matrix
        row = col = -1

        # Increments `b`. If `b` is larger than `bound` increments `a` and
        # sets `b` to `ret`.
        def calc(a, b, bound, ret):
            a = max(a, 0)
            b += 1
            if b > bound:
                a += 1
                b = ret
            return a, max(b, ret)

        # Generate the coordinates
        while True:
            if matrix == 'FULL':
                row, col = calc(row, col, size - 1, 0)
            elif matrix == 'UPPER' and direction == 'ROW':
                row, col = calc(row, col, size - 1, row + 1 + offset)
            elif matrix == 'LOWER' and direction == 'COL':
                col, row = calc(col, row, size - 1, col + 1 + offset)
            elif matrix == 'LOWER' and direction == 'ROW':
                row, col = calc(
                    row, col, row - offset if offset else max(row, 0), 0)
            elif matrix == 'UPPER' and direction == 'COL':
                col, row = calc(
                    col, row, col - offset if offset else max(col, 0), 0)

            # End when all coordinates are generated
            if row >= size or col >= size:
                break

            yield row, col

    def weight(self, i, j):
        """Calculates weight of the edge between specified nodes basing on
        EDGE_WEIGHT_TYPE property.

        :param int i: Index of the first node.
        :param int j: Index of the second node.
        :return: Weight of the edge.
        :rtype: int
        """

        if self.specification['EDGE_WEIGHT_TYPE'] == 'EXPLICIT':
            return (self.weights[i][j] if self.weights[i][j] != -1 else
                    self.weights[j][i])
        elif self.specification['EDGE_WEIGHT_TYPE'] == 'EUC_2D':
            return self._w_euc_2d(i, j)
        else:
            raise TypeError('Unsupported edge weight type.')

    def _w_euc_2d(self, i, j):
        """Calculates euclidean distance between nodes.
        """

        xd = self.coords[i][0] - self.coords[j][0]
        yd = self.coords[i][1] - self.coords[j][1]
        return self._nint(sqrt(xd ** 2 + yd ** 2))

    @staticmethod
    def _nint(x):
        """Rounds number to the nearest integer.

        :param float x: Number to round.
        :return: Nearest integer.
        :rtype int:
        """

        return int(x + 0.5)


class TSPLibTour:
    """Simple parser and writer for TSPLIB .tour files.
    """

    # Names of properties of integer type (all others are strings)
    _INT_PROPERTIES = ['DIMENSION']

    def __init__(self, file=None):
        # Initialize fileds
        self._lines = None
        self.specification = {}
        self.tour = []

        # Load from file if file is given
        if file:
            self.load(file)

    def load(self, file):
        """Loads lines from file, creates Lines iterable and starts parsing.

        :param string file: File to load.
        """

        with open(file, 'r') as f:
            self._lines = Lines(f.read().splitlines())

        self._parse()

    @classmethod
    def from_path(cls, path):
        """Creates TSPLibTour object from given path.

        :param Path path: Path to convert to TSPLibTour.
        :return: Tour coverted from path.
        :rtype: TSPLibTour
        """

        obj = cls()
        # TSPLib counts cities from 1, we start from 0
        tour = [s + 1 for s in path]
        # TSPLib doesn't include return to the starting city
        if tour[0] == tour[-1]:
            tour = tour[:-1]
        obj.tour = tour

        return obj

    def write(self, file):
        """Writes TSPLibTour to the file.
        """

        # Initialize output buffer
        out = ''

        # Print specification
        for key, value in self.specification.items():
            out += f'{key} : {value}\n'

        # Print the tour
        if self.tour:
            out += 'TOUR_SECTION\n'
            for s in self.tour:
                out += str(s) + '\n'
            out += '-1\n'

        # Append EOF
        out += 'EOF\n'

        # Write to file
        with open(file, 'w') as f:
            f.write(out)

    def _parse(self):
        """Iterates over lines and calls appropriate parses for each section
        of the file.
        """

        self.specification = {}

        while True:
            try:
                line = self._lines.current
                if ':' in line:
                    self.specification.update(self._parse_spec())
                elif line.startswith('TOUR_SECTION'):
                    next(self._lines)
                    self.tour = self._parse_tour()
                else:
                    break
            except StopIteration:
                break

        del self._lines

        if 'TYPE' in self.specification and \
                self.specification['TYPE'] != 'TOUR':
            raise TypeError('Unsupported TSPLib file type. Only TOUR type \
                            is supported')

    def _parse_spec(self):
        """Parses single line containing instance specification.

        :return: Single parsed specification.
        :rtype: dict
        """

        key, value = self._lines.current.split(':', 1)
        key, value = key.strip(), value.strip()
        value = int(value) if key in self._INT_PROPERTIES else value

        try:
            next(self._lines)
        except StopIteration:
            pass

        return {key: value}

    def _parse_tour(self):
        """Parses TOUR_SECTION of the tour file.
        """

        tour = []

        while True:
            try:
                s = int(self._lines.current)
                if s == -1:
                    return tour
                tour.append(s)
            except ValueError:
                break

            try:
                next(self._lines)
            except StopIteration:
                break

        return tour
