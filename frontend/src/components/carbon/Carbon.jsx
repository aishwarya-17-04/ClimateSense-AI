// src/components/carbon/Carbon.jsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaCar, 
  FaLightbulb, 
  FaWater, 
  FaUtensils, 
  FaTrashAlt, 
  FaCalculator, 
  FaSpinner, 
  FaExclamationTriangle
} from 'react-icons/fa';
import { analyzeLifestyle, getApiErrorMessage } from '../../services/api';
import GlassCard from '../common/GlassCard';
import CarbonResultCard from './CarbonResultCard';
import './Carbon.css';

const Carbon = () => {
  // Input Form States
  const [transport, setTransport] = useState('Walk');
  const [distance, setDistance] = useState(0);

  const [electricity, setElectricity] = useState('Laptop');
  const [hours, setHours] = useState(0);

  const [water, setWater] = useState('Shower');
  const [minutes, setMinutes] = useState(0);

  const [food, setFood] = useState('Vegetarian');

  const [waste, setWaste] = useState('Paper');
  const [quantity, setQuantity] = useState(0);

  // API Call States
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    // The backend parses these human-readable habit descriptions.
    const payload = {
      transport: `${transport} - ${parseFloat(distance) || 0} km`,
      electricity: `${electricity} - ${parseFloat(hours) || 0} hours`,
      water: `${parseFloat(minutes) || 0}-minute ${water}`,
      food,
      waste: `${parseFloat(quantity) || 0} kg ${waste}`,
    };

    try {
      const response = await analyzeLifestyle(payload);
      sessionStorage.setItem('latestAnalysis', JSON.stringify(response.data));
      setResults(response.data);
    } catch (err) {
      console.error("Carbon calculation failed:", err);
      setError(getApiErrorMessage(err, "Could not connect to the calculation engine. Please try again."));
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setTransport('Walk');
    setDistance(0);
    setElectricity('Laptop');
    setHours(0);
    setWater('Shower');
    setMinutes(0);
    setFood('Vegetarian');
    setWaste('Paper');
    setQuantity(0);
    setResults(null);
    setError(null);
  };

  return (
    <div className="carbon-page-container">
      {/* Header */}
      <header className="carbon-header">
        <motion.div 
          initial={{ opacity: 0, y: -20 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 0.5 }}
        >
          <h1>Carbon Footprint <span className="text-highlight">Calculator</span></h1>
          <p className="subtitle">Calculate your daily environmental impact and keep track of your footprint.</p>
        </motion.div>
      </header>

      <div className="carbon-grid">
        <AnimatePresence mode="wait">
          {!results ? (
            /* INPUT FORM PANEL */
            <motion.div 
              key="calculator-form"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.4 }}
              className="calculator-panel"
            >
              <GlassCard className="form-glass-card">
                <form onSubmit={handleSubmit} className="carbon-form">
                  
                  {/* Transport Segment */}
                  <div className="form-section">
                    <div className="section-title">
                      <FaCar className="section-icon" />
                      <h3>Transport</h3>
                    </div>
                    <div className="input-group-row">
                      <div className="input-field">
                        <label>Mode</label>
                        <select value={transport} onChange={(e) => setTransport(e.target.value)} className="glass-select">
                          <option value="Car">Car</option>
                          <option value="Bike">Bike</option>
                          <option value="Bus">Bus</option>
                          <option value="Train">Train</option>
                          <option value="Walk">Walk</option>
                        </select>
                      </div>
                      <div className="input-field">
                        <label>Distance (km)</label>
                        <input 
                          type="number" 
                          min="0" 
                          step="any"
                          value={distance} 
                          onChange={(e) => setDistance(e.target.value)} 
                          className="glass-input" 
                          required
                        />
                      </div>
                    </div>
                  </div>

                  {/* Electricity Segment */}
                  <div className="form-section">
                    <div className="section-title">
                      <FaLightbulb className="section-icon" />
                      <h3>Electricity</h3>
                    </div>
                    <div className="input-group-row">
                      <div className="input-field">
                        <label>Appliance</label>
                        <select value={electricity} onChange={(e) => setElectricity(e.target.value)} className="glass-select">
                          <option value="AC">AC</option>
                          <option value="Fan">Fan</option>
                          <option value="TV">TV</option>
                          <option value="Laptop">Laptop</option>
                          <option value="Light">Light</option>
                          <option value="Washing Machine">Washing Machine</option>
                        </select>
                      </div>
                      <div className="input-field">
                        <label>Usage (Hours)</label>
                        <input 
                          type="number" 
                          min="0" 
                          step="any"
                          value={hours} 
                          onChange={(e) => setHours(e.target.value)} 
                          className="glass-input" 
                          required
                        />
                      </div>
                    </div>
                  </div>

                  {/* Water Segment */}
                  <div className="form-section">
                    <div className="section-title">
                      <FaWater className="section-icon" />
                      <h3>Water Usage</h3>
                    </div>
                    <div className="input-group-row">
                      <div className="input-field">
                        <label>Activity</label>
                        <select value={water} onChange={(e) => setWater(e.target.value)} className="glass-select">
                          <option value="Shower">Shower</option>
                          <option value="Bath">Bath</option>
                          <option value="Dishwashing">Dishwashing</option>
                          <option value="Laundry">Laundry</option>
                          <option value="Handwashing">Handwashing</option>
                        </select>
                      </div>
                      <div className="input-field">
                        <label>Duration (Minutes)</label>
                        <input 
                          type="number" 
                          min="0" 
                          step="any"
                          value={minutes} 
                          onChange={(e) => setMinutes(e.target.value)} 
                          className="glass-input" 
                          required
                        />
                      </div>
                    </div>
                  </div>

                  {/* Food & Waste Segment */}
                  <div className="form-section double-section">
                    <div className="input-column">
                      <div className="section-title">
                        <FaUtensils className="section-icon" />
                        <h3>Diet</h3>
                      </div>
                      <div className="input-field">
                        <label>Dietary Choice</label>
                        <select value={food} onChange={(e) => setFood(e.target.value)} className="glass-select">
                          <option value="Vegan">Vegan</option>
                          <option value="Vegetarian">Vegetarian</option>
                          <option value="Non Vegetarian">Non Vegetarian</option>
                        </select>
                      </div>
                    </div>

                    <div className="input-column">
                      <div className="section-title">
                        <FaTrashAlt className="section-icon" />
                        <h3>Waste</h3>
                      </div>
                      <div className="input-group-row">
                        <div className="input-field">
                          <label>Material Type</label>
                          <select value={waste} onChange={(e) => setWaste(e.target.value)} className="glass-select">
                            <option value="Plastic Bottle">Plastic Bottle</option>
                            <option value="Plastic Bag">Plastic Bag</option>
                            <option value="Food Waste">Food Waste</option>
                            <option value="Paper">Paper</option>
                            <option value="Glass Bottle">Glass Bottle</option>
                            <option value="Aluminum Can">Aluminum Can</option>
                          </select>
                        </div>
                        <div className="input-field">
                          <label>Quantity (kg)</label>
                          <input 
                            type="number" 
                            min="0" 
                            step="any"
                            value={quantity} 
                            onChange={(e) => setQuantity(e.target.value)} 
                            className="glass-input" 
                            required
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Submission Error Card */}
                  {error && (
                    <motion.div 
                      initial={{ scale: 0.9, opacity: 0 }} 
                      animate={{ scale: 1, opacity: 1 }}
                      className="error-alert"
                    >
                      <FaExclamationTriangle className="alert-icon" />
                      <p>{error}</p>
                    </motion.div>
                  )}

                  {/* Form Action Button */}
                  <motion.button 
                    type="submit" 
                    className="btn-primary calculate-btn"
                    disabled={isLoading}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {isLoading ? (
                      <>
                        <FaSpinner className="spinner-icon spinning" />
                        <span>Calculating...</span>
                      </>
                    ) : (
                      <>
                        <FaCalculator />
                        <span>Calculate Carbon Footprint</span>
                      </>
                    )}
                  </motion.button>

                </form>
              </GlassCard>
            </motion.div>
          ) : (
            /* SUCCESS STATE - CALCULATOR RESULTS */
            <motion.div 
              key="calculator-results"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="results-panel"
            >
              <CarbonResultCard results={results} onReset={handleReset} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Carbon;
