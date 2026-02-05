import React, { useState, useEffect } from 'react';
import { adminComplaints, adminComplaintsMap, adminSetStatus, adminAssign, adminInsights } from '../api/client';
import './AdminDashboard.css';

const STATUS_OPTIONS = ['pending', 'in_progress', 'resolved'];

export default function AdminDashboard() {
  const [complaints, setComplaints] = useState([]);
  const [mapPoints, setMapPoints] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({ station: '', train_number: '', issue_type: '', status: '' });
  const [assigning, setAssigning] = useState(null);
  const [assignDeptByComplaint, setAssignDeptByComplaint] = useState({});
  const [view, setView] = useState('list'); // list | map

  const loadComplaints = () => {
    setLoading(true);
    adminComplaints(filter)
      .then((data) => setComplaints(data.complaints || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const loadMap = () => {
    adminComplaintsMap()
      .then((data) => setMapPoints(data.points || []))
      .catch(() => setMapPoints([]));
  };

  const loadInsights = () => {
    adminInsights()
      .then((data) => setInsights(data.insights))
      .catch(() => setInsights(null));
  };

  useEffect(() => {
    loadComplaints();
    loadMap();
    loadInsights();
  }, []);

  const handleFilter = (e) => {
    e.preventDefault();
    loadComplaints();
  };

  const handleStatusChange = (complaintId, status) => {
    adminSetStatus(complaintId, status)
      .then((data) => {
        setComplaints((prev) => prev.map((c) => c.complaintId === complaintId ? data.complaint : c));
      })
      .catch(console.error);
  };

  const handleAssign = (complaintId) => {
    const dept = (assignDeptByComplaint[complaintId] || '').trim();
    if (!dept) return;
    setAssigning(complaintId);
    adminAssign(complaintId, dept)
      .then((data) => {
        setComplaints((prev) => prev.map((c) => c.complaintId === complaintId ? data.complaint : c));
        setAssignDeptByComplaint((prev) => ({ ...prev, [complaintId]: '' }));
      })
      .catch(console.error)
      .finally(() => setAssigning(null));
  };

  if (error) return <div className="admin-error">Error: {error}</div>;

  return (
    <div className="admin-dashboard">
      <h2>Admin Dashboard</h2>

      {insights && (
        <div className="insights-bar">
          <div className="insight-item"><span className="label">By Category</span> {Object.keys(insights.byCategory || {}).length} categories</div>
          <div className="insight-item"><span className="label">By Status</span> {JSON.stringify(insights.byStatus || {})}</div>
          <div className="insight-item"><span className="label">By Priority</span> {JSON.stringify(insights.byPriority || {})}</div>
        </div>
      )}

      <div className="view-tabs">
        <button className={view === 'list' ? 'active' : ''} onClick={() => setView('list')}>List</button>
        <button className={view === 'map' ? 'active' : ''} onClick={() => setView('map')}>Map</button>
      </div>

      {view === 'list' && (
        <>
          <form className="filter-form" onSubmit={handleFilter}>
            <input placeholder="Station" value={filter.station} onChange={(e) => setFilter((f) => ({ ...f, station: e.target.value }))} />
            <input placeholder="Train number" value={filter.train_number} onChange={(e) => setFilter((f) => ({ ...f, train_number: e.target.value }))} />
            <input placeholder="Issue type" value={filter.issue_type} onChange={(e) => setFilter((f) => ({ ...f, issue_type: e.target.value }))} />
            <select value={filter.status} onChange={(e) => setFilter((f) => ({ ...f, status: e.target.value }))}>
              <option value="">All status</option>
              {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
            <button type="submit">Filter</button>
          </form>

          {loading ? <div className="admin-loading">Loading...</div> : (
            <div className="admin-complaint-list">
              {complaints.map((c) => (
                <div key={c.complaintId} className="admin-complaint-card">
                  <div className="admin-card-header">
                    <strong>{c.complaintId}</strong>
                    <span className={`status-badge ${c.status}`}>{c.status}</span>
                  </div>
                  <div className="admin-card-meta">{c.issueCategory} • {c.priority} • {c.department}</div>
                  {c.location?.nearestStation && <div>📍 {c.location.nearestStation}</div>}
                  {c.trainDetails?.trainNumber && <div>🚂 {c.trainDetails.trainNumber} {c.trainDetails.trainName}</div>}
                  <div className="admin-card-actions">
                    <select value={c.status} onChange={(e) => handleStatusChange(c.complaintId, e.target.value)}>
                      {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                    <input placeholder="Assign department" value={assignDeptByComplaint[c.complaintId] || ''} onChange={(e) => setAssignDeptByComplaint((prev) => ({ ...prev, [c.complaintId]: e.target.value }))} onKeyDown={(e) => e.key === 'Enter' && handleAssign(c.complaintId)} />
                    <button type="button" onClick={() => handleAssign(c.complaintId)} disabled={!(assignDeptByComplaint[c.complaintId] || '').trim() || assigning === c.complaintId}>Assign</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {view === 'map' && (
        <div className="map-placeholder">
          <p>Map view: {mapPoints.length} complaints with location</p>
          <ul className="map-point-list">
            {mapPoints.slice(0, 20).map((p) => (
              <li key={p.complaintId}>{p.complaintId} — {p.nearestStation} ({p.latitude?.toFixed(4)}, {p.longitude?.toFixed(4)})</li>
            ))}
          </ul>
          <p className="map-note">Integrate with Leaflet/Mapbox to show markers or heatmap.</p>
        </div>
      )}
    </div>
  );
}
