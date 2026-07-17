// src/components/challenge/ChallengeCard.jsx
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaCar, FaLightbulb, FaWater, FaUtensils, FaTrashAlt, FaLeaf,
  FaCheck, FaTimes, FaBolt, FaClock, FaStar, FaCloudDownloadAlt
} from 'react-icons/fa';
import GlassCard from '../common/GlassCard'; 
import './ChallengeCard.css';

const ChallengeCard = ({ challenge, onAccept, onComplete, onSkip, isLoadingAction }) => {
  const { title, description, category, difficulty, saving, xp, time, status } = challenge;

  const getCategoryIcon = (cat) => {
    switch (cat?.toLowerCase()) {
      case 'transport': return <FaCar />;
      case 'electricity': return <FaLightbulb />;
      case 'water': return <FaWater />;
      case 'food': return <FaUtensils />;
      case 'waste': return <FaTrashAlt />;
      default: return <FaLeaf />;
    }
  };

  return (
    <GlassCard className="main-challenge-card">
      {/* Decorative Gradient Background */}
      <div className={`challenge-bg-glow ${category?.toLowerCase()}-glow`}></div>

      <div className="challenge-card-header">
        <div className={`challenge-badge ${category?.toLowerCase()}-accent`}>
          {getCategoryIcon(category)} {category}
        </div>
        <div className={`difficulty-badge diff-${difficulty?.toLowerCase()}`}>
          {difficulty}
        </div>
      </div>

      <div className="challenge-card-body">
        <h2>{title}</h2>
        <p>{description}</p>
      </div>

      <div className="challenge-stats-grid">
        <div className="stat-box">
          <FaCloudDownloadAlt className="stat-icon saving-color" />
          <div className="stat-details">
            <span className="stat-val">{saving}</span>
            <span className="stat-lbl">Est. Saving</span>
          </div>
        </div>
        <div className="stat-box">
          <FaStar className="stat-icon xp-color" />
          <div className="stat-details">
            <span className="stat-val">+{xp} XP</span>
            <span className="stat-lbl">Reward</span>
          </div>
        </div>
        <div className="stat-box">
          <FaClock className="stat-icon time-color" />
          <div className="stat-details">
            <span className="stat-val">{time}</span>
            <span className="stat-lbl">Time Req.</span>
          </div>
        </div>
      </div>

      <div className="challenge-card-actions">
        <AnimatePresence mode="wait">
          {status === 'pending' && (
            <motion.div key="pending-actions" className="action-row" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <motion.button 
                className="btn-skip" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.95 }} onClick={onSkip} disabled={isLoadingAction}
              >
                <FaTimes /> Skip
              </motion.button>
              <motion.button 
                className="btn-accept" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.95 }} onClick={onAccept} disabled={isLoadingAction}
              >
                <FaBolt /> Accept Challenge
              </motion.button>
            </motion.div>
          )}

          {status === 'accepted' && (
            <motion.div key="accepted-actions" className="action-row" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <motion.button 
                className="btn-complete" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.95 }} onClick={onComplete} disabled={isLoadingAction}
              >
                <FaCheck /> Mark as Completed
              </motion.button>
            </motion.div>
          )}

          {status === 'completed' && (
            <motion.div key="completed-status" className="status-banner banner-success" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
              <FaCheck className="banner-icon" /> Challenge Completed! (+{xp} XP)
            </motion.div>
          )}

          {status === 'skipped' && (
            <motion.div key="skipped-status" className="status-banner banner-neutral" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
              <FaTimes className="banner-icon" /> Challenge Skipped
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </GlassCard>
  );
};

export default ChallengeCard;
