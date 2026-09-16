import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from './useAuth';

export function LoginPage() {
  const [username, setUsername] = useState('Vaishali');
  const [password, setPassword] = useState('Vaishali');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const login = useAuth((s) => s.login);
  const status = useAuth((s) => s.status);

  // Don't show the login form to someone who already has a valid session.
  if (status === 'authenticated') {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/', { replace: true });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : err?.response
            ? 'Invalid username or password'
            : 'Cannot reach the server. Is the backend running on port 8000?'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg p-4">
      <div className="w-full max-w-sm bg-surface-elevated p-6 rounded-xl shadow-md border border-border">
        <div className="text-center mb-6">
          <span className="inline-block px-3 py-1 bg-primary/10 text-primary text-xs font-semibold rounded-full mb-2">
            Supervisor Access
          </span>
          <h1 className="text-2xl font-bold text-text-primary">D.G. Tatkare School</h1>
          <p className="text-sm text-text-secondary mt-1">Proxy Management System (PMS)</p>
        </div>
        
        {error && (
          <div className="p-3 mb-4 text-xs font-medium text-error bg-error/10 border border-error/20 rounded-md">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Username</label>
            <input 
              type="text" 
              placeholder="Username" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 min-h-[44px] rounded-md border border-border bg-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Password</label>
            <input 
              type="password" 
              placeholder="Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 min-h-[44px] rounded-md border border-border bg-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              required
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-primary text-white font-medium py-3 rounded-md min-h-[44px] hover:bg-primary-hover active:scale-[0.99] transition-all text-sm mt-2 disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in as Supervisor'}
          </button>
        </form>
      </div>
    </div>
  );
}
