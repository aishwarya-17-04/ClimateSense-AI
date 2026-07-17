// src/pages/Settings.jsx
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaUser, FaPalette, FaBell, FaLock, FaRobot, 
  FaDatabase, FaInfoCircle, FaExclamationTriangle, 
  FaRedo, FaDownload, FaTrashAlt
} from 'react-icons/fa';
import api from '../services/api';
import SettingsCard from '../components/settings/Settingscard';
import ToggleSwitch from '../components/settings/ToggleSwitch';
import './Settings.css';

const DUMMY_SETTINGS = {
  account: {
    fullName: 'Alex Johnson',
    email: 'alex.j@example.com',
    phone: '+1 555-0198',
    country: 'Canada',
    language: 'English',
    timezone: 'America/Toronto'
  },
  appearance: {
    theme: 'system', // 'dark', 'light', 'system'
    accentColor: '#20c997'
  },
  notifications: {
    email: true,
    push: true,
    weeklyReports: true,
    dailyChallenge: false,
    aiAlerts: true
  },
  privacy: {
    privateProfile: false,
    shareWeeklyReport: true,
    communityVisibility: true
  },
  ai: {
    tone: 'intermediate', // 'beginner', 'intermediate', 'expert'
    focus: 'energy' // 'transport', 'energy', 'food', 'water', 'waste'
  }
};

const Settings = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const fetchSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/settings');
      setSettings(res.data);
    } catch (err) {
      console.warn("API Call Failed. Using fallback dummy data.", err);
      setSettings(DUMMY_SETTINGS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    const loadInitialSettings = async () => {
      try {
        const res = await api.get('/settings');
        if (isMounted) {
          setSettings(res.data);
        }
      } catch (err) {
        console.warn("API Call Failed. Using fallback dummy data.", err);
        if (isMounted) {
          setSettings(DUMMY_SETTINGS);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadInitialSettings();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleUpdate = async (category, key, value) => {
    // Optimistic UI Update
    const updatedSettings = {
      ...settings,
      [category]: {
        ...settings[category],
        [key]: value
      }
    };
    setSettings(updatedSettings);

    setIsSaving(true);
    try {
      await api.put('/settings/update', { category, key, value });
    } catch (err) {
      console.error("Failed to update setting remotely", err);
      // Revert in production, keeping optimistic for sandbox
    } finally {
      setIsSaving(false);
    }
  };

  const handleExportData = async () => {
    try {
      await api.post('/settings/export');
      alert("Data export initiated! You will receive an email shortly.");
    } catch {
      alert("Export mock triggered successfully.");
    }
  };

  const handleDeleteAccount = async () => {
    if (window.confirm("Are you sure you want to delete your account? This action is irreversible.")) {
      try {
        await api.delete('/account');
        alert("Account deleted.");
      } catch {
        alert("Account deletion mock triggered.");
      }
    }
  };

  return (
    <div className="settings-page-container">
      <header className="settings-header">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <h1>Settings</h1>
          <p className="page-subtitle">Customize your ClimateSense AI experience.</p>
        </motion.div>
        
        <AnimatePresence>
          {isSaving && (
            <motion.span 
              className="saving-indicator"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
            >
              Saving changes...
            </motion.span>
          )}
        </AnimatePresence>
      </header>

      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div key="loading" className="settings-skeleton pulse" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="skeleton-grid">
              <div className="sk-box"></div><div className="sk-box"></div>
              <div className="sk-box"></div><div className="sk-box"></div>
            </div>
          </motion.div>
        ) : error ? (
          <motion.div key="error" className="error-wrapper" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="glass-error-card">
              <FaExclamationTriangle className="error-icon" />
              <h3>Failed to load settings</h3>
              <button onClick={fetchSettings} className="btn-retry"><FaRedo /> Retry</button>
            </div>
          </motion.div>
        ) : (
          <motion.div key="content" className="settings-layout-grid" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            
            {/* ACCOUNT SETTINGS */}
            <SettingsCard title="Account Settings" icon={<FaUser />}>
              <div className="form-group-grid">
                <div className="input-group">
                  <label>Full Name</label>
                  <input type="text" className="glass-input" value={settings.account.fullName} onChange={(e) => handleUpdate('account', 'fullName', e.target.value)} />
                </div>
                <div className="input-group">
                  <label>Email</label>
                  <input type="email" className="glass-input" value={settings.account.email} readOnly />
                </div>
                <div className="input-group">
                  <label>Phone Number</label>
                  <input type="text" className="glass-input" value={settings.account.phone} onChange={(e) => handleUpdate('account', 'phone', e.target.value)} />
                </div>
                <div className="input-group">
                  <label>Country</label>
                  <input type="text" className="glass-input" value={settings.account.country} onChange={(e) => handleUpdate('account', 'country', e.target.value)} />
                </div>
                <div className="input-group">
                  <label>Language</label>
                  <select className="glass-select" value={settings.account.language} onChange={(e) => handleUpdate('account', 'language', e.target.value)}>
                    <option value="English">English</option>
                    <option value="French">French</option>
                    <option value="Spanish">Spanish</option>
                  </select>
                </div>
                <div className="input-group">
                  <label>Timezone</label>
                  <select className="glass-select" value={settings.account.timezone} onChange={(e) => handleUpdate('account', 'timezone', e.target.value)}>
                    <option value="America/Toronto">Eastern Time (ET)</option>
                    <option value="America/Vancouver">Pacific Time (PT)</option>
                    <option value="Europe/London">Greenwich Mean Time (GMT)</option>
                  </select>
                </div>
              </div>
              <div className="card-actions mt-4">
                <button className="btn-primary">Edit Profile</button>
                <button className="btn-secondary">Change Password</button>
              </div>
            </SettingsCard>

            {/* APPEARANCE */}
            <SettingsCard title="Appearance" icon={<FaPalette />}>
              <div className="input-group">
                <label>Theme</label>
                <div className="radio-group">
                  {['dark', 'light', 'system'].map(theme => (
                    <label key={theme} className="radio-label">
                      <input 
                        type="radio" 
                        name="theme" 
                        value={theme} 
                        checked={settings.appearance.theme === theme} 
                        onChange={(e) => handleUpdate('appearance', 'theme', e.target.value)}
                      />
                      <span className="radio-custom"></span>
                      {theme.charAt(0).toUpperCase() + theme.slice(1)}
                    </label>
                  ))}
                </div>
              </div>
              <div className="input-group mt-2">
                <label>Accent Color</label>
                <div className="color-picker-group">
                  {['#20c997', '#38bdf8', '#a855f7', '#f59e0b'].map(color => (
                    <div 
                      key={color} 
                      className={`color-swatch ${settings.appearance.accentColor === color ? 'selected' : ''}`}
                      style={{ backgroundColor: color }}
                      onClick={() => handleUpdate('appearance', 'accentColor', color)}
                    />
                  ))}
                </div>
              </div>
            </SettingsCard>

            {/* NOTIFICATIONS */}
            <SettingsCard title="Notifications" icon={<FaBell />}>
              <ToggleSwitch 
                label="Email Notifications" 
                description="Receive updates and alerts via email."
                isChecked={settings.notifications.email} 
                onChange={(val) => handleUpdate('notifications', 'email', val)} 
              />
              <ToggleSwitch 
                label="Push Notifications" 
                description="Receive alerts on your device."
                isChecked={settings.notifications.push} 
                onChange={(val) => handleUpdate('notifications', 'push', val)} 
              />
              <ToggleSwitch 
                label="Weekly Reports" 
                description="Get a summary of your carbon footprint every week."
                isChecked={settings.notifications.weeklyReports} 
                onChange={(val) => handleUpdate('notifications', 'weeklyReports', val)} 
              />
              <ToggleSwitch 
                label="Daily Eco Challenge Reminder" 
                isChecked={settings.notifications.dailyChallenge} 
                onChange={(val) => handleUpdate('notifications', 'dailyChallenge', val)} 
              />
              <ToggleSwitch 
                label="AI Recommendation Alerts" 
                isChecked={settings.notifications.aiAlerts} 
                onChange={(val) => handleUpdate('notifications', 'aiAlerts', val)} 
              />
            </SettingsCard>

            {/* PRIVACY */}
            <SettingsCard title="Privacy" icon={<FaLock />}>
              <ToggleSwitch 
                label="Private Profile" 
                description="Hide your profile from the community leaderboard."
                isChecked={settings.privacy.privateProfile} 
                onChange={(val) => handleUpdate('privacy', 'privateProfile', val)} 
              />
              <ToggleSwitch 
                label="Share Weekly Report" 
                description="Allow followers to see your weekly summaries."
                isChecked={settings.privacy.shareWeeklyReport} 
                onChange={(val) => handleUpdate('privacy', 'shareWeeklyReport', val)} 
              />
              <ToggleSwitch 
                label="Community Visibility" 
                description="Show your eco-challenges status in the community feed."
                isChecked={settings.privacy.communityVisibility} 
                onChange={(val) => handleUpdate('privacy', 'communityVisibility', val)} 
              />
            </SettingsCard>

            {/* AI SETTINGS */}
            <SettingsCard title="AI Settings" icon={<FaRobot />}>
              <div className="input-group">
                <label>Preferred AI Tone</label>
                <select className="glass-select" value={settings.ai.tone} onChange={(e) => handleUpdate('ai', 'tone', e.target.value)}>
                  <option value="beginner">Beginner (Simple & Encouraging)</option>
                  <option value="intermediate">Intermediate (Action-oriented)</option>
                  <option value="expert">Expert (Data-driven & Technical)</option>
                </select>
              </div>
              <div className="input-group mt-3">
                <label>Preferred Sustainability Focus</label>
                <select className="glass-select" value={settings.ai.focus} onChange={(e) => handleUpdate('ai', 'focus', e.target.value)}>
                  <option value="transport">Transportation</option>
                  <option value="energy">Home Energy</option>
                  <option value="food">Diet & Food</option>
                  <option value="water">Water Conservation</option>
                  <option value="waste">Waste & Recycling</option>
                </select>
              </div>
            </SettingsCard>

            {/* DATA MANAGEMENT */}
            <SettingsCard title="Data Management" icon={<FaDatabase />}>
              <p className="card-description">Control your personal data and carbon tracking history.</p>
              <div className="data-actions-grid">
                <button className="btn-secondary" onClick={handleExportData}>
                  <FaDownload /> Download My Data
                </button>
                <button className="btn-secondary" onClick={handleExportData}>
                  <FaDownload /> Export Carbon History
                </button>
                <button className="btn-secondary">
                  <FaRedo /> Clear Cache
                </button>
                <button className="btn-danger" onClick={handleDeleteAccount}>
                  <FaTrashAlt /> Delete Account
                </button>
              </div>
            </SettingsCard>

            {/* ABOUT */}
            <SettingsCard title="About" icon={<FaInfoCircle />}>
              <div className="about-list">
                <div className="about-item"><span>Version</span> <span>v2.4.0 (Build 492)</span></div>
                <div className="about-item"><span>Developer</span> <span>ClimateSense AI Inc.</span></div>
                <div className="about-item link"><span>Privacy Policy</span></div>
                <div className="about-item link"><span>Terms of Service</span></div>
                <div className="about-item link"><span>Support</span></div>
              </div>
            </SettingsCard>

          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Settings;
