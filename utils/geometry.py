from math import hypot, sin, cos, radians

EPS = 1e-7

data = [
    400, 300, 20, 
    9, 295, 22, 286, 22, 286, 142, 375, 142, 375, 23, 391, 23, 391, 9, 295,
    152, 96, 155, 93, 155, 93, 229, 30, 229, 30, 186, 132, 186, 132, 152, 96,
    61, 225, 138, 184, 138, 184, 158, 205, 158, 205, 82, 297, 82, 297, 61, 225,
    619, 325, 716, 304, 716, 304, 768, 494, 768, 494, 747, 485, 747, 485, 619, 325,
    0, 0, 799, 0, 799, 0, 799, 599, 799, 599, 0, 599, 0, 599, 0, 0
]


class Point:
    def __init__(self, *args):
        if isinstance(args[0], Point):
            self.x, self.y = args[0].x, args[0].y
        elif isinstance(args[0], int | float) and isinstance(args[1], int | float):
            if len(args) == 3 and args[2] == True:
                self.x, self.y = args[0] * cos(args[1]), args[0] * sin(args[1])
            else:
                self.x, self.y = args[0], args[1]
        else:
            raise TypeError("Wrong input type for Point")

    def __abs__(self) -> tuple | float:
        return self.dist()

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
    def dist(self, *args) -> tuple | float:
        if not args:
            x2 = y2 = 0
        elif isinstance(args[0], Point | Vector):
            x2, y2 = args[0].x, args[0].y
        elif len(args) == 2 and isinstance(args[0], int | float) and isinstance(args[1], int | float):
            x2, y2 = args
        else:
            raise TypeError("Wrong input for dist")
        return hypot(self.x - x2, self.y - y2)


class Vector(Point):
    def __init__(self, *args: int | float | Point, inp: bool = True):
        if len(args) == 1 and isinstance(args[0], Point):
            super().__init__(args[0].x, args[0].y)
        elif len(args) == 2 and isinstance(args[0], Point) and isinstance(args[1], Point):
            super().__init__(args[1].x - args[0].x, args[1].y - args[0].y)
        elif len(args) == 2 and isinstance(args[0], int | float) and isinstance(args[1], int | float):
            super().__init__(args[0], args[1])
        elif len(args) == 4 and all(isinstance(i, int | float) for i in args):
            super().__init__(args[2] - args[0], args[3] - args[1])
        else:
            raise TypeError("Wrong input type for Vector")

    def __mul__(self, other: "int | float | Vector") -> "int| float | Vector":
        if isinstance(other, int | float):
            return Vector(self.x * other, self.y * other)
        elif isinstance(other, Vector):
            return self.dot_product(other)
        else:
            raise TypeError("Wrong input type for Vector")
        
    def __rmul__(self, other) -> "float | Vector":
        return self * other
    
    def __xor__(self, other: "Vector") -> float:
        return self.cross_product(other)
    
    def __repr__(self) -> ...:
        return f"Vector{self}"
    
    def dot_product(self, other: "Vector") -> float:
        return self.x * other.x + self.y * other.y
    
    def cross_product(self, other: "Vector") -> float:
        return self.x * other.y - self.y * other.x


class Line:
    def __init__(self, *args: int | float | Vector | Point):
        if len(args) == 3 and all(isinstance(i, int | float) for i in args):
            self.a, self.b, self.c = args
        elif len(args) == 1 and isinstance(args[0], Vector):
            self.a, self.b, self.c = self.line_equation(0, 0, args[0].x, args[0].y)
        elif len(args) == 4 and all(isinstance(i, int | float) for i in args):
            self.a, self.b, self.c = self.line_equation(args[0], args[1], args[2], args[3])
        elif len(args) == 2 and all(isinstance(i, Point) for i in args):
            self.a, self.b, self.c = self.line_equation(args[0].x, args[0].y, args[1].x, args[1].y)
        else:
            raise TypeError("Wrong input type for Line")
        
    def line_equation(self, *args) -> tuple:
        if len(args) == 4 and all(isinstance(i, int | float) for i in args):
            x1, y1, x2, y2 = args
            return y2 - y1, x1 - x2, -(y2 - y1) * x2 - (x1 - x2) * y2
        elif len(args) == 3 and all(isinstance(i, int | float) for i in range(2)) and isinstance(args[2], Vector):
            return args[2].x, args[2].y, args[2].x * args[0] - args[2].y * args[1]
        elif len(args) == 2 and isinstance(args[0], Point) and isinstance(args[1], Vector):
            return args[1].x, args[1].y, args[1].x * args[0].x - args[1].y * args[0].y
        else:
            raise TypeError("Wrong input type for line_equation")
    
    def dist_from_dot(self, *args) -> float:
        if len(args) == 1 and isinstance(args[0], Point):
            return abs(self.a * args[0].x + self.b * args[0].y + self.c) / hypot(self.a, self.b)
        elif len(args) == 2 and all(isinstance(i, int) for i in args):
            return abs(self.a * args[0] + self.b * args[1] + self.c) / hypot(self.a, self.b)
        else:
            raise TypeError("Wrong input for dist_from_dot")

    def is_dot_on_line(self, *args) -> bool:
        if len(args) == 2 and all(isinstance(i, int) for i in args):
            if self.a * args[0] + self.b * args[1] + self.c == 0:
                return True
        elif len(args) == 1 and isinstance(args[0], Point):
            if self.a * args[0].x + self.b * args[0].y + self.c < 1e-9:
                return True
        return False
    
    def is_collinear(self, other: "Line") -> bool:
        return abs(self.a * other.b - other.a * self.b) < EPS


class Ray():
    def __init__(self, *args, inp: bool = True):
        if inp:
            if len(args) == 2 and all(isinstance(i, Point) for i in args):
                self.center = args[0]
                self.radius = args[1]
            elif len(args) == 3 and all(isinstance(i, int | float) for i in args):
                self.center = Point(args[0], args[1])
                self.radius = Point(args[0] + cos(radians(args[2])), args[1] + sin(radians(args[2])))
            else:
                raise TypeError("Wrong input type for Ray")
        else:
            raise TypeError("No input for ray")
        
class Segment:
    def __init__(self, a: Point, b: Point, inp=True):
        if inp:
            self.A = a
            self.B = b
        else:
            raise TypeError("No input for segment")

def crossRS(r: Ray, s: Segment) -> Vector | None:
    ray_line = Line(r.center, r.radius)
    seg_line = Line(s.A, s.B)

    ray_vec = Vector(r.radius.x - r.center.x, r.radius.y - r.center.y)
    seg_vec = Vector(s.B.x - s.A.x, s.B.y - s.A.y)
    
    oA = Vector(r.center, s.A)
    oB = Vector(r.center, s.B)
    rA = Vector(r.radius, s.A)
    rB = Vector(r.radius, s.B)

    if abs(ray_vec ^ seg_vec) <= EPS: #паралелльны
        if abs(oA ^ ray_vec) <= EPS: #коллиниарны
            if oA * oB > EPS and rA * rB > EPS:
                if r.center.dist(s.A) < r.center.dist(s.B): #OABR
                    if oA * ray_vec < -EPS: #за лучом
                        return None
                    return s.A
                else: #OBAR
                    if oB * ray_vec < -EPS: #за лучом
                        return None
                    return s.B
            elif oA * oB > EPS and not rA * rB > EPS:
                if r.center.dist(s.A) < r.center.dist(s.B): #OARB
                    if oA * ray_vec < -EPS: #за лучом
                        return None
                    return s.A
                else: #OBRA
                    if oB * ray_vec < -EPS: #за лучом
                        return None
                    return s.B
            elif not oA * oB > EPS and rA * rB > EPS: #AORB
                return r.center
            else: #BORA
                return r.center
        else:
            return None
    else:
        if abs(ray_line.a * seg_line.b - seg_line.a * ray_line.b) <= EPS:
            return None

        px = (ray_line.b * seg_line.c - seg_line.b * ray_line.c) / (ray_line.a * seg_line.b - seg_line.a * ray_line.b)
        py = (seg_line.a * ray_line.c - ray_line.a * seg_line.c) / (ray_line.a * seg_line.b - seg_line.a * ray_line.b)

        oP = Vector(r.center, Vector(px, py))
        aP = Vector(s.A, Point(px, py))
        bP = Vector(s.B, Point(px, py))

        if oP * ray_vec < -EPS: #за лучом
            return None
        if aP * bP > EPS: #не на отрезке
            return None
        
        return Vector(px, py)