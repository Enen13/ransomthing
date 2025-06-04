import React from 'react';
import './App.css';
import MainLeft from '../components/MainLeft';
import Sidebar from '../components/Sidebar';
import AlertHeader from '../components/AlertHeader';

function Mainpage() {
  return (
    <div className="App">
      <header className="header">RansomThing</header>
      <div className="content-wrapper">
        <div className="main-content">
          <AlertHeader />
          <MainLeft />
        </div>
        <Sidebar />
      </div>
    </div>
  );
}

export default Mainpage;