import math, random, time, concurrent.futures, sys
from PIL import Image

# === VECTOR / COLOR CLASS ===
class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    # Basic arithmetic (addition, subtraction)
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    # Multiplication: if the other is a scalar then scale; otherwise, component-wise multiply
    def __mul__(self, t):
        if isinstance(t, (int, float)):
            return Vector3(self.x * t, self.y * t, self.z * t)
        else:
            return Vector3(self.x * t.x, self.y * t.y, self.z * t.z)
    __rmul__ = __mul__

    def __truediv__(self, t):
        return self * (1 / t)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3(self.y * other.z - self.z * other.y,
                       self.z * other.x - self.x * other.z,
                       self.x * other.y - self.y * other.x)

    def length(self):
        return math.sqrt(self.length_squared())
    def length_squared(self):
        return self.x*self.x + self.y*self.y + self.z*self.z

    def normalize(self):
        return self / self.length()

    def near_zero(self):
        # Returns True if the vector is very close to zero in all dimensions.
        s = 1e-8
        return (abs(self.x) < s) and (abs(self.y) < s) and (abs(self.z) < s)

    def to_tuple(self):
        return (self.x, self.y, self.z)

    @staticmethod
    def random(min_val=0.0, max_val=1.0):
        return Vector3(random.uniform(min_val, max_val),
                       random.uniform(min_val, max_val),
                       random.uniform(min_val, max_val))

# Alias Color and Point3 for clarity.
Color = Vector3
Point3 = Vector3

def clamp(x, min_val, max_val):
    if x < min_val: return min_val
    if x > max_val: return max_val
    return x

def degrees_to_radians(degrees):
    return degrees * math.pi / 180

# === RANDOM SAMPLING FUNCTIONS ===
def random_in_unit_sphere():
    while True:
        p = Vector3.random(-1, 1)
        if p.length_squared() < 1:
            return p

def random_unit_vector():
    return random_in_unit_sphere().normalize()

def random_in_unit_disk():
    while True:
        p = Vector3(random.uniform(-1,1), random.uniform(-1,1), 0)
        if p.length_squared() < 1:
            return p

def random_double(min_val=0.0, max_val=1.0):
    return random.uniform(min_val, max_val)

def random_color(min_val=0.0, max_val=1.0):
    return Color(random_double(min_val, max_val),
                 random_double(min_val, max_val),
                 random_double(min_val, max_val))

# === REFLECTION AND REFRACTION HELPERS ===
def reflect(v, n):
    # Reflect vector v about normal n.
    return v - n * 2 * v.dot(n)

def refract(uv, n, etai_over_etat):
    cos_theta = min((-uv).dot(n), 1.0)
    r_out_perp = (uv + n * cos_theta) * etai_over_etat
    r_out_parallel = n * (-math.sqrt(abs(1.0 - r_out_perp.length_squared())))
    return r_out_perp + r_out_parallel

# === RAY CLASS ===
class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction
    def at(self, t):
        return self.origin + self.direction * t

# === HIT RECORD & HITTABLE INTERFACES ===
class HitRecord:
    def __init__(self):
        self.t = 0
        self.p = None
        self.normal = None
        self.front_face = True
        self.material = None
    def set_face_normal(self, ray, outward_normal):
        self.front_face = ray.direction.dot(outward_normal) < 0
        self.normal = outward_normal if self.front_face else -outward_normal

class Hittable:
    def hit(self, ray, t_min, t_max, rec):
        # Returns True if the ray hits the object and sets rec.
        pass

# === SPHERE (a Hittable) ===
class Sphere(Hittable):
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material
    def hit(self, ray, t_min, t_max, rec):
        oc = ray.origin - self.center
        a = ray.direction.length_squared()
        half_b = oc.dot(ray.direction)
        c = oc.length_squared() - self.radius*self.radius
        discriminant = half_b * half_b - a * c
        if discriminant < 0:
            return False
        sqrtd = math.sqrt(discriminant)
        # Find the nearest root in the acceptable range.
        root = (-half_b - sqrtd) / a
        if root < t_min or root > t_max:
            root = (-half_b + sqrtd) / a
            if root < t_min or root > t_max:
                return False
        rec.t = root
        rec.p = ray.at(rec.t)
        outward_normal = (rec.p - self.center) / self.radius
        rec.set_face_normal(ray, outward_normal)
        rec.material = self.material
        return True

# === HITTABLE LIST ===
class HittableList(Hittable):
    def __init__(self):
        self.objects = []
    def add(self, obj):
        self.objects.append(obj)
    def hit(self, ray, t_min, t_max, rec):
        temp_rec = HitRecord()
        hit_anything = False
        closest_so_far = t_max
        for obj in self.objects:
            if obj.hit(ray, t_min, closest_so_far, temp_rec):
                hit_anything = True
                closest_so_far = temp_rec.t
                rec.t = temp_rec.t
                rec.p = temp_rec.p
                rec.normal = temp_rec.normal
                rec.front_face = temp_rec.front_face
                rec.material = temp_rec.material
        return hit_anything

# === MATERIALS ===
class Material:
    # The scatter function returns a tuple: (bool, scattered_ray, attenuation)
    def scatter(self, ray_in, rec):
        pass

class Lambertian(Material):
    def __init__(self, albedo):
        self.albedo = albedo
    def scatter(self, ray_in, rec):
        scatter_direction = rec.normal + random_unit_vector()
        # Catch degenerate scatter direction
        if scatter_direction.near_zero():
            scatter_direction = rec.normal
        scattered = Ray(rec.p, scatter_direction)
        attenuation = self.albedo
        return True, scattered, attenuation

class Metal(Material):
    def __init__(self, albedo, fuzz):
        self.albedo = albedo
        self.fuzz = fuzz if fuzz < 1 else 1
    def scatter(self, ray_in, rec):
        reflected = reflect(ray_in.direction.normalize(), rec.normal)
        scattered = Ray(rec.p, reflected + random_in_unit_sphere() * self.fuzz)
        attenuation = self.albedo
        if scattered.direction.dot(rec.normal) > 0:
            return True, scattered, attenuation
        else:
            return False, None, None

class Dielectric(Material):
    def __init__(self, ref_idx):
        self.ref_idx = ref_idx
    def scatter(self, ray_in, rec):
        attenuation = Color(1, 1, 1)
        etai_over_etat = (1.0 / self.ref_idx) if rec.front_face else self.ref_idx
        unit_direction = ray_in.direction.normalize()
        cos_theta = min((-unit_direction).dot(rec.normal), 1.0)
        sin_theta = math.sqrt(1.0 - cos_theta * cos_theta)
        cannot_refract = etai_over_etat * sin_theta > 1.0

        # Schlick's approximation for reflectance.
        def reflectance(cosine, ref_idx):
            r0 = (1 - ref_idx) / (1 + ref_idx)
            r0 = r0 * r0
            return r0 + (1 - r0) * ((1 - cosine) ** 5)

        if cannot_refract or reflectance(cos_theta, etai_over_etat) > random.random():
            direction = reflect(unit_direction, rec.normal)
        else:
            direction = refract(unit_direction, rec.normal, etai_over_etat)
        scattered = Ray(rec.p, direction)
        return True, scattered, attenuation

# === CAMERA ===
class Camera:
    def __init__(self, lookfrom, lookat, vup, vfov, aspect_ratio, aperture, focus_dist):
        self.origin = lookfrom
        theta = degrees_to_radians(vfov)
        h = math.tan(theta / 2)
        viewport_height = 2.0 * h
        viewport_width = aspect_ratio * viewport_height

        # Orthonormal basis
        w = (lookfrom - lookat).normalize()
        u = vup.cross(w).normalize()
        v = w.cross(u)

        self.horizontal = u * viewport_width * focus_dist
        self.vertical = v * viewport_height * focus_dist
        self.lower_left_corner = self.origin - self.horizontal/2 - self.vertical/2 - w * focus_dist

        self.lens_radius = aperture / 2
        self.u = u
        self.v = v

    def get_ray(self, s, t):
        rd = random_in_unit_disk() * self.lens_radius
        offset = self.u * rd.x + self.v * rd.y
        direction = self.lower_left_corner + self.horizontal * s + self.vertical * t - self.origin - offset
        return Ray(self.origin + offset, direction)

# === RAY COLOR FUNCTION ===
def ray_color(ray, world, depth):
    if depth <= 0:
        return Color(0, 0, 0)
    rec = HitRecord()
    if world.hit(ray, 0.001, float('inf'), rec):
        scatter_result = rec.material.scatter(ray, rec)
        if scatter_result[0]:
            scattered = scatter_result[1]
            attenuation = scatter_result[2]
            return attenuation * ray_color(scattered, world, depth - 1)
        return Color(0, 0, 0)
    unit_direction = ray.direction.normalize()
    t = 0.5 * (unit_direction.y + 1.0)
    # Linear blend: white to blue
    return Color(1.0, 1.0, 1.0) * (1.0 - t) + Color(0.5, 0.7, 1.0) * t

# === COLOR OUTPUT (with gamma correction) ===
def write_color(pixel_color, samples_per_pixel):
    scale = 1.0 / samples_per_pixel
    # Gamma-correct with gamma=2 (i.e. take the square root).
    r = math.sqrt(pixel_color.x * scale)
    g = math.sqrt(pixel_color.y * scale)
    b = math.sqrt(pixel_color.z * scale)
    ir = int(256 * clamp(r, 0.0, 0.999))
    ig = int(256 * clamp(g, 0.0, 0.999))
    ib = int(256 * clamp(b, 0.0, 0.999))
    return (ir, ig, ib)

# === SCANLINE RENDERING FUNCTION (for the process pool) ===
def compute_scanline(j, image_width, image_height, samples_per_pixel, cam, world, max_depth):
    scanline = []
    for i in range(image_width):
        pixel_color = Color(0, 0, 0)
        for s in range(samples_per_pixel):
            u = (i + random_double()) / (image_width - 1)
            v = (j + random_double()) / (image_height - 1)
            r = cam.get_ray(u, v)
            pixel_color += ray_color(r, world, max_depth)
        scanline.append(write_color(pixel_color, samples_per_pixel))
    return j, scanline

# === MAIN FUNCTION: SETUP THE SCENE AND RENDER ===
def main():
    # Image settings.
    aspect_ratio = 2.0
    image_width = 400
    image_height = 200

    samples_per_pixel = 200
    max_depth = 20

    # World (a list of hittable objects)
    world = HittableList()

    # Ground: a large sphere.
    ground_material = Lambertian(Color(0.5, 0.5, 0.5))
    world.add(Sphere(Point3(0, -1000, 0), 1000, ground_material))

    # Random small spheres.
    for a in range(-11, 11):
        for b in range(-11, 11):
            choose_mat = random_double()
            center = Point3(a + 0.9 * random_double(), 0.2, b + 0.9 * random_double())
            if (center - Point3(4, 0.2, 0)).length() > 0.9:
                if choose_mat < 0.8:
                    # Diffuse.
                    albedo = random_color() * random_color()
                    sphere_material = Lambertian(albedo)
                    world.add(Sphere(center, 0.2, sphere_material))
                elif choose_mat < 0.95:
                    # Metal.
                    albedo = random_color(0.5, 1)
                    fuzz = random_double(0, 0.5)
                    sphere_material = Metal(albedo, fuzz)
                    world.add(Sphere(center, 0.2, sphere_material))
                else:
                    # Glass.
                    sphere_material = Dielectric(1.5)
                    world.add(Sphere(center, 0.2, sphere_material))

    # Three large spheres.
    material1 = Dielectric(1.5)
    world.add(Sphere(Point3(0, 1, 0), 1.0, material1))
    material2 = Lambertian(Color(0.4, 0.2, 0.1))
    world.add(Sphere(Point3(-4, 1, 0), 1.0, material2))
    material3 = Metal(Color(0.7, 0.6, 0.5), 0.0)
    world.add(Sphere(Point3(4, 1, 0), 1.0, material3))

    # Camera parameters.
    lookfrom = Point3(13, 2, 3)
    lookat = Point3(0, 0, 0)
    vup = Vector3(0, 1, 0)
    vfov = 20  # vertical field-of-view in degrees.
    focus_dist = 10.0
    aperture = 0.0  # aperture=0 means no defocus blur.

    cam = Camera(lookfrom, lookat, vup, vfov, aspect_ratio, aperture, focus_dist)

    # Create image.
    image = Image.new("RGB", (image_width, image_height))
    pixels = image.load()

    print("Rendering...")

    start_time = time.time()  # Start timer
    total_scanlines = image_height
    completed_scanlines = 0
    bar_length = 50  # length of progress bar

    # Use ProcessPoolExecutor for parallelism.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Submit one task per scanline (j goes from image_height-1 down to 0).
        futures = {executor.submit(compute_scanline, j, image_width, image_height, samples_per_pixel, cam, world, max_depth): j
                   for j in range(image_height - 1, -1, -1)}
        for future in concurrent.futures.as_completed(futures):
            j, scanline = future.result()
            row = image_height - j - 1
            for i, pixel in enumerate(scanline):
                pixels[i, row] = pixel
            completed_scanlines += 1

            # Calculate progress and estimated remaining time.
            elapsed = time.time() - start_time
            progress = completed_scanlines / total_scanlines
            estimated_total = elapsed / progress if progress > 0 else 0
            remaining = estimated_total - elapsed

            # Build progress bar string.
            num_hashes = int(progress * bar_length)
            progress_bar = '[' + '#' * num_hashes + '-' * (bar_length - num_hashes) + ']'
            sys.stdout.write(f"\rProgress: {progress_bar} {progress*100:5.1f}%  Elapsed: {elapsed:5.1f}s  ETA: {remaining:5.1f}s")
            sys.stdout.flush()

    end_time = time.time()  # End timer
    image.save("final_scene.png")
    print(f"\nDone. Total render time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
