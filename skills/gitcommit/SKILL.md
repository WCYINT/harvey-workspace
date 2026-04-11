---
name: git-commit
description: Generate git commit messages following Conventional Commits specification. Use this skill when users ask to: (1) Create a git commit with a meaningful message, (2) Generate commit messages from git changes, (3) Help write commit messages following best practices, (4) Format or improve existing commit messages. The skill supports both automatic analysis (by examining git diff) and interactive guided generation. Automatically detects project language style (Chinese/English) and adapts commit messages accordingly.
---

# Git Commit Message Generator

Generate conventional commit messages with automatic language style detection.

## Commit Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**: `feat` `fix` `docs` `style` `refactor` `perf` `test` `build` `ci` `chore` `revert`

**Rules**:
- Type: lowercase English
- Description: <72 chars, imperative mood, no period
- Body: explain what/why, not how

**Content Requirements**:
- **Concise**: Summarize clearly, no redundant words
- **Complete**: Don't omit important changes
- **Numbered**: Multiple changes use `1. 2. 3.` format
- **Specific**: **Must clearly indicate which modules/files were modified**

**Module Reference Format**:
- For each change, specify the affected module or file
- Format: `<Action> <module/file>`
- Example: `Fix bug in UserService`, `Update Button component`

## Language Detection

Auto-detect by checking recent commits:
```bash
git log -10 --oneline
```

**Detection Logic**:
1. If recent commits contain Chinese characters → Use Chinese
2. If unable to determine → **Default to Chinese**

| Style | Format Example |
|-------|---------------|
| English | `feat(api): add user authentication endpoint` |
| Chinese | `feat(用户管理): 添加登录功能` |

**Language Rules**:
- **Type**: Always English (`feat`, `fix`, `refactor`)
- **Scope**: Follow project style (English/Chinese)
- **Description/Body**: Chinese by default, or match project language

## Workflow

### 1. Parallel Analysis (single response)

```bash
git status
git diff --staged
git log -10 --oneline
```

### 2. Smart Type Inference

| Pattern | Type |
|---------|------|
| `*.test.*`, `*.spec.*`, `__tests__/` | `test` |
| `package.json`, `*.lock` | `build` |
| `.github/`, `*.yml` (CI) | `ci` |
| `*.md`, `docs/`, `README*` | `docs` |
| Only whitespace changes | `style` |
| Keywords: fix/bug/resolve | `fix` |
| Keywords: add/implement/create | `feat` |
| Keywords: refactor/extract | `refactor` |
| Keywords: optimize/cache/performance | `perf` |

### 3. Scope Inference

Extract from file paths:
- `src/api/user/*` → `(api)` or `(user)`
- `src/components/Button/*` → `(Button)`
- `src/views/目标管理/*` → `(目标管理)`

### 4. Present & Confirm

Show the generated message and await user approval before committing.

## Examples

### English
```
feat(api): add user authentication endpoint

1. Implement JWT-based authentication in AuthService for login/logout.
2. Add token refresh mechanism and session management in TokenManager.
3. Update routes/auth.ts with authentication middleware.

Closes #123
```

### Chinese
```
feat(用户管理): 添加登录功能

1. AuthService实现基于JWT的用户认证，支持登录和登出。
2. TokenManager添加令牌刷新机制和会话管理。
3. routes/auth.ts更新API路由增加认证中间件。

关联 #123
```

### Multi-Module Example
```
fix: resolve null pointer and update UI

1. UserService修复空指针异常，添加用户数据验证。
2. components/UserList.vue更新列表渲染逻辑。
3. utils/validator.ts添加空值检查工具函数。

关联 #456
```

## Git Safety

- NEVER use `--no-verify` unless explicitly requested
- NEVER amend commits - create NEW commits
- NEVER force push without explicit request
- ALWAYS use HEREDOC for commit messages
- Prefer `git add <files>` over `git add .`

## Commit Command

```bash
git commit -m "$(cat <<'EOF'
<commit message>

Co-Authored-By: Claude code <noreply@anthropic.com>
EOF
)"
```
