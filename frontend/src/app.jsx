import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';

import AskAI from './components/AskAI';
import GraphView from './components/GraphView';
import Recommend from './components/Recommend';

export default function App() {
  return (
    <BrowserRouter>
      <nav className="navbar">
        <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')}>
          问答
        </NavLink>
        <NavLink to="/graph" className={({ isActive }) => (isActive ? 'active' : '')}>
          知识图谱
        </NavLink>
        <NavLink to="/recommend" className={({ isActive }) => (isActive ? 'active' : '')}>
          推荐概念
        </NavLink>
      </nav>

      <div className="container">
        <Routes>
          <Route path="/" element={<AskAI />} />
          <Route path="/graph" element={<GraphView />} />
          <Route path="/recommend" element={<Recommend />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}