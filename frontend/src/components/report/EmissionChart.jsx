// src/components/report/EmissionChart.jsx
import { 
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import GlassCard from '../common/GlassCard';
import './EmissionChart.css';

const PIE_COLORS = ['#38bdf8', '#eab308', '#0ea5e9', '#10b981', '#ef4444'];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <p className="tooltip-label">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="tooltip-data" style={{ color: entry.color }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const EmissionChart = ({ dailyEmissions, dailyChallenges, emissionBreakdown }) => {
  return (
    <div className="charts-grid-container">
      {/* 1. Area Chart: Daily CO2 */}
      <GlassCard className="chart-card full-width">
        <h3 className="chart-title">Daily CO₂ Emissions (kg)</h3>
        <div className="chart-wrapper area-wrapper">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={dailyEmissions} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorCo2" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.6}/>
                  <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="day" stroke="#94a3b8" tick={{fontSize: 12}} axisLine={false} tickLine={false} />
              <YAxis stroke="#94a3b8" tick={{fontSize: 12}} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="emissions" name="CO₂" stroke="#38bdf8" strokeWidth={3} fillOpacity={1} fill="url(#colorCo2)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>

      {/* 2. Bar Chart: Challenges Completed */}
      <GlassCard className="chart-card">
        <h3 className="chart-title">Eco Challenges Completed</h3>
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dailyChallenges} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="day" stroke="#94a3b8" tick={{fontSize: 12}} axisLine={false} tickLine={false} />
              <YAxis stroke="#94a3b8" tick={{fontSize: 12}} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
              <Bar dataKey="completed" name="Completed" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>

      {/* 3. Pie Chart: Emission Breakdown */}
      <GlassCard className="chart-card">
        <h3 className="chart-title">Emission Sources</h3>
        <div className="chart-wrapper pie-wrapper">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={emissionBreakdown}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {emissionBreakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="pie-legend">
            {emissionBreakdown.map((entry, index) => (
              <div key={index} className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }}></span>
                <span className="legend-text">{entry.name}</span>
              </div>
            ))}
          </div>
        </div>
      </GlassCard>
    </div>
  );
};

export default EmissionChart;
