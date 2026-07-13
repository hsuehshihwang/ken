# A1 English Listening Test Generator

Generate audio files for A1 (beginner) English listening tests using text-to-speech.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate from built-in topics
python generate_test.py greetings family food

# Generate all 14 topics
python generate_test.py --all

# Generate from custom text file
python generate_from_file.py content/sample_greetings.txt
```

## Available Topics (14)

| Topic | Description |
|-------|-------------|
| greetings | Greetings & Introductions |
| family | Family members |
| food | Food & Drinks |
| daily_routine | Daily Routine |
| shopping | Shopping |
| travel | Travel & Directions |
| weather | Weather |
| health | Health & Doctor |
| numbers | Numbers & Counting |
| colors | Colors |
| time | Time & Schedules |
| work | Work & Jobs |
| hobbies | Hobbies & Free Time |
| animals | Animals & Pets |

## Features

### Two-Voice Dialogues
- **Male voice (Guy)**: Speaker A
- **Female voice (Jenny)**: Speaker B
- Real conversation-like dialogues

### Dialogue Comprehension Questions
After each dialogue, there are 1-2 questions to test understanding.
Audio files are generated for each question.

### Test Paper
Open `cases/test-paper.html` for a printable test paper with:
- Part 1: Listening - Sentences
- Part 2: Listening - Dialogues
- Part 3: Reading - Comprehension

## Output Structure

```
audio/
├── topics.json
├── test_structure.json
├── greetings/
│   ├── greetings_01.mp3          (sentence)
│   ├── greetings_dialogue_1.mp3  (two voices)
│   ├── greetings_dialogue_1_q1.mp3 (dialogue question)
│   ├── greetings_dialogue_1_q2.mp3
│   ├── greetings_question_1.mp3  (general question)
│   └── index.json
└── ...
```

## TTS Engine Options

**Edge TTS (Free - Default)**
- Uses Microsoft Edge's TTS voices
- No API key needed

**OpenAI TTS (Paid)**
- Higher quality voices
- Requires API key
- Set `USE_EDGE_TTS=false` in .env

## HTML Players

- `cases/test-player.html` - Interactive audio player
- `cases/test-paper.html` - Printable test paper
