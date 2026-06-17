import tseslint from 'typescript-eslint';
import angular from 'angular-eslint';
import boundaries from 'eslint-plugin-boundaries';

const LIB_TYPES = {
  CORE: 'core',
  SHARED: 'shared',
  DESIGN_SYSTEM: 'design-system',
  API_CLIENT: 'api-client',
  FEATURE: 'feature',
  APP: 'app',
};

export default tseslint.config(
  { ignores: ['dist/', 'node_modules/', '.angular/'] },
  {
    files: ['**/*.ts'],
    extends: [
      ...tseslint.configs.recommended,
      ...angular.configs.tsRecommended,
    ],
    processor: angular.processInlineTemplates,
    rules: {
      '@angular-eslint/directive-selector': ['error', { type: 'attribute', prefix: 'app', style: 'camelCase' }],
      '@angular-eslint/component-selector': ['error', { type: 'element', prefix: 'app', style: 'kebab-case' }],
    },
  },
  {
    files: ['**/*.html'],
    extends: [...angular.configs.templateRecommended, ...angular.configs.templateAccessibility],
  },
  {
    files: ['**/*.ts'],
    plugins: { boundaries },
    settings: {
      'boundaries/elements': [
        { type: LIB_TYPES.APP, pattern: ['src/**'], mode: 'full' },
        { type: LIB_TYPES.CORE, pattern: ['libs/core/**'], mode: 'full' },
        { type: LIB_TYPES.SHARED, pattern: ['libs/shared/**'], mode: 'full' },
        { type: LIB_TYPES.DESIGN_SYSTEM, pattern: ['libs/design-system/**'], mode: 'full' },
        { type: LIB_TYPES.API_CLIENT, pattern: ['libs/api-client/**'], mode: 'full' },
        {
          type: LIB_TYPES.FEATURE,
          pattern: ['libs/!(core|shared|design-system|api-client)/**'],
          mode: 'full',
          capture: ['featureName'],
        },
      ],
    },
    rules: {
      'boundaries/element-types': [
        'error',
        {
          default: 'disallow',
          rules: [
            { from: [LIB_TYPES.APP], allow: [LIB_TYPES.CORE, LIB_TYPES.SHARED, LIB_TYPES.DESIGN_SYSTEM, LIB_TYPES.API_CLIENT, LIB_TYPES.FEATURE] },
            { from: [LIB_TYPES.FEATURE], allow: [LIB_TYPES.CORE, LIB_TYPES.SHARED, LIB_TYPES.DESIGN_SYSTEM, LIB_TYPES.API_CLIENT] },
            { from: [LIB_TYPES.SHARED], allow: [LIB_TYPES.CORE, LIB_TYPES.DESIGN_SYSTEM] },
            { from: [LIB_TYPES.DESIGN_SYSTEM], allow: [LIB_TYPES.CORE] },
            { from: [LIB_TYPES.API_CLIENT], allow: [LIB_TYPES.CORE] },
            { from: [LIB_TYPES.CORE], allow: [] },
          ],
        },
      ],
    },
  },
);
