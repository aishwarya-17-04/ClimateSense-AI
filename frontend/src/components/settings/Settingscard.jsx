// src/components/SettingsCard.jsx
import { motion } from 'framer-motion';
import './SettingsCard.css';

const SettingsCard = ({ title, icon, children }) => {
  return (
    <motion.div 
      className="settings-card"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4 }}
    >
      <div className="settings-card-header">
        {icon && <span className="settings-card-icon">{icon}</span>}
        <h3 className="settings-card-title">{title}</h3>
      </div>
      <div className="settings-card-content">
        {children}
      </div>
    </motion.div>
  );
};

export default SettingsCard;
