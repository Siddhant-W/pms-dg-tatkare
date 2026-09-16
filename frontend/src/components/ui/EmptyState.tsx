export function EmptyState({ icon, title, description }: { icon: string; title: string; description?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center px-4">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-text-primary mb-1">{title}</h3>
      {description && <p className="text-text-secondary text-sm">{description}</p>}
    </div>
  );
}
