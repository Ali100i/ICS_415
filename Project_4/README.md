# Interactive Bézier Curve Editor - Project 4

This project is a visual editor built with React that allows you to interactively create and manipulate Bézier curves. Users can add control points by clicking on a canvas and dynamically visualize cubic and poly Bézier segments in real time.

## Features

- **Click-to-Add Points:** Add control points by clicking anywhere on the canvas.
- **Supports Poly Bézier Curves:** Every group of 4 points creates a new Bézier segment.
- **Live Curve Rendering:** Automatically redraws curves as you add or remove points.
- **High-Resolution Canvas:** Crisp rendering using device pixel ratio scaling.
- **Custom UI Styling:** A distinct modern theme for UI buttons and layout.

## Prerequisites

- **Node.js:** Version 18 or later is recommended.
- **Basic Knowledge:** Familiarity with React and browser-based canvas rendering is helpful.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Ali100i/ICS_415.git
  `
2. **Navigate to Project 4 Folder:**

  ```bash
  cd ICS_415/Project_4
  ```

3. **Install Dependencies:**

   ```bash
   npm install
   ```
   
4. **Run the Development Server:**

   ```bash
   npm run dev
   ```

## Usage

- Click anywhere on the canvas to add control points.
- Every 4 points defines a new cubic Bézier curve.
- Use the control buttons on the left to:
- Remove the last point
- Reset all points

## Output

below is an example of the Bezier curve editor UI:



## License

This project is open-source. Contributions are welcome — feel free to fork the repo, submit issues, or open pull requests!
