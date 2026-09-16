import { UserX, UsersRound, UserCheck, TriangleAlert } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { AnimatedCounter } from './AnimatedCounter';
import { cn } from '../../lib/utils';

const CONFIG = {
  absent: { text: 'text-error', bg: 'bg-error-bg', Icon: UserX },
  proxy: { text: 'text-warning', bg: 'bg-warning-bg', Icon: UsersRound },
  assigned: { text: 'text-success', bg: 'bg-success-bg', Icon: UserCheck },
  unresolved: { text: 'text-error', bg: 'bg-error-bg', Icon: TriangleAlert },
};

export function MetricCard({ value, label, type }: { value: number; label: string; type: keyof typeof CONFIG }) {
  const { text, bg, Icon } = CONFIG[type];
  return (
    <Card padding="md" className="flex flex-col items-center gap-2">
      <span className={cn('flex items-center justify-center w-9 h-9 rounded-full', bg)}>
        <Icon size={17} className={text} />
      </span>
      <span className={cn('text-3xl font-bold tabular-nums', text)}>
        <AnimatedCounter value={value} />
      </span>
      <span className="text-sm text-text-secondary text-center leading-tight">{label}</span>
    </Card>
  );
}
