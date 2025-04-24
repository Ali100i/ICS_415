import java.util.ArrayList;
import java.util.List;

public class World {
    private List<Block> blocks = new ArrayList<>();
    private Mesh mesh;

    public World() {
        mesh = new Mesh();
        generateFlatWorld();
    }

    public void generateFlatWorld() {
        int width = 16;
        int depth = 16;

        for (int x = -width / 2; x < width / 2; x++) {
            for (int z = -depth / 2; z < depth / 2; z++) {
                addBlock(x, 0, z); // y=0 for ground
            }
        }
    }

    public void addBlock(float x, float y, float z) {
        if (!hasBlock((int)x, (int)y, (int)z)) {
            blocks.add(new Block(x, y, z));
        }
    }


    public void removeBlock(float x, float y, float z) {
        blocks.removeIf(b -> b.getX() == x && b.getY() == y && b.getZ() == z);
    }

    public void render(Camera camera) {
        for (Block block : blocks) {
            mesh.renderBlockAt(
                block.getX(), block.getY(), block.getZ(),
                block.getColor()
            );
        }
    }
    
    public boolean hasBlock(int x, int y, int z) {
        return blocks.stream()
                     .anyMatch(b -> b.getX()==x && b.getY()==y && b.getZ()==z);
    }
}
