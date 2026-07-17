// src/pages/Dashboard.jsx
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Correct, unified React Icon Imports to prevent undefined references
import {
  FaLeaf,
  FaAward,
  FaBolt,
  FaArrowRight,
} from "react-icons/fa";

import { FiTrendingDown } from "react-icons/fi";
import { BsActivity } from "react-icons/bs";

import api from '../services/api';
import GlassCard from '../components/common/GlassCard';
import './Dashboard.css';

// --- DUMMY DATA ---
const mockUserData = {
  name: "Julian",
  climateScore: 84,
  co2Saved: "12.4",
  streak: 12
};

const mockChartData = [
  { day: 'Mon', emissions: 18.2 },
  { day: 'Tue', emissions: 16.5 },
  { day: 'Wed', emissions: 14.2 },
  { day: 'Thu', emissions: 15.0 },
  { day: 'Fri', emissions: 12.8 },
  { day: 'Sat', emissions: 10.5 },
  { day: 'Sun', emissions: 9.2 },
];

const mockActivities = [
  { id: 1, text: "Logged smart commute", points: "+15 XP", time: "2h ago" },
  { id: 2, text: "Completed Meat-free Monday", points: "+50 XP", time: "5h ago" },
  { id: 3, text: "Recycled electronics", points: "+30 XP", time: "1d ago" },
];

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadDashboard = async () => {
      try {
        const response = await api.get('/dashboard');
        if (isMounted) {
          setDashboardData(response.data);
        }
      } catch (err) {
        console.warn("Dashboard API unavailable, loading fallback data.", err);
        if (isMounted) {
          setDashboardData({
            user: mockUserData,
            chartData: mockChartData,
            activities: mockActivities,
            challenge: {
              title: "Zero-Waste Lunch",
              description: "Avoid single-use plastics today. Pack your meals using reusables.",
            },
          });
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      isMounted = false;
    };
  }, []);

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <motion.div 
          animate={{ rotate: 360 }} 
          transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
        >
          <FaLeaf size={48} color="var(--accent-seafoam)" />
        </motion.div>
      </div>
    );
  }

  const userData = dashboardData.user;
  const chartData = dashboardData.chartData;
  const activities = dashboardData.activities;
  const challenge = dashboardData.challenge;

  return (
    <div className="dashboard-container">
      
      {/* HEADER SECTION */}
      <header className="dashboard-header">
        <motion.div 
          initial={{ opacity: 0, x: -20 }} 
          animate={{ opacity: 1, x: 0 }} 
          transition={{ duration: 0.5 }}
        >
          <h1>Welcome back, <span className="text-highlight">{userData.name}</span></h1>
          <p className="subtitle">Let's make a positive impact today.</p>
        </motion.div>
        
        <motion.div 
          className="user-avatar"
          initial={{ opacity: 0, scale: 0.8 }} 
          animate={{ opacity: 1, scale: 1 }} 
          transition={{ delay: 0.2 }}
        >
          <img src={`https://ui-avatars.com/api/?name=${userData.name}&background=38bdf8&color=fff`} alt="User" />
        </motion.div>
      </header>

      <div className="dashboard-grid">
        
        {/* METRICS ROW */}
        <div className="metrics-row">
          <GlassCard delay={0.1} className="metric-card">
            <div className="metric-header">
              <div className="icon-box icon-seafoam"><FaLeaf /></div>
              <span>Climate Score</span>
            </div>
            <div className="metric-value">
              <h2>{userData.climateScore}</h2>
              <span className="badge positive">Top 15%</span>
            </div>
          </GlassCard>

          <GlassCard delay={0.2} className="metric-card">
            <div className="metric-header">
              <div className="icon-box icon-green"><FiTrendingDown /></div>
              <span>CO₂ Saved This Month</span>
            </div>
            <div className="metric-value">
              <h2>{userData.co2Saved} <span className="unit">kg</span></h2>
            </div>
          </GlassCard>

          <GlassCard delay={0.3} className="metric-card challenge-highlight">
            <div className="metric-header">
              <div className="icon-box icon-gold"><FaAward /></div>
              <span>Current Streak</span>
            </div>
            <div className="metric-value">
              <h2>{userData.streak} <span className="unit">Days</span></h2>
            </div>
          </GlassCard>
        </div>

        {/* MAIN CONTENT AREA */}
        <div className="main-content-row">
          
          {/* CHART COMPONENT */}
          <GlassCard delay={0.4} className="chart-card">
            <div className="card-header">
              <h3>Weekly Carbon Trend</h3>
              <select className="glass-select">
                <option>This Week</option>
                <option>Last Week</option>
              </select>
            </div>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorEmissions" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--accent-seafoam)" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="var(--accent-seafoam)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" vertical={false} />
                  <XAxis dataKey="day" stroke="var(--text-secondary)" tick={{fontSize: 12}} axisLine={false} tickLine={false} />
                  <YAxis stroke="var(--text-secondary)" tick={{fontSize: 12}} axisLine={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#112a38', border: '1px solid var(--glass-border)', borderRadius: '12px', color: '#fff' }}
                    itemStyle={{ color: 'var(--accent-seafoam)' }}
                  />
                  <Area type="monotone" dataKey="emissions" stroke="var(--accent-seafoam)" strokeWidth={3} fillOpacity={1} fill="url(#colorEmissions)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          {/* RIGHT SIDEBAR PANEL */}
          <div className="sidebar-column">
            
            {/* TODAY'S CHALLENGE */}
            <GlassCard delay={0.5} className="action-card">
              <div className="card-header">
                <h3>Today's Eco Challenge</h3>
                <FaBolt color="var(--accent-seafoam)" size={20} />
              </div>
              <div className="challenge-content">
                <h4>{challenge.title}</h4>
                <p>{challenge.description}</p>
                <motion.button 
                  className="btn-primary"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Accept Challenge
                </motion.button>
              </div>
            </GlassCard>

            {/* RECENT ACTIVITY */}
            <GlassCard delay={0.6} className="activity-card">
              <div className="card-header">
                <h3>Recent Activity</h3>
                <BsActivity color="var(--text-secondary)" />
              </div>
              <ul className="activity-list">
                {activities.map(activity => (
                  <li key={activity.id} className="activity-item">
                    <div className="activity-info">
                      <p>{activity.text}</p>
                      <span className="activity-time">{activity.time}</span>
                    </div>
                    <span className="activity-points">{activity.points}</span>
                  </li>
                ))}
              </ul>
            </GlassCard>

          </div>
        </div>

        {/* QUICK NAVIGATION / ACTIONS */}
        <div className="quick-actions-row">
          {['Log Daily Footprint', 'View AI Recommendations', 'Community Leaderboard'].map((title, index) => (
            <GlassCard key={index} delay={0.7 + (index * 0.1)} className="nav-card">
              <h4>{title}</h4>
              <div className="nav-icon"><FaArrowRight /></div>
            </GlassCard>
          ))}
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
