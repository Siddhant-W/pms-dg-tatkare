import { useEffect, useRef, useState } from 'react';

/** Counts up (or down) to `value`. Respects reduced-motion. */
export function AnimatedCounter({ value }: { value: number }) {
  const [count, setCount] = useState(0);
  const from = useRef(0);

  useEffect(() => {
    const start = from.current;
    if (start === value || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      from.current = value;
      setCount(value);
      return;
    }

    const duration = 600;
    let startTimestamp: number | null = null;
    let frame = 0;
    const step = (timestamp: number) => {
      startTimestamp ??= timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 4); // easeOutQuart
      setCount(Math.round(start + (value - start) * eased));
      if (progress < 1) frame = window.requestAnimationFrame(step);
      else from.current = value;
    };
    frame = window.requestAnimationFrame(step);
    return () => window.cancelAnimationFrame(frame);
  }, [value]);

  return <>{count}</>;
}
