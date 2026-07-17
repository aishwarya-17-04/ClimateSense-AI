// src/pages/Profile.jsx
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaChartLine, FaLeaf, FaTrophy, FaTree, FaMedal, 
  FaCog, FaHistory, FaBullseye, FaExclamationTriangle, FaRedo, FaSeedling, FaGlobe, FaShieldAlt, FaFire
} from 'react-icons/fa';
import api from '../services/api';
import ProfileCard from '../components/profile/ProfileCard';
import StatsCard from '../components/profile/StatsCard';
import AchievementCard from '../components/profile/AchievementCard';
import './ProfileCard.css';

// Sandbox Dummy Data
const DUMMY_DATA = {
  profile: {
    name: 'Alex Johnson',
    email: 'alex.j@example.com',
    country: 'Canada',
    city: 'Vancouver',
    memberSince: '2025',
    climateLevel: 'Sustainability Advocate',
    level: 12,
    currentXP: 4500,
    nextLevelXP: 5000,
    streak: 30,
    avatar: null
  },
  stats: {
    carbonScore: 85,
    co2Saved: '245 kg',
    challengesCompleted: 42,
    treesSaved: 14,
    currentRank: '#4,281'
  },
  achievements: [
    { id: 'a1', title: 'Eco Beginner', description: 'Calculated first footprint.', icon: <FaSeedling />, isUnlocked: true },
    { id: 'a2', title: '100kg Saved', description: 'Saved 100kg of CO2.', icon: <FaLeaf />, isUnlocked: true },
    { id: 'a3', title: '30-Day Streak', description: 'Maintained a 30-day active streak.', icon: <FaFire />, isUnlocked: true },
    { id: 'a4', title: 'Climate Hero', description: 'Reached top 5% in community.', icon: <FaGlobe />, isUnlocked: false },
    { id: 'a5', title: 'Green Warrior', description: 'Complete 100 challenges.', icon: <FaShieldAlt />, isUnlocked: false }
  ],
  goals: {
    weekly: { label: 'Weekly CO2 Target', current: 15, target: 25, unit: 'kg' },
    monthly: { label: 'Monthly Challenges', current: 8, target: 10, unit: 'challenges' },
    yearly: { label: 'Yearly Trees Equivalent', current: 14, target: 50, unit: 'trees' }
  },
  activity: [
    { id: 1, action: 'Followed AI recommendation', detail: 'Switched to cold water laundry.', time: '2 hours ago' },
    { id: 2, action: 'Completed challenge', detail: 'Zero Waste Weekend.', time: '1 day ago' },
    { id: 3, action: 'Updated footprint', detail: 'Logged daily commute.', time: '2 days ago' }
  ]
};

const achievementIcons = {
  seedling: <FaSeedling />,
  leaf: <FaLeaf />,
  fire: <FaFire />,
  globe: <FaGlobe />,
  shield: <FaShieldAlt />,
};

const withAchievementIcons = (achievements) => achievements.map((achievement) => ({
  ...achievement,
  icon: typeof achievement.icon === 'string'
    ? achievementIcons[achievement.icon] || <FaMedal />
    : achievement.icon,
}));

const Profile = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProfileData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [profRes, statsRes, achRes, goalsRes, activityRes] = await Promise.all([
        api.get('/profile').catch(() => ({ data: DUMMY_DATA.profile })),
        api.get('/profile/stats').catch(() => ({ data: DUMMY_DATA.stats })),
        api.get('/profile/achievements').catch(() => ({ data: DUMMY_DATA.achievements })),
        api.get('/profile/goals').catch(() => ({ data: DUMMY_DATA.goals })),
        api.get('/profile/activity').catch(() => ({ data: DUMMY_DATA.activity })),
      ]);

      setData({
        profile: profRes.data,
        stats: statsRes.data,
        achievements: withAchievementIcons(achRes.data),
        goals: goalsRes.data,
        activity: activityRes.data,
      });
    } catch (err) {
      console.warn("API Failed. Loading sandbox data.", err);
      setData(DUMMY_DATA);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    const loadInitialProfile = async () => {
      try {
        const [profRes, statsRes, achRes, goalsRes, activityRes] = await Promise.all([
          api.get('/profile').catch(() => ({ data: DUMMY_DATA.profile })),
          api.get('/profile/stats').catch(() => ({ data: DUMMY_DATA.stats })),
          api.get('/profile/achievements').catch(() => ({ data: DUMMY_DATA.achievements })),
          api.get('/profile/goals').catch(() => ({ data: DUMMY_DATA.goals })),
          api.get('/profile/activity').catch(() => ({ data: DUMMY_DATA.activity })),
        ]);

        if (isMounted) {
          setData({
            profile: profRes.data,
            stats: statsRes.data,
            achievements: withAchievementIcons(achRes.data),
            goals: goalsRes.data,
            activity: activityRes.data,
          });
        }
      } catch (err) {
        console.warn("API Failed. Loading sandbox data.", err);
        if (isMounted) {
          setData(DUMMY_DATA);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadInitialProfile();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleEditProfile = () => {
    alert("Edit Profile modal would open here.");
  };

  return (
    <div className="profile-page-container">
      {/* HEADER SECTION */}
      <header className="profile-header">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <h1>My Profile</h1>
          <p className="page-subtitle">Track your sustainability journey and achievements.</p>
        </motion.div>
        
        <motion.div className="header-actions" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          <button className="btn-icon-secondary"><FaChartLine /> View Weekly Report</button>
          <button className="btn-icon-secondary"><FaCog /> Open Settings</button>
        </motion.div>
      </header>

      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div key="loading" className="profile-skeleton pulse" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="skeleton-grid">
              <div className="sk-sidebar"><div className="sk-box tall"></div></div>
              <div className="sk-main">
                <div className="sk-stats-grid"><div className="sk-box"></div><div className="sk-box"></div><div className="sk-box"></div><div className="sk-box"></div></div>
                <div className="sk-box medium"></div>
              </div>
            </div>
          </motion.div>
        ) : error ? (
          <motion.div key="error" className="error-wrapper" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="glass-error-card">
              <FaExclamationTriangle className="error-icon" />
              <h3>Failed to load profile data</h3>
              <button onClick={fetchProfileData} className="btn-retry"><FaRedo /> Retry</button>
            </div>
          </motion.div>
        ) : (
          <motion.div key="content" className="profile-layout-grid" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            
            {/* LEFT COLUMN */}
            <div className="profile-sidebar">
              <ProfileCard user={data.profile} onEdit={handleEditProfile} />

              {/* PERSONAL GOALS */}
              <div className="glass-panel">
                <h3 className="panel-title"><FaBullseye className="title-icon" /> Personal Goals</h3>
                <div className="goals-list">
                  {Object.entries(data.goals).map(([key, goal]) => (
                    <div key={key} className="goal-item">
                      <div className="goal-info">
                        <span className="goal-label">{goal.label}</span>
                        <span className="goal-progress-text">{goal.current} / {goal.target} {goal.unit}</span>
                      </div>
                      <div className="goal-track">
                        <motion.div 
                          className="goal-fill" 
                          initial={{ width: 0 }} 
                          animate={{ width: `${(goal.current / goal.target) * 100}%` }} 
                          transition={{ duration: 1, ease: "easeOut" }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* RIGHT COLUMN */}
            <div className="profile-main-content">
              
              {/* STATISTICS GRID */}
              <div className="stats-grid">
                <StatsCard title="Carbon Score" value={data.stats.carbonScore} icon={<FaChartLine />} colorClass="seafoam" />
                <StatsCard title="Total CO₂ Saved" value={data.stats.co2Saved} icon={<FaLeaf />} colorClass="green" />
                <StatsCard title="Challenges" value={data.stats.challengesCompleted} icon={<FaTrophy />} colorClass="gold" />
                <StatsCard title="Trees Equivalent" value={data.stats.treesSaved} icon={<FaTree />} colorClass="green" />
                <StatsCard title="Current Rank" value={data.stats.currentRank} icon={<FaMedal />} colorClass="purple" />
              </div>

              {/* ACHIEVEMENTS */}
              <div className="glass-panel">
                <h3 className="panel-title"><FaMedal className="title-icon text-gold" /> Achievements</h3>
                <div className="achievements-grid">
                  {data.achievements.map((ach) => (
                    <AchievementCard key={ach.id} {...ach} />
                  ))}
                </div>
              </div>

              {/* RECENT ACTIVITY */}
              <div className="glass-panel">
                <h3 className="panel-title"><FaHistory className="title-icon" /> Recent Activity</h3>
                <ul className="activity-list">
                  {data.activity.map((item) => (
                    <li key={item.id} className="activity-item">
                      <div className="activity-bullet"></div>
                      <div className="activity-details">
                        <p className="activity-action"><strong>{item.action}:</strong> {item.detail}</p>
                        <span className="activity-time">{item.time}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>

            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Profile;
