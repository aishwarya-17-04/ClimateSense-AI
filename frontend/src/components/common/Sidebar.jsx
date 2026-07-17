import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaThLarge,
  FaChartPie,
  FaBullseye,
  FaUsers, 
  FaFileAlt,
  FaCog,
  FaUser,
  FaTimes
} from 'react-icons/fa';
import './Sidebar.css';

const navItems = [
  { path: '/dashboard', name: 'Dashboard', icon: FaThLarge },
  { path: '/carbon', name: 'Carbon Footprint', icon: FaChartPie },
  { path: '/recommendations', name: 'AI Interventions', icon: FaBullseye },
  { path: '/community', name: 'Community', icon: FaUsers },
  { path: '/report', name: 'Weekly Report', icon: FaFileAlt },
];

const bottomNavItems = [
  { path: '/profile', name: 'Profile', icon: FaUser },
  { path: '/settings', name: 'Settings', icon: FaCog },
];

const SidebarContent = ({ closeSidebar }) => (
  <>
    <div className="sidebar-header mobile-only">
      <span className="brand-text">Menu</span>
      <button className="close-btn" onClick={closeSidebar} aria-label="Close Sidebar">
        <FaTimes size={24} />
      </button>
    </div>

    <nav className="sidebar-nav">
      <span className="nav-label">Main Menu</span>
      <ul className="nav-list">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={closeSidebar}
              >
                <Icon className="nav-icon" />
                <span className="nav-text">{item.name}</span>
              </NavLink>
            </li>
          );
        })}
      </ul>

      <div className="sidebar-divider"></div>
      <span className="nav-label">Account</span>

      <ul className="nav-list">
        {bottomNavItems.map((item) => {
          const Icon = item.icon;
          return (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={closeSidebar}
              >
                <Icon className="nav-icon" />
                <span className="nav-text">{item.name}</span>
              </NavLink>
            </li>
          );
        })}
      </ul>
    </nav>

    <div className="sidebar-glow"></div>
  </>
);

const Sidebar = ({ isOpen, closeSidebar }) => {
  // Animation variants for the mobile sidebar overlay
  const mobileSidebarVariants = {
    closed: { x: '-100%', opacity: 0 },
    open: { x: 0, opacity: 1, transition: { type: 'spring', stiffness: 300, damping: 30 } }
  };

  return (
    <>
      {/* Desktop Sidebar (Always visible on large screens) */}
      <aside className="sidebar-container desktop-sidebar">
        <SidebarContent closeSidebar={closeSidebar} />
      </aside>

      {/* Mobile Sidebar (Controlled via framer-motion) */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div 
              className="mobile-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={closeSidebar}
            />
            <motion.aside 
              className="sidebar-container mobile-sidebar"
              variants={mobileSidebarVariants}
              initial="closed"
              animate="open"
              exit="closed"
            >
              <SidebarContent closeSidebar={closeSidebar} />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default Sidebar;
