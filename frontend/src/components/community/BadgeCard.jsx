// src/components/community/BadgeCard.jsx
import { motion } from 'framer-motion';
import { FaLock, FaUnlock } from 'react-icons/fa';
import './BadgeCard.css';

const BadgeCard = ({ icon, title, description, isUnlocked }) => {
  return (
    <motion.div 
      className={`badge-glass-card ${isUnlocked ? 'unlocked' : 'locked'}`}
      whileHover={{ y: isUnlocked ? -5 : 0 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <div className="badge-icon-wrapper">
        <div className="badge-icon">{icon}</div>
        <div className="badge-status">
          {isUnlocked ? <FaUnlock className="status-unlocked" /> : <FaLock className="status-locked" />}
        </div>
      </div>
      <h4 className="badge-title">{title}</h4>
      <p className="badge-desc">{description}</p>
    </motion.div>
  );
};

export default BadgeCard;
