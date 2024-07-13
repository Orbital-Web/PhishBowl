import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Home from './Home';
import ImageUpload from './ImageUpload';
import EmailForm from './EmailForm';

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/upload" element={<ImageUpload />} />
                <Route path="/email" element={<EmailForm />} />
                </Routes>
            </header>
        </div>
    );
}

export default App;
