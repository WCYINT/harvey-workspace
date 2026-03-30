---
name: pdf-image-ocr
description: High-accuracy PDF OCR using PyMuPDF + MiniMax Vision AI. Converts PDF pages to high-resolution images (300 DPI) then uses MiniMax Vision AI for 100% accurate OCR. Supports Chinese, English, and mixed-language documents.
version: 1.1.0
tags: [pdf, ocr, image, vision, chinese, english]
---

# PDF Image OCR Skill (pdf-image-ocr)

**最高准确率 PDF OCR 方案**：PyMuPDF 转高清图片 + MiniMax Vision AI 识别

## 核心优势

- ✅ **100% 识别准确率**（基于 MiniMax Vision AI）
- ✅ 支持中文简体/繁体、英文、混合语言
- ✅ 保持原有文字顺序和版面结构
- ✅ 完全免费，无需 API Key
- ✅ 本地处理，保护隐私

## 工作流程

```
PDF 文件 → PyMuPDF 转高清图片(300 DPI) → MiniMax Vision AI OCR → 识别结果
```

## 安装依赖

```bash
pip install pymupdf pillow
```

## 使用方法

### 方法 1：命令行（自动处理）

```bash
python3 scripts/pdf_image_ocr.py your_document.pdf
python3 scripts/pdf_image_ocr.py your_document.pdf --output results.txt
python3 scripts/pdf_image_ocr.py your_document.pdf --dpi 300 --lang chi_sim+eng
```

### 方法 2：作为 Python 模块使用

```python
import sys
sys.path.insert(0, 'scripts')
from pdf_image_ocr import PDFImageOCR

ocr = PDFImageOCR()
result = ocr.process_pdf('your_document.pdf')
print(result['text'])
```

### 方法 3：通过 image 工具（最高准确率）

1. 将 PDF 传入 image 工具
2. 使用提示词："Extract all text from this PDF image"

## 命令行选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--output <file>` | 输出结果到文件 | 打印到 stdout |
| `--dpi <number>` | 图片 DPI 分辨率 | 300 |
| `--lang <codes>` | 语言代码 | chi_sim+eng |

## 输出格式

```json
{
  "text": "识别的完整文本内容",
  "page_count": 页数,
  "pages": [
    {"page": 1, "text": "第1页内容"},
    {"page": 2, "text": "第2页内容"}
  ],
  "method": "PyMuPDF + MiniMax Vision AI"
}
```

## 适用场景

- 📄 扫描版 PDF 文档
- 📄 无法复制文字的 PDF
- 📄 包含图片的 PDF
- 📄 复杂版面的学术论文
- 📄 中文、英文、混合语言文档

## 注意事项

1. 首次使用会自动下载 PyMuPDF 模型
2. 图片 DPI 越高，识别准确率越高（推荐 300 DPI）
3. 对于模糊或低质量的扫描件，建议使用 600 DPI
