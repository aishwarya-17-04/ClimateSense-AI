// src/pages/Community.jsx
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaGlobe, FaUserFriends, FaLeaf, FaTrophy, 
  FaSearch, FaSeedling,
  FaExclamationTriangle, FaRedo, FaHistory
} from 'react-icons/fa';
import api from '../services/api';
import LeaderboardCard from '../components/community/LeaderboardCard';
import CommunityChallengeCard from '../components/community/CommunityChallengeCard';
import BadgeCard from '../components/community/BadgeCard';
import './Community.css';

// Sandbox Dummy Data
const CURRENT_USER_ID = 4;
const DUMMY_DATA = {
  stats: {
    globalRank: '4,281',
    friendsRank: '3',
    co2SavedTogether: '12,450 kg',
    challengesCompleted: '142'
  },
  leaderboard: [
    { id: 1, rank: 1, name: 'Elena R.', score: 15420, streak: 182, badge: 'Climate Hero', avatar: null },
    { id: 2, rank: 2, name: 'David K.', score: 14900, streak: 145, badge: 'Challenge Master', avatar: null },
    { id: 3, rank: 3, name: 'Sarah M.', score: 14250, streak: 90, badge: 'Green Influencer', avatar: null },
    { id: 4, rank: 4, name: 'You (Alex)', score: 13800, streak: 65, badge: '100kg Saved', avatar: null },
    { id: 5, rank: 5, name: 'James T.', score: 13100, streak: 42, badge: 'Eco Beginner', avatar: null },
    { id: 6, rank: 6, name: 'Maya P.', score: 12950, streak: 120, badge: 'Tree Planter', avatar: null },
    { id: 7, rank: 7, name: 'Chris W.', score: 12400, streak: 30, badge: 'Zero Waste', avatar: null },
    { id: 8, rank: 8, name: 'Nina S.', score: 11800, streak: 14, badge: 'Eco Beginner', avatar: null },
    { id: 9, rank: 9, name: 'Tom H.', score: 11200, streak: 7, badge: 'Newbie', avatar: null },
    { id: 10, rank: 10, name: 'Anna L.', score: 10500, streak: 5, badge: 'Newbie', avatar: null },
  ],
  challenges: [
    { id: 101, title: 'Bike to Work Week', description: 'Replace car commutes with cycling for 5 days.', participants: 8432, daysRemaining: 3, reward: '500 Pts + Badge' },
    { id: 102, title: 'Plastic Free Weekend', description: 'Avoid all single-use plastics from Friday to Sunday.', participants: 12050, daysRemaining: 1, reward: '300 Pts' },
    { id: 103, title: 'Tree Plantation Drive', description: 'Plant a tree in your local area and log it.', participants: 5210, daysRemaining: 14, reward: 'Exclusive Avatar' }
  ],
  badges: [
    { id: 'b1', title: 'Eco Beginner', desc: 'Completed first challenge.', icon: <FaSeedling />, isUnlocked: true },
    { id: 'b2', title: '100kg Saved', desc: 'Saved 100kg of CO2.', icon: <FaLeaf />, isUnlocked: true },
    { id: 'b3', title: 'Challenge Master', desc: 'Complete 50 challenges.', icon: <FaTrophy />, isUnlocked: false },
    { id: 'b4', title: 'Green Influencer', desc: 'Invite 5 friends.', icon: <FaUserFriends />, isUnlocked: false },
    { id: 'b5', title: 'Climate Hero', desc: 'Top 1% Global Rank.', icon: <FaGlobe />, isUnlocked: false }
  ],
  activity: [
    { id: 1, user: 'Alice', action: 'completed', target: 'Zero Waste Challenge', time: '2 hours ago' },
    { id: 2, user: 'John', action: 'reached', target: 'a 30-day streak', time: '4 hours ago' },
    { id: 3, user: 'Emma', action: 'planted', target: '5 trees', time: '5 hours ago' }
  ]
};

const badgeIcons = {
  seedling: <FaSeedling />,
  leaf: <FaLeaf />,
  trophy: <FaTrophy />,
  users: <FaUserFriends />,
  globe: <FaGlobe />,
};

const withBadgeIcons = (badges) => badges.map((badge) => ({
  ...badge,
  icon: typeof badge.icon === 'string' ? badgeIcons[badge.icon] || <FaLeaf /> : badge.icon,
}));

const Community = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('Global');

  const filters = ['All', 'Friends', 'College', 'Global'];

  const fetchCommunityData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Simulate parallel API calls
      const [statsRes, lbRes, chRes, actRes, badgesRes] = await Promise.all([
        api.get('/community/stats').catch(() => ({ data: DUMMY_DATA.stats })),
        api.get('/community/leaderboard').catch(() => ({ data: DUMMY_DATA.leaderboard })),
        api.get('/community/challenges').catch(() => ({ data: DUMMY_DATA.challenges })),
        api.get('/community/activity').catch(() => ({ data: DUMMY_DATA.activity })),
        api.get('/community/badges').catch(() => ({ data: DUMMY_DATA.badges }))
      ]);
      
      // In a real app, badges and stats might come from a user profile endpoint
      setData({
        stats: statsRes.data,
        leaderboard: lbRes.data,
        challenges: chRes.data,
        activity: actRes.data,
        badges: withBadgeIcons(badgesRes.data)
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

    const loadInitialCommunity = async () => {
      try {
        const [statsRes, lbRes, chRes, actRes, badgesRes] = await Promise.all([
          api.get('/community/stats').catch(() => ({ data: DUMMY_DATA.stats })),
          api.get('/community/leaderboard').catch(() => ({ data: DUMMY_DATA.leaderboard })),
          api.get('/community/challenges').catch(() => ({ data: DUMMY_DATA.challenges })),
          api.get('/community/activity').catch(() => ({ data: DUMMY_DATA.activity })),
          api.get('/community/badges').catch(() => ({ data: DUMMY_DATA.badges }))
        ]);

        if (isMounted) {
          setData({
            stats: statsRes.data,
            leaderboard: lbRes.data,
            challenges: chRes.data,
            activity: actRes.data,
            badges: withBadgeIcons(badgesRes.data)
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

    loadInitialCommunity();

    return () => {
      isMounted = false;
    };
  }, [activeFilter]); // Refetch when filter changes

  const handleJoinChallenge = async (id) => {
    try {
      await api.post('/community/join', { challengeId: id });
      alert('Successfully joined the challenge!');
    } catch {
      alert('Joined challenge! (Sandbox Mode)');
    }
  };

  const filteredLeaderboard = data?.leaderboard.filter(user => 
    user.name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="community-page-layout">
      {/* HEADER SECTION */}
      <header className="community-header">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <h1>Community</h1>
          <p className="page-subtitle">Compete, collaborate, and grow together for a greener future.</p>
        </motion.div>
      </header>

      {/* STATS SECTION */}
      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div key="loading" className="loading-skeleton pulse" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="sk-grid-4"><div className="sk-box"></div><div className="sk-box"></div><div className="sk-box"></div><div className="sk-box"></div></div>
            <div className="sk-grid-layout">
              <div className="sk-box large"></div>
              <div className="sk-col"><div className="sk-box medium"></div><div className="sk-box medium"></div></div>
            </div>
          </motion.div>
        ) : error ? (
          <motion.div key="error" className="error-container" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="glass-error-card">
              <FaExclamationTriangle className="error-icon" />
              <h3>Failed to load community data</h3>
              <button onClick={fetchCommunityData} className="btn-retry"><FaRedo /> Retry</button>
            </div>
          </motion.div>
        ) : (
          <motion.div key="content" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            
            <section className="community-stats-grid">
              <div className="stat-glass-card">
                <FaGlobe className="stat-icon seafoam" />
                <div className="stat-info">
                  <span className="stat-label">Global Rank</span>
                  <span className="stat-value">#{data.stats.globalRank}</span>
                </div>
              </div>
              <div className="stat-glass-card">
                <FaUserFriends className="stat-icon purple" />
                <div className="stat-info">
                  <span className="stat-label">Friends Rank</span>
                  <span className="stat-value">#{data.stats.friendsRank}</span>
                </div>
              </div>
              <div className="stat-glass-card">
                <FaLeaf className="stat-icon green" />
                <div className="stat-info">
                  <span className="stat-label">CO₂ Saved Together</span>
                  <span className="stat-value">{data.stats.co2SavedTogether}</span>
                </div>
              </div>
              <div className="stat-glass-card">
                <FaTrophy className="stat-icon gold" />
                <div className="stat-info">
                  <span className="stat-label">Challenges Completed</span>
                  <span className="stat-value">{data.stats.challengesCompleted}</span>
                </div>
              </div>
            </section>

            {/* CONTROLS (Search & Filters) */}
            <section className="community-controls">
              <div className="search-bar-container">
                <FaSearch className="search-icon" />
                <input 
                  type="text" 
                  placeholder="Search explorers..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                />
              </div>
              <div className="filter-tabs">
                {filters.map(filter => (
                  <button 
                    key={filter} 
                    className={`filter-btn ${activeFilter === filter ? 'active' : ''}`}
                    onClick={() => setActiveFilter(filter)}
                  >
                    {filter}
                  </button>
                ))}
              </div>
            </section>

            {/* MAIN GRID */}
            <div className="community-main-grid">
              
              {/* LEFT COLUMN: Leaderboard & Badges */}
              <div className="main-left-col">
                <section className="section-block">
                  <h2 className="section-title">Leaderboard</h2>
                  <LeaderboardCard users={filteredLeaderboard} currentUserId={CURRENT_USER_ID} />
                </section>

                <section className="section-block">
                  <h2 className="section-title">Your Badges</h2>
                  <div className="badges-grid">
                    {data.badges.map(badge => (
                      <BadgeCard key={badge.id} {...badge} />
                    ))}
                  </div>
                </section>
              </div>

              {/* RIGHT COLUMN: Challenges & Activity */}
              <div className="main-right-col">
                <section className="section-block">
                  <h2 className="section-title">Active Challenges</h2>
                  <div className="challenges-list">
                    {data.challenges.map(challenge => (
                      <CommunityChallengeCard 
                        key={challenge.id} 
                        challenge={challenge} 
                        onJoin={handleJoinChallenge} 
                      />
                    ))}
                  </div>
                </section>

                <section className="section-block">
                  <h2 className="section-title">Recent Activity</h2>
                  <div className="activity-glass-card">
                    <ul className="activity-list">
                      {data.activity.map((act) => (
                        <li key={act.id} className="activity-item">
                          <div className="activity-icon-wrapper"><FaHistory /></div>
                          <div className="activity-content">
                            <p><strong>{act.user}</strong> {act.action} <span className="activity-highlight">{act.target}</span></p>
                            <span className="activity-time">{act.time}</span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </section>
              </div>

            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Community;
