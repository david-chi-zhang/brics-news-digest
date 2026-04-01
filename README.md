# BRICS News Digest Skill

Daily BRICS+ Economic & Political News Digest skill using World News API.

## Features

- 🌍 **11 Countries/Regions**: 🇪🇺 Eurozone, 🇺🇸 US, 🇯🇵 Japan, 🇧🇷 Brazil, 🇷🇺 Russia, 🇮🇳 India, 🇨🇳 China, 🇿🇦 South Africa, 🇪🇬 Egypt, 🇧🇩 Bangladesh, 🇦🇪 UAE
- ⏰ **Daily Execution**: 8:00 AM (Beijing Time)
- 📰 **Categories**: Macroeconomics + Financial Markets + Politics/Geopolitics
- 🏠 **Domestic News Only**: Each country's news must be about that country
- 🇨🇳 **China National Filter**: National-level news only (NO provincial/local)
- 🌐 **Auto-Translation**: Non-English news translated to English
- 💾 **IMA Integration**: Auto-upload to IMA DailyNews notebook & knowledge base
- 💰 **Token Efficient**: ~4,000-5,000 tokens/day (99.5% savings)

## Installation

1. Copy skill to OpenClaw skills directory:
```bash
cp SKILL.md ~/.openclaw/skills/brics-news-digest/SKILL.md
```

2. Configure environment variables:
```bash
export WORLD_NEWS_API_KEY="your_api_key"
export IMA_OPENAPI_CLIENTID="your_client_id"
export IMA_OPENAPI_APIKEY="your_api_key"
export HTTP_PROXY="http://127.0.0.1:7897"
```

3. Set up cron job for daily execution at 8:00 AM (Beijing Time)

## News Filtering

### ✅ Collected
- Macroeconomics: GDP, inflation, trade, economic policy
- Financial Markets: stocks, forex, commodities, banking
- Politics/Geopolitics: elections, diplomacy, government policy

### ❌ Excluded
- Sports (football, basketball, world cup, etc.)
- Entertainment (movies, celebrities, awards)
- Lifestyle (fashion, food, travel)
- Local/Provincial news (for China: national-level only)

## Output Format

- English language (non-English translated)
- 5 news items per country
- Sorted by time (newest first)
- Each item: title, 2-3 sentence summary, source link

## Token Consumption

| Item | Tokens |
|------|--------|
| World News API (10 calls) | ~500 |
| Input content | ~3,000-4,000 |
| IMA API | ~500 |
| **Daily Total** | **~4,000-5,000** |

**Savings vs original**: 99.5% ✅

## License

MIT
