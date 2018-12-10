from typing import List


class Point2d(object):
    _TOLERANCE = 0.0000001

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        elif abs((self.x - other.x)) < self._TOLERANCE and abs((self.y - other.y)) < self._TOLERANCE:
            return True
        else:
            return False

    def __repr__(self):
        return "(%f, %f)" % (self.x, self.y)


class Edge(object):
    def __init__(self, A: Point2d, B: Point2d):
        if A == B:
            ValueError("An edge of zero length is invalid.")
        self.A = A
        self.B = B

    @property
    def points(self)-> List[Point2d]:
        return [self.A, self.B]

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        elif self.A == other.A:
            if self.B == other.B:
                return True

        elif self.A == other.B:
            if self.B == other.A:
                return True

        return False

    def __repr__(self):
        return "<%s, %s>" % (self.A, self.B)


class Simplex(object):
    def __init__(self, A: Point2d, B: Point2d, C: Point2d):
        if points_are_in_line(A, B, C):
            ValueError("Points for simplex are on a straight line")
        self.A = A
        self.B = B
        self.C = C
        self.edge_A = Edge(B, C)
        self.edge_B = Edge(A, C)
        self.edge_C = Edge(A, B)

    @classmethod
    def from_edges(cls, A: Edge, B: Edge, C: Edge):
        points = [A.A, A.B, B.A, B.B, C.A, C.B]
        uniques = []
        add_point = True
        for point in points:
            for unique in uniques:
                if point == unique:
                    add_point = False
            if add_point:
                uniques.append(point)
            add_point = True

        if len(uniques) != 3:
            ValueError("The group of edges given does not form a closed triangle.")

        return cls(uniques[0], uniques[1], uniques[2])

    @classmethod
    def from_point_and_edge(cls, E: Edge, P: Point2d):
        return cls(E.A, E.B, P)

    @property
    def edges(self)-> List[Edge]:
        return [self.edge_A, self.edge_B, self.edge_C]

    @property
    def points(self):
        return [self.A, self.B, self.C]

    def has_edge(self, e: Edge)-> bool:
        for edge in self.edges:
            if e == edge:
                return True
        return False

    def has_point(self, pt: Point2d)-> bool:
        for point in self.points:
            if pt == point:
                return True
        return False

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        counter = 0
        for point in self.points:
            if other.has_point(point):
                counter += 1

        return counter == 3

    def __repr__(self):
        return "<%s, %s, %s>" % (self.A, self.B, self.C)


def point2d_distance(pt1: Point2d, pt2: Point2d) -> float:
    x = abs(pt1.x - pt2.x)
    y = abs(pt1.y - pt2.y)
    return (x ** 2 + y ** 2) ** 0.5


def points_are_in_line(A: Point2d, B: Point2d, C: Point2d) -> bool:
    if A.x == B.x:  # Check vertical lines
        return A.x == C.x

    return abs((((B.y - A.y)/(B.x - A.x))*(C.x - A.x) + A.y) - C.y) <= A._TOLERANCE


def simplex_circumcircle(triangle: Simplex) -> (Point2d, float):
    return threePointCircleToCenterRad(triangle.A, triangle.B, triangle.C)


def threePointCircleToCenterRad(A: Point2d, B: Point2d, C: Point2d) -> (Point2d, float):
    """

    :param A: Point2d object
    :param B: Point2d object
    :param C: Point2d object
    :return: (centerPoint: Point2d, radius: Decimal)
    """

    if A == B or A == C or points_are_in_line(A, B, C):
        raise ValueError("Points are coincident or on a straight line")
    elif A.y == B.y:  # A and B are on a vertical line
        slopeBC = - (C.x - B.x) / (C.y - B.y)
        xMidBC = (B.x + C.x) / 2
        yMidBC = (B.y + C.y) / 2
        center_x = (B.x + A.x) / 2
        center_y = slopeBC * (center_x - xMidBC) + yMidBC
    elif C.y == B.y:  # B and C are on a vertical line
        slopeAB = (-1) * (B.x - A.x) / (B.y - A.y)
        xMidAB = (A.x + B.x) / 2
        yMidAB = (A.y + B.y) / 2
        center_x = (A.x + B.x) / 2
        center_y = slopeAB * (center_x - xMidAB) + yMidAB
    else:  # The normal case
        slopeAB = (-1) * (B.x - A.x) / (B.y - A.y)
        slopeBC = (-1) * (C.x - B.x) / (C.y - B.y)
        xMidAB = (A.x + B.x) / 2
        xMidBC = (B.x + C.x) / 2
        yMidAB = (A.y + B.y) / 2
        yMidBC = (B.y + C.y) / 2
        center_x = (slopeAB * xMidAB - slopeBC * xMidBC + yMidBC - yMidAB) / (slopeAB - slopeBC)
        if abs(A.y - B.y) > abs(B.y - C.y):
            center_y = slopeAB * (center_x - xMidAB) + yMidAB
        else:
            center_y = slopeBC * (center_x - xMidBC) + yMidBC

    centerPoint = Point2d(center_x, center_y)
    radius = point2d_distance(centerPoint, A)

    return centerPoint, radius


def isInSimplexCircumcircle(test: Point2d, triangle: Simplex)-> bool:
    return isInCircle(test, triangle.A, triangle.B, triangle.C)


def isInCircle(test: Point2d, A: Point2d, B: Point2d, C: Point2d) -> bool:
    """

    The boolean is True if point 'test' is within the circumcircle created by A, B, and C.
    The point is considered inside if it lies on the circle.

    """
    # TODO: more error checking

    if A == B or A == C or points_are_in_line(A, B, C):
        raise ValueError("Points are coincident or on a straight line")

    center, radius = threePointCircleToCenterRad(A, B, C)

    return point2d_distance(center, test) <= radius


def triangulate(vertices: List[Point2d]) -> List[Simplex]:
    # create a giant triangle that encompasses all the points

    if len(vertices) < 3:
        return []

    if len(vertices) == 3:
        return [Simplex(vertices[0], vertices[1], vertices[2])]

    points = sorted(sorted(vertices, key=lambda pt: pt.x, reverse=True), key=lambda pt: pt.y)

    triangles = []

    maxX = 0
    maxY = 0
    minX = 0
    minY = 0

    for point in points:
        if point.x > maxX:
            maxX = point.x
        if point.x < minX:
            minX = point.x
        if point.y > maxY:
            maxY = point.y
        if point.y < minY:
            minY = point.y

    x_span = maxX - minX
    y_span = maxY - minY
    sqrt_3 = 3 ** 0.5

    # To be safe from rounding, and avoiding straight line errors...
    safetyX = x_span * 0.01
    safetyY = y_span * 0.01

    minX -= safetyX
    maxX += safetyX
    x_span += 2*safetyX

    minY -= safetyY
    maxY += safetyY
    y_span += 2*safetyY

    # super triangle!
    supertriangle = Simplex(
        Point2d(minX - y_span * sqrt_3 * (1/3), minY),
        Point2d(maxX + y_span * sqrt_3 * (1/3), minY),
        Point2d((minX + maxX) * 0.5, maxY + x_span * sqrt_3 * 0.5)
    )
    print(supertriangle)
    triangles.append(supertriangle)

    # for each point, see if it falls in a particular triangles circumcircle.
    # Since we start out with a triangle that encompasses every point, getting started won't be a problem
    # And it'll guarantee that every point, when added, falls inside a triangle's circumcircle
    # If it does fall inside a triangles circumcircle, it's not a valid delaunay triangulation
    # Break all triangles into edges that meet this criteria, then create new triangles from those edges
    # Since the points are sorted on an axis, no criss-corssing of edges will occur either.
    for point in points:
        edge_set = []
        triangle_set = []

        for triangle in triangles:
            if isInSimplexCircumcircle(point, triangle):
                for edge in triangle.edges:
                    edge_set.append(edge)
            else:
                triangle_set.append(triangle)

        triangles = triangle_set

        unique_edges = []
        for edge in edge_set:
            is_unique = True
            for unique in unique_edges:
                if edge == unique:
                    is_unique = False
            if is_unique:
                unique_edges.append(edge)
            else:
                unique_edges.remove(edge)

        for edge in unique_edges:
            triangles.append(Simplex.from_point_and_edge(edge, point))

    # Remove all the triangles from the supertriangle
    out = []
    for triangle in triangles:
        if triangle.has_point(supertriangle.A) or triangle.has_point(supertriangle.B) or triangle.has_point(supertriangle.C):
            pass
        else:
            out.append(triangle)
    return out


if __name__ == "__main__":
    points = [
        Point2d(0.927888, 3.526930),
        Point2d(4.495172, 9.022303),
        Point2d(1.694921, 8.037935),
        Point2d(3.531021, 4.142644),
        Point2d(7.839869, 5.763940),
    ]

    triangles = triangulate(points)

    with open('out.txt', 'w') as f:
        for t in triangles:
            f.write(str(t) + '\n')
