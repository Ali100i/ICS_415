import org.lwjgl.opengl.GL11;
import org.joml.Vector3f;

public class Mesh {

    public void renderBlockAt(float x, float y, float z, Vector3f color) {
        GL11.glPushMatrix();
        GL11.glTranslatef(x, y, z);

        GL11.glColor3f(color.x, color.y, color.z);
        GL11.glBegin(GL11.GL_QUADS);
          // Front
          GL11.glNormal3f(0, 0, -1);
          GL11.glVertex3f(0, 0, 0);
          GL11.glVertex3f(1, 0, 0);
          GL11.glVertex3f(1, 1, 0);
          GL11.glVertex3f(0, 1, 0);

          // Back
          GL11.glNormal3f(0, 0, 1);
          GL11.glVertex3f(0, 0, 1);
          GL11.glVertex3f(1, 0, 1);
          GL11.glVertex3f(1, 1, 1);
          GL11.glVertex3f(0, 1, 1);

          // Left
          GL11.glNormal3f(-1, 0, 0);
          GL11.glVertex3f(0, 0, 0);
          GL11.glVertex3f(0, 0, 1);
          GL11.glVertex3f(0, 1, 1);
          GL11.glVertex3f(0, 1, 0);

          // Right
          GL11.glNormal3f(1, 0, 0);
          GL11.glVertex3f(1, 0, 0);
          GL11.glVertex3f(1, 0, 1);
          GL11.glVertex3f(1, 1, 1);
          GL11.glVertex3f(1, 1, 0);

          // Top
          GL11.glNormal3f(0, 1, 0);
          GL11.glVertex3f(0, 1, 0);
          GL11.glVertex3f(1, 1, 0);
          GL11.glVertex3f(1, 1, 1);
          GL11.glVertex3f(0, 1, 1);

          // Bottom
          GL11.glNormal3f(0, -1, 0);
          GL11.glVertex3f(0, 0, 0);
          GL11.glVertex3f(1, 0, 0);
          GL11.glVertex3f(1, 0, 1);
          GL11.glVertex3f(0, 0, 1);
        GL11.glEnd();

        GL11.glPopMatrix();
    }
}
