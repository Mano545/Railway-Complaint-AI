import React, { useState, useRef } from 'react';
import { resolveLocation, extractTicket, submitComplaint } from '../api/client';
import './ComplaintForm.css';

function ComplaintForm({ onSubmit, loading, error }) {
  const [submitting, setSubmitting] = useState(false);
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [additionalText, setAdditionalText] = useState('');
  const [location, setLocation] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [locationLoading, setLocationLoading] = useState(false);
  const [trainDetails, setTrainDetails] = useState(null);
  const [ticketFile, setTicketFile] = useState(null);
  const [ticketLoading, setTicketLoading] = useState(false);
  const [ticketError, setTicketError] = useState(null);
  const fileInputRef = useRef(null);
  const ticketInputRef = useRef(null);

  const captureLocation = () => {
    setLocationError(null);
    setLocationLoading(true);
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your browser.');
      setLocationLoading(false);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const res = await resolveLocation(
            pos.coords.latitude,
            pos.coords.longitude,
            pos.coords.accuracy
          );
          setLocation(res.location);
        } catch (e) {
          setLocationError('Could not resolve railway context.');
          setLocation({ latitude: pos.coords.latitude, longitude: pos.coords.longitude, accuracyM: pos.coords.accuracy });
        } finally {
          setLocationLoading(false);
        }
      },
      (err) => {
        setLocationError(err.message || 'Location permission denied.');
        setLocationLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleTicketChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setTicketError(null);
    setTicketFile(file);
    setTicketLoading(true);
    try {
      const data = await extractTicket(file);
      setTrainDetails(data.trainDetails);
    } catch (err) {
      setTicketError(err.message || 'Ticket OCR failed');
      setTrainDetails(null);
    } finally {
      setTicketLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) {
      alert('Please select an image');
      return;
    }
    const formData = new FormData();
    formData.append('image', image);
    if (additionalText.trim()) formData.append('text', additionalText.trim());
    if (location) {
      formData.append('latitude', location.latitude);
      formData.append('longitude', location.longitude);
      if (location.accuracyM != null) formData.append('accuracy_m', location.accuracyM);
    }
    if (trainDetails) {
      formData.append('train_details', JSON.stringify(trainDetails));
    }
    setSubmitting(true);
    try {
      const data = await submitComplaint(formData);
      onSubmit(data.complaint);
    } catch (err) {
      onSubmit(null, err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setImage(null);
    setImagePreview(null);
    setAdditionalText('');
    setLocation(null);
    setLocationError(null);
    setTrainDetails(null);
    setTicketFile(null);
    setTicketError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (ticketInputRef.current) ticketInputRef.current.value = '';
  };

  return (
    <div className="complaint-form-container">
      <form className="complaint-form" onSubmit={handleSubmit}>
        <div className="form-section">
          <label className="section-label">Issue image (required)</label>
          <label htmlFor="image-upload" className="upload-label">
            <div className="upload-area">
              {imagePreview ? (
                <div className="image-preview-container">
                  <img src={imagePreview} alt="Preview" className="image-preview" />
                  <button type="button" className="remove-image-btn" onClick={handleReset}>✕ Remove</button>
                </div>
              ) : (
                <div className="upload-placeholder">
                  <div className="upload-icon">📸</div>
                  <p>Click to upload image</p>
                  <p className="upload-hint">PNG, JPG, GIF, WEBP (max 10MB)</p>
                </div>
              )}
            </div>
            <input
              id="image-upload"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              ref={fileInputRef}
              className="file-input"
              disabled={loading || submitting}
            />
          </label>
        </div>

        <div className="form-section">
          <label className="section-label">Location (optional)</label>
          <button type="button" className="location-btn" onClick={captureLocation} disabled={locationLoading}>
            {locationLoading ? 'Getting location...' : '📍 Use my location'}
          </button>
          {locationError && <div className="location-error">{locationError}</div>}
          {location && (
            <div className="location-info">
              {location.nearestStation && <span>Nearest: {location.nearestStation}</span>}
              {location.stationProximityKm != null && <span> ~{location.stationProximityKm} km</span>}
            </div>
          )}
        </div>

        <div className="form-section">
          <label className="section-label">Train ticket (optional)</label>
          <input
            type="file"
            accept="image/*,.pdf"
            onChange={handleTicketChange}
            ref={ticketInputRef}
            className="file-input"
            disabled={loading || submitting}
          />
          {ticketLoading && <div className="ticket-loading">Extracting ticket...</div>}
          {ticketError && <div className="ticket-error">{ticketError}</div>}
          {trainDetails && (
            <div className="train-details-preview">
              {trainDetails.trainNumber && <span>Train: {trainDetails.trainNumber}</span>}
              {trainDetails.trainName && <span> {trainDetails.trainName}</span>}
              {trainDetails.coachNumber && <span> • Coach: {trainDetails.coachNumber}</span>}
              {trainDetails.seatNumber && <span> • Seat: {trainDetails.seatNumber}</span>}
              {trainDetails.boardingStation && <span> • From: {trainDetails.boardingStation}</span>}
              {trainDetails.destinationStation && <span> To: {trainDetails.destinationStation}</span>}
            </div>
          )}
        </div>

        <div className="form-section">
          <label htmlFor="additional-text" className="text-label">Additional details (optional)</label>
          <textarea
            id="additional-text"
            className="text-input"
            placeholder="Describe the issue..."
            value={additionalText}
            onChange={(e) => setAdditionalText(e.target.value)}
            disabled={loading || submitting}
            rows="4"
          />
        </div>

        {error && <div className="error-message">⚠️ {error}</div>}

        <button type="submit" className="submit-button" disabled={!image || loading || submitting}>
          {(loading || submitting) ? (<><span className="spinner"></span> Analyzing...</>) : '🚀 Submit Complaint'}
        </button>
      </form>
    </div>
  );
}

export default ComplaintForm;
