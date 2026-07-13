#!/usr/bin/env python3
"""
Story Audio Generator
Generates audio files for stories using Edge TTS (free).
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Voice configuration for stories
VOICES = {
    "narrator": "en-US-JennyNeural",      # Female narrator
    "female": "en-US-JennyNeural",         # Female characters (Mother)
    "male1": "en-US-GuyNeural",            # Pig 1 (Male)
    "male2": "en-US-BrianNeural",          # Pig 2 (Different male)
    "male3": "en-US-ChristopherNeural",    # Pig 3 (Another male)
    "wolf": "en-US-EricNeural",            # Wolf (Deep male voice)
    "default": "en-US-AnaNeural"
}

# Voice rate adjustments (slower for A1 level)
VOICE_RATES = {
    "narrator": "-5%",
    "female": "-5%",
    "male1": "-5%",
    "male2": "-5%",
    "male3": "-5%",
    "wolf": "-10%",
    "default": "-5%"
}


async def generate_audio(text: str, output_path: str, voice: str = "en-US-JennyNeural", rate: str = "-5%") -> bool:
    """Generate audio using Edge TTS."""
    import edge_tts
    
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def get_voice_for_speaker(speaker: str) -> tuple:
    """Get voice and rate for a speaker."""
    speaker_lower = speaker.lower()
    
    if "narrator" in speaker_lower:
        return VOICES["narrator"], VOICE_RATES["narrator"]
    elif "wolf" in speaker_lower:
        return VOICES["wolf"], VOICE_RATES["wolf"]
    elif "mother" in speaker_lower:
        return VOICES["female"], VOICE_RATES["female"]
    elif "pig 1" in speaker_lower or "pig1" in speaker_lower:
        return VOICES["male1"], VOICE_RATES["male1"]
    elif "pig 2" in speaker_lower or "pig2" in speaker_lower:
        return VOICES["male2"], VOICE_RATES["male2"]
    elif "pig 3" in speaker_lower or "pig3" in speaker_lower:
        return VOICES["male3"], VOICE_RATES["male3"]
    
    # Check voice field in dialogue
    return VOICES["default"], VOICE_RATES["default"]


async def generate_scene_audio(scene: dict, output_dir: Path, scene_num: int) -> list:
    """Generate audio for a single scene."""
    import tempfile
    import os
    
    generated_files = []
    temp_files = []
    
    # Create temp directory for scene components
    with tempfile.TemporaryDirectory() as temp_dir:
        file_index = 0
        
        # Generate narrator audio
        if scene.get("narrator"):
            narrator_text = scene["narrator"]
            temp_path = os.path.join(temp_dir, f"narrator.mp3")
            voice, rate = get_voice_for_speaker("narrator")
            
            print(f"    Generating narrator...")
            if await generate_audio(narrator_text, temp_path, voice, rate):
                temp_files.append(temp_path)
                file_index += 1
        
        # Generate dialogue audio
        for i, line in enumerate(scene.get("dialogue", [])):
            speaker = line.get("speaker", "Unknown")
            text = line.get("line", "")
            voice_key = line.get("voice", "default")
            
            voice = VOICES.get(voice_key, VOICES["default"])
            rate = VOICE_RATES.get(voice_key, VOICE_RATES["default"])
            
            temp_path = os.path.join(temp_dir, f"line_{i:02d}.mp3")
            
            print(f"    Generating {speaker}...")
            if await generate_audio(text, temp_path, voice, rate):
                temp_files.append(temp_path)
                file_index += 1
        
        # Concatenate all audio files into one scene file
        if temp_files:
            scene_filename = f"scene_{scene_num:02d}.mp3"
            scene_path = output_dir / scene_filename
            
            print(f"    Combining into {scene_filename}...")
            with open(scene_path, 'wb') as outfile:
                for temp_file in temp_files:
                    with open(temp_file, 'rb') as infile:
                        outfile.write(infile.read())
            
            generated_files.append({
                "file": scene_filename,
                "scene": scene_num,
                "title": scene.get("title", f"Scene {scene_num}")
            })
    
    return generated_files


async def generate_story(story_path: str):
    """Generate audio for an entire story."""
    story_path = Path(story_path)
    
    # Read story JSON
    with open(story_path, 'r', encoding='utf-8') as f:
        story = json.load(f)
    
    print(f"\n{'='*60}")
    print(f"Story: {story['title']}")
    print(f"Level: {story['level']}")
    print(f"Scenes: {len(story['scenes'])}")
    print(f"{'='*60}\n")
    
    # Create audio output directory
    audio_dir = story_path.parent / "audio"
    audio_dir.mkdir(exist_ok=True)
    
    generated_files = []
    
    for scene in story['scenes']:
        scene_num = scene['id']
        print(f"Scene {scene_num}: {scene.get('title', 'Untitled')}")
        
        files = await generate_scene_audio(scene, audio_dir, scene_num)
        generated_files.extend(files)
    
    # Save index file
    index_path = audio_dir / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(generated_files, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Story generation complete!")
    print(f"Audio files saved to: {audio_dir}")
    print(f"Total files: {len(generated_files)}")
    print(f"{'='*60}\n")
    
    return generated_files


async def main():
    if len(sys.argv) < 2:
        print("\nStory Audio Generator")
        print("=" * 40)
        print("\nUsage:")
        print("  python generate_story.py <story.json>")
        print("  python generate_story.py topic/story/three-little-pigs/story.json")
        return
    
    story_path = sys.argv[1]
    
    if not os.path.exists(story_path):
        print(f"Error: Story file not found: {story_path}")
        return
    
    await generate_story(story_path)


if __name__ == "__main__":
    asyncio.run(main())
