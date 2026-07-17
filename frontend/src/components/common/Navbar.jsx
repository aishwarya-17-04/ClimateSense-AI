import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FaLeaf, FaSearch, FaBell, FaBars } from 'react-icons/fa';
import './Navbar.css';

const Navbar = ({ toggleSidebar }) => {
  return (
    <nav className="navbar-container">
      
      {/* Brand / Logo + Mobile Toggle */}
      <div className="navbar-left">
        <motion.button 
          className="action-btn mobile-menu-btn"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={toggleSidebar}
          aria-label="Open Menu"
        >
          <FaBars size={24} />
        </motion.button>

        <Link to="/dashboard" style={{ textDecoration: 'none' }}>
          <motion.div 
            className="navbar-brand"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="brand-icon">
              <FaLeaf size={20} />
            </div>
            <span className="brand-text">ClimateSense AI</span>
          </motion.div>
        </Link>
      </div>

      {/* Search Bar */}
      <div className="navbar-search">
        <FaSearch className="search-icon" size={18} />
        <input 
          type="text" 
          className="search-input" 
          placeholder="Search insights, challenges, or community..." 
        />
      </div>

      {/* Right Actions & Profile */}
      <div className="navbar-actions">
        
        {/* Notifications */}
        <motion.button 
          className="action-btn"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          aria-label="Notifications"
        >
          <FaBell size={20} />
          <span className="notification-badge"></span>
        </motion.button>

        {/* User Profile Route link */}
        <Link to="/profile">
          <motion.button 
            className="profile-btn"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            aria-label="User Profile"
          >
            <img 
              src="https://ui-avatars.com/api/?name=Julian&background=38bdf8&color=fff" 
              alt="Profile" 
              className="profile-avatar" 
            />
          </motion.button>
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
