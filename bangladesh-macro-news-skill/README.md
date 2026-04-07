# 孟加拉宏观经济新闻收集 Skill

## 📦 快速安装

```bash
cp -r ~/openclaw/workspace/bangladesh-macro-news-skill ~/.openclaw/skills/
```

## 🚀 使用示例

### 基础用法
```
帮我总结过去 7 天孟加拉宏观经济新闻
```

### 输出
- 自动从 The Financial Express 收集新闻
- 过滤宏观经济相关主题（GDP、通胀、贸易、汇率等）
- 生成飞书文档，包含：
  - 新闻摘要（标题 + 链接 +50 字摘要）
  - 关键数据表格
  - 主题总结

## 📋 关注主题

- GDP 增长
- 工业生产
- 货币政策（Bangladesh Bank）
- 财政政策/预算
- 贸易（出口、进口、CEPA）
- 汇率（BDT）
- 国际收支
- 通胀（CPI、食品、非食品）
- 侨汇
- 外国直接投资（FDI）

## 🔧 技术特点

- ✅ 使用 `web_fetch` 而非 `browser`（token 节省 60-80%）
- ✅ 两阶段过滤（列表页 → 全文）
- ✅ 并行处理多篇文章
- ✅ 结构化飞书文档输出
- ✅ 支持自定义时间范围和新闻源

## 📁 文件结构

```
bangladesh-macro-news-skill/
├── SKILL.md          # Skill 定义和使用说明
└── README.md         # 本文件
```

---

**版本**: 1.0  
**创建日期**: 2026-03-20  
**基于**: 早晨实际执行的新闻收集任务
