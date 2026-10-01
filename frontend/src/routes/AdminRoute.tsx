import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert } from 'lucide-react';
import { useAuth } from '../features/auth/useAuth';
import { EmptyState } from '../components/ui/EmptyState';
import { Button } from '../components/ui/Button';

/** Hides admin-only screens from supervisors. The API enforces the same rule. */
export function AdminRoute({ children }: { children: React.ReactNode }) {
  const role = useAuth((s) => s.user?.role);
  if (role !== 'ADMIN') {
    return (
      <EmptyState
        className="py-24"
        icon={<ShieldAlert size={26} />}
        title="Admins only"
        description="Timetable settings can only be changed by an administrator."
        action={<Link to="/timetable"><Button variant="secondary">Back to timetable</Button></Link>}
      />
    );
  }
  return <>{children}</>;
}
