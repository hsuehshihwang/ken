#!/usr/bin/env python3
"""Generate a complete A1 test with all topics."""

import asyncio
from generate_test import TestGenerator


async def main():
    topics = [
        "greetings",
        "family", 
        "food",
        "daily_routine",
        "shopping",
        "travel",
        "weather",
        "health"
    ]
    
    generator = TestGenerator("audio/complete_test")
    
    print("=" * 60)
    print("GENERATING COMPLETE A1 ENGLISH LISTENING TEST")
    print("=" * 60)
    print(f"\nTopics: {len(topics)}")
    print("Using: Edge TTS (free Microsoft voices)")
    print()
    
    await generator.generate_test(topics)
    
    print("\n" + "=" * 60)
    print("COMPLETE TEST GENERATED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
