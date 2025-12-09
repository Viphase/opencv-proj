import math

EPS = 1e-7

class Point:
    def __init__(self, x, y, polar=False):
        if polar:
            rad = math.radians(y)
            self.x = x * math.cos(rad)
            self.y = x * math.sin(rad)
            self.angle = y % 360
        else:
            self.x, self.y = x, y
            self.angle = (math.degrees(math.atan2(self.y, self.x)) + 360) % 360

    def dist(self, *a):
        if not a:
            x, y = 0, 0
        elif len(a) == 2:
            x, y = a
        elif isinstance(a[0], Point):
            x, y = a[0].x, a[0].y
        else:
            raise ValueError("Invalid args")
        return math.hypot(self.x - x, self.y - y)

    def __eq__(self, other):
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

class Vector(Point):
    def __init__(self, *args, polar=False):
        if not polar:
            if len(args) == 1 and isinstance(args[0], Point):
                super().__init__(args[0].x, args[0].y)
            elif len(args) == 2 and all(isinstance(a, (int, float)) for a in args):
                super().__init__(*args)
            elif len(args) == 4 and all(isinstance(a, (int, float)) for a in args):
                super().__init__(args[2] - args[0], args[3] - args[1])
            elif len(args) == 2 and all(isinstance(a, Point) for a in args):
                super().__init__(args[1].x - args[0].x, args[1].y - args[0].y)
            else:
                raise ValueError("Invalid arguments for Vector constructor")
        else:
            super().__init__(args[0], args[1])

    def find_angle(self, other):
        angle_cos = (self * other) / (self.dist() * other.dist())
        return math.degrees(math.acos(angle_cos))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other)
        elif isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        else:
            raise TypeError("Unsupported operand for *")

    def __xor__(self, other):
        return self.x * other.y - self.y * other.x

class Line:
    def __init__(self, *args):
        if len(args) == 2 and all(isinstance(i, Point) for i in args):
            x1, y1 = args[0].x, args[0].y
            x2, y2 = args[1].x, args[1].y
            self.A = y2 - y1
            self.B = x1 - x2
            self.C = x2*y1 - x1*y2
        elif len(args) == 3:
            self.A, self.B, self.C = args

class Ray:
    def __init__(self, start=None, point=None, angle=None, polar=False):
        if polar:
            self.start = Point(*start)
            self.angle = angle
            dx = math.cos(math.radians(self.angle))
            dy = math.sin(math.radians(self.angle))
            self.point = Point(self.start.x + dx, self.start.y + dy)
        else:
            self.start = Point(*start)
            self.point = Point(*point)
            self.angle = math.degrees(math.atan2(self.point.y - self.start.y, self.point.x - self.start.x))

class Segment:
    def __init__(self, start=None, end=None):
        self.start = Point(*start)
        self.end = Point(*end)

    def contain_point(self, point):
        v_start = Vector(self.start, point)
        v_end = Vector(self.end, point)
        return (v_start ^ v_end < EPS and v_start * v_end <= EPS) or self.start == point or self.end == point

class StartPoint(Point):
    def __init__(self, x, y):
        super().__init__(x, y)

def crossRS(r: Ray, s: Segment):
    r_line = Line(r.start, r.point)
    seg_line = Line(s.start, s.end)
    v_ray = Vector(r.start, r.point)
    v_seg_end = Vector(r.start, s.end)
    if abs(seg_line.A * r_line.B - r_line.A * seg_line.B) >= EPS:
        x = (seg_line.B * r_line.C - seg_line.C * r_line.B) / (seg_line.A * r_line.B - r_line.A * seg_line.B)
        y = (r_line.C * seg_line.A - seg_line.C * r_line.A) / (r_line.A * seg_line.B - seg_line.A * r_line.B)
    else:
        if s.contain_point(r.start):
            x, y = r.start.x, r.start.y
        elif v_ray ^ v_seg_end == 0 and v_ray * v_seg_end > 0:
            if Segment((r.start.x, r.start.y), (s.start.x, s.start.y)).contain_point(s.end):
                x, y = s.end.x, s.end.y
            else:
                x, y = s.start.x, s.start.y
        else:
            return None
    result_v = Vector(r.start.x, r.start.y, x, y)
    if s.contain_point(Point(x, y)) and (v_ray ^ result_v < EPS and v_ray * result_v >= -EPS):
        return Vector(x, y)
    return None
