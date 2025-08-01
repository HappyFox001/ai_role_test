# VV 陪伴助手 API 规范文档

## 概述

本 API 专为多模态陪伴助手设计，采用简化的接口模式。系统内部维护对话历史，默认流式输出，支持按标点符号分割的文本块，并为每个文本块提供情绪、状态和动作标注。

## 流式响应格式

系统默认使用 Server-Sent Events (SSE) 格式返回流式响应。每个文本块作为独立事件推送：

### 响应事件类型

```

## 数据结构详解

### 文本块数据结构 (text_chunk)

```json
{
  "chunk_index": 0,
  "text": "文本内容",
  "emotion": {
    "type": "具体情绪类型", 
    "intensity": 0.8
  },
  "state": {
    "type": "具体状态表达"
  },
}
```

### 情绪系统 (emotion)

#### 情绪分组 (group)

Joy
Anticipation
Anger
Disgust
Sadness
Surprise
Fear
Trust


### 状态系统 (state)

Serenity
Interest
Annoyance
Boredom
Pensiveness
Anxiety
Morbidness
Ecstasy
Curiosity
Distraction