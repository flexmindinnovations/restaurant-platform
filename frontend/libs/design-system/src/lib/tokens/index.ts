/**
 * Design System Tokens — Central Export
 * All design tokens (colors, spacing, typography, effects) in one place
 */

export { colorTokens, cssColorVariables } from './colors';
export { spacingTokens, spacingPatterns, cssSpacingVariables } from './spacing';
export { typographyTokens, typographyStyles, cssTypographyVariables } from './typography';
export { effectTokens, animationTokens, cssEffectVariables } from './effects';

// Re-export as complete token object
import { colorTokens, cssColorVariables } from './colors';
import { spacingTokens, cssSpacingVariables } from './spacing';
import { typographyTokens, cssTypographyVariables } from './typography';
import { effectTokens, animationTokens, cssEffectVariables } from './effects';

export const designTokens = {
  colors: colorTokens,
  spacing: spacingTokens,
  typography: typographyTokens,
  effects: effectTokens,
  animations: animationTokens,
};

export const cssVariables = {
  ...cssColorVariables,
  ...cssSpacingVariables,
  ...cssTypographyVariables,
  ...cssEffectVariables,
};
