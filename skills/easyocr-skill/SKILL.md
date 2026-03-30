---
name: easyocr-skill
description: High-accuracy OCR using EasyOCR library. Supports 80+ languages including Chinese (simplified/traditional), English, and mixed-language documents. Better than Tesseract for multilingual OCR.
version: 1.0.0
---

# EasyOCR Skill

使用 EasyOCR 库进行高准确率 OCR 识别，支持 80+ 语言。

## 支持语言

- 中文（简体/繁体）
- 英文
- 日文、韩文等
- 混合语言文档

## 安装依赖

```bash
pip install easyocr
```

## 使用方法

```python
import easyocr

reader = easyocr.Reader(['ch_sim', 'en'])
result = reader.readtext('image.png')
for detection in result:
    print(detection[1])  # 识别的文字
```

## 命令行使用

```bash
python3 scripts/easyocr_cli.py <image_path> [--lang chi_sim+eng]
```
