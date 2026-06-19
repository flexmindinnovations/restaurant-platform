/**
 * Design System — Color Tokens
 * Emerald/Green theme with slate neutrals
 * Glassmorphism aesthetic with semantic colors
 */

export const colorTokens = {
  // Primary: Emerald (growth, restaurant, food)
  primary: {
    '50': '#f0fdf4',
    '100': '#dcfce7',
    '200': '#bbf7d0',
    '300': '#86efac',
    '400': '#4ade80',
    '500': '#22c55e', // Primary brand color
    '600': '#16a34a',
    '700': '#15803d',
    '800': '#166534',
    '900': '#145231',
    '950': '#052e16',
  },

  // Secondary: Purple (accents, highlights)
  secondary: {
    '50': '#faf5ff',
    '100': '#f3e8ff',
    '200': '#e9d5ff',
    '300': '#d8b4fe',
    '400': '#c084fc',
    '500': '#a855f7',
    '600': '#9333ea',
    '700': '#7e22ce',
    '800': '#6b21a8',
    '900': '#581c87',
  },

  // Neutral: Slate (backgrounds, text, borders)
  neutral: {
    '0': '#ffffff',
    '50': '#f9fafb',
    '100': '#f3f4f6',
    '200': '#e5e7eb',
    '300': '#d1d5db',
    '400': '#9ca3af',
    '500': '#6b7280',
    '600': '#4b5563',
    '700': '#374151',
    '800': '#1f2937',
    '900': '#111827',
    '950': '#030712',
  },

  // Semantic: Status colors
  semantic: {
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    pending: '#f59e0b',
  },

  // Glassmorphism: Overlay colors with transparency
  glass: {
    light: 'rgba(255, 255, 255, 0.7)',
    dark: 'rgba(15, 23, 42, 0.7)',
  },
};

/**
 * CSS Custom Properties for light/dark mode
 * Used in theme provider for dual-mode support
 */
export const cssColorVariables = {
  light: {
    '--color-primary': colorTokens.primary['500'],
    '--color-primary-dark': colorTokens.primary['600'],
    '--color-primary-light': colorTokens.primary['400'],

    '--color-bg-primary': colorTokens.neutral['0'],
    '--color-bg-secondary': colorTokens.neutral['50'],
    '--color-bg-tertiary': colorTokens.neutral['100'],

    '--color-text-primary': colorTokens.neutral['900'],
    '--color-text-secondary': colorTokens.neutral['600'],
    '--color-text-tertiary': colorTokens.neutral['500'],

    '--color-border': colorTokens.neutral['200'],
    '--color-border-light': colorTokens.neutral['100'],

    '--color-glass': colorTokens.glass.light,

    '--color-success': colorTokens.semantic.success,
    '--color-warning': colorTokens.semantic.warning,
    '--color-error': colorTokens.semantic.error,
    '--color-info': colorTokens.semantic.info,
  },
  dark: {
    '--color-primary': colorTokens.primary['400'],
    '--color-primary-dark': colorTokens.primary['500'],
    '--color-primary-light': colorTokens.primary['300'],

    '--color-bg-primary': colorTokens.neutral['950'],
    '--color-bg-secondary': colorTokens.neutral['900'],
    '--color-bg-tertiary': colorTokens.neutral['800'],

    '--color-text-primary': colorTokens.neutral['50'],
    '--color-text-secondary': colorTokens.neutral['400'],
    '--color-text-tertiary': colorTokens.neutral['500'],

    '--color-border': colorTokens.neutral['700'],
    '--color-border-light': colorTokens.neutral['800'],

    '--color-glass': colorTokens.glass.dark,

    '--color-success': colorTokens.semantic.success,
    '--color-warning': colorTokens.semantic.warning,
    '--color-error': colorTokens.semantic.error,
    '--color-info': colorTokens.semantic.info,
  },
};
