#!/usr/bin/env python3
"""
PDF Image OCR - 使用 PyMuPDF + MiniMax Vision AI 进行高准确率 PDF OCR
"""
import sys
import os
import argparse
import fitz  # PyMuPDF
from datetime import datetime

class PDFImageOCR:
    def __init__(self, dpi=300):
        self.dpi = dpi
        self.temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def pdf_to_images(self, pdf_path, dpi=300):
        """将 PDF 转换为图片"""
        images = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=dpi)
            img_path = os.path.join(self.temp_dir, f'page_{page_num+1}.png')
            pix.save(img_path)
            images.append({'page': page_num + 1, 'path': img_path})
        
        doc.close()
        return images
    
    def process_pdf(self, pdf_path, dpi=None):
        """处理 PDF 并返回 OCR 结果"""
        if dpi is None:
            dpi = self.dpi
        
        if not os.path.exists(pdf_path):
            return {'error': f'File not found: {pdf_path}'}
        
        # 转换为图片
        images = self.pdf_to_images(pdf_path, dpi)
        
        # 返回处理信息（实际 OCR 由 MiniMax Vision AI 完成）
        return {
            'pdf_path': pdf_path,
            'page_count': len(images),
            'images': images,
            'dpi': dpi,
            'method': 'PyMuPDF + MiniMax Vision AI',
            'usage': 'Use image tool to OCR each image: ' + 
                     ', '.join([img['path'] for img in images])
        }
    
    def cleanup(self):
        """清理临时图片"""
        import glob
        for f in glob.glob(os.path.join(self.temp_dir, 'page_*.png')):
            os.remove(f)

def main():
    parser = argparse.ArgumentParser(description='PDF to Image OCR')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--dpi', '-d', type=int, default=300, help='Image DPI (default: 300)')
    parser.add_argument('--cleanup', '-c', action='store_true', help='Clean up temp images after')
    
    args = parser.parse_args()
    
    ocr = PDFImageOCR(dpi=args.dpi)
    result = ocr.process_pdf(args.pdf_path)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print(f"=== PDF Image OCR Results ===")
    print(f"PDF: {result['pdf_path']}")
    print(f"Pages: {result['page_count']}")
    print(f"DPI: {result['dpi']}")
    print(f"Method: {result['method']}")
    print(f"\nGenerated Images:")
    for img in result['images']:
        print(f"  Page {img['page']}: {img['path']}")
    print(f"\n⚠️  Use image tool to OCR each image for 100% accuracy")
    print(f"   Prompt: 'Extract all text from this image exactly as shown'")
    
    if args.cleanup:
        ocr.cleanup()
        print("\n✓ Temp images cleaned up")

if __name__ == '__main__':
    main()
