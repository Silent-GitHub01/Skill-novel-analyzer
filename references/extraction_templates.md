# Extraction Templates — Per-Chapter Analysis

This document defines the structured extraction prompts used during Step 2 of the
novel analysis workflow. Each chapter is analyzed independently, then results are
aggregated in Step 3.

---

## Per-Chapter Extraction Prompt Template

When analyzing each chapter, use the following structured extraction. Output must
be valid JSON matching the schema in `output_schemas.md`.

### Prompt Structure

```
你是一位专业的文学分析师。请阅读以下小说章节文本，提取结构化信息。

## 章节信息
- 标题：{chapter_title}
- 索引：{chapter_index}
- 字数：{char_count}

## 章节文本
{chapter_text}

## 提取要求

请以 JSON 格式输出以下内容：

1. **characters（人物）**：本章出现的所有人物，包括：
   - name: 人物名称（含别称/绰号）
   - aliases: 其他称呼（如"林妹妹"对应林黛玉）
   - role: 角色定位（主角/配角/龙套/提及）
   - actions: 本章主要行为（1-3句概括）
   - state: 情感/处境状态（如"愤怒"、"陷入困境"）
   - first_appearance: 是否首次出场（true/false）

2. **relationships（关系）**：本章中体现的人物间关系：
   - char_a: 人物A
   - char_b: 人物B
   - relation_type: 关系类型（亲属/师徒/敌对/盟友/恋人/主仆/朋友/竞争/其他）
   - description: 关系描述（1句话）
   - change: 本章关系是否有变化（无变化/升温/恶化/建立/破裂/转变）

3. **locations（地点）**：本章涉及的场景地点：
   - name: 地点名称
   - type: 地点类型（城市/建筑/自然景观/虚构地点/其他）
   - description: 简述（1句话）

4. **events（事件）**：本章发生的关键事件：
   - summary: 事件概述（1句话）
   - participants: 参与人物列表
   - location: 发生地点
   - significance: 重要性（关键/重要/次要/铺垫）
   - consequence: 直接后果（如有）

5. **worldbuilding（世界观设定）**：本章揭示的世界观信息：
   - category: 类别（地理/历史/政治/经济/宗教/魔法体系/科技/种族/文化/其他）
   - content: 设定内容描述（1-2句）
   - is_new: 是否首次揭示（true/false）

6. **timeline（时间线）**：本章的时间信息：
   - time_ref: 时间标记（如"三年后"、"次日"、"同年冬天"，无则填"未明确"）
   - chronological_order: 在全书中的大致时间位置（估算）

7. **foreshadowing（伏笔与回收）**：
   - type: 类型（伏笔/回收/呼应）
   - content: 内容描述
   - related_chapter: 关联章节（如已知，否则填"未知"）

8. **chapter_summary（章节摘要）**：
   - one_line: 一句话概括
   - detailed: 3-5句详细摘要
   - emotional_tone: 情感基调（如"紧张"、"温馨"、"悲壮"）
   - tension_level: 张力等级（1-10，1最低10最高）
   - plot_advance: 剧情推进方向（起/承/转/合/伏/收）
```

---

## Extraction Guidelines

### Character Identification Rules
- 合并同一人物的不同称呼（如"宝玉"、"贾宝玉"、"宝二爷"应合并）
- 仅提取有名字或固定称呼的人物，群像（如"众人"、"百姓"）不单独列出
- "提及"指未实际出场但被提到名字的人物
- 首次出场的人物标记 `first_appearance: true`，后续章节为 `false`

### Relationship Extraction Rules
- 仅提取本章中**有实际互动或关系变化**的人物对
- 关系类型应选择最贴切的一个，可在 description 中补充细节
- 关系变化字段很重要——这是构建关系演化图的基础

### Event Significance Levels
- **关键**: 直接影响主线剧情走向
- **重要**: 推动支线或人物发展
- **次要**: 丰富叙事但不影响主线
- **铺垫**: 为后续情节埋下种子

### Tension Level Scale
- 1-2: 日常/过渡章节
- 3-4: 有小冲突或信息揭示
- 5-6: 中等冲突，剧情推进
- 7-8: 重大冲突或转折
- 9-10: 高潮/生死攸关

### Plot Advance Directions
- **起**: 新情节线开启
- **承**: 情节延续发展
- **转**: 意外转折
- **合**: 情节线收束
- **伏**: 纯铺垫章节
- **收**: 结尾/尾声

---

## Handling Edge Cases

### Very Short Chapters (< 500 chars)
- 仍执行完整提取，但 events 和 worldbuilding 可能为空数组

### Chapters with No Characters (pure description/worldbuilding)
- characters 和 relationships 为空数组
- worldbuilding 字段应尽量详细

### Ambiguous Timeline
- 如果无法确定时间顺序，chronological_order 填 -1
- time_ref 尽量从文本中找直接证据

### Multiple POV Chapters
- 在 chapter_summary 中注明视角人物
- characters 中标注 POV 角色的 role 为"主角（视角）"
