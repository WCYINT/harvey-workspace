#!/usr/bin/env python3
"""EasyOCR CLI for image text recognition"""
import sys
import easyocr

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 easyocr_cli.py <image_path> [--lang chi_sim+eng]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    lang = 'ch_sim+eng'
    
    for arg in sys.argv[2:]:
        if arg.startswith('--lang='):
            lang = arg.split('=')[1]
    
    langs = lang.split('+')
    
    print(f"Initializing EasyOCR with languages: {langs}...")
    reader = easyocr.Reader(langs, gpu=False)
    
    print(f"Recognizing text from: {image_path}")
    result = reader.readtext(image_path)
    
    print("\n=== Recognition Results ===")
    full_text = []
    for detection in result:
        bbox, text, confidence = detection
        full_text.append(text)
        print(f"  {text} (confidence: {confidence:.2f})")
    
    print("\n=== Full Text ===")
    print(' '.join(full_text))

if __name__ == '__main__':
    main()
