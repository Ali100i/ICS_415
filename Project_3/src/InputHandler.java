import static org.lwjgl.glfw.GLFW.*;
import org.joml.Vector3f;

public class InputHandler {
    private final long window;
    private final Camera camera;
    private final World world;
    private final int width, height;

    // mouse‐look state
    private double lastX, lastY;
    private boolean firstMouse = true;
    private final float mouseSensitivity = 0.1f;
    private final float moveSpeed = 0.1f;

    // highlight & placement cells
    private int targetX = Integer.MIN_VALUE,
                targetY = Integer.MIN_VALUE,
                targetZ = Integer.MIN_VALUE;
    private int placeX  = Integer.MIN_VALUE,
                placeY  = Integer.MIN_VALUE,
                placeZ  = Integer.MIN_VALUE;

    public InputHandler(long window,
                        Camera camera,
                        World world,
                        int width,
                        int height) {
        this.window = window;
        this.camera = camera;
        this.world  = world;
        this.width  = width;
        this.height = height;

        // 1) Warp the cursor to the centre of the window
        glfwSetCursorPos(window, width/2.0, height/2.0);
        // 2) Hide & grab it so it never leaves the window
        glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);

        // 3) “first‐mouse” callback to seed lastX/lastY and skip the giant jump
        glfwSetCursorPosCallback(window, (win, xpos, ypos) -> {
            if (firstMouse) {
                lastX = width/2.0;
                lastY = height/2.0;
                firstMouse = false;
                return;
            }
            double xoff = xpos - lastX;
            double yoff = ypos - lastY;  // non-inverted Y

            lastX = xpos;
            lastY = ypos;

            xoff *= mouseSensitivity;
            yoff *= mouseSensitivity;

            camera.rotation.y += (float)xoff;
            camera.rotation.x += (float)yoff;
            camera.rotation.x  = Math.max(-89f, Math.min(89f, camera.rotation.x));
        });

        // 4) Left/right click to break/place
        glfwSetMouseButtonCallback(window, (win, button, action, mods) -> {
            if (action != GLFW_PRESS) return;
            if (button == GLFW_MOUSE_BUTTON_LEFT)  handleBlockAction(false);
            if (button == GLFW_MOUSE_BUTTON_RIGHT) handleBlockAction(true);
        });
    }

    /** Called once per frame: moves camera and updates the highlight cell */
    public void update() {
        float yaw = (float)Math.toRadians(camera.rotation.y);

        // FPS-style forward (ignore pitch)
        Vector3f forward = new Vector3f(
            -(float)Math.sin(yaw),
            0,
            -(float)Math.cos(yaw)
        ).normalize();

        Vector3f right = new Vector3f(forward).cross(new Vector3f(0, 1, 0)).normalize();

        if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS)
            camera.position.fma(moveSpeed, forward);
        if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS)
            camera.position.fma(-moveSpeed, forward);
        if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS)
            camera.position.fma(moveSpeed, right);
        if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS)
            camera.position.fma(-moveSpeed, right);

        // Optional vertical fly
        if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS)
            camera.position.y += moveSpeed;
        if (glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS)
            camera.position.y -= moveSpeed;

        updateHighlight();
    }


    /** Ray-cast from the camera to add or remove one block */
    private void handleBlockAction(boolean place) {
        if (targetX == Integer.MIN_VALUE) return;

        if (place) {
            world.addBlock(placeX, placeY, placeZ);
        } else {
            world.removeBlock(targetX, targetY, targetZ);
        }
    }


    /** Walk the ray and set targetX/Y/Z & placeX/Y/Z */
    private void updateHighlight() {
        Vector3f origin = new Vector3f(camera.position);
        float pitch = (float)Math.toRadians(camera.rotation.x);
        float yaw   = (float)Math.toRadians(camera.rotation.y);

        Vector3f direction = new Vector3f(
            (float)(-Math.sin(yaw) * Math.cos(pitch)),
            (float)( Math.sin(pitch)),
            (float)(-Math.cos(yaw) * Math.cos(pitch))
        ).normalize();

        targetX = targetY = targetZ = Integer.MIN_VALUE;
        placeX  = placeY  = placeZ  = Integer.MIN_VALUE;

        float maxDist = 5f, step = 0.1f;
        int lastEmptyX = Integer.MIN_VALUE;
        int lastEmptyY = Integer.MIN_VALUE;
        int lastEmptyZ = Integer.MIN_VALUE;

        for (float t = 0; t < maxDist; t += step) {
            Vector3f point = new Vector3f(origin).fma(t, direction);
            int bx = (int)Math.floor(point.x);
            int by = (int)Math.floor(point.y);
            int bz = (int)Math.floor(point.z);

            if (world.hasBlock(bx, by, bz)) {
                targetX = bx;
                targetY = by;
                targetZ = bz;

                placeX = lastEmptyX;
                placeY = lastEmptyY;
                placeZ = lastEmptyZ;
                return;
            } else {
                lastEmptyX = bx;
                lastEmptyY = by;
                lastEmptyZ = bz;
            }
        }
    }


    // getters for placement‐grid in your renderer
    public int getPlaceX() { return placeX; }
    public int getPlaceY() { return placeY; }
    public int getPlaceZ() { return placeZ; }
}
