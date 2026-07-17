// src/components/GlassCard.jsx
import { motion } from 'framer-motion';
import './GlassCard.css';

const GlassCard = ({ children, className = '', delay = 0, onClick }) => {
  return (
    <motion.div
      className={`glass-card ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
      whileHover={onClick ? { y: -5, boxShadow: "0 12px 40px 0 rgba(0, 0, 0, 0.4)" } : {}}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {children}
    </motion.div>
  );
};

export default GlassCard;
