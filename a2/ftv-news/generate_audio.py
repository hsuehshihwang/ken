#!/usr/bin/env python3
"""
Generate TTS audio for A2 Taiwan News sentences.
Uses Edge TTS with multiple voices for variety.

Usage:
  python generate_audio.py                    # Generate audio for current date
  python generate_audio.py 2026-07-15         # Generate audio for specific date
  python generate_audio.py --all              # Generate audio for all dates
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

VOICES = [
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-BrianNeural",
    "en-US-AnaNeural",
    "en-US-ChristopherNeural",
    "en-US-AvaNeural",
]


async def generate_audio(text, voice, output_path):
    """Generate audio for a single sentence."""
    import edge_tts
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))
        return True
    except Exception as e:
        print(f"  Error generating audio: {e}")
        return False


async def generate_news_audio(date_str=None):
    """Generate audio for news articles."""
    script_dir = Path(__file__).parent
    
    if date_str:
        news_dir = script_dir / date_str
        news_file = news_dir / "news.json"
        
        if not news_file.exists():
            print(f"Error: {news_file} not found!")
            return
        
        audio_dir = news_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        await generate_date_audio(news_file, audio_dir)
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        news_dir = script_dir / today
        news_file = news_dir / "news.json"
        
        if not news_file.exists():
            print(f"Error: {news_file} not found!")
            print("Create news data first or specify a date.")
            return
        
        audio_dir = news_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        await generate_date_audio(news_file, audio_dir)


async def generate_all_audio():
    """Generate audio for all dates."""
    script_dir = Path(__file__).parent
    dates_file = script_dir / "dates.json"
    
    if not dates_file.exists():
        print("Error: dates.json not found!")
        return
    
    with open(dates_file, 'r') as f:
        dates = json.load(f)
    
    for date_str in sorted(dates):
        news_dir = script_dir / date_str
        news_file = news_dir / "news.json"
        
        if not news_file.exists():
            print(f"Skipping {date_str} - no news.json found")
            continue
        
        print(f"\n{'='*50}")
        print(f"Processing: {date_str}")
        print(f"{'='*50}")
        
        audio_dir = news_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        await generate_date_audio(news_file, audio_dir)


async def generate_date_audio(news_file, audio_dir):
    """Generate audio for a single date's news."""
    with open(news_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"Generating audio for {len(articles)} articles...\n")
    
    for article in articles:
        article_id = article['id']
        print(f"Article: {article['title']}")
        
        audio_files = []
        for i, sentence in enumerate(article['sentences'], 1):
            voice = VOICES[(i - 1) % len(VOICES)]
            filename = f"{article_id}_s{i:02d}.mp3"
            filepath = audio_dir / filename
            
            if filepath.exists():
                print(f"  [{i}/{len(article['sentences'])}] Already exists: {filename}")
                audio_files.append(f"audio/{filename}")
                continue
            
            voice_name = voice.split('-')[-1].replace('Neural', '')
            print(f"  [{i}/{len(article['sentences'])}] Generating with {voice_name}...")
            
            success = await generate_audio(sentence, voice, filepath)
            if success:
                audio_files.append(f"audio/{filename}")
            else:
                audio_files.append(None)
        
        article['audio_files'] = audio_files
        print()
    
    with open(news_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"Audio generation complete!")
    print(f"Audio files saved to: {audio_dir}")


async def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            await generate_all_audio()
        else:
            await generate_news_audio(sys.argv[1])
    else:
        await generate_news_audio()


if __name__ == "__main__":
    asyncio.run(main())
