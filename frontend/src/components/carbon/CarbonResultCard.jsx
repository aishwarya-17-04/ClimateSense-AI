// src/components/carbon/CarbonResultCard.jsx
import { motion } from 'framer-motion';
import { 
  FaCar, 
  FaLightbulb, 
  FaWater, 
  FaUtensils, 
  FaTrashAlt, 
  FaRedo
} from 'react-icons/fa';
import GlassCard from '../common/GlassCard';
import './CarbonResultCard.css';

const CarbonResultCard = ({ results, onReset }) => {
  // Safe extraction of metrics with fallbacks to avoid crashes
  const emissions = results.emissions_by_category ?? results.emissions ?? {};
  const transportEmissions = parseFloat(emissions.transport ?? 0).toFixed(2);
  const electricityEmissions = parseFloat(emissions.electricity ?? 0).toFixed(2);
  const waterEmissions = parseFloat(emissions.water ?? 0).toFixed(2);
  const foodEmissions = parseFloat(emissions.food ?? 0).toFixed(2);
  const wasteEmissions = parseFloat(emissions.waste ?? 0).toFixed(2);
  
  const totalCo2Value = Number(results.total_carbon_kg_co2 ?? results.total_co2 ?? 0);
  const totalCo2 = totalCo2Value.toFixed(2);
  const carbonScore = results.carbon_score ?? Math.max(0, Math.min(100, Math.round(100 - totalCo2Value * 2)));

  // Stagger animation rules
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const cardVariants = {
    hidden: { y: 25, opacity: 0 },
    show: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 100, damping: 15 } }
  };

  // Helper to dynamically style Carbon Score
  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'; // Green
    if (score >= 50) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  return (
    <div className="results-container">
      {/* Top Banner Row */}
      <div className="results-hero">
        <GlassCard className="score-glass-card">
          <div className="hero-grid">
            <div className="composite-metric-block">
              <span className="hero-label">Total Daily CO₂ Saved / Emitted</span>
              <h2 className="hero-value">{totalCo2} <span className="hero-unit">kg CO₂e</span></h2>
            </div>
            <div className="composite-metric-block border-left">
              <span className="hero-label">Your Carbon Score</span>
              <h2 className="hero-value" style={{ color: getScoreColor(carbonScore) }}>{carbonScore} <span className="hero-unit">/ 100</span></h2>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Grid of Micro-Metrics with stagger animations */}
      <motion.div 
        className="results-grid"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {/* Transport Emissions Card */}
        <motion.div variants={cardVariants}>
          <GlassCard className="result-metric-card">
            <div className="result-metric-header">
              <div className="metric-icon-box transport-accent"><FaCar /></div>
              <h4>Transport</h4>
            </div>
            <div className="result-metric-body">
              <h3>{transportEmissions} <span className="unit">kg</span></h3>
              <p className="metric-status">CO₂ Equivalent</p>
            </div>
          </GlassCard>
        </motion.div>

        {/* Electricity Emissions Card */}
        <motion.div variants={cardVariants}>
          <GlassCard className="result-metric-card">
            <div className="result-metric-header">
              <div className="metric-icon-box electricity-accent"><FaLightbulb /></div>
              <h4>Electricity</h4>
            </div>
            <div className="result-metric-body">
              <h3>{electricityEmissions} <span className="unit">kg</span></h3>
              <p className="metric-status">CO₂ Equivalent</p>
            </div>
          </GlassCard>
        </motion.div>

        {/* Water Emissions Card */}
        <motion.div variants={cardVariants}>
          <GlassCard className="result-metric-card">
            <div className="result-metric-header">
              <div className="metric-icon-box water-accent"><FaWater /></div>
              <h4>Water Usage</h4>
            </div>
            <div className="result-metric-body">
              <h3>{waterEmissions} <span className="unit">kg</span></h3>
              <p className="metric-status">CO₂ Equivalent</p>
            </div>
          </GlassCard>
        </motion.div>

        {/* Food Emissions Card */}
        <motion.div variants={cardVariants}>
          <GlassCard className="result-metric-card">
            <div className="result-metric-header">
              <div className="metric-icon-box food-accent"><FaUtensils /></div>
              <h4>Food Diet</h4>
            </div>
            <div className="result-metric-body">
              <h3>{foodEmissions} <span className="unit">kg</span></h3>
              <p className="metric-status">CO₂ Equivalent</p>
            </div>
          </GlassCard>
        </motion.div>

        {/* Waste Emissions Card */}
        <motion.div variants={cardVariants}>
          <GlassCard className="result-metric-card">
            <div className="result-metric-header">
              <div className="metric-icon-box waste-accent"><FaTrashAlt /></div>
              <h4>Waste Materials</h4>
            </div>
            <div className="result-metric-body">
              <h3>{wasteEmissions} <span className="unit">kg</span></h3>
              <p className="metric-status">CO₂ Equivalent</p>
            </div>
          </GlassCard>
        </motion.div>
      </motion.div>

      {/* Action Bar */}
      <div className="results-footer-actions">
        <motion.button 
          onClick={onReset} 
          className="btn-secondary reset-btn"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <FaRedo />
          <span>Recalculate Values</span>
        </motion.button>
      </div>
    </div>
  );
};

export default CarbonResultCard;
