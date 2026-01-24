import React, { useState, useRef } from 'react';
import './ComplaintForm.css';

function ComplaintForm({ onSubmit, loading, error }) {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [additionalText, setAdditionalText] = useState('');
  const fileInputRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!image) {
      alert('Please select an image');
      return;
    }

    const formData = new FormData();
    formData.append('image', image);
    if (additionalText.trim()) {
      formData.append('text', additionalText.trim());
    }

    onSubmit(formData);
  };

  const handleReset = () => {
    setImage(null);
    setImagePreview(null);
    setAdditionalText('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="complaint-form-container">
      <form className="complaint-form" onSubmit={handleSubmit}>
        <div className="form-section">
          <label htmlFor="image-upload" className="upload-label">
            <div className="upload-area">
              {imagePreview ? (
                <div className="image-preview-container">
                  <img 
                    src={imagePreview} 
                    alt="Preview" 
                    className="image-preview"
                  />
                  <button
                    type="button"
                    className="remove-image-btn"
                    onClick={handleReset}
                  >
                    ✕ Remove
                  </button>
                </div>
              ) : (
                <div className="upload-placeholder">
                  <div className="upload-icon">📸</div>
                  <p>Click to upload image</p>
                  <p className="upload-hint">or drag and drop</p>
                  <p className="upload-formats">PNG, JPG, GIF, WEBP (max 10MB)</p>
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
              disabled={loading}
            />
          </label>
        </div>

        <div className="form-section">
          <label htmlFor="additional-text" className="text-label">
            Additional Details (Optional)
          </label>
          <textarea
            id="additional-text"
            className="text-input"
            placeholder="Provide any additional context about the issue..."
            value={additionalText}
            onChange={(e) => setAdditionalText(e.target.value)}
            disabled={loading}
            rows="4"
          />
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <button
          type="submit"
          className="submit-button"
          disabled={!image || loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Analyzing Image...
            </>
          ) : (
            '🚀 Submit Complaint'
          )}
        </button>
      </form>
    </div>
  );
}

export default ComplaintForm;
