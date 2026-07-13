#!/usr/bin/env python3
"""
A1 English Listening Test Generator
Generates audio files for A1 level English listening tests.
"""

import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Check which TTS engine to use
USE_EDGE_TTS = os.getenv("USE_EDGE_TTS", "true").lower() == "true"

if not USE_EDGE_TTS:
    from openai import OpenAI


# ============================================================
# CONTENT TEMPLATES FOR A1 TOPICS
# ============================================================

A1_TOPICS = {
    "greetings": {
        "name": "Greetings & Introductions",
        "sentences": [
            "Hello, my name is Anna.",
            "Nice to meet you.",
            "How are you today?",
            "I am fine, thank you.",
            "Good morning!",
            "Good afternoon!",
            "Good evening!",
            "See you later!",
            "Goodbye!",
            "Thank you very much."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: Hello! What is your name?",
                    "Person B: Hi! My name is John.",
                    "Person A: Nice to meet you, John.",
                    "Person B: Nice to meet you too!"
                ],
                "questions": [
                    {
                        "question": "What is the boy's name?",
                        "answer": "John.",
                        "options": ["John", "Mike", "Peter"]
                    },
                    {
                        "question": "Where does this conversation happen?",
                        "answer": "We don't know.",
                        "options": ["At school", "At a party", "We don't know"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: How are you?",
                    "Person B: I'm fine, thank you. And you?",
                    "Person A: I'm good, thanks!",
                    "Person B: Have a nice day!",
                    "Person A: You too! Goodbye!"
                ],
                "questions": [
                    {
                        "question": "How is Person B?",
                        "answer": "Fine.",
                        "options": ["Tired", "Fine", "Sick"]
                    },
                    {
                        "question": "What does Person A say at the end?",
                        "answer": "You too! Goodbye!",
                        "options": ["See you", "You too! Goodbye!", "Thank you"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "What is the girl's name?",
                "answer": "Her name is Anna.",
                "options": ["Anna", "Maria", "Sarah"]
            },
            {
                "question": "How is John today?",
                "answer": "He is fine.",
                "options": ["Fine", "Tired", "Hungry"]
            }
        ]
    },
    "family": {
        "name": "Family",
        "sentences": [
            "This is my mother.",
            "My father is a teacher.",
            "I have one brother.",
            "My sister is ten years old.",
            "My grandmother is very kind.",
            "I love my family.",
            "My parents live in London.",
            "My brother likes football.",
            "My sister goes to school.",
            "We are a happy family."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: Do you have a big family?",
                    "Person B: Yes, I have two brothers and one sister.",
                    "Person A: What does your father do?",
                    "Person B: He is a doctor."
                ],
                "questions": [
                    {
                        "question": "How many brothers does Person B have?",
                        "answer": "Two brothers.",
                        "options": ["One", "Two", "Three"]
                    },
                    {
                        "question": "What does the father do?",
                        "answer": "He is a doctor.",
                        "options": ["Teacher", "Doctor", "Driver"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: How old is your sister?",
                    "Person B: She is eight years old.",
                    "Person A: Does she like school?",
                    "Person B: Yes, she loves it!"
                ],
                "questions": [
                    {
                        "question": "How old is the sister?",
                        "answer": "Eight years old.",
                        "options": ["Seven", "Eight", "Nine"]
                    },
                    {
                        "question": "Does the sister like school?",
                        "answer": "Yes, she loves it.",
                        "options": ["Yes", "No", "Maybe"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "How many brothers does the person have?",
                "answer": "Two brothers.",
                "options": ["One", "Two", "Three"]
            },
            {
                "question": "What does the father do?",
                "answer": "He is a doctor.",
                "options": ["Teacher", "Doctor", "Driver"]
            }
        ]
    },
    "food": {
        "name": "Food & Drinks",
        "sentences": [
            "I would like some water, please.",
            "I like apples and bananas.",
            "She drinks coffee every morning.",
            "We eat lunch at twelve o'clock.",
            "The food is very delicious.",
            "I don't like vegetables.",
            "Can I have some bread?",
            "I want an orange juice.",
            "This pizza is really good.",
            "Do you want some tea?"
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: What would you like to eat?",
                    "Person B: I'd like a sandwich, please.",
                    "Person A: Would you like something to drink?",
                    "Person B: Yes, a glass of orange juice.",
                    "Person A: Anything else?",
                    "Person B: No, thank you."
                ],
                "questions": [
                    {
                        "question": "What does Person B want to eat?",
                        "answer": "A sandwich.",
                        "options": ["Pizza", "A sandwich", "Salad"]
                    },
                    {
                        "question": "What does Person B want to drink?",
                        "answer": "Orange juice.",
                        "options": ["Water", "Orange juice", "Coffee"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: Do you like Chinese food?",
                    "Person B: Yes, I love it! I like noodles.",
                    "Person A: Me too! And I like rice.",
                    "Person B: Let's go to the Chinese restaurant."
                ],
                "questions": [
                    {
                        "question": "What food does Person B like?",
                        "answer": "Noodles.",
                        "options": ["Rice", "Noodles", "Dumplings"]
                    },
                    {
                        "question": "Where do they want to go?",
                        "answer": "To the Chinese restaurant.",
                        "options": ["To a pizza shop", "To the Chinese restaurant", "Home"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "What does the person want to eat?",
                "answer": "A sandwich.",
                "options": ["Pizza", "Sandwich", "Salad"]
            },
            {
                "question": "Does the person like Chinese food?",
                "answer": "Yes, she loves it.",
                "options": ["Yes, she loves it", "No, she doesn't", "Maybe"]
            }
        ]
    },
    "daily_routine": {
        "name": "Daily Routine",
        "sentences": [
            "I wake up at seven o'clock.",
            "I brush my teeth every morning.",
            "I have breakfast at eight.",
            "I go to work by bus.",
            "I eat lunch at twelve.",
            "I come home at six o'clock.",
            "I watch TV in the evening.",
            "I go to bed at ten.",
            "I take a shower every day.",
            "She reads a book before bed."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: What time do you wake up?",
                    "Person B: I wake up at six thirty.",
                    "Person A: Do you have breakfast?",
                    "Person B: Yes, I have coffee and toast.",
                    "Person A: How do you go to work?",
                    "Person B: I go by train."
                ],
                "questions": [
                    {
                        "question": "What time does Person B wake up?",
                        "answer": "Six thirty.",
                        "options": ["Six o'clock", "Six thirty", "Seven o'clock"]
                    },
                    {
                        "question": "How does Person B go to work?",
                        "answer": "By train.",
                        "options": ["By bus", "By train", "By car"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: What do you do in the evening?",
                    "Person B: I watch TV and cook dinner.",
                    "Person A: What time do you go to bed?",
                    "Person B: I go to bed at about eleven."
                ],
                "questions": [
                    {
                        "question": "What does Person B do in the evening?",
                        "answer": "Watch TV and cook dinner.",
                        "options": ["Read books", "Watch TV and cook dinner", "Go out"]
                    },
                    {
                        "question": "What time does Person B go to bed?",
                        "answer": "About eleven.",
                        "options": ["Ten o'clock", "About eleven", "Midnight"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "What time does the person wake up?",
                "answer": "At six thirty.",
                "options": ["Six o'clock", "Six thirty", "Seven o'clock"]
            },
            {
                "question": "How does the person go to work?",
                "answer": "By train.",
                "options": ["By bus", "By train", "By car"]
            }
        ]
    },
    "shopping": {
        "name": "Shopping",
        "sentences": [
            "How much is this shirt?",
            "I want to buy a new dress.",
            "The shop opens at nine.",
            "Do you accept credit cards?",
            "Can I try this on?",
            "This is too expensive.",
            "I need a large size, please.",
            "Where is the checkout?",
            "I'm just looking, thank you.",
            "The sale starts tomorrow."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: Can I help you?",
                    "Person B: Yes, I'm looking for a blue shirt.",
                    "Person A: What size do you need?",
                    "Person B: Medium, please.",
                    "Person A: Here you are. The changing room is there.",
                    "Person B: Thank you. How much is it?",
                    "Person A: It's thirty-five dollars."
                ],
                "questions": [
                    {
                        "question": "What color shirt is Person B looking for?",
                        "answer": "Blue.",
                        "options": ["Red", "Blue", "Green"]
                    },
                    {
                        "question": "How much is the shirt?",
                        "answer": "Thirty-five dollars.",
                        "options": ["Twenty-five", "Thirty-five", "Forty-five"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: Do you like this jacket?",
                    "Person B: Yes, it's nice. But it's expensive.",
                    "Person A: It's on sale today - fifty percent off!",
                    "Person B: Great! I'll take it."
                ],
                "questions": [
                    {
                        "question": "Why doesn't Person B want to buy the jacket at first?",
                        "answer": "It's expensive.",
                        "options": ["It's ugly", "It's expensive", "It's too big"]
                    },
                    {
                        "question": "What happens to the price?",
                        "answer": "It's fifty percent off.",
                        "options": ["It goes up", "It's fifty percent off", "It stays the same"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "What size shirt does the person want?",
                "answer": "Medium.",
                "options": ["Small", "Medium", "Large"]
            },
            {
                "question": "How much is the shirt?",
                "answer": "Thirty-five dollars.",
                "options": ["Twenty-five", "Thirty-five", "Forty-five"]
            }
        ]
    },
    "travel": {
        "name": "Travel & Directions",
        "sentences": [
            "Where is the train station?",
            "I need a ticket to Paris.",
            "How long does the flight take?",
            "Turn left at the traffic lights.",
            "The hotel is near the beach.",
            "I have a reservation for two nights.",
            "Where can I find a taxi?",
            "Is there a bus to the airport?",
            "I lost my passport.",
            "The museum is across from the park."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: Excuse me, where is the museum?",
                    "Person B: Go straight and turn left.",
                    "Person A: Is it far?",
                    "Person B: No, it's about five minutes.",
                    "Person A: Thank you very much!"
                ],
                "questions": [
                    {
                        "question": "Where is Person A going?",
                        "answer": "To the museum.",
                        "options": ["To the park", "To the museum", "To the hotel"]
                    },
                    {
                        "question": "How long does it take to walk there?",
                        "answer": "About five minutes.",
                        "options": ["Two minutes", "About five minutes", "Ten minutes"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: I'd like to book a room, please.",
                    "Person B: For how many nights?",
                    "Person A: Three nights, from Monday.",
                    "Person B: Would you like a single or double room?",
                    "Person A: A double room, please.",
                    "Person B: That's one hundred twenty dollars per night."
                ],
                "questions": [
                    {
                        "question": "How many nights does Person A want to stay?",
                        "answer": "Three nights.",
                        "options": ["One night", "Two nights", "Three nights"]
                    },
                    {
                        "question": "What kind of room does Person A want?",
                        "answer": "A double room.",
                        "options": ["A single room", "A double room", "A family room"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "Where is the museum?",
                "answer": "Go straight and turn left.",
                "options": ["Turn right", "Go straight and turn left", "It's behind you"]
            },
            {
                "question": "How many nights does the person want to stay?",
                "answer": "Three nights.",
                "options": ["One night", "Two nights", "Three nights"]
            }
        ]
    },
    "weather": {
        "name": "Weather",
        "sentences": [
            "It is sunny today.",
            "I think it will rain tomorrow.",
            "It's very cold outside.",
            "The weather is nice today.",
            "I need an umbrella.",
            "It's hot and humid.",
            "I like the snow.",
            "The wind is very strong.",
            "It's cloudy today.",
            "Summer is my favorite season."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: How's the weather today?",
                    "Person B: It's sunny and warm.",
                    "Person A: Should I bring a jacket?",
                    "Person B: No, it's not cold. But bring sunglasses.",
                    "Person A: Good idea!"
                ],
                "questions": [
                    {
                        "question": "What's the weather like today?",
                        "answer": "Sunny and warm.",
                        "options": ["Rainy", "Sunny and warm", "Cold"]
                    },
                    {
                        "question": "What should Person A bring?",
                        "answer": "Sunglasses.",
                        "options": ["An umbrella", "A jacket", "Sunglasses"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: I don't like this weather.",
                    "Person B: Me neither. It's raining again.",
                    "Person A: I hope it stops tomorrow.",
                    "Person B: The forecast says it will be sunny."
                ],
                "questions": [
                    {
                        "question": "What's the weather like now?",
                        "answer": "It's raining.",
                        "options": ["It's sunny", "It's raining", "It's snowing"]
                    },
                    {
                        "question": "What does the forecast say for tomorrow?",
                        "answer": "It will be sunny.",
                        "options": ["It will rain", "It will be sunny", "It will snow"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "What's the weather like?",
                "answer": "It's sunny and warm.",
                "options": ["Rainy and cold", "Sunny and warm", "Snowy"]
            },
            {
                "question": "What will the weather be like tomorrow?",
                "answer": "Sunny.",
                "options": ["Rainy", "Cloudy", "Sunny"]
            }
        ]
    },
    "health": {
        "name": "Health & Doctor",
        "sentences": [
            "I have a headache.",
            "I need to see a doctor.",
            "My stomach hurts.",
            "Take this medicine three times a day.",
            "How long have you been sick?",
            "I feel much better now.",
            "You should rest for two days.",
            "Do you have any allergies?",
            "I have a cold.",
            "The doctor will see you now."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: Good morning. What's the problem?",
                    "Person B: I have a bad headache.",
                    "Person A: How long have you had it?",
                    "Person B: Since yesterday.",
                    "Person A: I'll give you some medicine."
                ],
                "questions": [
                    {
                        "question": "What's wrong with Person B?",
                        "answer": "A bad headache.",
                        "options": ["Stomachache", "A bad headache", "Toothache"]
                    },
                    {
                        "question": "When did the headache start?",
                        "answer": "Since yesterday.",
                        "options": ["Today", "Since yesterday", "Last week"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: What's wrong?",
                    "Person B: I feel sick. My stomach hurts.",
                    "Person A: Did you eat something bad?",
                    "Person B: Maybe. I had seafood for dinner.",
                    "Person A: You should drink some water and rest."
                ],
                "questions": [
                    {
                        "question": "What does Person B feel?",
                        "answer": "Sick.",
                        "options": ["Happy", "Tired", "Sick"]
                    },
                    {
                        "question": "What did Person B eat for dinner?",
                        "answer": "Seafood.",
                        "options": ["Meat", "Seafood", "Vegetables"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "What's the patient's problem?",
                "answer": "A bad headache.",
                "options": ["Stomachache", "Headache", "Back pain"]
            },
            {
                "question": "How long has the patient had the headache?",
                "answer": "Since yesterday.",
                "options": ["Since today", "Since yesterday", "For a week"]
            }
        ]
    },
    "numbers": {
        "name": "Numbers & Counting",
        "sentences": [
            "I have three cats.",
            "There are twenty students in the class.",
            "My phone number is five five five, one two three four.",
            "I need ten apples.",
            "The bus comes at seven fifteen.",
            "I live on the third floor.",
            "She has fifty dollars.",
            "There are one hundred people here.",
            "My birthday is on the twenty-first.",
            "I wake up at six thirty every day."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: How many people are coming to the party?",
                    "Person B: Let me see. Eight people.",
                    "Person A: Should we order more food?",
                    "Person B: Yes, let's order for ten people.",
                    "Person A: Good idea."
                ],
                "questions": [
                    {
                        "question": "How many people are coming to the party?",
                        "answer": "Eight people.",
                        "options": ["Six", "Eight", "Ten"]
                    },
                    {
                        "question": "How many people should they order food for?",
                        "answer": "Ten people.",
                        "options": ["Eight", "Ten", "Twelve"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: What's your phone number?",
                    "Person B: It's zero one two, three four five, six seven eight nine.",
                    "Person A: Let me write that down. Zero one two...",
                    "Person B: Three four five, six seven eight nine.",
                    "Person A: Thank you!"
                ],
                "questions": [
                    {
                        "question": "What is Person B's phone number?",
                        "answer": "Zero one two, three four five, six seven eight nine.",
                        "options": ["Zero one two, three four five, six seven eight nine", "One two three, four five six, seven eight nine zero", "Zero nine eight, seven six five, four three two one"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "How many people are coming to the party?",
                "answer": "Eight people.",
                "options": ["Six", "Eight", "Ten"]
            },
            {
                "question": "What floor does the person live on?",
                "answer": "The third floor.",
                "options": ["First floor", "Second floor", "Third floor"]
            }
        ]
    },
    "colors": {
        "name": "Colors",
        "sentences": [
            "The sky is blue.",
            "I like the red dress.",
            "My favorite color is green.",
            "The cat is black and white.",
            "I have a yellow banana.",
            "The flowers are pink.",
            "Please give me the orange ball.",
            "The car is silver.",
            "I see a purple butterfly.",
            "The grass is green."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: What color is your new car?",
                    "Person B: It's dark blue.",
                    "Person A: Nice! I like blue cars.",
                    "Person B: Thank you. What color is your car?",
                    "Person A: Mine is silver."
                ],
                "questions": [
                    {
                        "question": "What color is Person B's new car?",
                        "answer": "Dark blue.",
                        "options": ["Black", "Dark blue", "Silver"]
                    },
                    {
                        "question": "What color is Person A's car?",
                        "answer": "Silver.",
                        "options": ["Blue", "Silver", "Red"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: Can I have the red pen, please?",
                    "Person B: This one?",
                    "Person A: No, the red one. Not the blue one.",
                    "Person B: Oh, here you are.",
                    "Person A: Thank you!"
                ],
                "questions": [
                    {
                        "question": "Which pen does Person A want?",
                        "answer": "The red pen.",
                        "options": ["Blue pen", "Red pen", "Green pen"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "What color is the new car?",
                "answer": "Dark blue.",
                "options": ["Black", "Dark blue", "Silver"]
            },
            {
                "question": "Which pen does the person want?",
                "answer": "The red pen.",
                "options": ["Blue pen", "Red pen", "Green pen"]
            }
        ]
    },
    "time": {
        "name": "Time & Schedules",
        "sentences": [
            "What time is it?",
            "It's nine o'clock.",
            "The meeting starts at two thirty.",
            "I have lunch at twelve.",
            "The movie begins at seven in the evening.",
            "I'm late for work.",
            "The train leaves at eight fifteen.",
            "School starts at nine in the morning.",
            "I finish work at five.",
            "Let's meet at half past three."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: Excuse me, what time is it?",
                    "Person B: It's ten forty-five.",
                    "Person A: Oh no! I'm late for my appointment.",
                    "Person B: What time is your appointment?",
                    "Person A: It's at eleven o'clock."
                ],
                "questions": [
                    {
                        "question": "What time is it now?",
                        "answer": "Ten forty-five.",
                        "options": ["Ten thirty", "Ten forty-five", "Eleven o'clock"]
                    },
                    {
                        "question": "What time is the appointment?",
                        "answer": "Eleven o'clock.",
                        "options": ["Ten thirty", "Ten forty-five", "Eleven o'clock"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: What time does the movie start?",
                    "Person B: It starts at seven thirty.",
                    "Person A: Should we arrive early?",
                    "Person B: Yes, let's be there at seven fifteen.",
                    "Person A: Good. I'll pick you up at seven."
                ],
                "questions": [
                    {
                        "question": "What time does the movie start?",
                        "answer": "Seven thirty.",
                        "options": ["Seven o'clock", "Seven fifteen", "Seven thirty"]
                    },
                    {
                        "question": "What time will Person A pick up Person B?",
                        "answer": "Seven o'clock.",
                        "options": ["Seven o'clock", "Seven fifteen", "Seven thirty"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "What time is it?",
                "answer": "Ten forty-five.",
                "options": ["Ten thirty", "Ten forty-five", "Eleven o'clock"]
            },
            {
                "question": "What time does the movie start?",
                "answer": "Seven thirty.",
                "options": ["Seven o'clock", "Seven fifteen", "Seven thirty"]
            }
        ]
    },
    "work": {
        "name": "Work & Jobs",
        "sentences": [
            "I work in an office.",
            "She is a nurse at the hospital.",
            "He drives a taxi.",
            "I start work at nine in the morning.",
            "My boss is very nice.",
            "I have a meeting this afternoon.",
            "She works five days a week.",
            "I need to send an email.",
            "The office is downtown.",
            "I like my job."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: What do you do for work?",
                    "Person B: I'm a teacher. I teach English.",
                    "Person A: That sounds interesting. Where do you teach?",
                    "Person B: At the language school downtown.",
                    "Person A: How do you get to work?",
                    "Person B: I take the bus."
                ],
                "questions": [
                    {
                        "question": "What does Person B do?",
                        "answer": "She is a teacher.",
                        "options": ["Doctor", "Teacher", "Nurse"]
                    },
                    {
                        "question": "How does Person B get to work?",
                        "answer": "By bus.",
                        "options": ["By car", "By bus", "By train"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: I'm looking for a job.",
                    "Person B: What kind of job do you want?",
                    "Person A: I want to work in a restaurant.",
                    "Person B: Can you cook?",
                    "Person A: Yes, I can cook very well.",
                    "Person B: Great! There's a restaurant near here."
                ],
                "questions": [
                    {
                        "question": "What kind of job does Person A want?",
                        "answer": "In a restaurant.",
                        "options": ["In an office", "In a restaurant", "At a school"]
                    },
                    {
                        "question": "Can Person A cook?",
                        "answer": "Yes, very well.",
                        "options": ["No", "Yes, very well", "A little"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "What does the person do for work?",
                "answer": "She is a teacher.",
                "options": ["Doctor", "Teacher", "Nurse"]
            },
            {
                "question": "How does the teacher get to work?",
                "answer": "By bus.",
                "options": ["By car", "By bus", "By train"]
            }
        ]
    },
    "hobbies": {
        "name": "Hobbies & Free Time",
        "sentences": [
            "I like reading books.",
            "She plays tennis every weekend.",
            "He enjoys cooking.",
            "I watch movies on Friday nights.",
            "My hobby is photography.",
            "They like swimming in the summer.",
            "I listen to music every day.",
            "She paints beautiful pictures.",
            "He plays the guitar.",
            "We play video games together."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: What do you do in your free time?",
                    "Person B: I like to read books. What about you?",
                    "Person A: I enjoy playing sports.",
                    "Person B: What sports do you play?",
                    "Person A: I play basketball and tennis.",
                    "Person B: That's great!"
                ],
                "questions": [
                    {
                        "question": "What does Person B like to do?",
                        "answer": "Read books.",
                        "options": ["Play sports", "Read books", "Watch movies"]
                    },
                    {
                        "question": "What sports does Person A play?",
                        "answer": "Basketball and tennis.",
                        "options": ["Soccer and tennis", "Basketball and tennis", "Basketball only"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: Do you want to go to the movies tonight?",
                    "Person B: What movie?",
                    "Person A: It's a comedy. It's very funny.",
                    "Person B: Sounds good! What time?",
                    "Person A: It starts at eight o'clock.",
                    "Person B: Perfect. I'll meet you there."
                ],
                "questions": [
                    {
                        "question": "What kind of movie is it?",
                        "answer": "A comedy.",
                        "options": ["A comedy", "A drama", "A horror movie"]
                    },
                    {
                        "question": "What time does the movie start?",
                        "answer": "Eight o'clock.",
                        "options": ["Seven o'clock", "Eight o'clock", "Nine o'clock"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "What does the person like to do in free time?",
                "answer": "Read books.",
                "options": ["Watch TV", "Read books", "Play sports"]
            },
            {
                "question": "What time does the movie start?",
                "answer": "Eight o'clock.",
                "options": ["Seven o'clock", "Eight o'clock", "Nine o'clock"]
            }
        ]
    },
    "animals": {
        "name": "Animals & Pets",
        "sentences": [
            "I have a dog at home.",
            "Cats are very cute.",
            "The bird can fly high.",
            "I like horses.",
            "She has a small fish.",
            "The lion is the king of animals.",
            "Dogs are very friendly.",
            "I see a rabbit in the garden.",
            "The elephant is very big.",
            "My cat likes to sleep."
        ],
        "dialogues": [
            {
                "lines": [
                    "Person A: Do you have any pets?",
                    "Person B: Yes, I have a dog and two cats.",
                    "Person A: What's your dog's name?",
                    "Person B: His name is Max.",
                    "Person A: Is he friendly?",
                    "Person B: Yes, he's very friendly!"
                ],
                "questions": [
                    {
                        "question": "What pets does Person B have?",
                        "answer": "A dog and two cats.",
                        "options": ["A dog only", "A cat and a dog", "A dog and two cats"]
                    },
                    {
                        "question": "What is the dog's name?",
                        "answer": "Max.",
                        "options": ["Tom", "Max", "Buddy"]
                    }
                ]
            },
            {
                "lines": [
                    "Person A: Look at that bird! It's beautiful.",
                    "Person B: Yes, it's blue and yellow.",
                    "Person A: I think it's a parrot.",
                    "Person B: Can parrots talk?",
                    "Person A: Yes, some parrots can talk!",
                    "Person B: Wow, that's amazing."
                ],
                "questions": [
                    {
                        "question": "What colors is the bird?",
                        "answer": "Blue and yellow.",
                        "options": ["Red and green", "Blue and yellow", "Black and white"]
                    },
                    {
                        "question": "Can parrots talk?",
                        "answer": "Yes, some can.",
                        "options": ["No", "Yes, some can", "All parrots can"]
                    }
                ]
            }
        ],
        "questions": [
            {
                "question": "How many pets does the person have?",
                "answer": "Three pets.",
                "options": ["One", "Two", "Three"]
            },
            {
                "question": "What colors is the bird?",
                "answer": "Blue and yellow.",
                "options": ["Red and green", "Blue and yellow", "Black and white"]
            }
        ]
    }
}


class ContentGenerator:
    """Generates A1 English content by topic."""
    
    def __init__(self):
        if not USE_EDGE_TTS:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate_topic_content(self, topic: str, use_ai: bool = False) -> Dict:
        """Get content for a topic, either from templates or AI-generated."""
        if topic in A1_TOPICS:
            return A1_TOPICS[topic]
        
        if use_ai:
            return self._generate_with_ai(topic)
        
        print(f"Topic '{topic}' not found. Available topics: {', '.join(A1_TOPICS.keys())}")
        print("Using 'greetings' as default.")
        return A1_TOPICS["greetings"]
    
    def _generate_with_ai(self, topic: str) -> Dict:
        """Generate A1 content using OpenAI API."""
        prompt = f"""Generate A1 (beginner) English listening test content about "{topic}".
        
Return ONLY a JSON object with this exact structure (no markdown, just JSON):
{{
    "name": "Topic Name",
    "sentences": ["sentence 1", "sentence 2", ...],
    "dialogues": [
        ["Person A: question", "Person B: answer", ...],
        ["Person A: question", "Person B: answer", ...]
    ],
    "questions": [
        {{
            "question": "question text",
            "answer": "correct answer",
            "options": ["option 1", "option 2", "option 3"]
        }}
    ]
}}

Generate exactly 10 sentences, 2 dialogues (4-6 lines each), and 3 questions.
Use simple A1-level vocabulary and short sentences."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        
        return json.loads(content)
    
    def get_all_topics(self) -> List[str]:
        """Return list of available topics."""
        return list(A1_TOPICS.keys())
    
    def generate_custom_content(self, sentences: List[str] = None, 
                                 dialogues: List[List[str]] = None,
                                 questions: List[Dict] = None) -> Dict:
        """Create custom content from provided data."""
        return {
            "name": "Custom Content",
            "sentences": sentences or [],
            "dialogues": dialogues or [],
            "questions": questions or []
        }


class AudioGenerator:
    """Generates audio files from text using TTS."""
    
    # Voice configuration for two-voice dialogues
    VOICE_MALE = "en-US-GuyNeural"      # Male voice (Speaker A)
    VOICE_FEMALE = "en-US-JennyNeural"   # Female voice (Speaker B)
    VOICE_DEFAULT = "en-US-AnaNeural"    # Default voice for sentences/questions
    
    def __init__(self, output_dir: str = "audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not USE_EDGE_TTS:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_audio_edge(self, text: str, output_path: str, 
                                   voice: str = "en-US-AnaNeural", 
                                   rate: str = "-10%") -> bool:
        """Generate audio using free Edge TTS."""
        import edge_tts
        
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"  Error generating audio: {e}")
            return False
    
    def generate_audio_openai(self, text: str, output_path: str,
                               voice: str = "alloy", speed: float = 0.9) -> bool:
        """Generate audio using OpenAI TTS."""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed
            )
            
            response.stream_to_file(output_path)
            return True
        except Exception as e:
            print(f"  Error generating audio: {e}")
            return False
    
    async def generate_audio(self, text: str, output_path: str, voice: str = None) -> bool:
        """Generate audio using configured TTS engine."""
        if USE_EDGE_TTS:
            v = voice or self.VOICE_DEFAULT
            return await self.generate_audio_edge(text, str(output_path), voice=v)
        else:
            return self.generate_audio_openai(text, str(output_path))
    
    def _sanitize_filename(self, name: str) -> str:
        """Clean text for use in filenames."""
        return re.sub(r'[^\w\s-]', '', name)[:50].strip().replace(' ', '_')
    
    def _parse_dialogue_line(self, line: str) -> tuple:
        """Parse a dialogue line and extract speaker and text.
        
        Returns (speaker_id, text) where speaker_id is 'A' or 'B'.
        Supports formats:
        - "Person A: text"
        - "Speaker A: text"
        - "A: text"
        """
        line = line.strip()
        
        # Match various speaker patterns
        patterns = [
            r'^(?:Person|Speaker|P)?\s*([AB])\s*[:\-]\s*(.+)$',
            r'^([AB])\s*[:\-]\s*(.+)$',
            r'^(Doctor|Patient|Teacher|Student|Clerk|Customer)\s*[:\-]\s*(.+)$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                if groups[0].upper() in ['A', 'B']:
                    return groups[0].upper(), groups[1].strip()
                else:
                    # For named speakers, alternate A/B
                    return None, line
        
        # Default: treat as speaker A if no match
        return 'A', line
    
    def _get_voice_for_speaker(self, speaker_id: str) -> str:
        """Get the appropriate voice for a speaker."""
        if USE_EDGE_TTS:
            return self.VOICE_MALE if speaker_id == 'A' else self.VOICE_FEMALE
        else:
            return "alloy" if speaker_id == 'A' else "nova"
    
    async def generate_dialogue_two_voice(self, dialogue_lines: List[str], 
                                           output_path: str) -> bool:
        """Generate a dialogue with two different voices.
        
        Each line is spoken by the appropriate voice based on speaker.
        Lines are concatenated into a single MP3 file.
        """
        import tempfile
        import os
        
        # Create temp directory for individual lines
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_files = []
            
            for i, line in enumerate(dialogue_lines):
                speaker_id, text = self._parse_dialogue_line(line)
                
                if speaker_id is None:
                    speaker_id = 'A' if i % 2 == 0 else 'B'
                
                voice = self._get_voice_for_speaker(speaker_id)
                temp_path = os.path.join(temp_dir, f"line_{i:02d}.mp3")
                
                if not await self.generate_audio(text, temp_path, voice=voice):
                    return False
                
                temp_files.append(temp_path)
            
            # Concatenate all audio files
            return self._concatenate_audio(temp_files, str(output_path))
    
    def _concatenate_audio(self, input_files: List[str], output_path: str) -> bool:
        """Concatenate multiple MP3 files into one."""
        try:
            # Write binary concatenation (works for MP3)
            with open(output_path, 'wb') as outfile:
                for input_file in input_files:
                    with open(input_file, 'rb') as infile:
                        outfile.write(infile.read())
            return True
        except Exception as e:
            print(f"  Error concatenating audio: {e}")
            return False
    
    async def generate_from_content(self, content: Dict, part_name: str = "part1") -> List[str]:
        """Generate audio files from content dictionary."""
        part_dir = self.output_dir / part_name
        part_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        index = 1
        
        # Generate sentences
        for sentence in content.get("sentences", []):
            filename = f"{part_name}_{index:02d}.mp3"
            filepath = part_dir / filename
            
            print(f"  Generating: {filename}")
            if await self.generate_audio(sentence, filepath):
                generated_files.append({
                    "file": filename,
                    "text": sentence,
                    "type": "sentence"
                })
            index += 1
        
        # Generate dialogues with two voices
        for i, dialogue in enumerate(content.get("dialogues", []), 1):
            # Handle both old format (list) and new format (dict with lines and questions)
            if isinstance(dialogue, dict):
                dialogue_lines = dialogue.get("lines", [])
                dialogue_questions = dialogue.get("questions", [])
            else:
                dialogue_lines = dialogue
                dialogue_questions = []
            
            filename = f"{part_name}_dialogue_{i}.mp3"
            filepath = part_dir / filename
            
            print(f"  Generating: {filename} (two voices)")
            if await self.generate_dialogue_two_voice(dialogue_lines, filepath):
                dialogue_entry = {
                    "file": filename,
                    "text": "\n".join(dialogue_lines),
                    "type": "dialogue",
                    "voices": ["male", "female"]
                }
                # Add dialogue-specific questions if present
                if dialogue_questions:
                    dialogue_entry["questions"] = dialogue_questions
                    
                    # Generate audio for dialogue questions
                    for j, q in enumerate(dialogue_questions, 1):
                        q_filename = f"{part_name}_dialogue_{i}_q{j}.mp3"
                        q_filepath = part_dir / q_filename
                        
                        print(f"  Generating: {q_filename}")
                        if await self.generate_audio(q["question"], q_filepath):
                            generated_files.append({
                                "file": q_filename,
                                "text": q["question"],
                                "answer": q.get("answer", ""),
                                "options": q.get("options", []),
                                "type": "dialogue_question",
                                "dialogue_index": i
                            })
                
                generated_files.append(dialogue_entry)
        
        # Generate questions
        for i, qa in enumerate(content.get("questions", []), 1):
            question_text = qa["question"]
            filename = f"{part_name}_question_{i}.mp3"
            filepath = part_dir / filename
            
            print(f"  Generating: {filename}")
            if await self.generate_audio(question_text, filepath):
                generated_files.append({
                    "file": filename,
                    "text": question_text,
                    "answer": qa.get("answer", ""),
                    "options": qa.get("options", []),
                    "type": "question"
                })
        
        # Save index file
        index_path = part_dir / "index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(generated_files, f, indent=2, ensure_ascii=False)
        
        return generated_files


class TestGenerator:
    """Main class to generate complete A1 listening tests."""
    
    def __init__(self, output_dir: str = "audio"):
        self.content_gen = ContentGenerator()
        self.audio_gen = AudioGenerator(output_dir)
        self.output_dir = Path(output_dir)
    
    async def generate_test(self, topics: List[str], part_names: List[str] = None):
        """Generate a complete test from multiple topics."""
        if part_names is None:
            part_names = [f"part{i+1}" for i in range(len(topics))]
        
        all_results = {}
        
        for topic, part_name in zip(topics, part_names):
            print(f"\n{'='*50}")
            print(f"Generating: {part_name.upper()} - {topic.upper()}")
            print(f"{'='*50}")
            
            content = self.content_gen.generate_topic_content(topic)
            print(f"Topic: {content['name']}")
            print(f"  Sentences: {len(content.get('sentences', []))}")
            print(f"  Dialogues: {len(content.get('dialogues', []))}")
            print(f"  Questions: {len(content.get('questions', []))}")
            
            files = await self.audio_gen.generate_from_content(content, part_name)
            all_results[part_name] = {
                "topic": content['name'],
                "files": files
            }
        
        # Save overall test structure
        test_file = self.output_dir / "test_structure.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        # Save topics list for HTML player
        topics_list = [{"id": k, "name": v["topic"]} for k, v in all_results.items()]
        topics_file = self.output_dir / "topics.json"
        with open(topics_file, 'w', encoding='utf-8') as f:
            json.dump(topics_list, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*50}")
        print(f"Test generation complete!")
        print(f"Audio files saved to: {self.output_dir}")
        print(f"Test structure saved to: {test_file}")
        print(f"Topics list saved to: {topics_file}")
        
        return all_results
    
    def list_topics(self):
        """Print all available topics."""
        print("\nAvailable A1 Topics:")
        print("-" * 30)
        for topic, data in A1_TOPICS.items():
            print(f"  {topic:20s} - {data['name']}")
        print()


async def main():
    generator = TestGenerator()
    
    # Print usage info
    if len(sys.argv) < 2:
        print("\nA1 English Listening Test Generator")
        print("=" * 40)
        generator.list_topics()
        print("Usage:")
        print("  python generate_test.py topic1 topic2 topic3")
        print("  python generate_test.py greetings family food")
        print("  python generate_test.py --all  (generate all topics)")
        print(f"\nCurrent TTS engine: {'Edge TTS (free)' if USE_EDGE_TTS else 'OpenAI TTS'}")
        return
    
    if sys.argv[1] == "--all":
        topics = list(A1_TOPICS.keys())
    else:
        topics = sys.argv[1:]
    
    # Use topic names as folder names (e.g., greetings, family)
    await generator.generate_test(topics, part_names=topics)


if __name__ == "__main__":
    asyncio.run(main())
