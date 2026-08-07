const RELEASE_RULES = [
    { "breaking": true, "release": 'major' },
    { "type": 'feat', "release": 'minor' },
    { "type": 'fix', "release": 'patch' },
    { "type": 'docs', "release": 'patch' },
    { "type": 'refactor', "release": 'patch' },
    { "type": 'chore', "release": false },
    { "type": 'ci', "release": false },
    { "type": 'style', "release": false },
    { "type": 'test', "release": false },
    { "type": 'build', "release": false },
    { "type": 'config', "release": false },
    { "type": 'infra', "release": false },
    { "type": 'git', "release": false },
];

const CHANGELOG_TYPES = [
    { "type": 'feat', "section": 'Features', "hidden": false },
    { "type": 'fix', "section": 'Bug Fixes', "hidden": false },
    { "type": 'docs', "section": 'Documentation', "hidden": false },
    { "type": 'refactor', "section": 'Refactoring', "hidden": false },
    { "type": 'chore', "hidden": true },
    { "type": 'ci', "hidden": true },
    { "type": 'style', "hidden": true },
    { "type": 'test', "hidden": true },
    { "type": 'build', "hidden": true },
    { "type": 'config', "hidden": true },
    { "type": 'infra', "hidden": true },
];

module.exports = { RELEASE_RULES, CHANGELOG_TYPES };
