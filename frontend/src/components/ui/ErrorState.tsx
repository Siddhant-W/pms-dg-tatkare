import { TriangleAlert, RotateCw } from 'lucide-react';
import { Button } from './Button';
import { EmptyState } from './EmptyState';

export function ErrorState({
  title = 'Something went wrong',
  description = 'We could not load this. Check your connection and try again.',
  onRetry,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <div role="alert">
      <EmptyState
        icon={<TriangleAlert size={26} />}
        title={title}
        description={description}
        action={
          onRetry && (
            <Button variant="secondary" leftIcon={<RotateCw size={16} />} onClick={onRetry}>
              Try again
            </Button>
          )
        }
      />
    </div>
  );
}
