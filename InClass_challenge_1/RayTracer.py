import numpy as np
from PIL import Image
import multiprocessing as mp

CANVAS_WIDTH = 1500
CANVAS_HEIGHT = 1500
VIEWPORT_WIDTH = 1
VIEWPORT_HEIGHT = 1
PROJECTION_PLANE_D = 1
BACKGROUND_COLOR = (0, 0, 0)

class Light:
    def __init__(self, type, intensity, position=None, direction=None):
        self.type = type
        self.intensity = intensity
        self.position = position
        self.direction = direction

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    def cross(self, other):
        return Vector3(self.y * other.z - self.z * other.y,
                       self.z * other.x - self.x * other.z,
                       self.x * other.y - self.y * other.x)
    def scale(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    def to_tuple(self):
        return (self.x, self.y, self.z)
    def __truediv__(self, scalar):
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    def length(self):
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)
    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector3(0, 0, 0)
        return self / l
    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

class Sphere:
    def __init__(self, center, radius, color, specular, reflective):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular
        self.reflective = reflective

class Cylinder:
    def __init__(self, center, radius, height, color, specular, reflective):
        self.center = center
        self.radius = radius
        self.height = height
        self.color = color
        self.specular = specular
        self.reflective = reflective

class Triangle:
    def __init__(self, v0, v1, v2, color):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.color = color

def canvas_to_viewport(x, y):
    return Vector3(x * VIEWPORT_WIDTH / CANVAS_WIDTH,
                   y * VIEWPORT_HEIGHT / CANVAS_HEIGHT,
                   PROJECTION_PLANE_D)

def intersect_ray_sphere(origin, direction, sphere):
    CO = origin - sphere.center
    a = direction.dot(direction)
    b = 2 * CO.dot(direction)
    c = CO.dot(CO) - sphere.radius ** 2
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return float('inf'), float('inf')
    t1 = (-b + np.sqrt(discriminant)) / (2 * a)
    t2 = (-b - np.sqrt(discriminant)) / (2 * a)
    return t1, t2

def intersect_ray_cylinder(origin, direction, cylinder):
    Ox, Oy, Oz = origin.x, origin.y, origin.z
    Dx, Dy, Dz = direction.x, direction.y, direction.z
    Cx, Cy, Cz = cylinder.center.x, cylinder.center.y, cylinder.center.z
    r = cylinder.radius
    h = cylinder.height
    t_min = np.inf
    hit_normal = None
    A = Dx**2 + Dz**2
    B = 2 * ((Ox - Cx) * Dx + (Oz - Cz) * Dz)
    C_val = (Ox - Cx)**2 + (Oz - Cz)**2 - r**2
    discriminant = B**2 - 4 * A * C_val
    if A != 0 and discriminant >= 0:
        sqrt_disc = np.sqrt(discriminant)
        t1 = (-B - sqrt_disc) / (2 * A)
        t2 = (-B + sqrt_disc) / (2 * A)
        for t in [t1, t2]:
            if t > 0:
                P = origin + direction * t
                if Cy - h/2 <= P.y <= Cy + h/2:
                    if t < t_min:
                        t_min = t
                        normal_side = Vector3(P.x - Cx, 0, P.z - Cz).normalize()
                        hit_normal = normal_side
    for cap_y, cap_normal in [(Cy + h/2, Vector3(0, 1, 0)), (Cy - h/2, Vector3(0, -1, 0))]:
        if Dy != 0:
            t_cap = (cap_y - Oy) / Dy
            if t_cap > 0:
                P_cap = origin + direction * t_cap
                if (P_cap.x - Cx)**2 + (P_cap.z - Cz)**2 <= r**2:
                    if t_cap < t_min:
                        t_min = t_cap
                        hit_normal = cap_normal
    return t_min, hit_normal

def intersect_ray_triangle(origin, direction, triangle):
    EPSILON = 1e-6
    v0 = triangle.v0
    v1 = triangle.v1
    v2 = triangle.v2
    edge1 = v1 - v0
    edge2 = v2 - v0
    h = direction.cross(edge2)
    a = edge1.dot(h)
    if abs(a) < EPSILON:
        return float('inf')
    f = 1.0 / a
    s = origin - v0
    u = f * s.dot(h)
    if u < 0.0 or u > 1.0:
        return float('inf')
    q = s.cross(edge1)
    v = f * direction.dot(q)
    if v < 0.0 or u + v > 1.0:
        return float('inf')
    t = f * edge2.dot(q)
    if t > EPSILON:
        return t
    return float('inf')

def ClosestIntersection(origin, direction, t_min_val, t_max, objects):
    closest_t = np.inf
    closest_obj = None
    closest_normal = None
    for obj in objects:
        if isinstance(obj, Sphere):
            t1, t2 = intersect_ray_sphere(origin, direction, obj)
            if t_min_val <= t1 <= t_max and t1 < closest_t:
                closest_t = t1
                closest_obj = obj
                closest_normal = None
            if t_min_val <= t2 <= t_max and t2 < closest_t:
                closest_t = t2
                closest_obj = obj
                closest_normal = None
        elif isinstance(obj, Cylinder):
            t, normal = intersect_ray_cylinder(origin, direction, obj)
            if t_min_val <= t <= t_max and t < closest_t:
                closest_t = t
                closest_obj = obj
                closest_normal = normal
        elif isinstance(obj, Triangle):
            t = intersect_ray_triangle(origin, direction, obj)
            if t_min_val <= t <= t_max and t < closest_t:
                closest_t = t
                closest_obj = obj
                edge1 = obj.v1 - obj.v0
                edge2 = obj.v2 - obj.v0
                closest_normal = edge1.cross(edge2).normalize()
    return closest_obj, closest_t, closest_normal

def reflect_ray(R, N):
    return N.scale(2 * N.dot(R)) - R

def computeLighting(P, N, V, s, lights, objects):
    i = 0.0
    for light in lights:
        L = None
        t_max = None
        if light.type == "ambient":
            i += light.intensity
        elif light.type == "point" and light.position is not None:
            L = light.position - P
            t_max = 1
        elif light.type == "directional" and light.direction is not None:
            L = light.direction
            t_max = np.inf
        if L is not None:
            shadow_obj, shadow_t, _ = ClosestIntersection(P, L, 0.001, t_max, objects)
            if shadow_obj is not None:
                continue
            L = L.normalize()
            n_dot_l = N.dot(L)
            if n_dot_l > 0:
                i += light.intensity * n_dot_l
            if s != -1:
                R = N.scale(2 * N.dot(L)) - L
                R = R.normalize()
                r_dot_v = R.dot(V)
                if r_dot_v > 0:
                    i += light.intensity * (r_dot_v ** s)
    return i

def trace_ray(origin, direction, t_min_val, t_max, objects, lights, recursion_depth):
    closest_obj, t, normal = ClosestIntersection(origin, direction, t_min_val, t_max, objects)
    if closest_obj is None:
        return BACKGROUND_COLOR
    P = origin + direction * t
    if isinstance(closest_obj, Sphere):
        N = (P - closest_obj.center).normalize()
    elif isinstance(closest_obj, Cylinder):
        N = normal
    elif isinstance(closest_obj, Triangle):
        N = normal
    else:
        N = Vector3(0, 0, 0)
    local_color = tuple(min(255, int(c * computeLighting(P, N, -direction, closest_obj.specular, lights, objects))) for c in closest_obj.color)
    r = closest_obj.reflective
    if recursion_depth <= 0 or r <= 0:
        return local_color
    R = reflect_ray(-direction, N)
    reflected_color = trace_ray(P, R, 0.001, float('inf'), objects, lights, recursion_depth - 1)
    final_color = tuple(min(255, int(local_color[i] * (1 - r) + reflected_color[i] * r)) for i in range(3))
    return final_color

def interpolate(i0, d0, i1, d1):
    if i1 == i0:
        return [d0]
    steps = int(i1 - i0)
    result = []
    for i in range(steps + 1):
        value = d0 + (d1 - d0) * i / steps
        result.append(value)
    return result

def draw_filled_triangle(tri, canvas):
    P0, P1, P2 = tri.v0, tri.v1, tri.v2
    vertices = [P0, P1, P2]
    vertices.sort(key=lambda p: (p.y, p.x))
    P0, P1, P2 = vertices
    y0 = int(round(P0.y))
    y1 = int(round(P1.y))
    y2 = int(round(P2.y))
    x0 = int(round(P0.x))
    x1 = int(round(P1.x))
    x2 = int(round(P2.x))
    x01 = interpolate(y0, x0, y1, x1)
    x12 = interpolate(y1, x1, y2, x2)
    x02 = interpolate(y0, x0, y2, x2)
    if len(x01) > 0:
        x01 = x01[:-1]
    x012 = x01 + x12
    m = len(x012) // 2
    if x02[m] < x012[m]:
        x_left = x02
        x_right = x012
    else:
        x_left = x012
        x_right = x02
    for y in range(y0, y2 + 1):
        idx = y - y0
        x_l = int(round(x_left[idx]))
        x_r = int(round(x_right[idx]))
        for x in range(x_l, x_r + 1):
            canvas.putpixel((x, y), tri.color)

def load_obj(filename, color, specular, reflective, scale=1.0, offset=None):
    if offset is None:
        offset = Vector3(0, 0, 0)
    vertices = []
    triangles = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.strip().split()
                x, y, z = map(float, parts[1:4])
                vertex = Vector3(x * scale + offset.x, y * scale + offset.y, z * scale + offset.z)
                vertices.append(vertex)
            elif line.startswith('f '):
                parts = line.strip().split()
                indices = []
                for part in parts[1:]:
                    idx = int(part.split('/')[0]) - 1
                    indices.append(idx)
                for i in range(1, len(indices) - 1):
                    tri = Triangle(vertices[indices[0]], vertices[indices[i]], vertices[indices[i+1]], color)
                    triangles.append(tri)
    return triangles

def compute_pixel(args):
    x, y, origin, objects, lights = args
    d = canvas_to_viewport(x, y)
    col = trace_ray(origin, d, 1, float('inf'), objects, lights, recursion_depth=1)
    return (x, y, col)

def render_scene():
    lights = [
        Light("ambient", 0.2),
        Light("point", 0.6, position=Vector3(1.6, 1, 0)),
        Light("directional", 0.2, direction=Vector3(1, 4, 4)),
    ]
    objects = [
        Sphere(Vector3(-0.5, 0, 6), 1, (0, 255, 0), 10, 0.2),
        Sphere(Vector3(0, -5001, 0), 5000, (255, 255, 0), 1000, 0),
        Cylinder(Vector3(1, 0, 4), 1, 2, (255, 0, 0), 60, 0.4)
    ]
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND_COLOR)
    pixels = image.load()
    origin = Vector3(0, 0, 0)
    args_list = []
    for x in range(-CANVAS_WIDTH // 2, CANVAS_WIDTH // 2):
        for y in range(-CANVAS_HEIGHT // 2, CANVAS_HEIGHT // 2):
            args_list.append((x, y, origin, objects, lights))
    pool = mp.Pool()
    results = pool.map(compute_pixel, args_list)
    pool.close()
    pool.join()
    for (x, y, col) in results:
        canvas_x = x + CANVAS_WIDTH // 2
        canvas_y = CANVAS_HEIGHT // 2 - y - 1
        pixels[canvas_x, canvas_y] = col
    image.save("raytraced_scene.png")

if __name__ == "__main__":
    render_scene()
