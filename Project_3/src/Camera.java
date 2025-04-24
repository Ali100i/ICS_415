import org.joml.Matrix4f;
import org.joml.Vector3f;

public class Camera {
    public Vector3f position;
    public Vector3f rotation;

    public Camera(int width, int height) {
    	this.position = new Vector3f(0, 10, 20);  // ↑ High + back
    	this.rotation = new Vector3f(30, 0, 0);   // ↘ Looking slightly down
    }

    public Matrix4f getViewMatrix() {
        Matrix4f view = new Matrix4f();
        view.rotate((float) Math.toRadians(rotation.x), new Vector3f(1, 0, 0))
            .rotate((float) Math.toRadians(rotation.y), new Vector3f(0, 1, 0))
            .translate(-position.x, -position.y, -position.z);
        return view;
    }
    
    public Matrix4f getProjectionMatrix(float fov, float aspect, float near, float far) {
        return new Matrix4f().perspective((float)Math.toRadians(fov), aspect, near, far);
    }

}
