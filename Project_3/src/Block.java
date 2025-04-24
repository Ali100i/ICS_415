import org.joml.Vector3f;
import java.util.Random;

public class Block {
    public static final float SIZE = 1.0f;
    private float x, y, z;
    private Vector3f color;
    private static final Random RAND = new Random();

    public Block(float x, float y, float z) {
        this.x = x; this.y = y; this.z = z;
        // pastel-ish random color
        this.color = new Vector3f(
            RAND.nextFloat() * 0.7f + 0.3f,
            RAND.nextFloat() * 0.7f + 0.3f,
            RAND.nextFloat() * 0.7f + 0.3f
        );
    }

    public float getX() { return x; }
    public float getY() { return y; }
    public float getZ() { return z; }
    public Vector3f getColor() { return color; }
}
