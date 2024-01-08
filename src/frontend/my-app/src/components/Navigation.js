import React from "react";
import { Link } from "react-router-dom";
import "../css/Navbar.css"

const Navigation = () => {
  return (
    <nav className="navbar background">
      <ul className="nav-list">
        <div className="logo">
          {/* Make the logo a Link to the main content (path="/") */}
          <Link to="/">
            <img src="logo-color.png" alt="Logo" />
          </Link>
        </div>
        <li className="text-mid">
          <Link to="/about">About Us</Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navigation;
