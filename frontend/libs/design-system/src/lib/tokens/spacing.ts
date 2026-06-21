/**
 * Design System — Spacing Tokens
 * 8px base unit for 8px grid alignment
 * Follows Material Design spacing scale
 */

export const spacingTokens = {
  // Base unit: 8px
  xs: '4px', // 0.5 unit - micro spacing
  sm: '8px', // 1 unit - small
  md: '16px', // 2 units - medium
  lg: '24px', // 3 units - large
  xl: '32px', // 4 units - extra large
  '2xl': '40px', // 5 units
  '3xl': '48px', // 6 units
  '4xl': '56px', // 7 units
  '5xl': '64px', // 8 units
  '6xl': '80px', // 10 units
};

/**
 * Component-specific spacing patterns
 */
export const spacingPatterns = {
  // Padding
  padding: {
    button: `${spacingTokens.sm} ${spacingTokens.md}`,
    card: spacingTokens.lg,
    section: spacingTokens.xl,
    page: spacingTokens.xl,
  },

  // Gaps
  gap: {
    compact: spacingTokens.xs,
    normal: spacingTokens.sm,
    comfortable: spacingTokens.md,
    relaxed: spacingTokens.lg,
    spacious: spacingTokens.xl,
  },

  // Margins
  margin: {
    section: spacingTokens.xl,
    paragraph: spacingTokens.md,
    inline: spacingTokens.sm,
  },
};

/**
 * CSS Custom Properties for spacing
 */
export const cssSpacingVariables = {
  '--space-xs': spacingTokens.xs,
  '--space-sm': spacingTokens.sm,
  '--space-md': spacingTokens.md,
  '--space-lg': spacingTokens.lg,
  '--space-xl': spacingTokens.xl,
  '--space-2xl': spacingTokens['2xl'],
  '--space-3xl': spacingTokens['3xl'],
  '--space-4xl': spacingTokens['4xl'],
  '--space-5xl': spacingTokens['5xl'],
  '--space-6xl': spacingTokens['6xl'],
};
