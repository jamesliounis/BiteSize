// App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './css/App.css';
import Navigation from './components/Navigation';
import MainContent from './pages/MainContent';
import About from './pages/About';
import Upload from './pages/Upload';
import MCQCard from './pages/MCQCard';
import SACard from './pages/SACard';
import Finish from './pages/Finish';
export const APP_VERSION = 1.0;

function App() {
  return (
    <Router>
      <div>
        <Navigation /> {/* This component holds the navigation links */}
        <Routes>
          <Route path="/" element={<MainContent />} />
          <Route path="/about" element={<About />} />
          <Route path="/upload" element={<Upload />} />
          <Route path='/mcqcard' element={<MCQCard />}/>
          <Route path='/sacard' element= {<SACard />} />
          <Route path='/finish' element= {<Finish />} />  
        </Routes>
      </div>
    </Router>
  );
}

export default App;
