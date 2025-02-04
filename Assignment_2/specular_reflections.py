import numpy as np
from PIL import Image

CANVAS_WIDTH = 1500
CANVAS_HEIGHT = 1500
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

class Sphere:
    def __init__(self, center, radius, color, specular):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular

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

def trace_ray(origin, direction, t_min, t_max, spheres, lights):
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

    P = origin + direction.scale(closest_t)
    N = P - closest_sphere.center
    N_length = np.sqrt(N.dot(N))
    if N_length > 0:
        N = N.scale(1 / N_length)

    V = direction.scale(-1)
    V_length = np.sqrt(V.dot(V))
    if V_length > 0:
        V = V.scale(1 / V_length)

    lighting = computeLighting(P, N, V, closest_sphere.specular, lights)

    sphere_color = closest_sphere.color
    return tuple(min(255, max(0, int(c * lighting))) for c in sphere_color)


def computeLighting(P, N, V, s, lights):
    i = 0.0
    for light in lights:
        L = None
        if light.type == "ambient":
            i += light.intensity
        elif light.type == "point" and light.position is not None:
            L = light.position - P
        else:
            L = light.direction

        if L is not None:
            L_length = np.sqrt(L.dot(L))
            if L_length > 0:
                L = L.scale(1 / L_length)

            n_dot_l = N.dot(L)
            if n_dot_l > 0:
                i += light.intensity * n_dot_l

            if s != -1:
                R = N.scale(2 * N.dot(L)) - L
                R_length = np.sqrt(R.dot(R))
                if R_length > 0:
                    R = R.scale(1 / R_length)

                r_dot_v = R.dot(V)
                if r_dot_v > 0:
                    i += light.intensity * (r_dot_v ** s)


    return i



def render_scene():

    lights = [
        Light("ambient", 0.2),
        Light("point", 0.6, Vector3(2, 1, 0)),
        Light("directional", 0.2, Vector3(1, 4, 4)),
        Light("point", 0.2, Vector3(20,60,80))
    ]

    spheres = [
        Sphere(Vector3(0, -1, 3), 1, (255, 0, 0), 500),  # Red sphere
        Sphere(Vector3(2, 0, 4), 1, (0, 0, 255), 500),  # Blue sphere
        Sphere(Vector3(-2, 0, 4), 1, (0, 255, 0), 10),   # Green sphere
        Sphere(Vector3(0, -5001, 0), 5000, (255, 255, 0), 1000) # Yellow Sphere 
    ]

    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND_COLOR)
    pixels = image.load()

    origin = Vector3(0, 0, 0)

    for x in range(-CANVAS_WIDTH // 2, CANVAS_WIDTH // 2):
        for y in range(-CANVAS_HEIGHT // 2, CANVAS_HEIGHT // 2):
            direction = canvas_to_viewport(x, y)
            color = trace_ray(origin, direction, 1, float('inf'), spheres, lights)
            canvas_x = x + CANVAS_WIDTH // 2
            canvas_y = CANVAS_HEIGHT // 2 - y - 1
            pixels[canvas_x, canvas_y] = color

    image.save("raytraced_scene.png")

if __name__ == "__main__":
    render_scene()
