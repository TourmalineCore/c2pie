'use strict';

const RELEASE_RULES = [
    { type: 'feat', release: 'minor' },
    { type: 'fix', release: 'patch' },
    { type: 'docs', release: 'patch' },
    { type: 'refactor', release: 'patch' },
    { type: 'chore', release: false },
    { type: 'ci', release: false },
    { type: 'style', release: false },
    { type: 'test', release: false },
    { type: 'build', release: false },
    { type: 'config', release: false },
];

const CHANGELOG_TYPES = [
    { type: 'feat', section: 'Features', hidden: false },
    { type: 'fix', section: 'Bug Fixes', hidden: false },
    { type: 'docs', section: 'Documentation', hidden: false },
    { type: 'refactor', section: 'Refactoring', hidden: false },
    { type: 'build', section: 'Build System', hidden: true },
    { type: 'chore', section: 'Chores', hidden: true },
    { type: 'ci', section: 'CI', hidden: true },
    { type: 'style', section: 'Style', hidden: true },
    { type: 'test', section: 'Tests', hidden: true },
    { type: 'config', section: 'Config', hidden: true },
];

module.exports = { RELEASE_RULES, CHANGELOG_TYPES };