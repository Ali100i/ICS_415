import org.lwjgl.opengl.GL11;
import org.joml.Matrix4f;
import org.lwjgl.BufferUtils;
import java.nio.FloatBuffer;

public class Renderer {

	public void render(World world, Camera camera) {
	    Matrix4f projection = camera.getProjectionMatrix(70f, 1280f / 720f, 0.1f, 100f);
	    loadMatrix(projection, GL11.GL_PROJECTION);

	    Matrix4f view = camera.getViewMatrix();
	    loadMatrix(view, GL11.GL_MODELVIEW);

	    world.render(camera);
	}


    /** call this *after* world.render(...) */
	public void renderPlacementGrid(int x, int y, int z) {
	    if (x == Integer.MIN_VALUE) return;

	    GL11.glDisable(GL11.GL_LIGHTING);
	    GL11.glColor3f(1f, 1f, 1f);

	    GL11.glPushMatrix();
	    GL11.glTranslatef(x, y, z + 0.001f);  // slight offset to avoid z-fighting

	    // Draw a full wireframe cube
	    GL11.glBegin(GL11.GL_LINES);

	    // Bottom square
	    GL11.glVertex3f(0, 0, 0); GL11.glVertex3f(1, 0, 0);
	    GL11.glVertex3f(1, 0, 0); GL11.glVertex3f(1, 0, 1);
	    GL11.glVertex3f(1, 0, 1); GL11.glVertex3f(0, 0, 1);
	    GL11.glVertex3f(0, 0, 1); GL11.glVertex3f(0, 0, 0);

	    // Top square
	    GL11.glVertex3f(0, 1, 0); GL11.glVertex3f(1, 1, 0);
	    GL11.glVertex3f(1, 1, 0); GL11.glVertex3f(1, 1, 1);
	    GL11.glVertex3f(1, 1, 1); GL11.glVertex3f(0, 1, 1);
	    GL11.glVertex3f(0, 1, 1); GL11.glVertex3f(0, 1, 0);

	    // Vertical lines
	    GL11.glVertex3f(0, 0, 0); GL11.glVertex3f(0, 1, 0);
	    GL11.glVertex3f(1, 0, 0); GL11.glVertex3f(1, 1, 0);
	    GL11.glVertex3f(1, 0, 1); GL11.glVertex3f(1, 1, 1);
	    GL11.glVertex3f(0, 0, 1); GL11.glVertex3f(0, 1, 1);

	    GL11.glEnd();
	    GL11.glPopMatrix();

	    GL11.glEnable(GL11.GL_LIGHTING);
	}


    private void loadMatrix(Matrix4f matrix, int mode) {
        FloatBuffer buffer = BufferUtils.createFloatBuffer(16);
        matrix.get(buffer);      // writes into buffer[0..15]
        // no flip()/rewind() needed here

        GL11.glMatrixMode(mode);
        GL11.glLoadIdentity();
        GL11.glLoadMatrixf(buffer);
    }
}
