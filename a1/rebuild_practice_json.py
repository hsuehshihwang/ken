#!/usr/bin/env python3
"""Rebuild practice_structure.json from existing audio files."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from generate_practice import PRACTICE_TOPICS, SENTENCE_VOICES

output_dir = Path("audio")
all_results = {}

for topic_id, topic_data in PRACTICE_TOPICS.items():
    topic_dir = output_dir / topic_id
    
    if not topic_dir.exists():
        print(f"SKIP {topic_id}: directory not found")
        continue
    
    # Check sentences
    sentence_files = []
    for i in range(1, 51):
        sfile = topic_dir / f"sentence_{i:02d}.mp3"
        if sfile.exists():
            voice = SENTENCE_VOICES[(i-1) % len(SENTENCE_VOICES)]
            sentence_files.append({
                "text": topic_data["sentences"][i-1] if i <= len(topic_data["sentences"]) else f"Sentence {i}",
                "file": f"{topic_id}/sentence_{i:02d}.mp3",
                "voice": voice
            })
    
    # Check dialogues
    dialogue_files = []
    for i in range(1, 11):
        dfile = topic_dir / f"dialogue_{i:02d}.mp3"
        if dfile.exists() and i <= len(topic_data["dialogues"]):
            dialogue_files.append({
                "lines": topic_data["dialogues"][i-1]["lines"],
                "file": f"{topic_id}/dialogue_{i:02d}.mp3"
            })
    
    all_results[topic_id] = {
        "name": topic_data["name"],
        "sentences": sentence_files,
        "dialogues": dialogue_files
    }
    
    print(f"{topic_id}: {len(sentence_files)} sentences, {len(dialogue_files)} dialogues")

# Save
with open(output_dir / "practice_structure.json", 'w') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

# Save topics list
topics_list = [{"id": k, "name": v["name"]} for k, v in PRACTICE_TOPICS.items()]
with open(output_dir / "practice_topics.json", 'w') as f:
    json.dump(topics_list, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(all_results)} topics to practice_structure.json")
