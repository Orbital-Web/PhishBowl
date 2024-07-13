import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
    return (
        <div>
        <h1>My React App</h1>
        <div className="buttons">
            <Link to="/upload">
                <button>Upload Image</button>
            </Link>
            <Link to="/email">
                <button>Email Form</button>
            </Link>
        </div>
        </div>
    );
}

export default Home;
