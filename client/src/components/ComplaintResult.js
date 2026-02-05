import React from 'react';
import './ComplaintResult.css';

function ComplaintResult({ complaint, onReset }) {
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'CRITICAL': return '#ff4444';
      case 'HIGH': return '#ff8800';
      case 'MEDIUM': return '#ffbb00';
      case 'LOW': return '#00aa00';
      default: return '#667eea';
    }
  };
  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'CRITICAL': return '🚨';
      case 'HIGH': return '⚠️';
      case 'MEDIUM': return '⚡';
      case 'LOW': return 'ℹ️';
      default: return '📋';
    }
  };
  const timestamp = complaint.createdAt || complaint.timestamp;
  const description = complaint.description || complaint.complaintDescription;

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
            <div className="info-value priority" style={{ color: getPriorityColor(complaint.priority) }}>
              {getPriorityIcon(complaint.priority)} {complaint.priority}
            </div>
          </div>
          <div className="info-card">
            <div className="info-label">Routed Department</div>
            <div className="info-value department">{complaint.department}</div>
          </div>
          {complaint.aiConfidence != null && (
            <div className="info-card">
              <div className="info-label">AI Confidence</div>
              <div className="info-value">{(complaint.aiConfidence * 100).toFixed(0)}%</div>
            </div>
          )}
          <div className="info-card full-width">
            <div className="info-label">Issue Details</div>
            <div className="info-value details">{complaint.issueDetails}</div>
          </div>
          {description && (
            <div className="info-card full-width">
              <div className="info-label">Complaint Description</div>
              <div className="info-value description">{description}</div>
            </div>
          )}
          {complaint.location && (
            <div className="info-card full-width">
              <div className="info-label">Location</div>
              <div className="info-value">
                {complaint.location.nearestStation && <span>Nearest: {complaint.location.nearestStation}</span>}
                {complaint.location.stationProximityKm != null && <span> (~{complaint.location.stationProximityKm} km)</span>}
                {complaint.location.railwayContext && <p className="small">{complaint.location.railwayContext}</p>}
              </div>
            </div>
          )}
          {complaint.trainDetails && (complaint.trainDetails.trainNumber || complaint.trainDetails.trainName) && (
            <div className="info-card full-width">
              <div className="info-label">Train Details</div>
              <div className="info-value">
                {complaint.trainDetails.trainNumber} {complaint.trainDetails.trainName}
                {complaint.trainDetails.coachNumber && ` • Coach: ${complaint.trainDetails.coachNumber}`}
                {complaint.trainDetails.seatNumber && ` • Seat: ${complaint.trainDetails.seatNumber}`}
                {complaint.trainDetails.boardingStation && ` • From: ${complaint.trainDetails.boardingStation}`}
                {complaint.trainDetails.destinationStation && ` To: ${complaint.trainDetails.destinationStation}`}
              </div>
            </div>
          )}
          <div className="info-card">
            <div className="info-label">Status</div>
            <div className="info-value status"><span className="status-badge">{complaint.status}</span></div>
          </div>
          {timestamp && (
            <div className="info-card">
              <div className="info-label">Submitted At</div>
              <div className="info-value timestamp">{new Date(timestamp).toLocaleString()}</div>
            </div>
          )}
        </div>

        <div className="result-footer">
          <button className="reset-button" onClick={onReset}>📸 Submit Another Complaint</button>
        </div>
      </div>
    </div>
  );
}

export default ComplaintResult;
