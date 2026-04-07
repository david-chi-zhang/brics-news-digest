# Agent 配置速查表

最后更新：2026-03-24

## 已配置的 Agent

| Agent ID | Workspace 路径 | 专属技能 | 用途 |
|----------|---------------|---------|------|
| `main` | `~/openclaw/workspace` | 通用技能 | 日常默认 |
| `imf-weo` | `~/openclaw/workspaces/imf-weo` | `imf-weo-analyzer` | IMF WEO 数据分析 |
| `macro-archiver` | `~/openclaw/workspaces/macro-archiver` | `ima-macro-archiver`, `macro-archiver` | 宏观经济归档 |

## 切换命令

```bash
# 切换到 imf-weo
openclaw agents bind --agent imf-weo --bind openim

# 切换到 macro-archiver
openclaw agents bind --agent macro-archiver --bind openim

# 切换回 main（默认）
openclaw agents bind --agent main --bind openim

# 查看当前配置
openclaw agents list
```

## 当前状态

- 当前对话绑定：`main`（默认）
- 所有 agent 使用相同 model：`gateway/qwen3.5-plus`
- 所有 agent 无 routing rules（默认路由）
