import React from "react";
import { Routes, Route } from "react-router-dom";
import "./App.css";

import Home from "./Home";
import AnalyzeEmailForm from "./AnalyzeEmail";
import AnalyzeImageForm from "./AnalyzeImage";

function App() {
  return (
    <div className="App">
      <header></header>

      <nav></nav>

      <section>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/email" element={<AnalyzeEmailForm />} />
          <Route path="/image" element={<AnalyzeImageForm />} />
        </Routes>
      </section>

      <footer></footer>
    </div>
  );
}

export default App;
