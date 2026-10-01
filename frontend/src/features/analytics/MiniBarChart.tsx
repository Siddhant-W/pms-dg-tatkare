import { TeacherCount } from '../../types';

export function MiniBarChart({ items, emptyLabel }: { items: TeacherCount[]; emptyLabel: string }) {
  if (items.length === 0) {
    return <p className="py-2 text-sm text-text-secondary">{emptyLabel}</p>;
  }
  const max = Math.max(...items.map((i) => i.count), 1);
  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li key={item.teacher_id}>
          <div className="mb-1 flex justify-between text-sm">
            <span className="truncate pr-2 font-medium">{item.teacher_name}</span>
            <span className="shrink-0 font-bold tabular-nums text-text-secondary">{item.count}</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-surface" role="presentation">
            <div className="h-full rounded-full bg-primary transition-[width] duration-500" style={{ width: `${Math.max((item.count / max) * 100, 4)}%` }} />
          </div>
        </li>
      ))}
    </ul>
  );
}
