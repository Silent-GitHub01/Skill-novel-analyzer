# Output Schemas — Structured Data Formats

This document defines the JSON schemas for all structured outputs in the novel
analysis workflow. All extraction and aggregation outputs must conform to these
schemas.

---

## 1. Per-Chapter Extraction Output (`chapter_{index}.json`)

```json
{
  "chapter_index": 0,
  "chapter_title": "第一章 风起",
  "characters": [
    {
      "name": "林云",
      "aliases": ["云少", "小云"],
      "role": "主角",
      "actions": "在书院中与赵轩对峙，展示出超常的灵力感知",
      "state": "隐忍中暗藏锋芒",
      "first_appearance": true
    }
  ],
  "relationships": [
    {
      "char_a": "林云",
      "char_b": "赵轩",
      "relation_type": "敌对",
      "description": "因家族旧怨在书院公开对立",
      "change": "建立"
    }
  ],
  "locations": [
    {
      "name": "青云书院",
      "type": "建筑",
      "description": "大陆最负盛名的修行学府"
    }
  ],
  "events": [
    {
      "summary": "林云在入学考核中意外触发上古阵法",
      "participants": ["林云", "赵轩", "王长老"],
      "location": "青云书院·考核场",
      "significance": "关键",
      "consequence": "引起各方势力关注"
    }
  ],
  "worldbuilding": [
    {
      "category": "魔法体系",
      "content": "修行者按灵力分为九境，每境三品",
      "is_new": true
    }
  ],
  "timeline": {
    "time_ref": "故事开篇",
    "chronological_order": 0
  },
  "foreshadowing": [
    {
      "type": "伏笔",
      "content": "林云体内的异常灵力波动暗示特殊血脉",
      "related_chapter": "未知"
    }
  ],
  "chapter_summary": {
    "one_line": "林云入学青云书院，在考核中展露异常天赋",
    "detailed": "林云带着家族期望进入青云书院。入学考核中...",
    "emotional_tone": "紧张中带期待",
    "tension_level": 6,
    "plot_advance": "起"
  }
}
```

---

## 2. Aggregated Character Relationship Graph (`characters.json`)

```json
{
  "nodes": [
    {
      "id": "林云",
      "label": "林云",
      "aliases": ["云少", "小云"],
      "role": "主角",
      "first_appearance_chapter": 0,
      "appearance_count": 45,
      "description": "故事核心人物，身负特殊血脉的少年"
    }
  ],
  "edges": [
    {
      "source": "林云",
      "target": "赵轩",
      "relation_type": "敌对",
      "weight": 8,
      "description": "因家族旧怨在书院公开对立",
      "evolution": [
        {"chapter": 0, "state": "建立"},
        {"chapter": 5, "state": "恶化"},
        {"chapter": 12, "state": "转变", "note": "联手对抗外敌"}
      ]
    }
  ]
}
```

### Edge Weight Calculation
- weight = number of chapters where this relationship appears
- Higher weight = more central relationship

---

## 3. Aggregated Worldbuilding Document (`worldbuilding.json`)

```json
{
  "categories": {
    "地理": [
      {
        "content": "大陆分为东、西、南、北四大域",
        "first_chapter": 0,
        "chapters": [0, 3, 7]
      }
    ],
    "魔法体系": [
      {
        "content": "修行者按灵力分为九境，每境三品",
        "first_chapter": 0,
        "chapters": [0, 2, 5]
      }
    ],
    "历史": [],
    "政治": [],
    "经济": [],
    "宗教": [],
    "科技": [],
    "种族": [],
    "文化": [],
    "其他": []
  }
}
```

---

## 4. Plot Timeline (`plot_timeline.json`)

```json
{
  "chapters": [
    {
      "index": 0,
      "title": "第一章 风起",
      "summary_one_line": "林云入学青云书院，在考核中展露异常天赋",
      "tension_level": 6,
      "emotional_tone": "紧张中带期待",
      "plot_advance": "起",
      "key_events": [
        "林云在入学考核中意外触发上古阵法"
      ],
      "time_ref": "故事开篇",
      "chronological_order": 0
    }
  ],
  "tension_curve": [
    {"x": 0, "y": 6, "label": "第一章"}
  ],
  "plot_arcs": [
    {
      "name": "入学篇",
      "start_chapter": 0,
      "end_chapter": 8,
      "description": "林云进入青云书院并崭露头角",
      "key_milestones": [0, 3, 7]
    }
  ]
}
```

---

## 5. Chapter Logic Chain (`chapter_logic.json`)

```json
{
  "chains": [
    {
      "type": "causal",
      "description": "因果链：入学考核触发阵法 → 引起关注 → 被卷入势力斗争",
      "links": [
        {"chapter": 0, "event": "触发上古阵法", "effect": "引起各方关注"},
        {"chapter": 3, "event": "被王长老收为弟子", "cause": "阵法事件展示的天赋"},
        {"chapter": 7, "event": "遭暗杀未遂", "cause": "引起敌对势力警觉"}
      ]
    },
    {
      "type": "foreshadowing",
      "description": "伏笔链：特殊血脉线索",
      "links": [
        {"chapter": 0, "type": "伏笔", "content": "体内异常灵力波动"},
        {"chapter": 5, "type": "呼应", "content": "梦境中出现远古影像"},
        {"chapter": 12, "type": "回收", "content": "血脉觉醒，身世揭晓"}
      ]
    }
  ]
}
```

---

## 6. Final Report Structure (`analysis_report.json`)

```json
{
  "metadata": {
    "title": "小说标题",
    "total_chapters": 50,
    "total_chars": 500000,
    "analysis_date": "2026-08-09",
    "language": "zh"
  },
  "summary": {
    "premise": "一句话概括故事核心设定",
    "themes": ["成长", "复仇", "守护"],
    "genre": "玄幻",
    "protagonist": "林云",
    "main_conflict": "林云对抗黑暗势力的成长之路"
  },
  "character_count": 30,
  "location_count": 12,
  "worldbuilding_entries": 25,
  "plot_arcs": 4,
  "foreshadowing_count": 15,
  "foreshadowing_resolved": 12
}
```
