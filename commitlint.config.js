module.exports = {
  extends: ['@commitlint/config-conventional'],
  // defaultIgnores: true is the default; merge commits are ignored automatically
  rules: {
    'type-enum': [
      2,
      'always',
      ['build', 'chore', 'ci', 'docs', 'feat', 'fix', 'perf', 'refactor', 'revert', 'style', 'test']
    ]
  }
};
