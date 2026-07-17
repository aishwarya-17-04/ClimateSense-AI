// src/components/profile/StatsCard.jsx
import { motion } from 'framer-motion';
import './StatsCard.css';

const StatsCard = ({ title, value, icon, colorClass }) => {
  return (
    <motion.div 
      className="profile-stats-card"
      whileHover={{ y: -5 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <div className={`stats-icon-wrapper ${colorClass}`}>
        {icon}
      </div>
      <div className="stats-info">
        <h4 className="stats-title">{title}</h4>
        <span className="stats-value">{value}</span>
      </div>
    </motion.div>
  );
};

export default StatsCard;
