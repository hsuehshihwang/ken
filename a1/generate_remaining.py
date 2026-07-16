#!/usr/bin/env python3
"""Generate remaining practice audio for missing topics."""
import asyncio
import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_practice import PRACTICE_TOPICS, SENTENCE_VOICES, DIALOGUE_VOICES

async def generate_sentence(output_dir, topic_id, num, text, voice):
    import edge_tts
    filename = f"sentence_{num:02d}.mp3"
    filepath = output_dir / topic_id / filename
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(filepath))
        print(f"  sentence {num}/50 [{voice.split('-')[-1].replace('Neural','')}]")
        return {"text": text, "file": f"{topic_id}/{filename}", "voice": voice}
    except Exception as e:
        print(f"  ERROR sentence {num}: {e}")
        return None

async def generate_dialogue(output_dir, topic_id, num, lines):
    import edge_tts
    filename = f"dialogue_{num:02d}.mp3"
    filepath = output_dir / topic_id / filename
    temp_files = []
    try:
        for i, line in enumerate(lines):
            tf = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            temp_files.append(tf.name)
            if line.startswith("Person A:"):
                voice = DIALOGUE_VOICES["A"]
                text = line.replace("Person A:", "").strip()
            else:
                voice = DIALOGUE_VOICES["B"]
                text = line.replace("Person B:", "").strip()
            comm = edge_tts.Communicate(text, voice)
            await comm.save(tf.name)
        
        concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        for tf in temp_files:
            concat_file.write(f"file '{tf}'\n")
        concat_file.close()
        
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file.name, "-c", "copy", str(filepath)
        ], capture_output=True, check=True, timeout=30)
        
        os.unlink(concat_file.name)
        for tf in temp_files:
            os.unlink(tf)
        
        print(f"  dialogue {num}/10")
        return {"lines": lines, "file": f"{topic_id}/{filename}"}
    except Exception as e:
        print(f"  ERROR dialogue {num}: {e}")
        for f in temp_files:
            if os.path.exists(f): os.unlink(f)
        return None

async def main():
    topics_to_do = sys.argv[1:] if len(sys.argv) > 1 else []
    if not topics_to_do:
        # Find missing topics
        for tid in PRACTICE_TOPICS:
            sfile = Path(f"audio/{tid}/sentence_50.mp3")
            dfile = Path(f"audio/{tid}/dialogue_10.mp3")
            if not sfile.exists() or not dfile.exists():
                topics_to_do.append(tid)
    
    if not topics_to_do:
        print("All topics already generated!")
        return
    
    print(f"Generating: {', '.join(topics_to_do)}")
    
    output_dir = Path("audio")
    all_results = {}
    
    for topic_id in topics_to_do:
        topic = PRACTICE_TOPICS[topic_id]
        topic_dir = output_dir / topic_id
        topic_dir.mkdir(exist_ok=True)
        
        print(f"\n{'='*50}")
        print(f"Topic: {topic['name']}")
        print(f"{'='*50}")
        
        # Sentences
        sentence_files = []
        for i, sentence in enumerate(topic["sentences"], 1):
            sfile = topic_dir / f"sentence_{i:02d}.mp3"
            if sfile.exists():
                voice = SENTENCE_VOICES[(i-1) % len(SENTENCE_VOICES)]
                sentence_files.append({"text": sentence, "file": f"{topic_id}/sentence_{i:02d}.mp3", "voice": voice})
                continue
            voice = SENTENCE_VOICES[(i-1) % len(SENTENCE_VOICES)]
            result = await generate_sentence(output_dir, topic_id, i, sentence, voice)
            if result:
                sentence_files.append(result)
        
        # Dialogues
        dialogue_files = []
        for i, dialogue in enumerate(topic["dialogues"], 1):
            dfile = topic_dir / f"dialogue_{i:02d}.mp3"
            if dfile.exists():
                dialogue_files.append({"lines": dialogue["lines"], "file": f"{topic_id}/dialogue_{i:02d}.mp3"})
                continue
            result = await generate_dialogue(output_dir, topic_id, i, dialogue["lines"])
            if result:
                dialogue_files.append(result)
        
        all_results[topic_id] = {
            "name": topic["name"],
            "sentences": sentence_files,
            "dialogues": dialogue_files
        }
    
    # Merge with existing
    existing = {}
    sf = output_dir / "practice_structure.json"
    if sf.exists():
        with open(sf) as f:
            existing = json.load(f)
    existing.update(all_results)
    
    with open(sf, 'w') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    
    topics_list = [{"id": k, "name": v["name"]} for k, v in PRACTICE_TOPICS.items()]
    with open(output_dir / "practice_topics.json", 'w') as f:
        json.dump(topics_list, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Saved to {sf}")

asyncio.run(main())
