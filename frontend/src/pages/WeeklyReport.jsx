// src/pages/WeeklyReport.jsx
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaFileDownload, FaShareAlt, FaLeaf, FaTrophy, FaFire, 
  FaExclamationTriangle, FaRedo, FaChartPie
} from 'react-icons/fa';
import api from '../services/api';
import GlassCard from '../components/common/GlassCard';
import ProgressBar from '../components/common/ProgressBar';
import WeeklySummaryCard from '../components/report/WeeklyReportCard';
import EmissionChart from '../components/report/EmissionChart';
import InsightsCard from '../components/report/InsightsCard';
import './WeeklyReport.css';

// Fallback Sandbox Data
const fallbackReport = {
  summary: {
    carbonScore: { value: 88, trend: 'up', trendValue: '+4' },
    co2Saved: { value: '18.5', unit: 'kg', trend: 'up', trendValue: '+2.1kg' },
    challenges: { value: 5, unit: 'completed', trend: 'up', trendValue: '+1' },
    rating: { value: 'Excellent', trend: 'neutral', trendValue: 'Maintained' }
  },
  charts: {
    dailyEmissions: [
      { day: 'Mon', emissions: 12.4 }, { day: 'Tue', emissions: 14.1 },
      { day: 'Wed', emissions: 10.2 }, { day: 'Thu', emissions: 11.5 },
      { day: 'Fri', emissions: 9.8 }, { day: 'Sat', emissions: 8.4 },
      { day: 'Sun', emissions: 7.2 }
    ],
    dailyChallenges: [
      { day: 'Mon', completed: 1 }, { day: 'Tue', completed: 0 },
      { day: 'Wed', completed: 2 }, { day: 'Thu', completed: 1 },
      { day: 'Fri', completed: 0 }, { day: 'Sat', completed: 1 },
      { day: 'Sun', completed: 0 }
    ],
    emissionBreakdown: [
      { name: 'Transport', value: 45 }, { name: 'Electricity', value: 25 },
      { name: 'Food', value: 15 }, { name: 'Water', value: 10 },
      { name: 'Waste', value: 5 }
    ]
  },
  insights: [
    { type: 'positive', text: 'You reduced transport emissions by 18% compared to last week.' },
    { type: 'negative', text: 'Electricity usage increased slightly on Tuesday and Thursday.' },
    { type: 'positive', text: 'You completed 5 eco challenges, keeping your streak alive!' }
  ],
  goals: {
    target: 100,
    current: 73.6
  }
};

const WeeklyReport = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/report/weekly');
      setData(response.data);
    } catch (err) {
      console.warn("API unavailable, loading offline sandbox.", err);
      setData(fallbackReport);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    const loadInitialReport = async () => {
      try {
        const response = await api.get('/report/weekly');
        if (isMounted) {
          setData(response.data);
        }
      } catch (err) {
        console.warn("API unavailable, loading offline sandbox.", err);
        if (isMounted) {
          setData(fallbackReport);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadInitialReport();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleDownload = async () => {
    try {
      // Simulate download trigger
      await api.get('/report/download', { responseType: 'blob' });
      alert("Report downloading...");
    } catch {
      alert("Download simulated in sandbox mode.");
    }
  };

  return (
    <div className="report-page-container">
      {/* HEADER */}
      <header className="report-header">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <h1>Weekly <span className="text-highlight">Sustainability Report</span></h1>
          <p className="subtitle">Track your environmental impact and progress over the last 7 days.</p>
        </motion.div>
        
        <motion.div className="header-actions" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          <button onClick={handleDownload} className="btn-secondary">
            <FaFileDownload /> Download PDF
          </button>
          <button className="btn-primary-outline">
            <FaShareAlt /> Share Report
          </button>
        </motion.div>
      </header>

      <AnimatePresence mode="wait">
        {loading ? (
          /* LOADING SKELETON */
          <motion.div key="loading" className="report-skeleton pulse" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="skeleton-grid-4"><div className="sk-box"></div><div className="sk-box"></div><div className="sk-box"></div><div className="sk-box"></div></div>
            <div className="sk-box large"></div>
            <div className="skeleton-grid-2"><div className="sk-box medium"></div><div className="sk-box medium"></div></div>
          </motion.div>
        ) : error ? (
          /* ERROR STATE */
          <motion.div key="error" className="error-panel" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <GlassCard className="error-card">
              <FaExclamationTriangle className="error-icon" />
              <h3>Report Generation Failed</h3>
              <p>{error}</p>
              <button onClick={fetchReport} className="btn-secondary"><FaRedo /> Retry</button>
            </GlassCard>
          </motion.div>
        ) : (
          /* MAIN CONTENT */
          <motion.div key="content" className="report-content" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            
            {/* SUMMARY CARDS */}
            <div className="summary-cards-grid">
              <WeeklySummaryCard 
                title="Weekly Carbon Score" value={data.summary.carbonScore.value} unit="/ 100"
                icon={<FaChartPie />} colorClass="color-seafoam"
                trend={data.summary.carbonScore.trend} trendValue={data.summary.carbonScore.trendValue}
              />
              <WeeklySummaryCard 
                title="Total CO₂ Saved" value={data.summary.co2Saved.value} unit={data.summary.co2Saved.unit}
                icon={<FaLeaf />} colorClass="color-green"
                trend={data.summary.co2Saved.trend} trendValue={data.summary.co2Saved.trendValue}
              />
              <WeeklySummaryCard 
                title="Challenges Completed" value={data.summary.challenges.value} unit=""
                icon={<FaTrophy />} colorClass="color-gold"
                trend={data.summary.challenges.trend} trendValue={data.summary.challenges.trendValue}
              />
              <WeeklySummaryCard 
                title="Sustainability Rating" value={data.summary.rating.value} unit=""
                icon={<FaFire />} colorClass="color-purple"
                trend={data.summary.rating.trend} trendValue={data.summary.rating.trendValue}
              />
            </div>

            {/* CHARTS */}
            <EmissionChart 
              dailyEmissions={data.charts.dailyEmissions} 
              dailyChallenges={data.charts.dailyChallenges}
              emissionBreakdown={data.charts.emissionBreakdown}
            />

            <div className="bottom-grid">
              {/* GOALS & ACHIEVEMENTS */}
              <div className="goals-achievements-column">
                <GlassCard className="goals-card">
                  <h3>Weekly Goal Progress</h3>
                  <div className="goal-stats">
                    <span className="goal-label">Target: {data.goals.target} kg CO₂</span>
                    <span className="goal-label">Current: {data.goals.current} kg CO₂</span>
                  </div>
                  <ProgressBar 
                    progress={(data.goals.current / data.goals.target) * 100} 
                    label="Allowance Used" 
                    color={data.goals.current > data.goals.target ? "#ef4444" : "#38bdf8"} 
                  />
                </GlassCard>

                <GlassCard className="achievements-card">
                  <h3>Top Achievements</h3>
                  <ul className="achievement-list">
                    <li><FaFire className="ach-icon text-gold" /> Longest Streak: 14 Days</li>
                    <li><FaLeaf className="ach-icon text-green" /> Top Saver: Transport (12kg saved)</li>
                    <li><FaTrophy className="ach-icon text-seafoam" /> Master: 5 Challenges</li>
                  </ul>
                </GlassCard>
              </div>

              {/* AI INSIGHTS */}
              <InsightsCard insights={data.insights} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default WeeklyReport;
