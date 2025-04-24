# Project_3: Minecraft-style 3D Block World (LWJGL)

This is a lightweight Minecraft-style voxel engine built with Java and LWJGL 3. It allows you to fly around, place, and destroy colored blocks in a 3D space using FPS-style controls.

📁 GitHub Path: `ICS_415/Project_3`

---

## 🎮 Features

- 3D block rendering with OpenGL
- Free-fly FPS camera with mouse look
- Raycast-based block interaction
- Block placement preview grid
- Infinite block stacking and destruction

---

## 🧰 Requirements

- Java JDK 17 or higher
- Eclipse IDE (or any Java IDE)
- LWJGL 3 library
- OpenGL-compatible graphics card

---

## 🧑‍💻 Setup Instructions (Eclipse)

### 1. Clone the Repository

```bash
git clone https://github.com/Ali100i/ICS_415.git
cd ICS_415/Project_3
```

### 2. Import the project into Eclipse

- Open Eclipse

- Go to File > Import > Existing Projects into Workspace

- Choose the path: ICS_415/Project_3

- Click Finish

### 3. Add LWJGL 3 libraries

Download LWJGL from https://www.lwjgl.org/customize

In Eclipse:

  - Right-click the project > Build Path > Configure Build Path

  - Under Libraries, click Add External JARs...

  - Add all required .jar files from lwjgl/lib

  - Under Native Library Location, point each JAR to the native folder for your platform (e.g. native/windows or native/macos)

### 4. Running the project

  - Right-Click Main.java > Run as > Java Application
