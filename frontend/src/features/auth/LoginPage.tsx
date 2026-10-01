import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from './useAuth';
import { Button } from '../../components/ui/Button';
import { Field, Input } from '../../components/ui/Field';
import { parseApiError } from '../../lib/errors';

export function LoginPage() {
  // The seeded demo account is pre-filled only in local development.
  const [username, setUsername] = useState(import.meta.env.DEV ? 'Vaishali' : '');
  const [password, setPassword] = useState(import.meta.env.DEV ? 'Vaishali' : '');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const login = useAuth((s) => s.login);
  const status = useAuth((s) => s.status);

  // Don't show the login form to someone who already has a valid session.
  if (status === 'authenticated') return <Navigate to="/" replace />;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username.trim(), password);
      navigate('/', { replace: true });
    } catch (err) {
      const parsed = parseApiError(err, 'Invalid username or password');
      setError(parsed.status === 401 || parsed.status === 400 ? 'Invalid username or password' : parsed.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-dvh items-center justify-center bg-bg p-4">
      <main className="w-full max-w-sm animate-slide-up rounded-2xl border border-border bg-surface-elevated p-6 shadow-md sm:p-8">
        <div className="mb-6 text-center">
          <img src="/assets/presento-logo.png" alt="Presento" className="mx-auto mb-3 h-auto w-full max-w-[300px]" />
          <h1 className="sr-only">Sign in to Presento</h1>
          <p className="text-sm text-text-secondary">D.G. Tatkare School · Supervisor access</p>
        </div>

        {error && (
          <p role="alert" className="mb-4 rounded-lg border border-error/20 bg-error-bg p-3 text-sm font-medium text-error">{error}</p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Username">
            {(p) => <Input {...p} value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" autoCapitalize="none" required />}
          </Field>
          <Field label="Password">
            {(p) => <Input {...p} type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required />}
          </Field>
          <Button type="submit" size="lg" className="w-full" isLoading={loading}>{loading ? 'Signing in' : 'Sign in'}</Button>
        </form>
      </main>
    </div>
  );
}
