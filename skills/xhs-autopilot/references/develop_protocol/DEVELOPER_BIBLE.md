# 📖 XHS Autopilot: The Developer's Bible
## 开发、扩展与维护的终极指南

**版本**: v2.0（基于实际运营经验优化）  
**最后更新**: 2026-03-07

---

## 🏗️ 核心架构：大脑与手臂 (Brain vs. Hands)

本项目遵循**寄生式自动化流**：
- **大脑 (Agent)**: 负责高层逻辑、文案生成、决策规划（读取 Memory，调用 Scripts）。
- **手臂 (Scripts)**: 位于 `scripts/` 下的原子化工具，负责具体的浏览器操作（Playwright）。

**关键原则**: 
- 脚本保持"笨拙"与"纯粹"，只负责接收指令并返回执行状态
- 业务决策由 Agent 根据 Memory 中的战略和模式做出
- **新发现**: Agent 必须在关键步骤使用 `image` 工具检查输出，不能盲目信任脚本

---

## 🧩 脚本开发标准 (BSP Protocol)

所有新增脚本必须位于 `scripts/[module_name]/` 下，并包含 `run.py` 和 `README.md`。

### 1. 命令行接口 (CLI)
- **参数化**: 必须使用 `argparse` 处理输入
- **路径**: 所有路径参数应支持绝对路径
- **帮助信息**: 必须包含 `--help` 说明

### 2. 标准输出 (Stdout) 标签
Agent 通过解析 stdout 来感知进度。脚本必须打印：
- `[STATUS:INFO]`: 一般信息，表示步骤进度
- `[STATUS:SUCCESS]`: 操作成功
- `[STATUS:FAILURE]`: 失败原因（用于 Agent 自动调优）
- `[STATUS:WARNING]`: 警告，非致命错误
- `[OUTPUT:KEY] value`: 返回的数据（如图片路径、笔记 ID）

**示例**:
```python
print("[STATUS:INFO] Uploading 3 image(s)...")
print("[STATUS:SUCCESS] Upload completed")
print("[OUTPUT:COVER] /path/to/cover.png")
```

### 3. 退出码 (Exit Codes)
- `0`: 成功
- `1`: 一般性失败（配置错误、参数缺失）
- `2`: 浏览器 CDP 连接失败
- `3`: 目标页面操作异常（元素丢失/超时）

---

## 🌐 浏览器控制与安全 (Anti-Ban & Stability)

### 1. CDP 寄生模式 (Parasitic Connect)
**禁止通过 `launch()` 启动浏览器**。

```python
# ✅ 正确：必须连接至宿主 Chrome (Port 9222)
browser = p.chromium.connect_over_cdp("http://localhost:9222")

# ❌ 错误：会启动无登录态的新浏览器
browser = p.chromium.launch()
```

**为什么**: 
- 继承真人的登录态和指纹
- 免受滑块验证干扰
- 保持用户数据（cookies、localStorage）

### 2. XHS 交互 SOP (The Golden Rules)

#### 拟人化输入
- 输入文字必须设置 `delay`（建议 50-150ms）
- **严禁**使用 `fill()`（瞬间注入会触发检测）
- **推荐**使用 `type()` 或 `press()` 逐字输入

```python
# ✅ 正确
locator.type(text, delay=random.randint(50, 150))

# ❌ 错误
locator.fill(text)  # 瞬间注入，可能触发检测
```

#### JS 注入 (Viewport Trap Fix)
对于 Playwright 报错 "outside of viewport" 的按钮/输入框，**必须使用 JS 强制触发**：

```python
# 当普通 click() 失败时
page.evaluate("el => el.click()", element_handle)
```

**典型场景**:
- 小红书发布页的"上传图文" Tab
- 某些浮层按钮
- 超出视口的元素

#### 状态机导航
- **绝不要**直接 `goto` 内部页面（可能导致状态错误）
- **推荐**通过点击导航栏位，并等待随机延迟

```python
# ✅ 推荐：点击导航
tab.click()
human_sleep(2, 5)  # 等待页面切换

# ❌ 不推荐：直接跳转
goto("https://creator.xiaohongshu.com/publish/publish")
```

---

## ⚠️ 历史踩坑与避雷针 (Lessons Learned)

### 运营层面的坑（Agent 必须注意）

| 场景 | 坑位 (The Trap) | 解决方案 (The Bible) | 发现时间 |
| :--- | :--- | :--- | :--- |
| **封面页码** | 单图封面标"1/7"但实际只有1张图 | **单图不标页码，多图才标** | 2026-03-07 |
| **随机图片** | 使用 picsum.photos 下载与内容无关的图片 | **强制使用 Canvas 或 即梦AI** | 2026-03-07 |
| **视觉检查** | 不检查就发布，导致中文显示方框 | **必须用 image 工具确认封面** | 2026-03-07 |
| **标题长度** | 超过 20 字会产生静默发布失败 | 强制截断标题至 18 字符内 (`title[:18]`) | - |

### 技术层面的坑（Scripts 必须处理）

| 场景 | 坑位 (The Trap) | 解决方案 (The Bible) |
| :--- | :--- | :--- |
| **发布页** | 默认在"上传视频" Tab | 必须显式检测并点击"上传图文" Tab |
| **登录态** | 宿主 Chrome 崩溃或未启动 | 脚本启动前必须先探测 `localhost:9222` 可连通性 |
| **元素遮挡** | "新功能引导"浮窗拦截点击 | 编写全局的 `close_modals()` 函数，处理常见的 XHS 弹窗 |
| **中文显示** | Canvas 封面中文显示为方框 | 使用支持中文的字体（梦源黑体/思源黑体）|
| **页面加载** | 元素未加载完成就操作 | 使用 `wait_for_selector` 或 `wait_for_load_state` |

---

## 🔧 脚本更新记录

### cover/run.py
- **v1.0**: 初始版本，使用 DejaVuSans 字体
- **v1.1** (2026-03-07): 修复中文显示问题，添加 `get_chinese_font()` 函数，自动检测系统中文字体

### publish/run.py
- **v1.0**: 基础发布功能
- **v1.1**: 添加输入验证和详细日志
- **v1.2**: 添加自动更新选题库功能
- **v1.3** (2026-03-07): 优化标题和正文输入，使用 fill+type 混合策略，解决卡顿问题

### search/run.py
- **v1.0**: 基础搜索功能
- **v1.1** (2026-03-07): 添加"Next steps"提示，引导后续操作

---

## 🛠️ 新增工具流程

1. **创建目录**: `scripts/my_new_tool/`
2. **编写逻辑**: 
   - 使用 `playwright` + CDP
   - 遵循拟人化延迟
   - 输出标准状态标签
3. **编写 README**: 更新该目录下的 `README.md`，包含使用示例
4. **注册说明**: 在根目录 `SKILL.md` 的"工具箱"部分添加该工具的描述
5. **测试验证**: 至少发布3篇笔记验证工具稳定性

---

## 📝 Agent 开发指南

### 关键认知

1. **脚本不是万能的**
   - 脚本只能执行原子操作
   - 业务决策必须由 Agent 根据 Memory 做出
   - **必须在关键步骤检查输出**（如封面必须用 image 工具查看）

2. **Memory 是大脑**
   - 所有战略、原则、经验都存储在 Memory
   - 每次执行前必须加载相关记忆
   - 执行后必须更新记忆（复盘）

3. **持续优化**
   - 每个模式都是活的，根据反馈迭代
   - 踩坑后立即记录到 MEMORY.md
   - 定期回顾和优化流程

### 典型工作流程

```
读取 Memory（战略+模式）
    ↓
选择脚本工具
    ↓
执行脚本
    ↓
检查输出（image工具等）
    ↓
判断结果
    ↓
更新 Memory（复盘）
```

---

## 🎯 核心原则

1. **质量 > 数量** - 宁可少发，也要保证质量
2. **检查 > 信任** - 关键步骤必须人工确认（image工具）
3. **记录 > 记忆** - 所有经验教训必须写入文件
4. **迭代 > 完美** - 先发布，再根据反馈优化
5. **用户 > 技术** - 技术服务于用户体验

---

*本文档是技术规范，面向未来开发者扩展系统。运营层面的规范请参见 `MEMORY.md` 和 `templates/`。*
