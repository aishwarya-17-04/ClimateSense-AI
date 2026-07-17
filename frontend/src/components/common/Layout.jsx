// src/components/common/Layout.jsx
import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import './Layout.css';

const Layout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="layout-container">
      {/* Sidebar handles its own mobile visibility based on state */}
      <Sidebar isOpen={isSidebarOpen} closeSidebar={() => setIsSidebarOpen(false)} />
      
      <div className="layout-content">
        <Navbar toggleSidebar={toggleSidebar} />
        
        {/* Main scrollable content area */}
        <main className="main-viewport">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
