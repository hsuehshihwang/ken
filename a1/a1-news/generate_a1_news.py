#!/usr/bin/env python3
"""
Generate audio for A1 simplified news articles using Edge TTS.
Creates audio for full article and individual sentences.
"""
import asyncio
import json
import os
import sys

try:
    import edge_tts
except ImportError:
    print("Installing edge-tts...")
    os.system(f"{sys.executable} -m pip install edge-tts -q")
    import edge_tts


# Voice configuration - slow and clear for A1 learners
VOICE = "en-US-JennyNeural"
RATE = "-15%"  # Slower than normal for A1


async def generate_audio(text, output_file, rate=RATE):
    """Generate audio file from text using Edge TTS."""
    try:
        communicate = edge_tts.Communicate(text, VOICE, rate=rate)
        await communicate.save(output_file)
        return True
    except Exception as e:
        print(f"    Error generating audio: {e}")
        return False


async def process_article(article, audio_dir):
    """Process a single article - generate audio for full article and each sentence."""
    article_id = article['id']
    sentences = article.get('sentences', [])
    
    if not sentences:
        print(f"  No sentences found for {article_id}")
        return False
    
    # Create article audio directory
    article_dir = os.path.join(audio_dir, article_id)
    os.makedirs(article_dir, exist_ok=True)
    
    # Generate full article audio (join all sentences with pauses)
    full_text = ' ... '.join(sentences)  # Use ellipsis for natural pause
    full_audio = os.path.join(article_dir, 'full.mp3')
    
    print(f"    Generating full article audio ({len(full_text)} chars)...")
    if not await generate_audio(full_text, full_audio):
        return False
    
    # Generate audio for each sentence
    sentence_files = []
    for i, sentence in enumerate(sentences):
        sentence_file = os.path.join(article_dir, f'sentence_{i+1:02d}.mp3')
        print(f"    Sentence {i+1}/{len(sentences)}...")
        
        if not await generate_audio(sentence, sentence_file, rate="-10%"):
            print(f"      Failed to generate sentence {i+1}")
            continue
        
        sentence_files.append(f'{article_id}/sentence_{i+1:02d}.mp3')
    
    # Update article with audio file paths (relative to article.html)
    article['audio_file'] = f'audio/{article_id}/full.mp3'
    article['sentence_files'] = [f'audio/{f}' for f in sentence_files]
    
    return True


async def main():
    # Check for a1-news.json
    if not os.path.exists('a1-news.json'):
        print("Error: a1-news.json not found!")
        print("Run fetch_a1_news.py first to download and simplify articles.")
        return
    
    # Load news data
    with open('a1-news.json', 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    articles = news_data.get('articles', [])
    if not articles:
        print("No articles found in a1-news.json")
        return
    
    print(f"Found {len(articles)} articles to process")
    print(f"Voice: {VOICE}")
    print(f"Rate: {RATE}")
    
    # Create audio directory
    audio_dir = 'audio'
    os.makedirs(audio_dir, exist_ok=True)
    
    # Process each article
    success_count = 0
    for i, article in enumerate(articles):
        print(f"\n[{i+1}/{len(articles)}] {article['title']}")
        
        if await process_article(article, audio_dir):
            success_count += 1
    
    # Save updated a1-news.json with audio paths
    with open('a1-news.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Generated audio for {success_count}/{len(articles)} articles")
    print(f"Audio files saved to: {audio_dir}/")
    print(f"Updated a1-news.json with audio paths")


if __name__ == '__main__':
    asyncio.run(main())
