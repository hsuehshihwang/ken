#!/usr/bin/env python3
"""
Generate audio from a custom text file.
Format:
  ---sentence---
  Your sentence here.
  
  ---dialogue---
  Person A: Hello
  Person B: Hi there
  
  ---question---
  Question: What is this?
  Answer: It is a book.
  Options: Book, Pen, Phone
"""

import asyncio
import json
import re
import sys
from pathlib import Path

# Import from main module
from generate_test import AudioGenerator


def parse_text_file(filepath: str) -> dict:
    """Parse a formatted text file into content structure."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {
        "name": Path(filepath).stem,
        "sentences": [],
        "dialogues": [],
        "questions": []
    }
    
    # Split by markers
    sections = re.split(r'---(\w+)---', content)
    
    current_type = None
    current_block = []
    
    for section in sections:
        section = section.strip()
        if section in ['sentence', 'dialogue', 'question']:
            current_type = section
            current_block = []
        elif current_type and section:
            lines = [l.strip() for l in section.split('\n') if l.strip()]
            
            if current_type == 'sentence':
                result["sentences"].extend(lines)
            
            elif current_type == 'dialogue':
                if lines:
                    result["dialogues"].append(lines)
            
            elif current_type == 'question':
                # Parse question block
                question_data = {"question": "", "answer": "", "options": []}
                for line in lines:
                    if line.lower().startswith("question:"):
                        question_data["question"] = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("answer:"):
                        question_data["answer"] = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("options:"):
                        opts = line.split(":", 1)[1].strip()
                        question_data["options"] = [o.strip() for o in opts.split(",")]
                
                if question_data["question"]:
                    result["questions"].append(question_data)
    
    return result


async def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_from_file.py <text_file> [output_dir]")
        print("\nText file format:")
        print("  ---sentence---")
        print("  Your sentence here.")
        print("  ---dialogue---")
        print("  Person A: Hello")
        print("  Person B: Hi there")
        print("  ---question---")
        print("  Question: What is this?")
        print("  Answer: A book.")
        print("  Options: Book, Pen, Phone")
        return
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "audio"
    
    print(f"Reading content from: {input_file}")
    content = parse_text_file(input_file)
    
    print(f"\nParsed content:")
    print(f"  Sentences: {len(content['sentences'])}")
    print(f"  Dialogues: {len(content['dialogues'])}")
    print(f"  Questions: {len(content['questions'])}")
    
    print(f"\nGenerating audio to: {output_dir}/")
    audio_gen = AudioGenerator(output_dir)
    files = await audio_gen.generate_from_content(content, "custom")
    
    print(f"\nDone! Generated {len(files)} audio files.")


if __name__ == "__main__":
    asyncio.run(main())
