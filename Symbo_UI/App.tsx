import { useState } from "react";
import { MathInterface } from "./components/MathInterface";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black">
      <MathInterface />
    </div>
  );
}
