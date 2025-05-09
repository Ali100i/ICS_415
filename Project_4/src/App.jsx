import React from "react";
import BezierEditor from "./components/BezierEditor";
import "./App.css";

function App() {
  return (
    <div className="app">
      <h1 className="app-title">Bézier Curve Editor</h1>
      <p className="app-subtitle">Draw and Edit Bezier curves.</p>
      <BezierEditor />
    </div>
  );
}

export default App;