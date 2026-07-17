// src/components/community/LeaderboardCard.jsx
import { FaFire, FaMedal } from 'react-icons/fa';
import './LeaderBoardCard.css';

const LeaderboardCard = ({ users, currentUserId }) => {
  const renderRank = (rank) => {
    if (rank === 1) return <span className="rank-badge gold">1st</span>;
    if (rank === 2) return <span className="rank-badge silver">2nd</span>;
    if (rank === 3) return <span className="rank-badge bronze">3rd</span>;
    return <span className="rank-text">#{rank}</span>;
  };

  return (
    <div className="leaderboard-glass-container">
      <div className="table-responsive">
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Explorer</th>
              <th>Climate Score</th>
              <th>Current Streak</th>
              <th>Top Badge</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className={user.id === currentUserId ? 'current-user-row' : ''}>
                <td className="col-rank">{renderRank(user.rank)}</td>
                <td className="col-user">
                  <div className="user-info">
                    <div className="avatar-placeholder">
                      {user.avatar ? <img src={user.avatar} alt={user.name} /> : user.name.charAt(0)}
                    </div>
                    <span className="user-name">{user.name} {user.id === currentUserId && '(You)'}</span>
                  </div>
                </td>
                <td className="col-score">
                  <span className="score-value">{user.score.toLocaleString()}</span>
                </td>
                <td className="col-streak">
                  <div className="streak-badge">
                    <FaFire className="streak-icon" /> {user.streak} Days
                  </div>
                </td>
                <td className="col-badge">
                  <div className="top-badge">
                    <FaMedal className="badge-icon-small" /> {user.badge}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LeaderboardCard;
