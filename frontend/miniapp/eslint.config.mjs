import uni from '@uni-helper/eslint-config'

export default uni(
  {
    unocss: true,
    rules: {
      'no-console': 'off',
      'eslint-comments/no-unlimited-disable': 'off',
      'antfu/top-level-function': 'off',
    },
    ignores: [
      'src/uni_modules/**/*',
      'docs/.vitepress/dist',
      'docs/.vitepress/cache',
      '**/*.md',
    ],
  },
)
