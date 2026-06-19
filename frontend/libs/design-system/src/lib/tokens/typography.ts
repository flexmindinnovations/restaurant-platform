/**
 * Design System — Typography Tokens
 * Inter/Geist Sans typeface
 * Scales designed for readability and hierarchy
 */

export const typographyTokens = {
  // Font families
  fontFamily: {
    sans: `"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif`,
    mono: `"Monaco", "Menlo", "Ubuntu Mono", monospace`,
  },

  // Font sizes (16px base)
  fontSize: {
    xs: { size: '12px', lineHeight: '16px' },
    sm: { size: '14px', lineHeight: '20px' },
    base: { size: '16px', lineHeight: '24px' },
    lg: { size: '18px', lineHeight: '28px' },
    xl: { size: '20px', lineHeight: '28px' },
    '2xl': { size: '24px', lineHeight: '32px' },
    '3xl': { size: '30px', lineHeight: '36px' },
    '4xl': { size: '36px', lineHeight: '40px' },
    '5xl': { size: '48px', lineHeight: '48px' },
  },

  // Font weights
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },

  // Letter spacing
  letterSpacing: {
    tighter: '-0.02em',
    tight: '-0.01em',
    normal: '0em',
    wide: '0.01em',
    wider: '0.02em',
  },
};

/**
 * Semantic typography styles
 * Used for consistent text rendering across components
 */
export const typographyStyles = {
  // Headings
  h1: {
    fontSize: typographyTokens.fontSize['5xl'].size,
    lineHeight: typographyTokens.fontSize['5xl'].lineHeight,
    fontWeight: typographyTokens.fontWeight.bold,
    letterSpacing: typographyTokens.letterSpacing.tighter,
  },
  h2: {
    fontSize: typographyTokens.fontSize['4xl'].size,
    lineHeight: typographyTokens.fontSize['4xl'].lineHeight,
    fontWeight: typographyTokens.fontWeight.bold,
    letterSpacing: typographyTokens.letterSpacing.tighter,
  },
  h3: {
    fontSize: typographyTokens.fontSize['3xl'].size,
    lineHeight: typographyTokens.fontSize['3xl'].lineHeight,
    fontWeight: typographyTokens.fontWeight.semibold,
    letterSpacing: typographyTokens.letterSpacing.tight,
  },
  h4: {
    fontSize: typographyTokens.fontSize['2xl'].size,
    lineHeight: typographyTokens.fontSize['2xl'].lineHeight,
    fontWeight: typographyTokens.fontWeight.semibold,
    letterSpacing: typographyTokens.letterSpacing.normal,
  },
  h5: {
    fontSize: typographyTokens.fontSize.xl.size,
    lineHeight: typographyTokens.fontSize.xl.lineHeight,
    fontWeight: typographyTokens.fontWeight.semibold,
    letterSpacing: typographyTokens.letterSpacing.normal,
  },
  h6: {
    fontSize: typographyTokens.fontSize.lg.size,
    lineHeight: typographyTokens.fontSize.lg.lineHeight,
    fontWeight: typographyTokens.fontWeight.semibold,
    letterSpacing: typographyTokens.letterSpacing.normal,
  },

  // Body text
  bodyLarge: {
    fontSize: typographyTokens.fontSize.lg.size,
    lineHeight: typographyTokens.fontSize.lg.lineHeight,
    fontWeight: typographyTokens.fontWeight.normal,
  },
  body: {
    fontSize: typographyTokens.fontSize.base.size,
    lineHeight: typographyTokens.fontSize.base.lineHeight,
    fontWeight: typographyTokens.fontWeight.normal,
  },
  bodySmall: {
    fontSize: typographyTokens.fontSize.sm.size,
    lineHeight: typographyTokens.fontSize.sm.lineHeight,
    fontWeight: typographyTokens.fontWeight.normal,
  },

  // Labels & captions
  label: {
    fontSize: typographyTokens.fontSize.sm.size,
    lineHeight: typographyTokens.fontSize.sm.lineHeight,
    fontWeight: typographyTokens.fontWeight.medium,
    letterSpacing: typographyTokens.letterSpacing.wide,
  },
  caption: {
    fontSize: typographyTokens.fontSize.xs.size,
    lineHeight: typographyTokens.fontSize.xs.lineHeight,
    fontWeight: typographyTokens.fontWeight.normal,
    letterSpacing: typographyTokens.letterSpacing.wide,
  },

  // Code
  code: {
    fontSize: typographyTokens.fontSize.sm.size,
    lineHeight: typographyTokens.fontSize.sm.lineHeight,
    fontFamily: typographyTokens.fontFamily.mono,
    fontWeight: typographyTokens.fontWeight.normal,
  },
};

/**
 * CSS Custom Properties for typography
 */
export const cssTypographyVariables = {
  '--font-sans': typographyTokens.fontFamily.sans,
  '--font-mono': typographyTokens.fontFamily.mono,

  '--text-xs-size': typographyTokens.fontSize.xs.size,
  '--text-xs-height': typographyTokens.fontSize.xs.lineHeight,

  '--text-sm-size': typographyTokens.fontSize.sm.size,
  '--text-sm-height': typographyTokens.fontSize.sm.lineHeight,

  '--text-base-size': typographyTokens.fontSize.base.size,
  '--text-base-height': typographyTokens.fontSize.base.lineHeight,

  '--text-lg-size': typographyTokens.fontSize.lg.size,
  '--text-lg-height': typographyTokens.fontSize.lg.lineHeight,

  '--font-weight-light': typographyTokens.fontWeight.light,
  '--font-weight-normal': typographyTokens.fontWeight.normal,
  '--font-weight-medium': typographyTokens.fontWeight.medium,
  '--font-weight-semibold': typographyTokens.fontWeight.semibold,
  '--font-weight-bold': typographyTokens.fontWeight.bold,
};
