const memos = {
  memos: [
    {tags: ['自我吐槽']},
    {tags: ['区域/中国', '经济/汇率']},
    {tags: ['思考', '国际政治', '区域/拉美']},
    {tags: ['读书/浪潮将至']},
    {tags: ['读书/浪潮将至']},
    {tags: ['思考']},
    {tags: ['读书/浪潮将至']},
    {tags: ['读书/浪潮将至']},
    {tags: []},
    {tags: ['经济/新能源']},
    {tags: ['经济/基建']},
    {tags: ['冷知识']},
    {tags: ['经济/新能源']},
    {tags: ['经济/国际货币体系']},
    {tags: ['经济/黄金']},
    {tags: ['经济/数字基础设施']},
    {tags: ['经济/国际投资']},
    {tags: ['经济/产业链']},
    {tags: ['经济/产业链', '经济/大宗商品']},
    {tags: ['经济/国际贸易']},
    {tags: ['区域/金砖']},
    {tags: ['区域/拉美']},
    {tags: ['经济/数字基础设施']},
    {tags: ['经济/产业链']},
    {tags: ['经济/国际贸易']},
    {tags: ['经济/大宗商品']},
    {tags: ['经济/产业政策', '区域/印度']},
    {tags: ['经济/能源', '南非']},
    {tags: ['区域/非洲']},
    {tags: ['经济/能源']},
    {tags: ['经济/基建']},
    {tags: ['经济/能源']},
    {tags: ['经济/基建']},
    {tags: []},
    {tags: ['经济/能源']},
    {tags: ['经济/教育']},
    {tags: ['经济/产业链']},
    {tags: ['气候']},
    {tags: ['区域/中国']},
    {tags: ['经济/能源']},
    {tags: ['指标']},
    {tags: ['经济/城投']},
    {tags: ['经济/国际贸易']},
    {tags: ['指标']},
    {tags: ['经济/能源']},
    {tags: ['经济/城投']},
    {tags: ['指标', '经济/产业链']},
    {tags: ['经济/新能源车']},
    {tags: ['气候']},
    {tags: ['经济/产业链']}
  ]
};

// 统计标签频率
const tagCount = {};
memos.memos.forEach(memo => {
  memo.tags.forEach(tag => {
    tagCount[tag] = (tagCount[tag] || 0) + 1;
  });
});

// 转换为数组并排序
const tagArray = Object.entries(tagCount).map(([tag, count]) => ({tag, count}));
tagArray.sort((a, b) => b.count - a.count);

console.log('=== 标签使用频率统计 ===\n');
console.log('总笔记数:', memos.memos.length);
console.log('有标签笔记:', memos.memos.filter(m => m.tags.length > 0).length);
console.log('无标签笔记:', memos.memos.filter(m => m.tags.length === 0).length);
console.log('唯一标签数:', Object.keys(tagCount).length);
console.log('\n--- 标签频率排名 (Top 20) ---\n');

tagArray.slice(0, 20).forEach((item, index) => {
  const bar = '█'.repeat(item.count);
  console.log(`${index + 1}. ${item.tag.padEnd(25)} ${item.count.toString().padStart(2)}次 ${bar}`);
});

console.log('\n--- 按分类统计 ---\n');

// 按一级分类统计
const categoryCount = {};
Object.keys(tagCount).forEach(tag => {
  const parts = tag.split('/');
  const category = parts[0];
  if (!categoryCount[category]) {
    categoryCount[category] = {count: 0, subtags: []};
  }
  categoryCount[category].count += tagCount[tag];
  if (parts.length > 1) {
    categoryCount[category].subtags.push(tag);
  }
});

const categoryArray = Object.entries(categoryCount).map(([cat, data]) => ({
  category: cat,
  count: data.count,
  subtags: data.subtags
}));
categoryArray.sort((a, b) => b.count - a.count);

categoryArray.forEach((cat, index) => {
  console.log(`${index + 1}. ${cat.category}: ${cat.count}次`);
  if (cat.subtags.length > 0) {
    cat.subtags.forEach(sub => {
      console.log(`   - ${sub}: ${tagCount[sub]}次`);
    });
  }
  console.log('');
});
