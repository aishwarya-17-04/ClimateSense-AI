import { Routes, Route, Navigate } from 'react-router-dom';

import Layout from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import Carbon from './components/carbon/Carbon';
import Recommendations from './pages/Recommendations';
import Challenge from './pages/Challenge';
import Community from './pages/Community';
import WeeklyReport from './pages/WeeklyReport';
import Profile from './pages/Profile';
import Settings from './pages/Settings';

const App = () => {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/carbon" element={<Carbon />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="/challenge" element={<Challenge />} />
        <Route path="/community" element={<Community />} />
        <Route path="/report" element={<WeeklyReport />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default App;
