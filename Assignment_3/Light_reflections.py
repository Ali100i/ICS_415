import numpy as np
from PIL import Image

CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 1000
VIEWPORT_WIDTH = 1
VIEWPORT_HEIGHT = 1
PROJECTION_PLANE_D = 1
BACKGROUND_COLOR = (255, 255, 255)  # White

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
        length = self.length()
        if length == 0:
            return Vector3(0, 0, 0)
        return self / length

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)


class Sphere:
    def __init__(self, center, radius, color, specular, reflective):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular
        self.reflective = reflective

def canvas_to_viewport(x, y):
    return Vector3(
        x * VIEWPORT_WIDTH / CANVAS_WIDTH,
        y * VIEWPORT_HEIGHT / CANVAS_HEIGHT,
        PROJECTION_PLANE_D
    )

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

def computeLighting(P, N, V, s, lights, spheres):
    i = 0.0
    for light in lights:
        L = None
        if light.type == "ambient":
            i += light.intensity
        elif light.type == "point" and light.position is not None:
            L = light.position - P
            t_max = 1
        elif light.type == "directional" and light.direction is not None:
            L = light.direction
            t_max = np.inf

        if L is not None:
            shadow_sphere, shadow_t = ClosestIntersection(P, L, 0.001, t_max, spheres)
            if shadow_sphere is not None:
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

def ClosestIntersection(origin, direction, t_min, t_max, spheres):
    closest_t = np.inf
    closest_sphere = None
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, sphere)
        if t_min <= t1 <= t_max and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if t_min <= t2 <= t_max and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere
            
    return closest_sphere, closest_t

def reflect_ray(R , N):
    return N.scale(2 * N.dot(R)) - R

def trace_ray(origin, direction, t_min, t_max, spheres, lights, recursion_depth):
    closest_sphere, closest_t = ClosestIntersection(origin, direction, t_min, t_max, spheres)
    if closest_sphere is None:
        return BACKGROUND_COLOR

    P = origin + direction * closest_t
    N = (P - closest_sphere.center).normalize()
    local_color = tuple(
        min(255, int(c * computeLighting(P, N, -direction, closest_sphere.specular, lights, spheres)))
        for c in closest_sphere.color
    )

    r = closest_sphere.reflective
    if recursion_depth <= 0 or r <= 0:
        return local_color

    R = reflect_ray(-direction, N)
    reflected_color = trace_ray(P, R, 0.001, np.inf, spheres, lights, recursion_depth - 1)

    final_color = tuple(
        min(255, int(local_color[i] * (1 - r) + reflected_color[i] * r))
        for i in range(3)
    )
    return final_color


def render_scene():
    lights = [
        Light("ambient", 0.2),
        Light("point", 0.6, position=Vector3(2, 1, 0)),
        Light("directional", 0.2, direction=Vector3(1, 4, 4)),
    ]

    spheres = [
        Sphere(Vector3(0, -1, 3), 1, (255, 0, 0), 500, 0.09),  # Red sphere
        Sphere(Vector3(2, 0, 4), 1, (0, 0, 255), 500, 0.2),  # Blue sphere
        Sphere(Vector3(-2, 0, 4), 1, (0, 255, 0), 10, 0.2),   # Green sphere
        Sphere(Vector3(0, -5001, 0), 5000, (255, 255, 0), 1000, 0)  # Yellow Sphere
    ]

    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND_COLOR)
    pixels = image.load()

    origin = Vector3(0, 0, 0)

    for x in range(-CANVAS_WIDTH // 2, CANVAS_WIDTH // 2):
        for y in range(-CANVAS_HEIGHT // 2, CANVAS_HEIGHT // 2):
            direction = canvas_to_viewport(x, y)
            color = trace_ray(origin, direction, 1, float('inf'), spheres, lights, 1)
            canvas_x = x + CANVAS_WIDTH // 2
            canvas_y = CANVAS_HEIGHT // 2 - y - 1
            pixels[canvas_x, canvas_y] = color

    image.save("raytraced_scene.png")

if __name__ == "__main__":
    render_scene()
