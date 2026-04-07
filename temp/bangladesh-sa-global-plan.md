# 孟加拉 & 南非 & 全球宏观经济数据更新计划

创建时间：2026-03-21 12:25

## 指标列表

### Bangladesh (孟加拉)
- [ ] Inflation: CPI

### SouthAfrica (南非)
- [ ] GDP: GDPGrowth
- [ ] RealSector: ManufacturingProduction, MiningProduction, LeadingIndicator, RetailSales
- [ ] PMI: CompositePMI

### Global (全球)
- ⚠️ CommodityPrices 和 InternationalTrade 在 url-library.json 中标记为 TBD
- [ ] 需要查找替代数据源

## 步骤
1. [ ] 并行抓取所有指标数据
2. [ ] 提取关键数据和日期
3. [ ] 保存到本地文件
4. [ ] 写入 IMA 笔记

## 当前进度
✅ 步骤 1 - 数据抓取：完成
✅ 步骤 2 - 本地文件保存：完成
✅ 步骤 3 - IMA 写入：完成

## 完成摘要

### Bangladesh (孟加拉) - 1 个文件
- ✅ Inflation.md - CPI 9.13% (2026-02) → IMA: Bangladesh - Inflation - 2026

### SouthAfrica (南非) - 3 个文件
- ✅ GDP.md - Q4 2025: +0.4% qoq → IMA: SouthAfrica - GDP - 2026
- ✅ RealSector.md - 制造业、矿业、领先指标、零售销售 (2025-12/2026-01) → IMA: SouthAfrica - RealSector - 2026
- ✅ PMI.md - Composite 50 (2026-02) → IMA: SouthAfrica - PMI - 2026

### Global (全球) - 1 个文件
- ⚠️ CommodityPrices.md - 需要替代数据源 (TradingEconomics 大宗商品页面需要 JS 渲染) → IMA: Global - CommodityPrices - 2026

## IMA 笔记状态

✅ **已完成** - 5 个笔记已创建并归类：
- Bangladesh 文件夹：1 个笔记
- SouthAfrica 文件夹：3 个笔记
- Global 文件夹：1 个笔记

## 注意事项

⚠️ **Global 大宗商品价格**：TradingEconomics 的大宗商品页面 (Gold, Oil, Copper) 需要 JavaScript 渲染，无法通过 web_fetch 直接抓取。建议：
- 使用 MCP finance-data skill 获取实时价格
- 使用专用大宗商品 API (Alpha Vantage, Quandl 等)
- 手动从可靠来源更新
