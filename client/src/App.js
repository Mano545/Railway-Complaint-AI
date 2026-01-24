import React, { useState } from 'react';
import './App.css';
import ComplaintForm from './components/ComplaintForm';
import ComplaintResult from './components/ComplaintResult';

function App() {
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setComplaint(null);

    try {
      const response = await fetch('/api/complaint/submit', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to submit complaint');
      }

      const data = await response.json();
      setComplaint(data.complaint);
    } catch (err) {
      setError(err.message);
      console.error('Error submitting complaint:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setComplaint(null);
    setError(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚂 Railway Complaint AI</h1>
        <p className="description">
          Upload an image of a railway issue and let AI analyze, classify, and file your complaint automatically
        </p>
      </header>

      <main className="App-main">
        {!complaint ? (
          <ComplaintForm 
            onSubmit={handleSubmit} 
            loading={loading}
            error={error}
          />
        ) : (
          <ComplaintResult 
            complaint={complaint} 
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  );
}

export default App;
