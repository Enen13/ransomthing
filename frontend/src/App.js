import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Mainpage from './pages/Mainpage';
import AttackerPattern from './pages/AttackerPattern';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Mainpage />} />
        <Route path="/attacker-pattern" element={<AttackerPattern />} />
      </Routes>
    </Router>
  );
}

export default App;