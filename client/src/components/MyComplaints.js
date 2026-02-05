import React, { useState, useEffect } from 'react';
import { getMyComplaints } from '../api/client';
import './MyComplaints.css';

export default function MyComplaints() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getMyComplaints()
      .then((data) => setComplaints(data.complaints || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const getStatusClass = (s) => s === 'resolved' ? 'resolved' : s === 'in_progress' ? 'in-progress' : 'pending';

  if (loading) return <div className="my-complaints-loading">Loading your complaints...</div>;
  if (error) return <div className="my-complaints-error">Error: {error}</div>;

  return (
    <div className="my-complaints">
      <h2>My Complaints</h2>
      {complaints.length === 0 ? (
        <p className="no-complaints">No complaints yet. Submit one from the home page.</p>
      ) : (
        <ul className="complaint-list">
          {complaints.map((c) => (
            <li key={c.complaintId} className="complaint-item">
              <div className="complaint-item-header">
                <strong>{c.complaintId}</strong>
                <span className={`status-badge ${getStatusClass(c.status)}`}>{c.status}</span>
              </div>
              <div className="complaint-item-meta">
                {c.issueCategory} • {c.priority} • {c.department}
              </div>
              {c.location?.nearestStation && <div className="complaint-item-loc">📍 {c.location.nearestStation}</div>}
              <div className="complaint-item-time">{new Date(c.createdAt).toLocaleString()}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
