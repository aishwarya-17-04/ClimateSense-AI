// src/components/common/ProgressBar.jsx
import { motion } from 'framer-motion';
import './ProgressBar.css';

const ProgressBar = ({ 
  progress = 0, 
  type = 'linear', 
  label, 
  color = 'var(--accent-seafoam, #38bdf8)' 
}) => {
  // Ensure progress stays between 0 and 100
  const safeProgress = Math.min(Math.max(progress, 0), 100);

  if (type === 'circular') {
    const radius = 40;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (safeProgress / 100) * circumference;

    return (
      <div className="progress-circular-wrapper">
        <svg className="progress-ring" width="100" height="100">
          <circle
            className="progress-ring-track"
            strokeWidth="8"
            fill="transparent"
            r={radius}
            cx="50"
            cy="50"
          />
          <motion.circle
            className="progress-ring-fill"
            strokeWidth="8"
            stroke={color}
            fill="transparent"
            r={radius}
            cx="50"
            cy="50"
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{ strokeDasharray: circumference }}
          />
        </svg>
        <div className="progress-circular-text">
          <span className="progress-value">{safeProgress}%</span>
        </div>
        {label && <span className="progress-label">{label}</span>}
      </div>
    );
  }

  // Linear Progress Bar
  return (
    <div className="progress-linear-wrapper">
      {label && (
        <div className="progress-linear-header">
          <span className="progress-label">{label}</span>
          <span className="progress-value">{safeProgress}%</span>
        </div>
      )}
      <div className="progress-linear-track">
        <motion.div 
          className="progress-linear-fill"
          initial={{ width: 0 }}
          animate={{ width: `${safeProgress}%` }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          style={{ backgroundColor: color }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
