---
name: "@3182/zodiac-pastlife-myth"
version: 1.0.0
author: Agentway
tags: [myth, zodiac, story, illustration, poetry, chinese-style]
description: |
  Generate a personalized “constellation past-life myth”: ~800 Chinese characters story + one epic illustration + a short destiny prophecy poem.

  Use when a user provides zodiac sign, birth date, and 3 personality keywords, and wants a romantic Chinese-myth-style fate narrative.
metadata:
  starchild:
    emoji: "✨"
    skillKey: zodiac-pastlife-myth
    requires:
      bins: [python3]
user-invocable: true
---

# AI定制「星座前世神话」

你要把用户输入（星座 + 出生日期 + 3个性格关键词）转成一份可收藏的命运叙事作品：
- 前世神话故事（约800字，中文）
- 史诗级插画（1张）
- 命运预言短诗（4-8行）
- 一页式 HTML 神话画卷

## 输入规则（先收集）

必须有：
1. 星座（如：天蝎座）
2. 出生日期（YYYY-MM-DD）
3. 3个性格关键词（如：冷静、执拗、温柔）

可选：
- 性别/代称
- 想要的情感主色（如：宿命浪漫、克制深情、热烈守护）
- 禁忌元素（如：不要悲剧结局）

如果缺字段，先补齐再生成。

## 一致性校验

- 若“星座”与“出生日期”推导结果明显不一致，先用一句话确认：
  - “你希望以你填写的星座为准，还是以生日推导星座为准？”
- 用户未回复时，默认以“用户显式填写的星座”为准。

## 输出结构（固定）

### 1) 前世神话故事（约800字）

风格：中式神话风 + 浪漫宿命感。

四段式骨架：
1. **天命开端**（≈150字）
   - 以星河、司命、古殿、灵器等意象开场。
   - 把“星座特质”翻译成神话身份（例如：天蝎→夜渊守誓者）。
2. **前世试炼**（≈250字）
   - 结合3个关键词设计三重试炼或三道誓约。
   - 每个关键词必须体现在具体行为，不写空泛形容词。
3. **宿命转折**（≈250字）
   - 设置一次“爱与天命”的冲突，给出抉择代价。
   - 保持治愈感：可有遗憾，但不写绝望结局。
4. **今生回响**（≈150字）
   - 把前世烙印映射到用户今生性格与关系模式。
   - 结尾要有被命运温柔注视的感觉。

硬规则：
- 必须出现输入的3个关键词对应行动。
- 不可写成星座运势口水文，不要“今天宜/忌”。
- 避免现代网络梗，保持古典抒情。

### 2) 命运预言短诗（4-8行）

- 文风偏古风新诗，语句短，留白感强。
- 必须呼应故事中的“核心誓约/信物/星象”。
- 最后一行落在“祝福式命定感”。

### 3) 史诗级插画（1张）

在故事完成后再生成插画，保证画面与剧情一致。

统一提示词框架（按故事替换变量）：
- 主体：用户前世神话身份 + 关键信物 + 星座象征
- 场景：中式神话场域（天阙、灵山、星海、古祭坛等）
- 氛围：romantic fate, epic, celestial, emotional, cinematic
- 风格锚点：
  `epic Chinese mythology illustration, celestial romance, ornate costume, flowing silk, ancient palace ruins, star river, volumetric light, dramatic composition, ultra-detailed, painterly, no text`

建议参数：
- `model="nanopro"`
- `aspect_ratio="landscape"`
- `quality="high"`
- `n=1`

必须从工具结果读取真实图片路径，禁止猜测路径。

## 组装成神话画卷

1. 将故事与诗写入 JSON（schema 见 `scripts/build_mythbook.py` 文件头）。
2. 执行：
   `python3 skills/zodiac-pastlife-myth/scripts/build_mythbook.py <myth.json> <out.html>`
3. 输出目录：
   `output/zodiac-pastlife-myth/<name_or_sign>/`

至少产出：
- `myth.json`
- `mythbook.html`
- `illustration.png`

## 对用户的交付话术

交付时简洁说明：
- 已完成故事 + 插画 + 预言诗
- 给出完整路径 `output/.../mythbook.html`
- 询问是否需要公开发布（若用户要公开，再走发布流程）

## 发布（用户要求“发布”时执行）

- 这是“技能发布”而不是项目发布：使用 skillmarket 发布流程。
- 发布前确认 SKILL.md frontmatter 包含 `name/version/author/tags`。
- 版本不可覆盖；有改动必须升级版本号再发。
- 返回 tag（如 `@3182/zodiac-pastlife-myth@1.0.0`）和 release 链接。

## 质量自检

- 是否精确使用用户的星座、生日、3关键词
- 故事是否约800字且分层清晰
- 预言诗是否与故事意象一致
- 插画是否为中式神话 + 浪漫命运感
- HTML 是否可直接打开阅读
- 文件路径是否完整可点
