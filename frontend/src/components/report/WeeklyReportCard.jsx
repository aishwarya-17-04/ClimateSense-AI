// src/components/report/WeeklySummaryCard.jsx
import { motion } from 'framer-motion';
import { FaArrowUp, FaArrowDown, FaMinus } from 'react-icons/fa';
import GlassCard from '../common/GlassCard';
import './WeeklyReportCard.css';

const WeeklySummaryCard = ({ title, value, unit, icon, trend, trendValue, colorClass }) => {
  const renderTrendIcon = () => {
    if (trend === 'up') return <FaArrowUp />;
    if (trend === 'down') return <FaArrowDown />;
    return <FaMinus />;
  };

  return (
    <motion.div whileHover={{ y: -5 }}>
      <GlassCard className="weekly-summary-card">
        <div className="summary-header">
          <div className={`summary-icon-box ${colorClass}`}>
            {icon}
          </div>
          <span className="summary-title">{title}</span>
        </div>
        
        <div className="summary-body">
          <h2 className="summary-value">
            {value} <span className="summary-unit">{unit}</span>
          </h2>
        </div>

        <div className={`summary-footer trend-${trend}`}>
          <span className="trend-icon">{renderTrendIcon()}</span>
          <span className="trend-text">{trendValue} vs last week</span>
        </div>
      </GlassCard>
    </motion.div>
  );
};

export default WeeklySummaryCard;
