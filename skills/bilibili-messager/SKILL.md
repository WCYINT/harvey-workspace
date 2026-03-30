---
name: bilibili-messager
description: "Send Bilibili DMs, reply, and read chat history through browser automation. 自动发送 B 站私信、回复消息、读取聊天记录。"
---

# Bilibili Private Messaging | B站私信自动化

Send Bilibili DMs, reply to messages, and read chat history through browser automation. 通过浏览器自动化发送 B 站私信、回复消息，并读取聊天记录。

## Preconditions | 前置条件

- The user must already be logged in to Bilibili in the browser profile used for automation.  
  用户必须先在用于自动化的浏览器 profile 中登录 Bilibili。
- For sending, confirm the target account and message content with the user before any external action.  
  如需发送消息，执行任何对外发送前，必须先向用户确认目标账号和消息内容。
- For history reading, prefer a read-only flow first.  
  如需读取聊天记录，优先先走只读流程。

## Execution principles | 执行原则

1. **Do not stop halfway through a deliberate flow.** Once you begin a send or read sequence, complete the planned steps unless a blocker appears.  
   **不要半途停住。** 一旦进入明确的发送或读取流程，除非出现阻塞，否则应完成预定步骤。

2. **Use snapshots sparingly.** Snapshots are expensive; capture them when they add real value.  
   **谨慎使用快照。** 快照成本高，只有在确实增加判断价值时才获取。

3. **Do not guess sender ownership from left/right layout alone.** Bilibili message layout can be misleading.  
   **不要只靠左右布局猜发送方。** B 站私信页面布局可能会误导归属判断。

4. **Treat forwarded videos, shared cards, and images as part of chat history.** Chat history is not text-only.  
   **转发视频、分享卡片和图片都属于聊天记录。** 聊天记录不只是纯文本。

## Recommended flow for sending | 推荐发送流程

### 1. Open the whisper page | 打开私信页

```text
browser action=open targetUrl=https://message.bilibili.com/#/whisper
```

### 2. Confirm login state | 确认登录状态

If the page redirects to login, stop and ask the user to log in first.  
如果页面跳到登录页，就先停下，让用户完成登录。

### 3. Find the target conversation | 找到目标会话

Use snapshot only when needed to identify the target user or conversation.  
只在需要识别目标用户或会话时才获取快照。

### 4. Open the conversation | 打开会话

Click the target conversation and verify that the URL or conversation header changes.  
点击目标会话，并确认 URL 或会话标题已经变化。

### 5. Write the message | 写入消息

Prefer DOM-based insertion compatible with the actual editor on the page.  
优先使用与页面实际编辑器兼容的 DOM 写入方式。

### 6. Send only after confirmation | 确认后再发送

Do not trigger a real send unless the user already confirmed both target and content.  
除非用户已经确认目标和内容，否则不要触发真实发送。

## Reading chat history | 读取聊天记录

### Message ownership: correct rule | 发送方归属：正确规则

**Do not use left/right position as the primary rule.**  
**不要把左右位置当成主规则。**

Use the message container first. On the current Bilibili page structure, a message container may expose class markers like:
- `_Msg_*`
- `_MsgIsMe_*`

在当前 B 站页面结构中，消息容器可能带有如下 class 标记：
- `_Msg_*`
- `_MsgIsMe_*`

### Ownership logic | 归属判断逻辑

1. Find the message container first.  
   先找到消息容器。
2. If the container class includes `_MsgIsMe_`, treat it as **my message**.  
   如果容器 class 包含 `_MsgIsMe_`，就判定为**我发的**。
3. If it is a valid message container without `_MsgIsMe_`, treat it as **the other side**.  
   如果是有效消息容器但不包含 `_MsgIsMe_`，就判定为**对方发的**。
4. Use left/right position only as a secondary sanity check, never as the main rule.  
   左右位置只能作为辅助校验，不能作为主判断规则。

### Message types to keep | 需要保留的消息类型

When extracting chat history, keep all meaningful message types:  
提取聊天记录时，要保留所有有意义的消息类型：

- text messages  
  文本消息
- forwarded or shared videos  
  转发或分享的视频
- images  
  图片
- rich cards or structured shares  
  富卡片或结构化分享

Do not drop a message just because it is not plain text.  
不要因为消息不是纯文本，就把它丢掉。

### Practical extraction order | 实际提取顺序

1. Detect the chat message list container.  
   找到聊天消息列表容器。
2. Iterate message containers instead of raw text nodes.  
   遍历消息容器，而不是直接遍历原始文本节点。
3. Determine ownership from container class.  
   通过容器 class 判断发送方归属。
4. Determine message type from internal structure: text, image, video card, or other share.  
   再根据内部结构判断消息类型：文本、图片、视频卡片或其他分享。
5. Read nearby date/time separators to rebuild the timeline.  
   结合附近的日期/时间分隔信息重建时间线。
6. Exclude page UI noise such as counters, helper widgets, and editor hints.  
   排除页面 UI 噪音，例如计数器、助手组件和输入提示。

## Practical findings from validation | 实测结论

The following findings were validated on the live Bilibili message page and should guide future changes:  
以下结论已在真实 B 站私信页面中验证，应作为后续实现依据：

- The whisper page can be opened after login.  
  登录后可以正常打开私信页。
- A conversation can be opened successfully from the recent contact list.  
  可以从最近联系人列表中成功打开会话。
- Sender ownership cannot be judged reliably from left/right layout alone.  
  不能仅凭左右布局稳定判断发送方归属。
- `_MsgIsMe_*` on the message container is a stronger signal for "my message".  
  消息容器上的 `_MsgIsMe_*` 是判断“我发的消息”的更强信号。
- Shared video cards appear inside the chat flow and must be preserved as chat history items.  
  分享视频卡片会出现在聊天流中，必须作为聊天记录的一部分保留。

## Example implementation idea | 实现思路示例

```javascript
() => {
  const containers = Array.from(document.querySelectorAll('[class*="_Msg_"]'));
  return containers.map((el) => {
    const cls = el.className || '';
    const sender = cls.includes('_MsgIsMe_') ? 'me' : 'other';
    const text = (el.textContent || '').trim();
    const hasImage = !!el.querySelector('img');
    const hasVideoCard = !!Array.from(el.querySelectorAll('*')).find(n => (n.textContent || '').includes('投稿视频'));
    let type = 'text';
    if (hasVideoCard) type = 'video_share';
    else if (hasImage) type = 'image_or_avatar';
    return { sender, type, text };
  });
}
```

This snippet is only a starting point. In real use, you must filter out avatars and page decoration.  
这个示例只是起点，真实使用时必须继续排除头像和页面装饰元素。

## Notes | 备注

- Message length limits still apply; split long messages if necessary.  
  仍需注意消息长度限制，必要时分段发送。
- Avoid high-frequency sending.  
  避免高频发送。
- For history export, prioritize correctness of ownership and message type before chasing more history depth.  
  导出聊天记录时，先保证发送方归属和消息类型正确，再去追求更深的历史深度。
- If browser behavior looks different, re-check the live DOM before hardening the logic.  
  如果浏览器页面行为变了，先重新检查真实 DOM，再固化逻辑。
