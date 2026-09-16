import { TeacherCount } from '../../types';

export function MiniBarChart({ items, emptyLabel }: { items: TeacherCount[]; emptyLabel: string }) {
  if (items.length === 0) {
    return <div className="text-sm text-text-secondary py-2">{emptyLabel}</div>;
  }
  const max = Math.max(...items.map((i) => i.count), 1);
  return (
    <div className="space-y-2.5">
      {items.map((item) => (
        <div key={item.teacher_id}>
          <div className="flex justify-between text-sm mb-1">
            <span className="font-medium truncate pr-2">{item.teacher_name}</span>
            <span className="text-text-secondary shrink-0">{item.count}</span>
          </div>
          <div className="h-2 rounded-full bg-surface overflow-hidden">
            <div
              className="h-full rounded-full bg-primary"
              style={{ width: `${Math.max((item.count / max) * 100, 4)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
