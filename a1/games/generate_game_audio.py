#!/usr/bin/env python3
"""
Generate audio for game introduction content using Edge TTS.
Reads JSON files and creates MP3 files for each article.
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


# Voice configuration
VOICE = "en-US-JennyNeural"
RATE = "-15%"


async def generate_audio(text, output_file, rate=RATE):
    """Generate audio file from text using Edge TTS."""
    try:
        communicate = edge_tts.Communicate(text, VOICE, rate=rate)
        await communicate.save(output_file)
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False


async def process_section(section, audio_dir):
    """Process a single section - generate audio for full text and each sentence."""
    section_id = section['id']
    sentences = section.get('sentences', [])
    
    if not sentences:
        print(f"  No sentences for {section_id}")
        return False
    
    # Create section audio directory
    section_dir = os.path.join(audio_dir, section_id)
    os.makedirs(section_dir, exist_ok=True)
    
    # Generate full section audio
    full_text = ' ... '.join(sentences)
    full_audio = os.path.join(section_dir, 'full.mp3')
    
    print(f"    Full audio ({len(full_text)} chars)...")
    if not await generate_audio(full_text, full_audio):
        return False
    
    # Generate audio for each sentence
    sentence_files = []
    for i, sentence in enumerate(sentences):
        sentence_file = os.path.join(section_dir, f'sentence_{i+1:02d}.mp3')
        print(f"    Sentence {i+1}/{len(sentences)}...")
        
        if not await generate_audio(sentence, sentence_file, rate="-10%"):
            print(f"      Failed")
            continue
        
        sentence_files.append(f'audio/{section_id}/sentence_{i+1:02d}.mp3')
    
    # Update section with audio paths
    section['audio_file'] = f'audio/{section_id}/full.mp3'
    section['sentence_files'] = sentence_files
    
    return True


async def process_game(game_dir, game_name):
    """Process all sections for a game."""
    print(f"\n{'='*60}")
    print(f"Processing: {game_name}")
    print(f"Directory: {game_dir}")
    
    # Find all JSON files (except game data)
    json_files = []
    for f in os.listdir(game_dir):
        if f.endswith('.json') and f not in ['game-data.json']:
            json_files.append(f)
    
    if not json_files:
        print("No JSON content files found")
        return
    
    for json_file in sorted(json_files):
        json_path = os.path.join(game_dir, json_file)
        print(f"\n  File: {json_file}")
        
        # Load JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Find sections to process
        sections = []
        if 'sections' in data:
            sections = data['sections']
        elif 'heroes' in data:
            sections = data['heroes']
        elif 'mobs' in data:
            sections = data['mobs']
        
        if not sections:
            print("    No sections found")
            continue
        
        print(f"  Found {len(sections)} sections")
        
        # Process each section
        audio_dir = os.path.join(game_dir, 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        
        success_count = 0
        for i, section in enumerate(sections):
            print(f"\n  [{i+1}/{len(sections)}] {section.get('name', section.get('title', 'Unknown'))}")
            
            if await process_section(section, audio_dir):
                success_count += 1
        
        # Save updated JSON with audio paths
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n  Generated audio for {success_count}/{len(sections)} sections")


async def main():
    games_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Process each game
    games = [
        ('brawl-stars', 'Brawl Stars'),
        ('minecraft', 'Minecraft')
    ]
    
    for game_dir_name, game_name in games:
        game_path = os.path.join(games_dir, game_dir_name)
        
        if not os.path.exists(game_path):
            print(f"Skipping {game_name} - directory not found")
            continue
        
        await process_game(game_path, game_name)
    
    print(f"\n{'='*60}")
    print("All games processed!")


if __name__ == '__main__':
    asyncio.run(main())
