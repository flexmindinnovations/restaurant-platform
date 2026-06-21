/**
 * Design System — Effects Tokens
 * Shadows, glassmorphism blur, border radius, animations
 * Professional smooth transitions (300-400ms)
 */

export const effectTokens = {
  // Shadows (for elevation, depth)
  shadow: {
    none: 'none',
    xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
  },

  // Glassmorphism: Backdrop blur effect
  glass: {
    light: {
      backdropFilter: 'blur(10px)',
      background: 'rgba(255, 255, 255, 0.7)',
      border: '1px solid rgba(255, 255, 255, 0.3)',
    },
    dark: {
      backdropFilter: 'blur(10px)',
      background: 'rgba(15, 23, 42, 0.7)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
    },
  },

  // Border radius
  borderRadius: {
    none: '0px',
    xs: '2px',
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    '2xl': '20px',
    '3xl': '24px',
    full: '9999px',
  },

  // Focus ring (for accessibility)
  focus: {
    ring: '2px solid',
    ringOffset: '2px',
  },
};

/**
 * Animation and transition tokens
 * Smooth, professional transitions (300-400ms)
 */
export const animationTokens = {
  // Duration
  duration: {
    instant: '0ms',
    fast: '150ms',
    base: '300ms',
    slow: '400ms',
    slower: '500ms',
    slowest: '600ms',
  },

  // Easing functions (professional, smooth)
  easing: {
    linear: 'cubic-bezier(0, 0, 1, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOutQuart: 'cubic-bezier(0.165, 0.84, 0.44, 1)',
    easeOutExpo: 'cubic-bezier(0.16, 1, 0.3, 1)',
  },

  // Common transitions
  transition: {
    none: 'none',
    all: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    colors:
      'color, background-color, border-color, text-decoration-color, fill, stroke 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    opacity: 'opacity 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    transform: 'transform 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    shadow: 'box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    smooth: 'all 400ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
};

/**
 * CSS Custom Properties for effects
 */
export const cssEffectVariables = {
  // Shadows
  '--shadow-xs': effectTokens.shadow.xs,
  '--shadow-sm': effectTokens.shadow.sm,
  '--shadow-md': effectTokens.shadow.md,
  '--shadow-lg': effectTokens.shadow.lg,
  '--shadow-xl': effectTokens.shadow.xl,
  '--shadow-2xl': effectTokens.shadow['2xl'],
  '--shadow-inner': effectTokens.shadow.inner,

  // Border radius
  '--radius-xs': effectTokens.borderRadius.xs,
  '--radius-sm': effectTokens.borderRadius.sm,
  '--radius-md': effectTokens.borderRadius.md,
  '--radius-lg': effectTokens.borderRadius.lg,
  '--radius-xl': effectTokens.borderRadius.xl,
  '--radius-full': effectTokens.borderRadius.full,

  // Animations
  '--duration-base': animationTokens.duration.base,
  '--duration-slow': animationTokens.duration.slow,
  '--easing-default': animationTokens.easing.easeOut,
};
