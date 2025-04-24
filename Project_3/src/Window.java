import org.lwjgl.*;
import org.lwjgl.glfw.*;
import org.lwjgl.opengl.*;
import org.lwjgl.system.*;

import java.nio.FloatBuffer;
import org.lwjgl.BufferUtils;
import java.nio.IntBuffer;

import static org.lwjgl.glfw.Callbacks.*;
import static org.lwjgl.glfw.GLFW.*;
import static org.lwjgl.opengl.GL11.*;
import static org.lwjgl.system.MemoryStack.*;
import static org.lwjgl.system.MemoryUtil.*;

public class Window {
    private long window;
    private int width, height;
    private String title;
    private Renderer renderer;
    private World world;
    private Camera camera;
    private InputHandler input;

    // for the “first-mouse” logic
    private boolean firstMouse = true;
    private double lastX, lastY;
    private final float mouseSensitivity = 0.1f;

    public Window(int width, int height, String title) {
        this.width = width;
        this.height = height;
        this.title = title;
    }

    public void run() {
        init();
        loop();

        glfwFreeCallbacks(window);
        glfwDestroyWindow(window);
        glfwTerminate();
        glfwSetErrorCallback(null).free();
    }

    private void init() {
        // ---- GLFW init ----
        GLFWErrorCallback.createPrint(System.err).set();
        if (!glfwInit()) throw new IllegalStateException("Unable to initialize GLFW");

        glfwDefaultWindowHints();
        glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);
        glfwWindowHint(GLFW_RESIZABLE, GLFW_TRUE);

        window = glfwCreateWindow(width, height, title, NULL, NULL);
        if (window == NULL) throw new RuntimeException("Failed to create GLFW window");

        try ( MemoryStack stack = stackPush() ) {
            IntBuffer pW = stack.mallocInt(1);
            IntBuffer pH = stack.mallocInt(1);
            glfwGetWindowSize(window, pW, pH);
            GLFWVidMode vd = glfwGetVideoMode(glfwGetPrimaryMonitor());
            glfwSetWindowPos(window,
                (vd.width()  - pW.get(0)) / 2,
                (vd.height() - pH.get(0)) / 2
            );
        }

        glfwMakeContextCurrent(window);
        glfwSwapInterval(1);
        glfwShowWindow(window);

        // ---- OpenGL init ----
        GL.createCapabilities();
        glViewport(0, 0, width, height);
        glEnable(GL_DEPTH_TEST);

        // lighting, fog, etc…
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);
        glEnable(GL_COLOR_MATERIAL);
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE);
        glShadeModel(GL_SMOOTH);
        float[] lightPos = {0f,10f,5f,1f};
        glLightfv(GL_LIGHT0, GL_POSITION, asFloatBuffer(lightPos));
        float[] diff = {1,1,1,1};
        glLightfv(GL_LIGHT0, GL_DIFFUSE, asFloatBuffer(diff));
        float[] amb = {0.2f,0.2f,0.2f,1f};
        glLightfv(GL_LIGHT0, GL_AMBIENT, asFloatBuffer(amb));
        glEnable(GL_FOG);
        float[] fogColor = {0.52f,0.80f,0.92f,1f};
        glFogfv(GL_FOG_COLOR, asFloatBuffer(fogColor));
        glFogi(GL_FOG_MODE, GL_LINEAR);
        glFogf(GL_FOG_START, 15f);
        glFogf(GL_FOG_END, 60f);

        // ---- Game setup ----
        renderer = new Renderer();
        camera   = new Camera(width, height);
        world    = new World();

        // ---- Mouse look setup ----
        // 1) Warp to center
        glfwSetCursorPos(window, width/2.0, height/2.0);
        // 2) Hide & capture
        glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
        // 3) Install first-mouse callback
        glfwSetCursorPosCallback(window, (win, xpos, ypos) -> {
            if (firstMouse) {
                lastX = width/2.0;
                lastY = height/2.0;
                firstMouse = false;
                return;            // skip the jump on first frame
            }
            double xoff = xpos - lastX;
            double yoff = ypos - lastY;    // non-inverted Y

            lastX = xpos;
            lastY = ypos;

            xoff *= mouseSensitivity;
            yoff *= mouseSensitivity;

            camera.rotation.y += (float)xoff;
            camera.rotation.x += (float)yoff;
            camera.rotation.x  = Math.max(-89f, Math.min(89f, camera.rotation.x));
        });

        // ---- Input handler (keys, clicks, highlight) ----
        input = new InputHandler(window, camera, world, width, height);
    }

    private void loop() {
        while (!glfwWindowShouldClose(window)) {
            glClearColor(0.52f,0.80f,0.92f,1f);
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

            input.update();
            renderer.render(world, camera);

            renderer.renderPlacementGrid(
                input.getPlaceX(),
                input.getPlaceY(),
                input.getPlaceZ()
            );
            drawCrosshair();

            glfwSwapBuffers(window);
            glfwPollEvents();
        }
    }

    private void drawCrosshair() {
        // 2D overlay
        glMatrixMode(GL_PROJECTION);
        glPushMatrix();
          glLoadIdentity();
          glOrtho(0, width, height, 0, -1, 1);
        glMatrixMode(GL_MODELVIEW);
        glPushMatrix();
          glLoadIdentity();
          glDisable(GL_DEPTH_TEST);

          glColor3f(1f,1f,1f);
          glBegin(GL_LINES);
            int cx = width/2, cy = height/2;
            glVertex2i(cx-8, cy); glVertex2i(cx+8, cy);
            glVertex2i(cx, cy-8); glVertex2i(cx, cy+8);
          glEnd();

          glEnable(GL_DEPTH_TEST);
        glPopMatrix();
        glMatrixMode(GL_PROJECTION);
        glPopMatrix();
        glMatrixMode(GL_MODELVIEW);
    }

    private FloatBuffer asFloatBuffer(float[] vals) {
        FloatBuffer buf = BufferUtils.createFloatBuffer(vals.length);
        buf.put(vals).flip();
        return buf;
    }
}
