// src/components/community/CommunityChallengeCard.jsx
import { motion } from 'framer-motion';
import { FaUsers, FaClock, FaGift, FaArrowRight } from 'react-icons/fa';
import './CommunityChallengeCard.css';

const CommunityChallengeCard = ({ challenge, onJoin }) => {
  return (
    <motion.div 
      className="challenge-glass-card"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="challenge-card-header">
        <h3 className="challenge-title">{challenge.title}</h3>
        <span className="challenge-badge">Active</span>
      </div>
      
      <p className="challenge-description">{challenge.description}</p>
      
      <div className="challenge-meta-grid">
        <div className="meta-item">
          <FaUsers className="meta-icon" />
          <span>{challenge.participants.toLocaleString()} Joined</span>
        </div>
        <div className="meta-item">
          <FaClock className="meta-icon" />
          <span>{challenge.daysRemaining} Days Left</span>
        </div>
        <div className="meta-item reward">
          <FaGift className="meta-icon" />
          <span>{challenge.reward}</span>
        </div>
      </div>

      <button onClick={() => onJoin(challenge.id)} className="btn-join-challenge">
        Join Challenge <FaArrowRight />
      </button>
    </motion.div>
  );
};

export default CommunityChallengeCard;
