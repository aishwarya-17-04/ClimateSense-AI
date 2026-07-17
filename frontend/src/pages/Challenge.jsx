// src/pages/Challenge.jsx
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaTrophy, FaMedal, FaHistory, FaBrain, FaExclamationTriangle, FaRedo, FaCheckCircle, FaTimesCircle, FaLeaf
} from 'react-icons/fa';
import api from '../services/api';
import GlassCard from '../components/common/GlassCard';
import ProgressBar from '../components/common/ProgressBar';
import ChallengeCard from '../components/challenge/ChallengeCard';
import './Challenge.css';

// Fallback data if FastAPI is offline
const fallbackData = {
  challenge: {
    id: "chl-99",
    title: "Walk Instead of Driving",
    description: "Replace all driving trips under 2 km with walking today. Not only does this heavily reduce carbon emissions, but it improves cardiovascular health.",
    category: "Transport",
    difficulty: "Easy",
    saving: "2.5 kg CO₂",
    xp: 50,
    time: "20 minutes",
    status: "pending" // pending | accepted | completed | skipped
  },
  progress: {
    streak: 14,
    weeklyProgress: 75,
    monthlyProgress: 42
  },
  motivation: "Every small action creates a greener tomorrow. You've saved 12kg of CO₂ this week—keep the momentum going!",
  achievements: [
    { id: 1, title: "Eco Beginner", icon: <FaLeaf /> },
    { id: 2, title: "Green Warrior", icon: <FaMedal /> },
    { id: 3, title: "100kg CO₂ Saved", icon: <FaTrophy /> }
  ],
  history: [
    { id: "h1", title: "Meatless Monday", status: "completed", date: "Yesterday", xp: 50 },
    { id: "h2", title: "Unplug Devices", status: "skipped", date: "2 days ago", xp: 0 },
    { id: "h3", title: "Zero Waste Lunch", status: "completed", date: "3 days ago", xp: 75 }
  ]
};

const Challenge = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/challenge/today');
      setData(response.data);
    } catch (err) {
      console.warn("API unavailable, loading premium offline sandbox.", err);
      setData(fallbackData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    const loadInitialChallenge = async () => {
      try {
        const response = await api.get('/challenge/today');
        if (isMounted) {
          setData(response.data);
        }
      } catch (err) {
        console.warn("API unavailable, loading premium offline sandbox.", err);
        if (isMounted) {
          setData(fallbackData);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadInitialChallenge();

    return () => {
      isMounted = false;
    };
  }, []);

  // API Interaction Handlers
  const handleAction = async (endpoint, newStatus) => {
    setActionLoading(true);
    try {
      // E.g., api.post('/challenge/complete', { challengeId: data.challenge.id })
      await api.post(`/challenge/${endpoint}`, { id: data.challenge.id });
      setData(prev => ({
        ...prev,
        challenge: { ...prev.challenge, status: newStatus }
      }));
    } catch {
      // Sandbox Mode: simulate success locally if backend is off
      setData(prev => ({
        ...prev,
        challenge: { ...prev.challenge, status: newStatus }
      }));
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="challenge-page-container">
      {/* HEADER SECTION */}
      <header className="page-header">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <h1>Daily Eco <span className="text-highlight">Challenge</span></h1>
          <p className="subtitle">Complete today's challenge to improve your Climate Score and earn XP.</p>
        </motion.div>
      </header>

      <AnimatePresence mode="wait">
        {loading ? (
          /* SKELETON LOADER */
          <motion.div key="loading" className="challenge-grid" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="left-column">
              <div className="skeleton-box pulse" style={{ height: '400px', borderRadius: '24px' }}></div>
              <div className="skeleton-box pulse" style={{ height: '120px', borderRadius: '24px', marginTop: '24px' }}></div>
            </div>
            <div className="right-column">
              <div className="skeleton-box pulse" style={{ height: '250px', borderRadius: '24px', marginBottom: '24px' }}></div>
              <div className="skeleton-box pulse" style={{ height: '300px', borderRadius: '24px' }}></div>
            </div>
          </motion.div>
        ) : error ? (
          /* ERROR STATE */
          <motion.div key="error" className="error-panel" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <GlassCard className="error-card">
              <FaExclamationTriangle className="error-icon" />
              <h3>Unable to load challenge</h3>
              <p>{error}</p>
              <button onClick={fetchDashboardData} className="btn-retry">
                <FaRedo /> Retry Connection
              </button>
            </GlassCard>
          </motion.div>
        ) : (
          /* MAIN GRID */
          <motion.div key="content" className="challenge-grid" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            
            {/* LEFT COLUMN: Core Interactions */}
            <div className="left-column">
              <ChallengeCard 
                challenge={data.challenge}
                isLoadingAction={actionLoading}
                onAccept={() => handleAction('accept', 'accepted')}
                onComplete={() => handleAction('complete', 'completed')}
                onSkip={() => handleAction('skip', 'skipped')}
              />

              {/* AI Motivation Widget */}
              <GlassCard className="motivation-card" delay={0.2}>
                <div className="motivation-header">
                  <FaBrain className="ai-icon" /> <span>AI Coach Insight</span>
                </div>
                <p>"{data.motivation}"</p>
              </GlassCard>
            </div>

            {/* RIGHT COLUMN: Progress & History */}
            <div className="right-column">
              
              {/* Progress Summary */}
              <GlassCard className="progress-card" delay={0.3}>
                <h3>Your Progress</h3>
                <div className="streak-banner">
                  <FaTrophy className="streak-icon" />
                  <div>
                    <h4>{data.progress.streak} Day Streak!</h4>
                    <p>Keep it up, you're on a roll.</p>
                  </div>
                </div>
                
                <div className="progress-bars-container">
                  <div className="circular-progress-row">
                    <ProgressBar type="circular" progress={data.progress.weeklyProgress} label="Weekly Goal" />
                    <ProgressBar type="circular" progress={data.progress.monthlyProgress} label="Monthly Goal" color="var(--accent-green, #10b981)" />
                  </div>
                  <ProgressBar type="linear" progress={data.progress.weeklyProgress} label="XP to Next Level" color="#f59e0b" />
                </div>
              </GlassCard>

              {/* Badges & Achievements */}
              <GlassCard className="achievements-card" delay={0.4}>
                <h3>Earned Badges</h3>
                <div className="badges-grid">
                  {data.achievements.map(badge => (
                    <div key={badge.id} className="badge-item">
                      <div className="badge-icon-wrapper">
                        <FaMedal /> {/* Using standard medal fallback for safety */}
                      </div>
                      <span>{badge.title}</span>
                    </div>
                  ))}
                </div>
              </GlassCard>

              {/* Challenge History */}
              <GlassCard className="history-card" delay={0.5}>
                <div className="history-header">
                  <h3>Recent Challenges</h3>
                  <FaHistory className="history-title-icon" />
                </div>
                <ul className="history-list">
                  {data.history.map(item => (
                    <li key={item.id} className="history-item">
                      <div className="history-item-left">
                        {item.status === 'completed' ? (
                          <FaCheckCircle className="status-icon success-icon" />
                        ) : (
                          <FaTimesCircle className="status-icon neutral-icon" />
                        )}
                        <div>
                          <h4>{item.title}</h4>
                          <span className="history-date">{item.date}</span>
                        </div>
                      </div>
                      {item.xp > 0 && <span className="history-xp">+{item.xp} XP</span>}
                    </li>
                  ))}
                </ul>
              </GlassCard>

            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Challenge;
