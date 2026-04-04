# Video Generator Skill | 视频生成器技能

**English** | [中文](#中文版本)

---

## English Version

Automated text-to-video generation system with multi-provider TTS/ASR support.

### Version

**Current Version**: v1.3.1 + Visual Optimizations
**Latest Commit**: 74661f1 (main branch)
**Release Date**: 2026-03-11

### What's New (Latest)

#### Latest Improvements (Commit 74661f1)
- **Optimized default background parameters**: +300% visibility improvement
- **Background video clearly visible by default**: Opacity increased from 0.3 to 0.7
- **Improved text clarity**: Maintains readability with better contrast
- **No manual configuration needed**: Optimal visual quality out of the box

#### v1.3.1 Critical Bug Fixes
- **Fixed Aliyun ASR timestamp sync issue**: Reduced error from -75% to 0% using ffprobe
- **Added smart text segmentation**: Improved from 1 segment to 6+ segments for Aliyun ASR
- **Fixed OpenAI Whisper data format bug**: Corrected segments extraction
- **Significantly improved subtitle display effect**: Subtitles now display naturally one by one

### Features

- **Multi-provider TTS/ASR support**: OpenAI, Azure, Aliyun (阿里云), Tencent (腾讯云)
- **Automatic fallback mechanism**: Auto-switch on provider failure
- **Smart text segmentation**: Intelligent punctuation-based splitting
- **Precise timestamp synchronization**: ffprobe-based, 0% error
- **Background video support**: Custom backgrounds with adjustable opacity
- **Cyber wireframe visual effects**: Stunning animations and glitch effects
- **Fully automated pipeline**: One command from text to final video

### Quick Start

#### Installation

```bash
# Install via npm (recommended)
npm install -g openclaw-video-generator

# Or via ClawHub
clawhub install ZhenStaff/video-generator
```

#### Basic Usage

```bash
# Generate video from text script
openclaw-video-generator script.txt --voice nova --speed 1.15

# Using Aliyun (recommended for Chinese users)
openclaw-video-generator script.txt --voice Aibao --speed 1.15

# With background video
openclaw-video-generator script.txt \
  --voice Aibao \
  --bg-video background.mp4 \
  --bg-opacity 0.4
```

### Configuration

#### Environment Variables

**OpenAI (Default)**
```bash
export OPENAI_API_KEY="your-key"
```

**Aliyun (阿里云)**
```bash
export ALIYUN_ACCESS_KEY_ID="your-id"
export ALIYUN_ACCESS_KEY_SECRET="your-secret"
export ALIYUN_APP_KEY="your-app-key"
```

**Azure**
```bash
export AZURE_SPEECH_KEY="your-key"
export AZURE_SPEECH_REGION="your-region"
```

**Tencent Cloud (腾讯云)**
```bash
export TENCENT_SECRET_ID="your-id"
export TENCENT_SECRET_KEY="your-key"
export TENCENT_APP_ID="your-app-id"
```

#### Provider Priority

```bash
# Set provider priority (default: openai,azure,aliyun,tencent)
export TTS_PROVIDERS="aliyun,openai,azure,tencent"
export ASR_PROVIDERS="openai,aliyun,azure,tencent"
```

### Commands

#### Generate Video

```bash
openclaw-video-generator <script.txt> [options]
```

**Options:**
- `--voice <name>` - TTS voice (default: nova)
  - OpenAI: alloy, echo, nova, shimmer
  - Aliyun: Aibao, Aiqi, Aimei, Aida, etc.
- `--speed <number>` - TTS speed (0.25-4.0, default: 1.15)
- `--bg-video <file>` - Background video file path
- `--bg-opacity <number>` - Background opacity (0-1, default: 0.3)
- `--bg-overlay <color>` - Overlay color (default: rgba(10,10,15,0.6))

#### Examples

```bash
# Simple generation
openclaw-video-generator my-script.txt

# Custom voice and speed
openclaw-video-generator my-script.txt --voice Aibao --speed 1.2

# With background video
openclaw-video-generator my-script.txt \
  --voice nova \
  --bg-video backgrounds/tech/video.mp4 \
  --bg-opacity 0.4
```

### Output

The command generates:
- `audio/<name>.mp3` - TTS audio file
- `audio/<name>-timestamps.json` - Timestamp data
- `src/scenes-data.ts` - Scene configuration
- `out/<name>.mp4` - Final video (1080x1920, 30fps)

### Performance

- **Video generation time**: ~2 minutes for 20-second video
- **Resolution**: 1080x1920 (vertical/portrait)
- **Frame rate**: 30 fps
- **Bitrate**: ~4.6 Mbps
- **Rendering concurrency**: 6x

### Troubleshooting

#### Audio/Subtitle Sync Issues
✅ **Fixed in v1.3.1** - Now uses ffprobe for precise timestamp detection

#### Single Segment Display
✅ **Fixed in v1.3.1** - Smart segmentation generates multiple segments

#### Provider Failures
- Check API credentials in environment variables
- Verify provider priority settings
- System automatically falls back to next provider

### Links

- **GitHub**: https://github.com/ZhenRobotics/openclaw-video-generator
- **npm**: https://www.npmjs.com/package/openclaw-video-generator
- **Issues**: https://github.com/ZhenRobotics/openclaw-video-generator/issues
- **Documentation**: See GitHub repository for detailed docs

### License

MIT License - See LICENSE file for details

### Support

For issues or questions:
1. Check GitHub Issues
2. Read documentation in repository
3. Create new issue with details

---

## 中文版本

**[English](#english-version)** | 中文

多厂商 TTS/ASR 支持的自动化文本转视频系统。

### 版本

**当前版本**: v1.3.1 + 视觉优化
**最新提交**: 74661f1 (main 分支)
**发布日期**: 2026-03-11

### 最新功能

#### 最新改进（提交 74661f1）
- **优化默认背景参数**：可见度提升 +300%
- **背景视频默认清晰可见**：透明度从 0.3 提升到 0.7
- **改善文字清晰度**：保持可读性，对比度更好
- **无需手动配置**：开箱即用的最佳视觉质量

#### v1.3.1 重要 Bug 修复
- **修复阿里云 ASR 时间戳同步问题**：使用 ffprobe 将误差从 -75% 降至 0%
- **添加智能文本分段**：阿里云 ASR 从 1 个片段提升到 6+ 个片段
- **修复 OpenAI Whisper 数据格式问题**：修正 segments 提取
- **显著改善字幕显示效果**：字幕现在自然逐句显示

### 功能特性

- **多厂商 TTS/ASR 支持**：OpenAI、Azure、阿里云、腾讯云
- **自动降级机制**：提供商失败时自动切换
- **智能文本分段**：基于标点符号的智能分割
- **精确时间戳同步**：基于 ffprobe，0% 误差
- **背景视频支持**：自定义背景，可调透明度
- **赛博线框视觉效果**：炫酷动画和故障效果
- **全自动化流水线**：一条命令完成从文本到视频

### 快速开始

#### 安装

```bash
# 通过 npm 安装（推荐）
npm install -g openclaw-video-generator

# 或通过 ClawHub
clawhub install ZhenStaff/video-generator
```

#### 基础使用

```bash
# 从文本脚本生成视频
openclaw-video-generator script.txt --voice nova --speed 1.15

# 使用阿里云（推荐中国用户）
openclaw-video-generator script.txt --voice Aibao --speed 1.15

# 带背景视频
openclaw-video-generator script.txt \
  --voice Aibao \
  --bg-video background.mp4 \
  --bg-opacity 0.4
```

### 配置

#### 环境变量

**OpenAI（默认）**
```bash
export OPENAI_API_KEY="your-key"
```

**阿里云**
```bash
export ALIYUN_ACCESS_KEY_ID="your-id"
export ALIYUN_ACCESS_KEY_SECRET="your-secret"
export ALIYUN_APP_KEY="your-app-key"
```

**Azure**
```bash
export AZURE_SPEECH_KEY="your-key"
export AZURE_SPEECH_REGION="your-region"
```

**腾讯云**
```bash
export TENCENT_SECRET_ID="your-id"
export TENCENT_SECRET_KEY="your-key"
export TENCENT_APP_ID="your-app-id"
```

#### 提供商优先级

```bash
# 设置提供商优先级（默认：openai,azure,aliyun,tencent）
export TTS_PROVIDERS="aliyun,openai,azure,tencent"
export ASR_PROVIDERS="openai,aliyun,azure,tencent"
```

### 命令

#### 生成视频

```bash
openclaw-video-generator <script.txt> [选项]
```

**选项：**
- `--voice <名称>` - TTS 音色（默认：nova）
  - OpenAI: alloy, echo, nova, shimmer
  - 阿里云: Aibao, Aiqi, Aimei, Aida 等
- `--speed <数字>` - TTS 语速（0.25-4.0，默认：1.15）
- `--bg-video <文件>` - 背景视频文件路径
- `--bg-opacity <数字>` - 背景不透明度（0-1，默认：0.3）
- `--bg-overlay <颜色>` - 遮罩颜色（默认：rgba(10,10,15,0.6)）

#### 示例

```bash
# 简单生成
openclaw-video-generator my-script.txt

# 自定义音色和语速
openclaw-video-generator my-script.txt --voice Aibao --speed 1.2

# 带背景视频
openclaw-video-generator my-script.txt \
  --voice Aibao \
  --bg-video backgrounds/tech/video.mp4 \
  --bg-opacity 0.4
```

### 输出

命令生成：
- `audio/<名称>.mp3` - TTS 音频文件
- `audio/<名称>-timestamps.json` - 时间戳数据
- `src/scenes-data.ts` - 场景配置
- `out/<名称>.mp4` - 最终视频（1080x1920，30fps）

### 性能

- **视频生成时间**：20 秒视频约 2 分钟
- **分辨率**：1080x1920（竖屏）
- **帧率**：30 fps
- **比特率**：~4.6 Mbps
- **渲染并发**：6x

### 故障排除

#### 音频/字幕不同步问题
✅ **已在 v1.3.1 修复** - 现在使用 ffprobe 精确时间戳检测

#### 单片段显示
✅ **已在 v1.3.1 修复** - 智能分段生成多个片段

#### 提供商失败
- 检查环境变量中的 API 凭证
- 验证提供商优先级设置
- 系统会自动降级到下一个提供商

### 链接

- **GitHub**: https://github.com/ZhenRobotics/openclaw-video-generator
- **npm**: https://www.npmjs.com/package/openclaw-video-generator
- **问题反馈**: https://github.com/ZhenRobotics/openclaw-video-generator/issues
- **文档**: 详细文档见 GitHub 仓库

### 许可证

MIT License - 详见 LICENSE 文件

### 支持

如有问题或疑问：
1. 查看 GitHub Issues
2. 阅读仓库中的文档
3. 创建新 issue 并提供详细信息

---

**Version | 版本**: v1.3.1
**Last Updated | 最后更新**: 2026-03-11
**Maintainer | 维护者**: ZhenStaff
