// src/components/ToggleSwitch.jsx
import { motion } from 'framer-motion';
import './Toggleswitch.css';

const ToggleSwitch = ({ label, description, isChecked, onChange }) => {
  return (
    <div className="toggle-switch-container" onClick={() => onChange(!isChecked)}>
      <div className="toggle-info">
        <span className="toggle-label">{label}</span>
        {description && <span className="toggle-desc">{description}</span>}
      </div>
      <div className={`toggle-track ${isChecked ? 'active' : ''}`}>
        <motion.div
          className="toggle-thumb"
          layout
          transition={{ type: 'spring', stiffness: 700, damping: 30 }}
        />
      </div>
    </div>
  );
};

export default ToggleSwitch;
