import numpy as np
from PIL import Image

CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500
VIEWPORT_WIDTH = 1
VIEWPORT_HEIGHT = 1
PROJECTION_PLANE_D = 1
BACKGROUND_COLOR = (255, 255, 255)  # White

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def scale(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def to_tuple(self):
        return (self.x, self.y, self.z)

class Sphere:
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.color = color

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

def trace_ray(origin, direction, t_min, t_max, spheres):
    closest_t = float('inf')
    closest_sphere = None

    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, sphere)
        if t_min <= t1 <= t_max and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if t_min <= t2 <= t_max and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere

    if closest_sphere is None:
        return BACKGROUND_COLOR
    return closest_sphere.color

def render_scene():
    spheres = [
        Sphere(Vector3(0, -1, 3), 1, (255, 0, 0)),  # Red sphere
        Sphere(Vector3(2, 0, 4), 1, (0, 0, 255)),  # Blue sphere
        Sphere(Vector3(-2, 0, 4), 1, (0, 255, 0))   # Green sphere
    ]

    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND_COLOR)
    pixels = image.load()

    origin = Vector3(0, 0, 0)

    for x in range(-CANVAS_WIDTH // 2, CANVAS_WIDTH // 2):
        for y in range(-CANVAS_HEIGHT // 2, CANVAS_HEIGHT // 2):
            direction = canvas_to_viewport(x, y)
            color = trace_ray(origin, direction, 1, float('inf'), spheres)
            canvas_x = x + CANVAS_WIDTH // 2
            canvas_y = CANVAS_HEIGHT // 2 - y - 1
            pixels[canvas_x, canvas_y] = color

    image.save("raytraced_scene.png")

if __name__ == "__main__":
    render_scene()
