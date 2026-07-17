// src/components/profile/AchievementCard.jsx
import { motion } from 'framer-motion';
import { FaLock, FaCheckCircle } from 'react-icons/fa';
import './AchievementCard.css';

const AchievementCard = ({ icon, title, description, isUnlocked }) => {
  return (
    <motion.div 
      className={`achievement-card ${isUnlocked ? 'unlocked' : 'locked'}`}
      whileHover={isUnlocked ? { scale: 1.03 } : {}}
    >
      <div className="achievement-icon-container">
        <div className="achievement-icon">{icon}</div>
        <div className="achievement-status">
          {isUnlocked ? <FaCheckCircle className="status-check" /> : <FaLock className="status-lock" />}
        </div>
      </div>
      <div className="achievement-details">
        <h4 className="achievement-title">{title}</h4>
        <p className="achievement-desc">{description}</p>
      </div>
    </motion.div>
  );
};

export default AchievementCard;
