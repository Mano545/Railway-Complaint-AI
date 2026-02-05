import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import './App.css';
import { AuthProvider, useAuth } from './context/AuthContext';
import ComplaintForm from './components/ComplaintForm';
import ComplaintResult from './components/ComplaintResult';
import Login from './components/Login';
import Register from './components/Register';
import MyComplaints from './components/MyComplaints';
import AdminDashboard from './components/AdminDashboard';

function Nav() {
  const { user, logout, isAdmin } = useAuth();
  return (
    <nav className="App-nav">
      <Link to="/">Home</Link>
      {user ? (
        <>
          <Link to="/my-complaints">My Complaints</Link>
          {isAdmin && <Link to="/admin">Admin</Link>}
          <button type="button" className="nav-logout" onClick={logout}>Logout</button>
        </>
      ) : (
        <>
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
        </>
      )}
    </nav>
  );
}

function HomePage() {
  const [complaint, setComplaint] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = (complaintData, errorMessage) => {
    if (errorMessage) {
      setError(errorMessage);
      setComplaint(null);
    } else {
      setComplaint(complaintData);
      setError(null);
    }
  };

  const handleReset = () => {
    setComplaint(null);
    setError(null);
  };

  return (
    <main className="App-main">
      {!complaint ? (
        <ComplaintForm onSubmit={handleSubmit} loading={false} error={error} />
      ) : (
        <ComplaintResult complaint={complaint} onReset={handleReset} />
      )}
    </main>
  );
}

function AuthPage({ type }) {
  const [isLogin, setIsLogin] = useState(type === 'login');
  return isLogin ? (
    <Login onSwitchToRegister={() => setIsLogin(false)} />
  ) : (
    <Register onSwitchToLogin={() => setIsLogin(true)} />
  );
}

function ProtectedRoute({ children, adminOnly }) {
  const { user, loading, isAdmin } = useAuth();
  if (loading) return <div className="App-main">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && !isAdmin) return <Navigate to="/" replace />;
  return children;
}

function AppRoutes() {
  return (
    <>
      <header className="App-header">
        <h1>Railway Complaint AI</h1>
        <p className="description">
          Report railway issues with location, ticket details, and AI-powered classification
        </p>
        <Nav />
      </header>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<div className="page-content auth-page"><AuthPage type="login" /></div>} />
        <Route path="/register" element={<div className="page-content auth-page"><AuthPage type="register" /></div>} />
        <Route path="/my-complaints" element={<ProtectedRoute><div className="page-content"><MyComplaints /></div></ProtectedRoute>} />
        <Route path="/admin" element={<ProtectedRoute adminOnly><div className="page-content"><AdminDashboard /></div></ProtectedRoute>} />
      </Routes>
    </>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
