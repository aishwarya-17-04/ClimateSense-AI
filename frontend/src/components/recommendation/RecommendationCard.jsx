// src/components/recommendation/RecommendationCard.jsx
import { motion } from 'framer-motion';
import { 
  FaCar, 
  FaLightbulb, 
  FaWater, 
  FaUtensils, 
  FaTrashAlt, 
  FaLeaf, 
  FaCloudDownloadAlt 
} from 'react-icons/fa';
import GlassCard from '../common/GlassCard';
import './RecommendationCard.css';

const RecommendationCard = ({ recommendation }) => {
  const { category, title, description, saving, difficulty } = recommendation;

  // Map categories to Font Awesome Icons
  const getCategoryIcon = (cat) => {
    switch (cat?.toLowerCase()) {
      case 'transport':
        return <FaCar />;
      case 'electricity':
        return <FaLightbulb />;
      case 'water':
        return <FaWater />;
      case 'food':
        return <FaUtensils />;
      case 'waste':
        return <FaTrashAlt />;
      default:
        return <FaLeaf />;
    }
  };

  // Assign semantic dynamic CSS classes based on task difficulty
  const getDifficultyClass = (diff) => {
    switch (diff?.toLowerCase()) {
      case 'easy':
        return 'diff-easy';
      case 'medium':
        return 'diff-medium';
      case 'hard':
        return 'diff-hard';
      default:
        return 'diff-easy';
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -6, transition: { duration: 0.2 } }}
      className="recommendation-card-wrapper"
    >
      <GlassCard className="rec-card">
        <div className={`rec-category-badge ${category?.toLowerCase()}-accent`}>
          <span className="rec-icon">{getCategoryIcon(category)}</span>
          <span className="rec-cat-text">{category}</span>
        </div>

        <div className="rec-content">
          <h3 className="rec-title">{title}</h3>
          <p className="rec-description">{description}</p>
        </div>

        <div className="rec-footer">
          <div className="rec-stat">
            <span className="stat-label">Est. Saving</span>
            <span className="stat-value saving-highlight">
              <FaCloudDownloadAlt className="stat-icon" />
              {saving}
            </span>
          </div>

          <div className="rec-stat">
            <span className="stat-label">Difficulty</span>
            <span className={`difficulty-badge ${getDifficultyClass(difficulty)}`}>
              {difficulty}
            </span>
          </div>
        </div>
      </GlassCard>
    </motion.div>
  );
};

export default RecommendationCard;
