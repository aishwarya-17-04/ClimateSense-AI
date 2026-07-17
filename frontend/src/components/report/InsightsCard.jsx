// src/components/report/InsightsCard.jsx
import { FaBrain, FaCheckCircle, FaExclamationCircle, FaInfoCircle } from 'react-icons/fa';
import GlassCard from '../common/GlassCard';
import './InsightsCard.css';

const InsightsCard = ({ insights }) => {
  const getIcon = (type) => {
    switch(type) {
      case 'positive': return <FaCheckCircle className="insight-icon text-green" />;
      case 'negative': return <FaExclamationCircle className="insight-icon text-red" />;
      default: return <FaInfoCircle className="insight-icon text-seafoam" />;
    }
  };

  return (
    <GlassCard className="insights-glass-card">
      <div className="insights-header">
        <div className="ai-badge">
          <FaBrain /> AI Analysis
        </div>
        <h3>Weekly Insights</h3>
      </div>
      <ul className="insights-list">
        {insights.map((insight, index) => (
          <li key={index} className="insight-item">
            {getIcon(insight.type)}
            <p>{insight.text}</p>
          </li>
        ))}
      </ul>
    </GlassCard>
  );
};

export default InsightsCard;
