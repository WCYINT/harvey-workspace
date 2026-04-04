---
name: douyin-send-message
description: 在抖音网页版发送私信消息。当用户想发送抖音私信、提醒续火花、或者提到"抖音发消息"、"发抖音私信"、"douyin send message"时触发。支持快速查找联系人、自动发送并关闭页面。
---

# 抖音私信发送

## 参数

调用时传入两个参数（由调用方实时提供，不要写死）：
- `联系人`：下拉列表中显示的联系人名字（可以是完整名字或部分匹配）
- `消息内容`：要发送的具体内容（字符串，支持 emoji）

## 执行步骤

### Step 1: 打开私信列表页面

```javascript
browser(action="open", url="https://www.douyin.com/chat", profile="openclaw")
browser(action="act", kind="wait", timeMs=2000, targetId="<pageId>")
```

### Step 2: 查找并点击目标联系人

**用一条 snapshot 搞定查找（默认 snapshot 包含 ref，速度较快）：**

```javascript
browser(action="snapshot", targetId="<pageId>")
```

在结果中找到目标联系人的 listitem ref（格式：`listitem [ref=e数字]`，在联系人名字元素附近）。

然后直接点击 ref：

```javascript
browser(action="act", ref="<ref>", kind="click", targetId="<pageId>")
browser(action="act", kind="wait", timeMs=1000, targetId="<pageId>")
```

### Step 3: 输入并发送

```javascript
browser(action="act", kind="evaluate", fn="() => { var msg = 'MESSAGE_CONTENT'; var inputs = document.querySelectorAll('[contenteditable=\"true\"]'); for (var input of inputs) { var rect = input.getBoundingClientRect(); if (rect.width > 0 && rect.height > 0) { input.focus(); for (var i = 0; i < msg.length; i++) { document.execCommand('insertText', false, msg[i]); } return 'OK'; } } return 'No input'; }", targetId="<pageId>")
browser(action="act", kind="press", key="Enter", targetId="<pageId>")
browser(action="act", kind="wait", timeMs=1000, targetId="<pageId>")
```

### Step 4: 关闭页面

```javascript
browser(action="close", targetId="<pageId>")
```

## 关键 DOM（2026-03-22 验证）

- 私信列表页面：`https://www.douyin.com/chat`
- 列表项结构：`listitem [ref=e数字]`，在联系人名字元素附近
- 聊天输入框：`[contenteditable="true"]`，class 含 `messageEditorinputArea`
- **必须用 `document.execCommand('insertText')` 逐字输入**

## 执行流程（最优步骤数）

1. `open` → 等 2s
2. `snapshot`（默认，含 ref）→ 找到联系人的 `listitem ref`
3. `click` ref → 等 1s
4. `evaluate` 输入 → `press` Enter → 等 1s
5. `close`

**总计 5 个 browser 操作**，平均总耗时约 40-60 秒（主要瓶颈在浏览器工具自身延迟，无法进一步优化）。

## 注意事项

- `TARGET_NAME` 和 `MESSAGE_CONTENT` 是占位符，调用时替换为实际值
- 发送完毕后**必须关闭页面**释放资源
- 建议超时 90 秒
- 联系人名字支持部分匹配，如"小楠子"可匹配"小楠子爱跳舞"