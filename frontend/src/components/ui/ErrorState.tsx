import { EmptyState } from './EmptyState';
import { Button } from './Button';

export function ErrorState({ title = 'Something went wrong', description, onRetry }: { title?: string; description?: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center p-6 text-center h-full">
      <EmptyState icon="⚠️" title={title} description={description} />
      {onRetry && (
        <Button variant="primary" onClick={onRetry} className="mt-4">
          Try Again
        </Button>
      )}
    </div>
  );
}
