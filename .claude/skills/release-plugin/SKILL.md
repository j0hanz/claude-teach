---
name: release-plugin
description: Use when cutting a new version release for the teach Claude Code plugin — version bump, tag, or GitHub release.
---

Version-bump-and-ship workflow for **this repo only** — teach is a Claude Code
plugin, not an npm package.

## Files that carry the version (both kept in sync)

| File                              | Field                                        |
| --------------------------------- | -------------------------------------------- |
| `.claude-plugin/plugin.json`      | `"version"`                                  |
| `.claude-plugin/marketplace.json` | `plugins[0].version` (nested, not top-level) |

## Determine bump type

```bash
git describe --tags --abbrev=0          # last release tag (fails if no tags yet — then this is the first release; use all commits)
git log <last-tag>..HEAD --oneline       # commits since then
```

- Any `feat:` commit → **MINOR**
- Any `!` or `BREAKING CHANGE` → **MAJOR**
- Otherwise (`fix:`, `chore:`, `docs:`, `refactor:`) → **PATCH**

## Steps

1. **Bump** both JSON manifests to the same `<NEW>` version.
2. **Verify**:
   ```bash
   git grep -n "\"version\": \"<NEW>\"" -- .claude-plugin/plugin.json .claude-plugin/marketplace.json   # must print exactly 2 lines
   git grep -n "\"version\": \"<OLD>\"" -- .claude-plugin/plugin.json .claude-plugin/marketplace.json   # must print zero
   ```
3. **Validate**: run exactly `claude plugin validate . --strict` — must pass before committing.
4. **Commit** (stage only the two manifests):
   ```bash
   git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
   git commit -m "chore: bump version to <NEW>"
   ```
5. **Tag**: `git tag -a v<NEW> -m "Version <NEW>"`.
6. **Confirm with the user before pushing** — push is visible to others and not easily reversible.
7. **Push**: `git push origin main && git push origin v<NEW>`.
8. **Release**: `gh release create v<NEW> --title "v<NEW>" --notes "<notes>"`, notes summarizing the commits since `<last-tag>` grouped by fix/feat/etc. `gh release view v<NEW>` must print it.
9. **Finalize**: `git status` must show a clean working tree.

## Out of scope

- `npm publish` — not npm-distributed.
- CHANGELOG.md / changelog-generation script — doesn't exist here.
