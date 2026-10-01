/** A theme colour that still works with Tailwind's opacity modifiers (bg-primary/10): CSS-variable
 *  colours can't be given an alpha channel directly, so mix with transparent when one is requested. */
const c = (variable: string) =>
  ({ opacityValue }: { opacityValue?: string }) =>
    // Plain utilities (bg-primary) arrive with no value or the `var(--tw-*-opacity)` placeholder.
    opacityValue === undefined || opacityValue.startsWith('var(') || opacityValue === '1'
      ? `var(${variable})`
      : `color-mix(in srgb, var(${variable}) ${Math.round(Number(opacityValue) * 100)}%, transparent)`;

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: c('--color-bg'),
        surface: c('--color-surface'),
        'surface-elevated': c('--color-surface-elevated'),
        border: c('--color-border'),
        'border-subtle': c('--color-border-subtle'),
        primary: c('--color-primary'),
        'primary-hover': c('--color-primary-hover'),
        'primary-soft': c('--color-primary-soft'),
        accent: c('--color-accent'),
        'accent-bg': c('--color-accent-bg'),
        'accent-fg': c('--color-accent-fg'),
        'accent-ink': c('--color-accent-ink'),
        nav: c('--color-nav-bg'),
        'nav-hover': c('--color-nav-hover'),
        'nav-fg': c('--color-nav-fg'),
        'nav-muted': c('--color-nav-muted'),
        success: c('--color-success'),
        'success-bg': c('--color-success-bg'),
        warning: c('--color-warning'),
        'warning-bg': c('--color-warning-bg'),
        error: c('--color-error'),
        'error-bg': c('--color-error-bg'),
        'text-primary': c('--color-text-primary'),
        'text-secondary': c('--color-text-secondary'),
        'text-muted': c('--color-text-muted'),
        present: c('--color-present'),
        'present-bg': c('--color-present-bg'),
        absent: c('--color-absent'),
        'absent-bg': c('--color-absent-bg'),
        'not-marked': c('--color-not-marked'),
        'not-marked-bg': c('--color-not-marked-bg'),
        pending: c('--color-pending'),
        'pending-bg': c('--color-pending-bg'),
        assigned: c('--color-assigned'),
        'assigned-bg': c('--color-assigned-bg'),
        unresolved: c('--color-unresolved'),
        'unresolved-bg': c('--color-unresolved-bg'),
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
      },
      fontFamily: {
        sans: ['var(--font-sans)'],
        heading: ['var(--font-heading)'],
      },
      transitionDuration: {
        fast: '150ms',
        base: '200ms',
        slow: '250ms',
      },
    },
  },
  plugins: [],
};
