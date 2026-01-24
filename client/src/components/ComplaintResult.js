import React from 'react';
import './ComplaintResult.css';

function ComplaintResult({ complaint, onReset }) {
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'CRITICAL':
        return '#ff4444';
      case 'HIGH':
        return '#ff8800';
      case 'MEDIUM':
        return '#ffbb00';
      case 'LOW':
        return '#00aa00';
      default:
        return '#667eea';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'CRITICAL':
        return '🚨';
      case 'HIGH':
        return '⚠️';
      case 'MEDIUM':
        return '⚡';
      case 'LOW':
        return 'ℹ️';
      default:
        return '📋';
    }
  };

  return (
    <div className="complaint-result-container">
      <div className="complaint-result">
        <div className="result-header">
          <div className="success-icon">✅</div>
          <h2>Complaint Submitted Successfully!</h2>
          <p className="complaint-id">Complaint ID: <strong>{complaint.complaintId}</strong></p>
        </div>

        <div className="result-content">
          <div className="info-card">
            <div className="info-label">Issue Category</div>
            <div className="info-value category">{complaint.issueCategory}</div>
          </div>

          <div className="info-card">
            <div className="info-label">Priority</div>
            <div 
              className="info-value priority"
              style={{ color: getPriorityColor(complaint.priority) }}
            >
              {getPriorityIcon(complaint.priority)} {complaint.priority}
            </div>
          </div>

          <div className="info-card">
            <div className="info-label">Routed Department</div>
            <div className="info-value department">{complaint.department}</div>
          </div>

          <div className="info-card full-width">
            <div className="info-label">Issue Details</div>
            <div className="info-value details">{complaint.issueDetails}</div>
          </div>

          <div className="info-card full-width">
            <div className="info-label">Complaint Description</div>
            <div className="info-value description">{complaint.complaintDescription}</div>
          </div>

          <div className="info-card">
            <div className="info-label">Status</div>
            <div className="info-value status">
              <span className="status-badge">{complaint.status}</span>
            </div>
          </div>

          <div className="info-card">
            <div className="info-label">Submitted At</div>
            <div className="info-value timestamp">
              {new Date(complaint.timestamp).toLocaleString()}
            </div>
          </div>
        </div>

        <div className="result-footer">
          <button className="reset-button" onClick={onReset}>
            📸 Submit Another Complaint
          </button>
          <div className="integration-note">
            <p>🔗 This complaint will be automatically filed into the Rail Madad system.</p>
            <p className="note-small">Integration status: {complaint.railMadadStatus}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ComplaintResult;
