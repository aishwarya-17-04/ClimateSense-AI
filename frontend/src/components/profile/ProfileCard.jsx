// src/components/profile/ProfileCard.jsx
import { FaMapMarkerAlt, FaCalendarAlt, FaFire, FaEdit, FaLevelUpAlt } from 'react-icons/fa';
import './ProfileCard.css';

const ProfileCard = ({ user, onEdit }) => {
  const xpPercentage = (user.currentXP / user.nextLevelXP) * 100;

  return (
    <div className="profile-hero-card">
      <div className="profile-header-bg"></div>
      
      <div className="profile-content">
        <div className="profile-avatar-container">
          {user.avatar ? (
            <img src={user.avatar} alt={user.name} className="profile-avatar" />
          ) : (
            <div className="profile-avatar-placeholder">{user.name.charAt(0)}</div>
          )}
          <div className="profile-level-badge">{user.level}</div>
        </div>

        <div className="profile-info-primary">
          <h2 className="profile-name">{user.name}</h2>
          <p className="profile-email">{user.email}</p>
        </div>

        <div className="profile-meta">
          <div className="meta-item">
            <FaMapMarkerAlt className="meta-icon" />
            <span>{user.city}, {user.country}</span>
          </div>
          <div className="meta-item">
            <FaCalendarAlt className="meta-icon" />
            <span>Member since {user.memberSince}</span>
          </div>
          <div className="meta-item streak">
            <FaFire className="meta-icon text-gold" />
            <span>{user.streak} Day Streak</span>
          </div>
        </div>

        <div className="profile-xp-section">
          <div className="xp-header">
            <span><FaLevelUpAlt className="text-seafoam" /> {user.climateLevel}</span>
            <span>{user.currentXP} / {user.nextLevelXP} XP</span>
          </div>
          <div className="xp-track">
            <div className="xp-fill" style={{ width: `${xpPercentage}%` }}></div>
          </div>
        </div>

        <button className="btn-edit-profile" onClick={onEdit}>
          <FaEdit /> Edit Profile
        </button>
      </div>
    </div>
  );
};

export default ProfileCard;
