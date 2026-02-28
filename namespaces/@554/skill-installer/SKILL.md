---
name: skill-installer
version: 2.0.0
description: "Search, install, and publish skills from the Starchild Community Marketplace and SkillsMP. Use when the user wants to find, discover, install, or share skills."

metadata:
  starchild:
    emoji: "📦"
    skillKey: skill-installer

user-invocable: true
---

# Skill Installer

Search, install, and publish skills from two sources:

1. **Starchild Marketplace** (primary) — community skills at `skills-market-gateway.fly.dev`
2. **SkillsMP** (fallback) — open-source skills via `skillsmp_search` tool

## Gateway

| Endpoint | URL |
|----------|-----|
| Public | `https://skills-market-gateway.fly.dev` |
| Fly internal | `http://skills-market-gateway.internal:8080` |

Read operations (search, install) are public. Write operations (publish) require Fly OIDC auth.

---

## 1. Search

### Starchild Marketplace (preferred)

```bash
curl -s "https://skills-market-gateway.fly.dev/skills/search?q=QUERY" | python3 -m json.tool
```

| Param | Default | Options |
|-------|---------|---------|
| `q` | `""` | Free-text (name, description, namespace, tags) |
| `tag` | `""` | Filter by exact tag |
| `sort` | `stars` | `stars`, `recent`, `installs` |
| `page` | `1` | Page number |
| `limit` | `20` | Max 100 |

### SkillsMP (fallback)

Use the `skillsmp_search` tool when the user explicitly asks for SkillsMP, or when Starchild Marketplace returns no relevant results.

### Workflow

1. **Always search Starchild Marketplace first** via `bash curl`.
2. Present results with namespace, name, description, stars, installs.
3. If no good match found, search SkillsMP as fallback and tell the user.
4. Recommend based on: description match > installs > stars > recency.

---

## 2. Install

### From Starchild Marketplace

**Step 1: Fetch skill files as JSON**

```bash
curl -s "https://skills-market-gateway.fly.dev/skills/NAMESPACE/SKILLNAME/install?format=json"
```

- `NAMESPACE` — without `@` (e.g. `alice`, not `@alice`)
- Add `?version=1.0.0` for a specific version (default: latest)

**Step 2: Write files to local skills directory**

```bash
python3 -c "
import json, os, urllib.request

url = 'https://skills-market-gateway.fly.dev/skills/NAMESPACE/SKILLNAME/install?format=json'
data = json.loads(urllib.request.urlopen(url).read())
skill_dir = f'./skills/{data[\"name\"]}'
for fname, content in data['files'].items():
    path = os.path.join(skill_dir, fname)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
print(f'Installed {data[\"namespace\"]}/{data[\"name\"]} v{data[\"version\"]} -> {skill_dir}')
"
```

**Step 3: Call `skill_refresh()`** to reload the skills cache.

### From SkillsMP

```bash
npx skills add <githubUrl>
```

Use the `GitHub` field from `skillsmp_search` results. If `npx skills` isn't available, fall back to manual:
1. Extract raw SKILL.md URL from `githubUrl`
2. Fetch with `web_fetch`
3. Write to `skills/<name>/SKILL.md`
4. Call `skill_refresh()`

### Post-Install

**Always** call `skill_refresh()` after installation from either source and confirm the skill appears in the refreshed list.

---

## 3. Publish

Upload a local skill to the Starchild Community Marketplace.

### SKILL.md Requirements

Every skill must have YAML frontmatter:

```yaml
---
name: my-skill
version: 1.0.0
description: What this skill does
author: your-name
tags: [tag1, tag2]
---
```

| Field | Required | Rules |
|-------|----------|-------|
| `name` | ✅ | Lowercase, alphanumeric + hyphens, 2-64 chars |
| `version` | ✅ | Semver (e.g. `1.0.0`) — immutable once published |
| `description` | Recommended | Short summary for search |
| `author` | Recommended | Author name |
| `tags` | Recommended | Array of tags for discoverability |

### Workflow

**Step 1: Validate the skill directory**

```bash
# Check SKILL.md exists and has required frontmatter
SKILL_DIR="./skills/my-skill"
head -20 "$SKILL_DIR/SKILL.md"
```

Verify `name` and `version` fields are present in frontmatter.

**Step 2: Get OIDC token**

```bash
TOKEN=$(curl -s --unix-socket /.fly/api \
  -X POST -H "Content-Type: application/json" \
  "http://localhost/v1/tokens/oidc" \
  -d '{"aud": "skills-market-gateway"}')
```

**Step 3: Build and send publish request**

```bash
SKILL_DIR="./skills/my-skill"
GATEWAY="https://skills-market-gateway.fly.dev"

PAYLOAD=$(python3 -c "
import os, json
files = {}
for root, dirs, fnames in os.walk('$SKILL_DIR'):
    for f in fnames:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, '$SKILL_DIR')
        with open(full) as fh:
            files[rel] = fh.read()
print(json.dumps({'files': files}))
")

curl -s -X POST "$GATEWAY/skills/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | python3 -m json.tool
```

### Publish Response (201)

```json
{
  "namespace": "@your-namespace",
  "name": "my-skill",
  "version": "1.0.0",
  "tag": "@your-namespace/my-skill@1.0.0",
  "download_url": "https://github.com/.../bundle.zip",
  "release_url": "https://github.com/.../releases/tag/..."
}
```

### Publish Errors

| Status | Meaning |
|--------|---------|
| `400` | Missing SKILL.md, invalid name/version, missing frontmatter |
| `401` | Missing or invalid OIDC token |
| `409` | Version already exists — bump the version number |
| `500` | Server error |

### Version Rules

- Each version is **immutable** — once `1.0.0` is published, it cannot be overwritten.
- To update, bump the version (e.g. `1.0.1`) and publish again.
- Old versions are never deleted — all download links remain valid.

---

## Decision Tree

```
User wants to find a skill
  → Search Starchild Marketplace first (curl gateway)
  → No results? Search SkillsMP (skillsmp_search tool)
  → Present ranked results from whichever source

User wants to install a skill
  → From Starchild: curl install endpoint → write files → skill_refresh()
  → From SkillsMP: npx skills add <url> or manual fetch → skill_refresh()

User wants to publish/share a skill
  → Validate SKILL.md frontmatter (name, version)
  → Get OIDC token → POST to gateway
  → Report published namespace/name/version/URL
```

## Notes

- Starchild Marketplace skills are namespaced by publisher identity (`@namespace/skill-name`)
- SkillsMP skills come from individual GitHub repos — watch for monorepo star inflation
- Always `skill_refresh()` after any installation
- The gateway namespace is derived from the Fly OIDC token — publishers cannot impersonate others
