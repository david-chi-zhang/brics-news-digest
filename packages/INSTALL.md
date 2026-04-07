# 孟加拉新闻收集 Skill - 使用说明

## 📦 下载位置

打包文件已创建在：
```
/home/admin/openclaw/workspace/packages/bangladesh-news-skill-20260320_101919.tar.gz
```

## 🚀 快速安装

### 方法 1: 直接复制（最简单）

```bash
cp -r ~/openclaw/workspace/bangladesh-news-skill ~/.openclaw/skills/
```

### 方法 2: 使用压缩包

```bash
cd ~/.openclaw/skills/
tar -xzf ~/openclaw/workspace/packages/bangladesh-news-skill-*.tar.gz
```

## ✅ 验证安装

```bash
ls ~/.openclaw/skills/bangladesh-news-skill/
# 应该看到：SKILL.md, README.md
```

## 📖 使用示例

安装完成后，你可以这样使用：

### 1. 获取最新新闻
```
帮我收集今天的孟加拉新闻
```

### 2. 搜索特定主题
```
搜索孟加拉经济发展相关新闻
```

### 3. 监控政治新闻
```
帮我看看孟加拉今天的政治新闻
```

### 4. 设置定时收集
```
设置每 6 小时自动收集孟加拉新闻
```

## 🔧 核心功能

### 支持的新闻源

**英文媒体：**
- The Daily Star (thedailystar.net)
- Dhaka Tribune (dhakatribune.com)
- The Business Standard (tbsnews.net)
- New Age (newagebd.net)
- UNB News (unb.com.bd)

**孟加拉语媒体：**
- Prothom Alo (prothomalo.com)
- Kaler Kantho (kalerkantho.com)
- Jugantor (jugantor.com)
- Ittefaq (ittefaq.com.bd)

### 技术实现

- 使用 Jina Reader (`r.jina.ai`) 抓取网页内容
- 支持 RSS 源监控 (feedparser)
- 可集成飞书多维表格存储
- 支持定时任务自动收集

## 📋 依赖项

必需：
- `curl` - 网页抓取
- `bash` - 脚本执行

可选：
- `Python 3` - RSS 解析
- `feedparser` - `pip install feedparser`

## 🆘 故障排查

### 问题 1: 某些网站无法访问
**解决：** 使用 Jina Reader 代理
```bash
curl -s "https://r.jina.ai/https://www.thedailystar.net"
```

### 问题 2: Skill 未生效
**解决：** 重启 Gateway
```bash
openclaw gateway restart
```

### 问题 3: 孟加拉语乱码
**解决：** 设置 UTF-8
```bash
export LANG=en_US.UTF-8
```

## 📞 更多帮助

查看完整的 SKILL.md 文档：
```bash
cat ~/.openclaw/skills/bangladesh-news-skill/SKILL.md
```

---

**创建时间**: 2026-03-20  
**版本**: 1.0
