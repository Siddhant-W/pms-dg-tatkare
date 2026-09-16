import os

base_dir = r"s:\PMS\frontend"

remaining_files = {
    "src/services/teacherService.ts": """import { api } from '../lib/api';
import { TeacherWithAttendance, TimetableEntry } from '../types';

export const teacherService = {
  getTeachers: async (date: string) => {
    const { data } = await api.get<TeacherWithAttendance[]>(`/teachers`, { params: { date } });
    return data;
  },
  getTeacherTimetable: async (teacherId: string, day: string) => {
    const { data } = await api.get<TimetableEntry[]>(`/teachers/${teacherId}/timetable`, { params: { day } });
    return data;
  }
};
""",
    "src/services/attendanceService.ts": """import { api } from '../lib/api';
import { AttendanceStatus } from '../types';

export const attendanceService = {
  getAttendance: async (date: string) => {
    const { data } = await api.get(`/attendance`, { params: { date } });
    return data;
  },
  markAttendance: async (teacherId: string, status: AttendanceStatus) => {
    const { data } = await api.put(`/attendance/${teacherId}`, { status });
    return data;
  }
};
""",
    "src/services/proxyService.ts": """import { api } from '../lib/api';

export const proxyService = {
  getProxyRequirements: async (date: string) => {
    const { data } = await api.get(`/proxy`, { params: { date } });
    return data;
  },
  getCandidates: async (requirementId: string) => {
    const { data } = await api.get(`/proxy/${requirementId}/candidates`);
    return data;
  },
  assignProxy: async (requirementId: string, proxyTeacherId: string) => {
    const { data } = await api.post(`/proxy-assignments`, { requirement_id: requirementId, proxy_teacher_id: proxyTeacherId });
    return data;
  },
  cancelAssignment: async (assignmentId: string) => {
    const { data } = await api.delete(`/proxy-assignments/${assignmentId}`);
    return data;
  }
};
""",
    "src/services/timetableService.ts": """import { api } from '../lib/api';

export const timetableService = {
  getTimetable: async (day: string, teacherId?: string) => {
    const { data } = await api.get(`/timetable`, { params: { day, teacher_id: teacherId } });
    return data;
  }
};
""",
    "src/services/analyticsService.ts": """import { api } from '../lib/api';

export const analyticsService = {
  getDailyStats: async (date: string) => {
    const { data } = await api.get(`/analytics/daily`, { params: { date } });
    return data;
  }
};
""",
    "src/services/historyService.ts": """import { api } from '../lib/api';

export const historyService = {
  getHistory: async (date?: string, teacherId?: string) => {
    const { data } = await api.get(`/history`, { params: { date, teacher_id: teacherId } });
    return data;
  }
};
""",
    "src/components/ui/IconButton.tsx": """import React from 'react';
import { cn } from '../../lib/utils';
import { ButtonProps } from './Button';

export const IconButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'ghost', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          'inline-flex items-center justify-center rounded-full transition-colors focus-visible:outline-none disabled:opacity-50 disabled:pointer-events-none',
          {
            'bg-primary text-white hover:bg-primary-hover': variant === 'primary',
            'bg-transparent text-text-primary hover:bg-surface': variant === 'ghost',
            'bg-error text-white hover:bg-error/90': variant === 'destructive',
            'w-9 h-9': size === 'sm',
            'w-11 h-11 min-h-[44px] min-w-[44px]': size === 'md',
            'w-14 h-14': size === 'lg',
          },
          className
        )}
        {...props}
      >
        {isLoading ? <span className="border-2 border-t-transparent border-current rounded-full w-4 h-4 animate-spin"></span> : children}
      </button>
    );
  }
);
IconButton.displayName = 'IconButton';
""",
    "src/components/ui/Badge.tsx": """import { cn } from '../../lib/utils';

export function Badge({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-surface border border-border text-text-primary', className)}>
      {children}
    </span>
  );
}
""",
    "src/components/ui/ErrorState.tsx": """import { EmptyState } from './EmptyState';
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
""",
    "src/features/dashboard/MetricCard.tsx": """import { Card } from '../../components/ui/Card';
import { AnimatedCounter } from './AnimatedCounter';
import { cn } from '../../lib/utils';

export function MetricCard({ value, label, type }: { value: number; label: string; type: 'absent' | 'proxy' | 'assigned' | 'unresolved' }) {
  const colorMap = {
    absent: 'text-error',
    proxy: 'text-warning',
    assigned: 'text-success',
    unresolved: 'text-error'
  };
  return (
    <Card padding="md" className="flex flex-col items-center">
      <span className={cn("text-3xl font-bold", colorMap[type])}>
        <AnimatedCounter value={value} />
      </span>
      <span className="text-sm text-text-secondary mt-1">{label}</span>
    </Card>
  );
}
""",
    "src/features/dashboard/AnimatedCounter.tsx": """import { useEffect, useState } from 'react';

export function AnimatedCounter({ value }: { value: number }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = value;
    if (start === end) return;
    
    // Check for reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      setCount(end);
      return;
    }

    const duration = 600;
    let startTimestamp: number | null = null;
    
    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      // easeOutQuart
      const easeProgress = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(easeProgress * (end - start) + start));
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        setCount(end);
      }
    };
    window.requestAnimationFrame(step);
  }, [value]);

  return <>{count}</>;
}
"""
}

# Ensure directories exist and write files
for filepath, content in remaining_files.items():
    full_path = os.path.join(base_dir, filepath.replace('/', '\\'))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Scaffolded {len(remaining_files)} remaining files successfully.")
