#!/usr/bin/env python3
"""
Word count tool for MBA thesis analysis
"""

import sys
import os
import re
from pathlib import Path

def count_words(text):
    """Count words in text (Chinese and English)"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Count Chinese characters (each char counts as 1 word)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    # Count English words
    english_words = len(re.findall(r'[a-zA-Z\']+', text))
    
    # Count numbers and other characters as part of words
    other_words = len(re.findall(r'[0-9]+', text))
    
    total_words = chinese_chars + english_words + other_words
    
    return {
        'chinese_chars': chinese_chars,
        'english_words': english_words,
        'other_words': other_words,
        'total_words': total_words
    }

def analyze_file(filepath):
    """Analyze file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='gbk') as f:
                content = f.read()
        except:
            return None
    
    # Count words
    word_counts = count_words(content)
    
    # Count paragraphs
    paragraphs = [p for p in content.split('\n\n') if p.strip()]
    
    # Count sentences (simple approximation)
    sentences = len(re.findall(r'[。！？.!?]', content))
    
    return {
        'filename': os.path.basename(filepath),
        'word_counts': word_counts,
        'paragraphs': len(paragraphs),
        'sentences': sentences,
        'avg_sentence_length': word_counts['total_words'] / max(sentences, 1)
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python word_count.py <file1> [file2 ...]")
        sys.exit(1)
    
    print("MBA Thesis Word Count Analysis")
    print("=" * 50)
    
    for filepath in sys.argv[1:]:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
        
        result = analyze_file(filepath)
        if result is None:
            print(f"Cannot read file: {filepath}")
            continue
        
        print(f"\nFile: {result['filename']}")
        print(f"  Total words: {result['word_counts']['total_words']}")
        print(f"  Chinese characters: {result['word_counts']['chinese_chars']}")
        print(f"  English words: {result['word_counts']['english_words']}")
        print(f"  Paragraphs: {result['paragraphs']}")
        print(f"  Sentences: {result['sentences']}")
        print(f"  Avg words per sentence: {result['avg_sentence_length']:.1f}")
        
        # Provide recommendations
        total_words = result['word_counts']['total_words']
        if total_words < 20000:
            print("  ⚠️  Warning: Thesis may be too short (typical MBA thesis: 20,000-50,000 words)")
        elif total_words > 80000:
            print("  ⚠️  Warning: Thesis may be too long (typical MBA thesis: 20,000-50,000 words)")
        
        avg_length = result['avg_sentence_length']
        if avg_length > 30:
            print("  ⚠️  Suggestion: Some sentences may be too long (aim for 15-25 words per sentence)")
        elif avg_length < 10:
            print("  ⚠️  Suggestion: Some sentences may be too short (aim for 15-25 words per sentence)")

if __name__ == "__main__":
    main()