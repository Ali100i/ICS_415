import { useRef, useState, useEffect } from "react";
import "./BezierEditor.css";

export default function BezierEditor() {
  const canvasRef = useRef(null);
  const [points, setPoints] = useState([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    canvas.width = 800 * dpr;
    canvas.height = 500 * dpr;
    canvas.style.width = "800px";
    canvas.style.height = "500px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  }, [points]);

  const handleCanvasClick = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setPoints([...points, { x, y }]);
  };

  const draw = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i + 3 < points.length; i += 3) {
      ctx.beginPath();
      ctx.moveTo(points[i].x, points[i].y);
      ctx.bezierCurveTo(
        points[i + 1].x,
        points[i + 1].y,
        points[i + 2].x,
        points[i + 2].y,
        points[i + 3].x,
        points[i + 3].y
      );
      ctx.strokeStyle = "black";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.strokeStyle = "#ccc";
      ctx.beginPath();
      ctx.moveTo(points[i].x, points[i].y);
      ctx.lineTo(points[i + 1].x, points[i + 1].y);
      ctx.moveTo(points[i + 2].x, points[i + 2].y);
      ctx.lineTo(points[i + 3].x, points[i + 3].y);
      ctx.stroke();
    }

    points.forEach((pt, index) => {
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 5, 0, Math.PI * 2);
      ctx.fillStyle = index % 3 === 0 ? "red" : "blue";
      ctx.fill();
    });
  };

  const reset = () => {
    setPoints([]);
  };

  return (
    <div className="editor-container">
      <div className="card">
        <h3>Controls</h3>
        <button className="btn green" onClick={() => {
          alert("Click directly on the canvas to add points now.");
        }}>
          Add Point (Click Canvas)
        </button>
        <button className="btn yellow" onClick={() => {
          const newPoints = points.slice(0, -1);
          setPoints(newPoints);
        }}>
          Remove Last Point
        </button>
        <button className="btn red" onClick={reset}>Reset</button>
      </div>

      <canvas
        ref={canvasRef}
        className="editor-canvas"
        onClick={handleCanvasClick}
      ></canvas>
    </div>
  );
}