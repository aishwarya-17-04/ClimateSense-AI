// src/pages/Recommendations.jsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  FaLeaf, 
  FaAward, 
  FaCloud, 
  FaPiggyBank, 
  FaCalculator 
} from 'react-icons/fa';
import GlassCard from '../components/common/GlassCard';
import RecommendationCard from '../components/recommendation/RecommendationCard';
import './Recommendations.css';

// Rich local backup data in case backend recommendations are not yet evaluated
const fallbackData = {
  summary: {
    carbonScore: 84,
    totalEmissions: "14.2",
    estimatedSavings: "12.8",
    rating: "Good"
  },
  recommendations: [
    {
      category: "Transport",
      title: "Walk for Short Trips",
      description: "Replace driving trips under 2 km with walking. Not only does this reduce your carbon output, but it also improves cardiovascular health.",
      saving: "2.5 kg CO₂/week",
      difficulty: "Easy"
    },
    {
      category: "Electricity",
      title: "Transition to LED Bulbs",
      description: "Replace standard incandescent light bulbs with high-efficiency LEDs. They consume up to 85% less energy and last 25 times longer.",
      saving: "3.2 kg CO₂/week",
      difficulty: "Easy"
    },
    {
      category: "Water",
      title: "Reduce Shower Time by 2 Mins",
      description: "Cutting just two minutes off your daily shower saves water and significantly lowers the electricity/gas required to heat it.",
      saving: "1.8 kg CO₂/week",
      difficulty: "Easy"
    },
    {
      category: "Food",
      title: "Implement Meatless Mondays",
      description: "Swap meat-based meals for plant-based alternatives just one day a week. Animal agriculture is a leading driver of global greenhouse gases.",
      saving: "4.1 kg CO₂/week",
      difficulty: "Medium"
    },
    {
      category: "Waste",
      title: "Initiate Home Composting",
      description: "Divert food scraps and paper waste from landfills by starting a compost bin. This reduces potent methane emissions from decomposing organic matter.",
      saving: "2.2 kg CO₂/week",
      difficulty: "Medium"
    }
  ]
};

const getLatestAnalysisData = () => {
  try {
    const savedAnalysis = sessionStorage.getItem('latestAnalysis');
    if (!savedAnalysis) {
      return fallbackData;
    }

    const analysis = JSON.parse(savedAnalysis);
    const recommendations = (analysis.recommendations || []).map((recommendation) => ({
      category: recommendation.category || 'General',
      title: recommendation.title,
      description: recommendation.description,
      saving: `${Number(recommendation.estimated_impact_kg_co2 || 0).toFixed(1)} kg CO2e/day`,
      difficulty: recommendation.priority <= 2 ? 'Medium' : 'Easy',
    }));

    if (recommendations.length === 0) {
      return fallbackData;
    }

    const totalEmissions = Number(analysis.total_carbon_kg_co2 || 0);
    const estimatedSavings = recommendations.reduce(
      (total, recommendation) => total + Number.parseFloat(recommendation.saving),
      0,
    );

    return {
      summary: {
        carbonScore: Math.max(0, Math.round(100 - totalEmissions * 2)),
        totalEmissions: totalEmissions.toFixed(1),
        estimatedSavings: estimatedSavings.toFixed(1),
        rating: analysis.impact_level || 'Good',
      },
      recommendations,
    };
  } catch {
    return fallbackData;
  }
};

const Recommendations = () => {
  const navigate = useNavigate();
  const [data] = useState(getLatestAnalysisData);
  const [activeFilter, setActiveFilter] = useState('All');

  const handleFilterChange = (filter) => {
    setActiveFilter(filter);
  };

  // Safely filter based on selections
  const filteredRecommendations = data?.recommendations?.filter(rec => 
    activeFilter === 'All' || rec.category?.toLowerCase() === activeFilter.toLowerCase()
  ) || [];

  const filterCategories = ['All', 'Transport', 'Electricity', 'Water', 'Food', 'Waste'];

  return (
    <div className="recommendations-page">
      {/* HEADER SECTION */}
      <header className="rec-header">
        <motion.div 
          initial={{ opacity: 0, y: -15 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 0.5 }}
        >
          <h1>AI <span className="text-highlight">Recommendations</span></h1>
          <p className="subtitle">Personalized sustainability suggestions based on your latest carbon footprint.</p>
        </motion.div>
      </header>

      <AnimatePresence mode="wait">
        {!data || data.recommendations?.length === 0 ? (
          /* EMPTY STATE */
          <motion.div 
            key="empty"
            className="empty-panel"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
          >
            <GlassCard className="empty-glass-card">
              <FaLeaf className="empty-leaf-icon" />
              <h3>No recommendations available yet</h3>
              <p>Calculate your daily carbon footprint first so the AI engine can target custom solutions.</p>
              <button onClick={() => navigate('/carbon')} className="btn-action">
                <FaCalculator /> Go to Calculator
              </button>
            </GlassCard>
          </motion.div>
        ) : (
          /* MAIN CONTENT VIEWS */
          <motion.div 
            key="content"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="main-rec-content"
          >
            {/* SUMMARY SCORE CARD */}
            <section className="summary-section">
              <GlassCard className="summary-glass-card">
                <div className="summary-metric-block">
                  <div className="metric-box">
                    <div className="metric-icon-wrapper score-glow"><FaAward /></div>
                    <div className="metric-text-wrapper">
                      <span className="summary-metric-label">Carbon Score</span>
                      <h2 className="summary-metric-value text-highlight">{data.summary.carbonScore} <span className="unit-label">/100</span></h2>
                    </div>
                  </div>

                  <div className="metric-box">
                    <div className="metric-icon-wrapper emission-glow"><FaCloud /></div>
                    <div className="metric-text-wrapper">
                      <span className="summary-metric-label">Total Emissions</span>
                      <h2 className="summary-metric-value">{data.summary.totalEmissions} <span className="unit-label">kg CO₂e</span></h2>
                    </div>
                  </div>

                  <div className="metric-box">
                    <div className="metric-icon-wrapper savings-glow"><FaPiggyBank /></div>
                    <div className="metric-text-wrapper">
                      <span className="summary-metric-label">Monthly Savings</span>
                      <h2 className="summary-metric-value green-glow">{data.summary.estimatedSavings} <span className="unit-label">kg CO₂e</span></h2>
                    </div>
                  </div>

                  <div className="metric-box">
                    <div className="metric-icon-wrapper rating-glow"><FaLeaf /></div>
                    <div className="metric-text-wrapper">
                      <span className="summary-metric-label">Overall Rating</span>
                      <h2 className="summary-metric-value text-rating">{data.summary.rating}</h2>
                    </div>
                  </div>
                </div>
              </GlassCard>
            </section>

            {/* INTERACTIVE FILTERS BAR */}
            <div className="filters-container">
              {filterCategories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => handleFilterChange(cat)}
                  className={`filter-tab ${activeFilter === cat ? 'active' : ''}`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* RECS CARDS GRID SYSTEM */}
            <motion.div layout className="recommendations-grid">
              <AnimatePresence mode="popLayout">
                {filteredRecommendations.length > 0 ? (
                  filteredRecommendations.map((rec, index) => (
                    <RecommendationCard key={rec.title || index} recommendation={rec} />
                  ))
                ) : (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="no-filter-results"
                  >
                    <p>No actionable suggestions found for the category: "{activeFilter}"</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Recommendations;
