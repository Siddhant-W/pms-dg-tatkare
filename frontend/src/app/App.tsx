import { useEffect } from 'react';
import { RouterProvider } from 'react-router-dom';
import { router } from '../routes';
import { QueryProvider } from './QueryProvider';
import { Toaster } from '../components/ui/Toaster';
import { useAuth } from '../features/auth/useAuth';

export function App() {
  const bootstrap = useAuth((s) => s.bootstrap);

  // Attempt a silent refresh once on mount so an existing session survives a
  // page reload.
  useEffect(() => {
    void bootstrap();
  }, [bootstrap]);

  return (
    <QueryProvider>
      <RouterProvider router={router} />
      <Toaster />
    </QueryProvider>
  );
}
