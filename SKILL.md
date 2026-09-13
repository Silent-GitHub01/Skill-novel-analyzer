---
name: novel-analyzer
description: "长篇小说深度解析技能。对长篇小说（中文/英文）进行结构化分析，提取世界观设定、人物关系图谱、章节逻辑链和情节发展时间线，生成交互式可视化报告。触发词：小说解析、小说分析、长篇小说、人物关系、世界观提取、情节分析、章节逻辑、novel analysis、story analysis。当用户提供小说文本文件（txt/md/epub）并希望分析其结构、人物、情节或世界观时使用本技能。"
agent_created: true
---

# Novel Analyzer — 长篇小说深度解析

## 概述

对长篇小说进行四维度结构化分析：**世界观设定**、**人物关系图谱**、**章节逻辑链**、**情节发展时间线**。通过分块提取 + 聚合分析的方式，生成包含交互式可视化的 HTML 分析报告。

## 触发条件

以下场景使用本技能：
- 用户提供小说文本文件（.txt / .md / .epub）并要求分析
- 用户要求提取小说的人物关系、世界观、情节结构
- 用户提到"小说解析"、"分析这部小说"、"人物关系图"、"世界观梳理"等
- 用户提供长篇故事文本（>1万字）要求结构化拆解

## 工作流程

### Step 0: 确认输入

1. 确认小说文本来源（文件路径 / 直接粘贴 / URL）
2. 确认分析语言（中文/英文/双语）
3. 确认分析深度：
   - **快速模式**：仅输出章节摘要 + 人物列表 + 关系图（适合 >50 万字超长篇）
   - **标准模式**（默认）：完整四维度分析
   - **深度模式**：标准模式 + 伏笔追踪 + 文风分析 + 主题提炼
4. 创建工作目录：`{workspace}/novel-analysis/{novel_name}/`

### Step 1: 章节分割

使用 `scripts/chapter_splitter.py` 自动检测章节边界并分割：

```bash
python scripts/chapter_splitter.py <input_file> --output {work_dir}/chapters
```

该脚本：
- 自动检测中文章节标记（第X章/回/卷/节/篇、序章、楔子、番外等）
- 自动检测英文章节标记（Chapter X、PART X、Prologue、Epilogue 等）
- 自动检测文件编码（UTF-8/GBK/GB2312/Big5 等）
- 输出 `{novel_name}_chapters.json`（元数据）和 `{novel_name}_chapters_full.json`（含全文）
- 输出独立章节文件 `{novel_name}_chapter_000.txt` 等

**特殊情况处理**：
- 无法检测到章节标记时，按 ~200 行自动分块
- EPUB 文件需先用 `ebooklib` 转为纯文本
- 文件过大（>10MB）时，分批读取处理

### Step 2: 逐章结构化提取

对每个章节执行结构化提取，提取模板见 `references/extraction_templates.md`。

**关键规则**：
- 每章独立提取，输出 JSON 格式，schema 见 `references/output_schemas.md` 第1节
- 人物合并：同一人物的不同称呼必须合并（如"宝玉"="贾宝玉"="宝二爷"）
- 仅为有实际互动或关系变化的人物对提取关系
- 标记首次出场人物、伏笔、世界观新设定

**批量处理策略**：
- 每次处理 1-3 章（视字数而定，单次上下文不超过 ~3 万字）
- 将每章提取结果保存为 `{work_dir}/extractions/chapter_{index}.json`
- 处理过程中维护一个"人物别名映射表"，确保跨章节人物名一致

### Step 3: 聚合分析

读取所有章节提取结果，执行四维度聚合：

#### 3.1 人物关系图谱
- 合并所有章节的 characters，去重，统计出场次数
- 合并所有 relationships，构建网络图节点和边
- 边权重 = 出现该关系的章节数
- 记录关系演化轨迹（每章的关系状态变化）
- 输出 `characters.json`（schema 见 `references/output_schemas.md` 第2节）

#### 3.2 世界观设定集
- 按 10 个类别聚合：地理/历史/政治/经济/宗教/魔法体系/科技/种族/文化/其他
- 合并重复条目，记录每个设定首次出现的章节和后续提及的章节
- 输出 `worldbuilding.json`（schema 见第3节）

#### 3.3 情节时间线
- 提取每章摘要、张力等级、情感基调、剧情推进方向
- 构建张力曲线（章节为X轴，张力等级为Y轴）
- 识别情节弧（连续的起承转合段落）
- 输出 `plot_timeline.json`（schema 见第4节）

#### 3.4 章节逻辑链
- **因果链**：追踪事件的因果传递（A导致B，B导致C）
- **伏笔链**：追踪伏笔的埋设、呼应和回收
- 输出 `chapter_logic.json`（schema 见第5节）

### Step 4: 生成可视化报告

使用 `assets/report_template.html` 作为模板，生成最终交互式 HTML 报告。

**操作步骤**：
1. 读取 `assets/report_template.html`
2. 将 `REPORT_DATA` 对象中的示例数据替换为实际分析结果
3. 替换模板占位符（`{{NOVEL_TITLE}}`、`{{TOTAL_CHAPTERS}}` 等）
4. 将生成的 HTML 保存为 `{work_dir}/{novel_name}_analysis_report.html`
5. 使用 `present_files` 展示给用户

**报告包含 6 个标签页**：
- 人物关系图谱（vis.js 交互式网络图，可拖拽/缩放）
- 情节时间线（Chart.js 张力曲线 + 情节弧展示）
- 章节逻辑链（因果链 + 伏笔链可视化）
- 世界观设定集（分类展示）
- 人物图鉴（卡片列表，按重要性排序）
- 章节摘要表（可滚动表格）

### Step 5: 输出交付

最终交付物：
1. **交互式 HTML 报告**（主交付物）—— 使用 `present_files` 展示
2. **结构化 JSON 数据**（characters.json / worldbuilding.json / plot_timeline.json / chapter_logic.json）—— 供后续使用
3. **Markdown 摘要**（可选）—— 包含核心发现的文字版

## 资源文件说明

### scripts/
- `chapter_splitter.py` — 章节自动分割工具。支持中英文章节标记检测、自动编码识别、大文件分块

### references/
- `extraction_templates.md` — 逐章提取的完整提示模板和提取规则指南
- `output_schemas.md` — 所有结构化输出的 JSON Schema 定义（6种输出格式）

### assets/
- `report_template.html` — 交互式 HTML 报告模板，含 vis.js 人物关系网络图和 Chart.js 张力曲线图

## 处理超长小说的策略

对于超长小说（>50 万字 / >100 章）：

1. **分段处理**：每 5-10 章为一批，先提取再聚合
2. **增量人物表**：维护全局人物别名映射表，每批处理前加载已有映射
3. **采样精读**：对过渡章节可仅提取摘要，关键章节做完整提取
4. **分批报告**：可按"卷"或"情节弧"生成分段报告，最后合并

## 注意事项

- 人物别名合并是最关键的质量控制点，务必在 Step 2 开始时就建立映射表
- 伏笔追踪需要跨章节关联，建议在 Step 2 提取时记录伏笔关键词，Step 3 聚合时全文搜索匹配
- 张力等级评估应考虑：冲突强度、信息揭示量、情感冲击、悬念程度
- 如果小说已有明确的卷/部划分，应尊重原结构作为分析的高层组织单位
- HTML 报告中的 `REPORT_DATA` 必须是合法 JSON（注意转义引号和换行符）
