import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../features/auth/useAuth';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const status = useAuth((s) => s.status);

  // Wait for the silent-refresh attempt to settle before deciding, otherwise a
  // page reload always redirects to /login.
  if (status === 'checking') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg">
        <div
          className="h-8 w-8 rounded-full border-2 border-border border-t-primary animate-spin"
          role="status"
          aria-label="Checking your session"
        />
      </div>
    );
  }

  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
