#!/usr/bin/env python3
"""
A1 English Practice Generator
Generates practice audio with 50 sentences (multi-voice) and 10 dialogues per topic.
"""

import asyncio
import json
import os
import random
import sys
from pathlib import Path

# Edge TTS voices for sentences (alternating male/female)
SENTENCE_VOICES = [
    "en-US-GuyNeural",         # Male 1
    "en-US-JennyNeural",       # Female 1
    "en-US-BrianNeural",       # Male 2
    "en-US-AnaNeural",         # Female 2
    "en-US-ChristopherNeural", # Male 3
    "en-US-AvaNeural",         # Female 3
    "en-US-AndrewNeural",      # Male 4
    "en-US-EmmaNeural",        # Female 4
]

# Dialogue voices
DIALOGUE_VOICES = {
    "A": "en-US-GuyNeural",    # Person A = Male
    "B": "en-US-JennyNeural"   # Person B = Female
}

# ============================================================
# PRACTICE CONTENT - 50 SENTENCES + 10 DIALOGUES PER TOPIC
# ============================================================

PRACTICE_TOPICS = {
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
            "Thank you very much.",
            "What is your name?",
            "My name is John.",
            "I am from England.",
            "Where are you from?",
            "I am twelve years old.",
            "How old are you?",
            "This is my friend.",
            "She is very nice.",
            "He is my brother.",
            "We are students.",
            "I live in London.",
            "Do you live here?",
            "Yes, I do.",
            "No, I don't.",
            "Nice weather today!",
            "It is very sunny.",
            "I like this place.",
            "Me too!",
            "Thank you for your help.",
            "You are welcome.",
            "Have a good day!",
            "You too!",
            "See you tomorrow.",
            "Good night!",
            "Sleep well!",
            "Nice to see you again.",
            "How is your family?",
            "They are great.",
            "What do you do?",
            "I am a student.",
            "That is interesting.",
            "Can I help you?",
            "Yes, please.",
            "No, thank you.",
            "I don't understand.",
            "Please speak slowly.",
            "I am learning English.",
            "It is fun!",
            "Practice makes perfect.",
            "Keep going!",
            "You are doing great!"
        ],
        "dialogues": [
            {"lines": ["Person A: Hello! What is your name?", "Person B: Hi! My name is John.", "Person A: Nice to meet you, John.", "Person B: Nice to meet you too!"]},
            {"lines": ["Person A: How are you?", "Person B: I'm fine, thank you. And you?", "Person A: I'm good, thanks!", "Person B: Have a nice day!"]},
            {"lines": ["Person A: Where are you from?", "Person B: I'm from Canada.", "Person A: Really? I love Canada!", "Person B: Thank you! It's beautiful."]},
            {"lines": ["Person A: How old are you?", "Person B: I'm fifteen. And you?", "Person A: I'm fifteen too!", "Person B: We are the same age!"]},
            {"lines": ["Person A: Nice to see you again!", "Person B: Hi! It's been a long time!", "Person A: How have you been?", "Person B: Great! I missed you."]},
            {"lines": ["Person A: Good morning! How are you?", "Person B: Good morning! I'm well, thanks.", "Person A: Ready for class?", "Person B: Yes, let's go!"]},
            {"lines": ["Person A: What is your name?", "Person B: My name is Sarah.", "Person A: I'm Mike. Nice to meet you!", "Person B: Nice to meet you, Mike!"]},
            {"lines": ["Person A: Do you live in London?", "Person B: Yes, I do. Do you?", "Person A: No, I live in Manchester.", "Person B: Oh, that's nice!"]},
            {"lines": ["Person A: Can I help you?", "Person B: Yes, please. Where is the station?", "Person A: Go straight, then turn left.", "Person B: Thank you so much!"]},
            {"lines": ["Person A: Thank you for today!", "Person B: You're welcome! It was fun.", "Person A: See you next week!", "Person B: See you! Bye!"]}
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
            "We are a happy family.",
            "How many people are in your family?",
            "There are five people.",
            "My dad is very tall.",
            "My mom has brown hair.",
            "I am the oldest child.",
            "My brother is younger than me.",
            "My sister likes to read.",
            "We have a cat and a dog.",
            "My grandfather tells stories.",
            "My grandmother cooks very well.",
            "I have two uncles.",
            "My aunt lives in America.",
            "We visit them every summer.",
            "My cousin is my best friend.",
            "My parents met at university.",
            "My father drives a blue car.",
            "My mother works at a hospital.",
            "My brother plays the guitar.",
            "My sister dances ballet.",
            "I play tennis with my dad.",
            "We eat dinner together.",
            "I help my mom in the kitchen.",
            "My dad helps me with homework.",
            "My family goes to the park.",
            "We watch movies on weekends.",
            "I am proud of my family.",
            "They support me always.",
            "My baby brother is cute.",
            "My sister wants to be a doctor.",
            "My father wants to travel.",
            "We have many family photos.",
            "I love taking family pictures.",
            "My mom is the best cook.",
            "My dad tells funny jokes.",
            "My grandmother knits sweaters.",
            "We celebrate birthdays together.",
            "Family is important to me.",
            "I call my parents every day.",
            "We share everything.",
            "I am grateful for my family."
        ],
        "dialogues": [
            {"lines": ["Person A: Do you have a big family?", "Person B: Yes, I have two brothers and one sister.", "Person A: What does your father do?", "Person B: He is a doctor."]},
            {"lines": ["Person A: How old is your sister?", "Person B: She is eight years old.", "Person A: Does she like school?", "Person B: Yes, she loves it!"]},
            {"lines": ["Person A: Where do your parents live?", "Person B: They live in Bristol.", "Person A: Do you see them often?", "Person B: Yes, every weekend."]},
            {"lines": ["Person A: Is that your brother?", "Person B: No, that is my cousin.", "Person A: He looks like you!", "Person B: People say that a lot."]},
            {"lines": ["Person A: How many people are in your family?", "Person B: Four - my parents, my sister, and me.", "Person A: That's nice!", "Person B: Yes, we are close."]},
            {"lines": ["Person A: What does your mother do?", "Person B: She is a nurse.", "Person A: That's a good job.", "Person B: She helps sick people."]},
            {"lines": ["Person A: Do you have any pets?", "Person B: Yes, we have a dog named Max.", "Person A: What breed?", "Person B: He is a golden retriever."]},
            {"lines": ["Person A: When is your father's birthday?", "Person B: It's on March 15th.", "Person A: What will you give him?", "Person B: I'll give him a book."]},
            {"lines": ["Person A: Who do you look like?", "Person B: I look like my mother.", "Person A: Does she have the same hair?", "Person B: Yes, we both have curly hair."]},
            {"lines": ["Person A: Do you live with your family?", "Person B: No, I live alone.", "Person A: Do you miss them?", "Person B: Yes, I call them every day."]}
        ]
    },
    "numbers": {
        "name": "Numbers & Counting",
        "sentences": [
            "I have two cats.",
            "There are five apples on the table.",
            "My phone number is 555-0123.",
            "I am twenty-five years old.",
            "She has three brothers.",
            "We live at 10 Downing Street.",
            "I need six eggs, please.",
            "The bus comes at eight o'clock.",
            "There are twelve months in a year.",
            "I have twenty dollars.",
            "One plus two equals three.",
            "I want four slices of pizza.",
            "My classroom has thirty students.",
            "I wake up at seven every day.",
            "She reads fifty pages a day.",
            "There are seven days in a week.",
            "I have fifteen friends.",
            "The train leaves at nine.",
            "I bought twenty apples.",
            "My sister is three years older.",
            "I need one hundred dollars.",
            "There are twenty-four hours in a day.",
            "I have sixty minutes for lunch.",
            "My school has four hundred students.",
            "I am the first in line.",
            "She is second in the race.",
            "I live on the third floor.",
            "He is number ten on the team.",
            "We have fifteen minutes left.",
            "I eat three meals a day.",
            "My dog has four legs.",
            "There are ten fingers on my hands.",
            "I have two hands.",
            "My sister has two eyes.",
            "We have three classes today.",
            "I need five more minutes.",
            "The test has ten questions.",
            "I scored nine out of ten.",
            "There are six colors in the rainbow.",
            "I want to buy seven books.",
            "My family has four people.",
            "I walk two miles every day.",
            "She has eleven cousins.",
            "We celebrate on December 25th.",
            "The meeting is at three o'clock.",
            "I have eight pairs of shoes.",
            "My teacher is thirty-five years old.",
            "I have two best friends.",
            "There are nine planets in space.",
            "I need three tickets, please."
        ],
        "dialogues": [
            {"lines": ["Person A: How old are you?", "Person B: I'm twenty-two.", "Person A: And where do you live?", "Person B: I live at 45 Park Street."]},
            {"lines": ["Person A: What time is it?", "Person B: It's half past three.", "Person A: I have a meeting at four.", "Person B: You have thirty minutes then."]},
            {"lines": ["Person A: How many people are coming?", "Person B: Fifteen confirmed.", "Person A: Do we have enough chairs?", "Person B: Yes, we have twenty."]},
            {"lines": ["Person A: What's your phone number?", "Person B: It's 555-0198.", "Person A: Can you repeat that?", "Person B: Sure, 555-0198."]},
            {"lines": ["Person A: How much is this shirt?", "Person B: It's twenty-five dollars.", "Person A: That's a good price!", "Person B: Yes, it's on sale."]},
            {"lines": ["Person A: What time does the bus come?", "Person B: At eight fifteen.", "Person A: I'll be late for work.", "Person B: Take a taxi instead."]},
            {"lines": ["Person A: How many students are in your class?", "Person B: There are thirty-two.", "Person A: That's a big class!", "Person B: Yes, it's very crowded."]},
            {"lines": ["Person A: Can I have three apples, please?", "Person B: Sure. That's one dollar fifty.", "Person A: Here you go.", "Person B: Thank you! Have a nice day."]},
            {"lines": ["Person A: What time do you wake up?", "Person B: At six thirty.", "Person A: That's early!", "Person B: I have to catch the seven o'clock bus."]},
            {"lines": ["Person A: How many questions are on the test?", "Person B: Twenty-five.", "Person A: How long is the test?", "Person B: Forty-five minutes."]}
        ]
    },
    "colors": {
        "name": "Colors",
        "sentences": [
            "The sky is blue.",
            "I like the color red.",
            "My car is black.",
            "The grass is green.",
            "She has brown hair.",
            "I want a white shirt.",
            "The sun is yellow.",
            "My favorite color is purple.",
            "That flower is pink.",
            "The cat is orange.",
            "I see a gray bird.",
            "The book is green.",
            "My eyes are brown.",
            "The house is white.",
            "I like dark blue.",
            "She wears a red dress.",
            "The table is brown.",
            "My phone is silver.",
            "The shoes are black.",
            "I see colorful flowers.",
            "The rainbow has seven colors.",
            "Orange is a nice color.",
            "I painted my room blue.",
            "Her jacket is yellow.",
            "The pillow is soft and white.",
            "My pen is purple.",
            "The car is fast and red.",
            "I like light green.",
            "The tree has brown bark.",
            "My bag is dark gray.",
            "She loves pink flowers.",
            "The wall is cream colored.",
            "I see a blue butterfly.",
            "The dress is very elegant.",
            "My favorite shirt is striped.",
            "The sunset is beautiful.",
            "I like simple colors.",
            "The toy is colorful.",
            "My notebook is yellow.",
            "The carpet is dark red.",
            "I prefer warm colors.",
            "She chose a pink balloon.",
            "The walls are light blue.",
            "My glasses are brown.",
            "The shoes are white.",
            "I love purple flowers.",
            "The car is very shiny.",
            "My room is painted green.",
            "I see a rainbow.",
            "The colors are bright."
        ],
        "dialogues": [
            {"lines": ["Person A: What is your favorite color?", "Person B: I like blue.", "Person A: Me too! I love the sky.", "Person B: Yes, it's beautiful."]},
            {"lines": ["Person A: What color is your car?", "Person B: It's red.", "Person A: Nice! Red is a good color.", "Person B: Thank you! I like it."]},
            {"lines": ["Person A: Can I have the blue pen?", "Person B: Sure. Here you go.", "Person A: Do you have a red one too?", "Person B: Yes, I do."]},
            {"lines": ["Person A: What color are her eyes?", "Person B: They are green.", "Person A: Wow, that's rare!", "Person B: Yes, she has beautiful eyes."]},
            {"lines": ["Person A: I like your yellow shirt.", "Person B: Thanks! It's my favorite.", "Person A: Yellow looks good on you.", "Person B: You're so kind!"]},
            {"lines": ["Person A: What color do you want?", "Person B: I'll take the white one.", "Person A: Great choice!", "Person B: Thank you."]},
            {"lines": ["Person A: My room is blue.", "Person B: Mine is green.", "Person A: I like both colors.", "Person B: They look nice together."]},
            {"lines": ["Person A: Look at that purple flower!", "Person B: It's beautiful!", "Person A: I want to pick it.", "Person B: Don't, it's protected."]},
            {"lines": ["Person A: What color is the sky now?", "Person B: It's orange. Sunset!", "Person A: It's so pretty!", "Person B: I love this time of day."]},
            {"lines": ["Person A: Do you like pink?", "Person B: Yes, it's very pretty.", "Person A: I prefer green.", "Person B: Both are nice colors."]}
        ]
    },
    "time": {
        "name": "Time & Schedules",
        "sentences": [
            "I wake up at seven o'clock.",
            "Breakfast is at eight.",
            "School starts at nine.",
            "Lunch is at twelve.",
            "I finish school at three.",
            "Dinner is at six.",
            "I go to bed at ten.",
            "What time is it?",
            "It is half past two.",
            "It's quarter to four.",
            "It's quarter past five.",
            "It's nine thirty.",
            "The movie starts at seven.",
            "I have a meeting at ten.",
            "Let's meet at noon.",
            "The bus comes at eight fifteen.",
            "I exercise in the morning.",
            "She reads before bed.",
            "I work from nine to five.",
            "We eat lunch at noon.",
            "The shop opens at nine.",
            "The shop closes at six.",
            "I have class on Monday.",
            "Today is Tuesday.",
            "Tomorrow is Wednesday.",
            "Yesterday was Sunday.",
            "I was born in January.",
            "Christmas is in December.",
            "Summer starts in June.",
            "My birthday is in March.",
            "I have a dentist appointment on Friday.",
            "The concert is next Saturday.",
            "I'm meeting friends tonight.",
            "Let's have lunch tomorrow.",
            "I need more time.",
            "Time flies when you're having fun.",
            "I'm always on time.",
            "Don't be late!",
            "The meeting is at 3:30.",
            "I'll be there in five minutes.",
            "How long does it take?",
            "It takes about ten minutes.",
            "The class lasts one hour.",
            "I have free time on weekends.",
            "Let's check the schedule.",
            "What's the plan for today?",
            "First, we have English.",
            "Then, we have math.",
            "After lunch, we have art.",
            "Finally, we go home."
        ],
        "dialogues": [
            {"lines": ["Person A: What time is it?", "Person B: It's half past two.", "Person A: When does the movie start?", "Person B: At three o'clock."]},
            {"lines": ["Person A: Do you have class today?", "Person B: Yes, at nine.", "Person A: What class?", "Person B: English. I'm excited!"]},
            {"lines": ["Person A: Let's meet for lunch.", "Person B: Sure! What time?", "Person A: How about noon?", "Person B: Perfect! See you then."]},
            {"lines": ["Person A: What time do you wake up?", "Person B: At six.", "Person A: That's so early!", "Person B: I have to catch the bus."]},
            {"lines": ["Person A: When is your birthday?", "Person B: It's on October 15th.", "Person A: What will you do?", "Person B: I'll have a party!"]},
            {"lines": ["Person A: How long is the movie?", "Person B: About two hours.", "Person A: It starts at seven.", "Person B: So it ends at nine."]},
            {"lines": ["Person A: What's the schedule today?", "Person B: English at nine, math at ten.", "Person A: Lunch at twelve?", "Person B: Yes, then science at one."]},
            {"lines": ["Person A: When does the shop close?", "Person B: At six.", "Person A: I need to hurry!", "Person B: You have twenty minutes."]},
            {"lines": ["Person A: Do you have time this weekend?", "Person B: Yes, I'm free on Saturday.", "Person A: Let's go to the park!", "Person B: Great idea!"]},
            {"lines": ["Person A: What time does the train leave?", "Person B: At 4:45.", "Person A: We should leave soon.", "Person B: Yes, let's go now!"]}
        ]
    },
    "daily_routine": {
        "name": "Daily Routine",
        "sentences": [
            "I wake up early.",
            "I brush my teeth.",
            "I take a shower.",
            "I get dressed.",
            "I eat breakfast.",
            "I drink coffee.",
            "I go to school.",
            "I do my homework.",
            "I eat lunch.",
            "I play outside.",
            "I watch TV.",
            "I eat dinner.",
            "I read a book.",
            "I go to bed.",
            "I sleep well.",
            "I set my alarm.",
            "I make my bed.",
            "I wash my face.",
            "I comb my hair.",
            "I put on my shoes.",
            "I pack my bag.",
            "I catch the bus.",
            "I walk to school.",
            "I have PE class.",
            "I eat an apple.",
            "I drink water.",
            "I talk to my friends.",
            "I study English.",
            "I help my mom.",
            "I clean my room.",
            "I water the plants.",
            "I walk the dog.",
            "I cook dinner.",
            "I wash the dishes.",
            "I dry the dishes.",
            "I put away laundry.",
            "I call my friend.",
            "I play games.",
            "I listen to music.",
            "I write in my diary.",
            "I take a break.",
            "I eat a snack.",
            "I brush my hair.",
            "I check my email.",
            "I charge my phone.",
            "I turn off the lights.",
            "I say goodnight.",
            "I dream about flying.",
            "I sleep for eight hours.",
            "I am ready for tomorrow."
        ],
        "dialogues": [
            {"lines": ["Person A: What time do you wake up?", "Person B: At seven.", "Person A: What do you do first?", "Person B: I brush my teeth."]},
            {"lines": ["Person A: Do you eat breakfast?", "Person B: Yes, I eat cereal.", "Person A: What do you drink?", "Person B: I drink orange juice."]},
            {"lines": ["Person A: What do you do after school?", "Person B: I do my homework.", "Person A: How long does it take?", "Person B: About one hour."]},
            {"lines": ["Person A: Do you help at home?", "Person B: Yes, I wash the dishes.", "Person A: That's nice!", "Person B: I also clean my room."]},
            {"lines": ["Person A: What time do you go to bed?", "Person B: At nine thirty.", "Person A: Do you read before bed?", "Person B: Yes, I read for thirty minutes."]},
            {"lines": ["Person A: What do you do in the morning?", "Person B: I take a shower and get dressed.", "Person A: Do you eat breakfast?", "Person B: Yes, I eat toast and eggs."]},
            {"lines": ["Person A: Do you exercise?", "Person B: Yes, I jog in the morning.", "Person A: How often?", "Person B: Every day, for thirty minutes."]},
            {"lines": ["Person A: What do you do on weekends?", "Person B: I play video games.", "Person A: Do you do homework too?", "Person B: Yes, on Sunday evening."]},
            {"lines": ["Person A: Do you walk to school?", "Person B: No, I take the bus.", "Person A: What time does it come?", "Person B: At eight fifteen."]},
            {"lines": ["Person A: What's the last thing you do?", "Person B: I brush my teeth.", "Person A: Me too! Good night!", "Person B: Good night! Sleep well!"]}
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
            "Do you want some tea?",
            "I love chocolate ice cream.",
            "Please pass me the salt.",
            "I'm hungry.",
            "I'm thirsty.",
            "Let's have dinner together.",
            "What would you like to eat?",
            "I'll have the chicken, please.",
            "Is there any milk?",
            "I need two eggs.",
            "The soup is hot.",
            "I like my coffee with sugar.",
            "Do you have any fruit?",
            "Yes, we have apples and pears.",
            "I don't eat meat.",
            "I'm a vegetarian.",
            "Can I see the menu?",
            "What do you recommend?",
            "The fish is fresh today.",
            "I'll have a glass of water.",
            "How much is the pizza?",
            "I want a small salad.",
            "Add some pepper, please.",
            "The bread is delicious.",
            "I eat rice every day.",
            "I like to cook.",
            "My mom makes great pasta.",
            "I want to try sushi.",
            "Do you like spicy food?",
            "No, I don't like spicy food.",
            "I prefer sweet food.",
            "The cake is for you.",
            "Happy birthday! Make a wish!",
            "I'll have dessert later.",
            "Can I have the bill, please?",
            "Thank you, the food was great!",
            "I had a wonderful meal.",
            "Let's eat!",
            "Enjoy your meal!",
            "The food smells good!",
            "I'm full now."
        ],
        "dialogues": [
            {"lines": ["Person A: What would you like to eat?", "Person B: I'd like a sandwich, please.", "Person A: Would you like something to drink?", "Person B: Yes, a glass of orange juice."]},
            {"lines": ["Person A: Do you like pizza?", "Person B: Yes, I love it!", "Person A: What toppings do you want?", "Person B: I want cheese and tomato."]},
            {"lines": ["Person A: Are you hungry?", "Person B: Yes, very!", "Person A: Let's go to the restaurant.", "Person B: Great idea! I'm starving!"]},
            {"lines": ["Person A: What time do you eat lunch?", "Person B: At twelve.", "Person A: Where do you eat?", "Person B: In the school cafeteria."]},
            {"lines": ["Person A: Can I have some water?", "Person B: Sure. Still or sparkling?", "Person A: Still, please.", "Person B: Here you go."]},
            {"lines": ["Person A: Do you cook?", "Person B: Yes, I cook dinner.", "Person A: What do you make?", "Person B: I make pasta and salad."]},
            {"lines": ["Person A: How much is the coffee?", "Person B: It's three dollars.", "Person A: Here you go.", "Person B: Thank you! Enjoy!"]},
            {"lines": ["Person A: What's your favorite food?", "Person B: I love chocolate!", "Person A: Me too! It's delicious.", "Person B: Let's have some later."]},
            {"lines": ["Person A: Do you want some tea?", "Person B: No, thank you.", "Person A: Coffee?", "Person B: Yes, please. With milk."]},
            {"lines": ["Person A: The food is ready!", "Person B: It smells amazing!", "Person A: Let's eat together.", "Person B: I'm so hungry!"]}
        ]
    },
    "shopping": {
        "name": "Shopping",
        "sentences": [
            "I need to buy new shoes.",
            "How much is this?",
            "Can I try this on?",
            "Do you have this in blue?",
            "I'll take this one, please.",
            "Where is the fitting room?",
            "The store is open until nine.",
            "I'm just looking, thanks.",
            "Do you accept credit cards?",
            "This is too expensive.",
            "I want to return this.",
            "Do you have a receipt?",
            "Can I get a refund?",
            "I'm looking for a gift.",
            "What size do you wear?",
            "I wear size medium.",
            "This is on sale!",
            "How much does this cost?",
            "I have a coupon.",
            "That's a good deal!",
            "I need a bigger size.",
            "I need a smaller size.",
            "Do you have a fitting room?",
            "I'll buy two of these.",
            "Where is the checkout?",
            "Is there a discount?",
            "I'm shopping for clothes.",
            "I'm looking for shoes.",
            "Do you have bags?",
            "I need a gift bag.",
            "Can I pay with cash?",
            "Do you have change?",
            "The shirt is nice.",
            "I like this color.",
            "How much for both?",
            "Can I use my card?",
            "Do you ship online?",
            "What are your hours?",
            "When do you open?",
            "The shop is closed today.",
            "I want to buy flowers.",
            "These flowers are beautiful.",
            "I'll take the red ones.",
            "That's twenty dollars total.",
            "Here's your change.",
            "Thank you very much!",
            "Have a nice day!",
            "I'll come back tomorrow.",
            "This is my favorite store.",
            "I love shopping here!"
        ],
        "dialogues": [
            {"lines": ["Person A: How much is this shirt?", "Person B: It's twenty dollars.", "Person A: I'll take it!", "Person B: Great choice!"]},
            {"lines": ["Person A: Can I try this on?", "Person B: Of course. The fitting room is over there.", "Person A: Thank you!", "Person B: Let me know if you need help."]},
            {"lines": ["Person A: Do you have this in size large?", "Person B: Yes, we do.", "Person A: Can I see it?", "Person B: Sure! Here you go."]},
            {"lines": ["Person A: I'm looking for a gift.", "Person B: What kind of gift?", "Person A: For my mother.", "Person B: We have nice scarves."]},
            {"lines": ["Person A: Do you accept credit cards?", "Person B: Yes, we accept all cards.", "Person A: Perfect!", "Person B: Your total is fifteen dollars."]},
            {"lines": ["Person A: Can I return this?", "Person B: Do you have the receipt?", "Person A: Yes, here it is.", "Person B: Sure, I'll give you a refund."]},
            {"lines": ["Person A: I'm just looking.", "Person B: Okay, let me know if you need help.", "Person A: Thanks!", "Person B: Take your time."]},
            {"lines": ["Person A: Is this on sale?", "Person B: Yes, it's 50% off!", "Person A: That's a great deal!", "Person B: Yes, buy it now!"]},
            {"lines": ["Person A: Where is the checkout?", "Person B: It's at the front.", "Person A: Thank you.", "Person B: Have a nice day!"]},
            {"lines": ["Person A: I need shopping bags.", "Person B: Sure, paper or plastic?", "Person A: Paper, please.", "Person B: Here you go. That's fifty cents."]}
        ]
    },
    "travel": {
        "name": "Travel & Directions",
        "sentences": [
            "Where is the train station?",
            "I need a taxi, please.",
            "How do I get to the airport?",
            "Turn left at the corner.",
            "Go straight for two blocks.",
            "The hotel is on Main Street.",
            "I need to buy a ticket.",
            "What platform is the train?",
            "How long is the journey?",
            "I have a reservation.",
            "Can I have a map, please?",
            "Where is the nearest subway?",
            "I'm lost. Can you help me?",
            "Where are you from?",
            "I'm a tourist here.",
            "How far is it to the beach?",
            "Let's take a taxi.",
            "The bus stop is over there.",
            "I want to visit the museum.",
            "What time does the train leave?",
            "The flight is delayed.",
            "I need to check in.",
            "Where is my gate?",
            "Boarding starts at ten.",
            "Where is baggage claim?",
            "I lost my passport!",
            "I need to call the embassy.",
            "Where can I exchange money?",
            "I need a room for two nights.",
            "Is breakfast included?",
            "What is the Wi-Fi password?",
            "Can I have the key, please?",
            "I want to check out.",
            "Where is the elevator?",
            "How do I use this machine?",
            "Can you take my photo?",
            "What is this place?",
            "I love this city!",
            "The weather is beautiful here.",
            "I want to try local food.",
            "Where is the best restaurant?",
            "How much is a ticket?",
            "I want a round trip ticket.",
            "Do I need a visa?",
            "Where is customs?",
            "I have nothing to declare.",
            "My flight is at noon.",
            "The plane is on time.",
            "I love to travel.",
            "I want to see the world!"
        ],
        "dialogues": [
            {"lines": ["Person A: Excuse me, where is the train station?", "Person B: Go straight, then turn right.", "Person A: How far is it?", "Person B: About ten minutes."]},
            {"lines": ["Person A: I need a taxi.", "Person B: Where to?", "Person A: The airport, please.", "Person B: No problem. It's twenty dollars."]},
            {"lines": ["Person A: Do you have a map?", "Person B: Yes, here you go.", "Person A: Thank you! I'm a tourist.", "Person B: Welcome to our city!"]},
            {"lines": ["Person A: What time does the bus leave?", "Person B: At three thirty.", "Person A: I have a question.", "Person B: Go ahead!"]},
            {"lines": ["Person A: Can I help you? You look lost.", "Person B: Yes, please. Where is the hotel?", "Person A: Turn left, it's on your right.", "Person B: Thank you so much!"]},
            {"lines": ["Person A: How do I get to the museum?", "Person B: Take bus number five.", "Person A: Where do I catch it?", "Person B: The stop is across the street."]},
            {"lines": ["Person A: I'd like to book a room.", "Person B: For how many nights?", "Person A: Three nights.", "Person B: That's $150 total."]},
            {"lines": ["Person A: Where is baggage claim?", "Person B: Follow the signs.", "Person A: I can't find my suitcase.", "Person B: Let me help you."]},
            {"lines": ["Person A: Can you take our photo?", "Person B: Sure! Where do you want it?", "Person A: In front of the statue.", "Person B: Say cheese!"]},
            {"lines": ["Person A: What time is check-in?", "Person B: At 3 PM.", "Person A: Can I check in early?", "Person B: Let me check for you."]}
        ]
    },
    "weather": {
        "name": "Weather",
        "sentences": [
            "It is sunny today.",
            "It is raining outside.",
            "The weather is nice.",
            "It is very cold.",
            "It is hot today.",
            "I need an umbrella.",
            "It is cloudy.",
            "The wind is strong.",
            "It is snowing!",
            "I love sunny days.",
            "It is humid today.",
            "The weather is terrible.",
            "It is windy.",
            "I need a jacket.",
            "It is warm today.",
            "The sun is shining.",
            "It is foggy outside.",
            "I can't see anything.",
            "The storm is coming.",
            "Stay inside!",
            "It is freezing cold.",
            "My hands are cold.",
            "I need hot chocolate.",
            "The snow is beautiful.",
            "Let's build a snowman!",
            "I love rainy days.",
            "The puddles are fun.",
            "I like jumping in puddles.",
            "The rainbow is beautiful.",
            "It is partly cloudy.",
            "What's the temperature?",
            "It is twenty degrees.",
            "It is very warm.",
            "The weather is perfect.",
            "I love this weather!",
            "It is a beautiful day.",
            "Let's go to the beach!",
            "I need sunscreen.",
            "The sun is very strong.",
            "I'm going to get sunburned.",
            "The weather changes fast.",
            "It might rain later.",
            "Check the forecast.",
            "What will the weather be?",
            "It will be sunny tomorrow.",
            "I hope it doesn't rain.",
            "The storm passed.",
            "The weather is calm now.",
            "I love all seasons.",
            "The weather is great!"
        ],
        "dialogues": [
            {"lines": ["Person A: How's the weather today?", "Person B: It's sunny and warm.", "Person A: Perfect for a walk!", "Person B: Yes, let's go outside."]},
            {"lines": ["Person A: Do you have an umbrella?", "Person B: Yes, it's in my bag.", "Person A: It might rain.", "Person B: Good idea to bring it."]},
            {"lines": ["Person A: It's very cold today!", "Person B: Yes, wear a warm coat.", "Person A: I forgot my gloves.", "Person B: You can borrow mine."]},
            {"lines": ["Person A: Look! It's snowing!", "Person B: How exciting!", "Person A: Let's make a snowman!", "Person B: Yes! Let's go!"]},
            {"lines": ["Person A: What's the weather like tomorrow?", "Person B: It will be rainy.", "Person A: Oh no, I hate rain.", "Person B: Bring an umbrella."]},
            {"lines": ["Person A: It's really hot today.", "Person B: Yes, very humid.", "Person A: Let's go swimming.", "Person B: Great idea!"]},
            {"lines": ["Person A: The weather is beautiful!", "Person B: Yes, it's perfect.", "Person A: Let's have a picnic.", "Person B: I'll bring the food!"]},
            {"lines": ["Person A: Is it going to rain?", "Person B: The forecast says yes.", "Person A: I'll bring my umbrella.", "Person B: Smart choice."]},
            {"lines": ["Person A: I love autumn.", "Person B: Me too. The leaves are beautiful.", "Person A: And the weather is nice.", "Person B: Not too hot, not too cold."]},
            {"lines": ["Person A: What season do you like?", "Person B: I love summer.", "Person A: Me too! Beach time!", "Person B: Yes! I love the sun!"]}
        ]
    },
    "health": {
        "name": "Health & Doctor",
        "sentences": [
            "I don't feel well.",
            "I have a headache.",
            "I have a cold.",
            "I need to see a doctor.",
            "Take this medicine.",
            "You need to rest.",
            "I have a fever.",
            "My stomach hurts.",
            "I feel dizzy.",
            "Call an ambulance!",
            "How are you feeling?",
            "I feel much better.",
            "You look sick.",
            "I need some water.",
            "Please sit down.",
            "Take deep breaths.",
            "I have allergies.",
            "I'm allergic to peanuts.",
            "I wear glasses.",
            "My back hurts.",
            "I have a toothache.",
            "I need to go to the dentist.",
            "I feel tired today.",
            "I didn't sleep well.",
            "I have sore muscles.",
            "I went jogging this morning.",
            "Exercise is good for health.",
            "I eat healthy food.",
            "Vegetables are good for you.",
            "I drink eight glasses of water.",
            "I don't smoke.",
            "I don't drink alcohol.",
            "I go to the gym.",
            "I feel strong and healthy.",
            "The doctor is busy.",
            "When is my appointment?",
            "I need to make a call.",
            "The nurse is very kind.",
            "My temperature is normal.",
            "I need a checkup.",
            "I feel much better now.",
            "Thank you, doctor.",
            "When should I come back?",
            "Take care of yourself.",
            "I hope you get well soon.",
            "Thank you for your help.",
            "Health is very important.",
            "I want to stay healthy.",
            "Prevention is better than cure.",
            "I love being healthy!"
        ],
        "dialogues": [
            {"lines": ["Person A: What's wrong?", "Person B: I have a headache.", "Person A: Take some medicine.", "Person B: Thank you, I will."]},
            {"lines": ["Person A: How are you feeling today?", "Person B: I feel much better.", "Person A: That's great news!", "Person B: Yes, the medicine helped."]},
            {"lines": ["Person A: I don't feel well.", "Person B: What's the matter?", "Person A: My stomach hurts.", "Person B: You should see a doctor."]},
            {"lines": ["Person A: Do you exercise?", "Person B: Yes, three times a week.", "Person A: What do you do?", "Person B: I jog and do yoga."]},
            {"lines": ["Person A: Take this medicine twice a day.", "Person B: With food?", "Person A: Yes, after breakfast and dinner.", "Person B: Okay, thank you."]},
            {"lines": ["Person A: I need to make an appointment.", "Person B: Sure. When are you free?", "Person A: How about Monday?", "Person B: Monday at 10 AM."]},
            {"lines": ["Person A: You look pale.", "Person B: I feel tired.", "Person A: You should rest.", "Person B: I think you're right."]},
            {"lines": ["Person A: Are you allergic to anything?", "Person B: Yes, peanuts.", "Person A: I'll note that down.", "Person B: Thank you."]},
            {"lines": ["Person A: What time is my appointment?", "Person B: At 2:30.", "Person A: Do I need to arrive early?", "Person B: Yes, 15 minutes early."]},
            {"lines": ["Person A: Get well soon!", "Person B: Thank you! I'm almost better.", "Person A: That's wonderful!", "Person B: I feel great now!"]}
        ]
    },
    "work": {
        "name": "Work & Jobs",
        "sentences": [
            "I am a teacher.",
            "She is a doctor.",
            "He is a lawyer.",
            "I work in an office.",
            "I work from home.",
            "What do you do for a living?",
            "I start work at nine.",
            "I finish work at five.",
            "I have a meeting today.",
            "My boss is very nice.",
            "I like my job.",
            "I need a new job.",
            "Can you send me the report?",
            "The deadline is Friday.",
            "I'm very busy today.",
            "I have too much work.",
            "Let's have a meeting.",
            "Please check your email.",
            "I'm going on a business trip.",
            "I work hard every day.",
            "My colleague is helpful.",
            "I love my coworkers.",
            "The office is very quiet.",
            "I need a vacation.",
            "I want to get promoted.",
            "I work in marketing.",
            "She works in finance.",
            "He works in IT.",
            "I'm looking for a job.",
            "Here is my resume.",
            "The interview is tomorrow.",
            "I want a higher salary.",
            "I work overtime sometimes.",
            "My job is stressful.",
            "I need better work-life balance.",
            "I enjoy working with people.",
            "I'm a good team player.",
            "I have important skills.",
            "I'm organized and efficient.",
            "I communicate well.",
            "I'm a leader.",
            "I solve problems.",
            "I'm very creative.",
            "I'm always learning.",
            "I'm professional.",
            "I'm dedicated.",
            "I'm responsible.",
            "I'm reliable.",
            "I'm honest.",
            "I'm hardworking.",
            "I'm passionate about my work."
        ],
        "dialogues": [
            {"lines": ["Person A: What do you do?", "Person B: I'm a teacher.", "Person A: What subject?", "Person B: I teach English."]},
            {"lines": ["Person A: Do you like your job?", "Person B: Yes, I love it!", "Person A: What do you like most?", "Person B: I like helping people."]},
            {"lines": ["Person A: What time do you start work?", "Person B: At nine.", "Person A: Do you work late?", "Person B: Sometimes, until six."]},
            {"lines": ["Person A: I have an interview tomorrow.", "Person B: Good luck! What job?", "Person A: Marketing manager.", "Person B: You'll do great!"]},
            {"lines": ["Person A: Can you send me the report?", "Person B: Sure. When do you need it?", "Person A: By Friday, please.", "Person B: I'll send it tomorrow."]},
            {"lines": ["Person A: Where do you work?", "Person B: I work downtown.", "Person A: How do you get there?", "Person B: I take the subway."]},
            {"lines": ["Person A: I'm going to quit.", "Person B: Why? What happened?", "Person A: I found a better job.", "Person B: Congratulations!"]},
            {"lines": ["Person A: Are you busy today?", "Person B: Yes, I have three meetings.", "Person A: Can we talk later?", "Person B: Yes, after lunch."]},
            {"lines": ["Person A: I need a raise.", "Person B: Talk to your boss.", "Person A: I'm nervous.", "Person B: You deserve it!"]},
            {"lines": ["Person A: How was work?", "Person B: It was good. I finished my project.", "Person A: Great job!", "Person B: Thank you! I worked hard."]}
        ]
    },
    "hobbies": {
        "name": "Hobbies & Free Time",
        "sentences": [
            "I like reading books.",
            "I love playing football.",
            "She likes painting.",
            "He enjoys cooking.",
            "We like watching movies.",
            "I play the guitar.",
            "I love listening to music.",
            "She dances very well.",
            "I like taking photos.",
            "He enjoys fishing.",
            "I like swimming in the pool.",
            "She loves gardening.",
            "I play video games.",
            "He likes hiking.",
            "We enjoy camping.",
            "I like doing puzzles.",
            "She loves writing stories.",
            "I like collecting stamps.",
            "He enjoys playing chess.",
            "I love dancing.",
            "I like singing songs.",
            "She enjoys reading magazines.",
            "I like watching sports.",
            "He enjoys playing basketball.",
            "I like riding my bike.",
            "She loves making crafts.",
            "I enjoy walking in the park.",
            "He likes building things.",
            "I like playing cards.",
            "She enjoys knitting.",
            "I love traveling.",
            "He enjoys photography.",
            "I like playing tennis.",
            "She loves yoga.",
            "I enjoy meditation.",
            "He likes running.",
            "I like playing the piano.",
            "She enjoys cooking Italian food.",
            "I love making art.",
            "He enjoys watching documentaries.",
            "I like learning languages.",
            "She loves doing yoga.",
            "I enjoy going to the gym.",
            "He likes playing video games.",
            "I like gardening.",
            "She enjoys painting pictures.",
            "I love reading comics.",
            "He enjoys playing sports.",
            "I like doing exercise.",
            "She loves having fun!"
        ],
        "dialogues": [
            {"lines": ["Person A: What do you do in your free time?", "Person B: I like reading books.", "Person A: What kind of books?", "Person B: I love detective stories."]},
            {"lines": ["Person A: Do you play any sports?", "Person B: Yes, I play football.", "Person A: How often do you play?", "Person B: Every Saturday with friends."]},
            {"lines": ["Person A: What are your hobbies?", "Person B: I like painting and dancing.", "Person A: That's creative!", "Person B: Yes, it makes me happy."]},
            {"lines": ["Person A: Do you like music?", "Person B: Yes, I play the guitar.", "Person A: Can you play a song?", "Person B: Sure, I'll play for you."]},
            {"lines": ["Person A: What do you do on weekends?", "Person B: I watch movies.", "Person A: What kind of movies?", "Person B: I love comedies."]},
            {"lines": ["Person A: Do you like cooking?", "Person B: Yes, I love it!", "Person A: What do you cook?", "Person B: I make pasta and pizza."]},
            {"lines": ["Person A: Do you have any hobbies?", "Person B: Yes, I like taking photos.", "Person A: What do you photograph?", "Person B: Nature and animals."]},
            {"lines": ["Person A: What games do you play?", "Person B: I play video games.", "Person A: What's your favorite?", "Person B: I love adventure games."]},
            {"lines": ["Person A: Do you exercise?", "Person B: Yes, I go to the gym.", "Person A: How often?", "Person B: Three times a week."]},
            {"lines": ["Person A: I love traveling!", "Person B: Me too! Where have you been?", "Person A: I went to Japan.", "Person B: I want to go there!"]}
        ]
    },
    "animals": {
        "name": "Animals & Pets",
        "sentences": [
            "I have a dog.",
            "Cats are cute.",
            "The bird is singing.",
            "I like horses.",
            "The fish is swimming.",
            "She has a rabbit.",
            "He likes turtles.",
            "The snake is dangerous.",
            "I love animals.",
            "Dogs are loyal.",
            "Cats are independent.",
            "Birds can fly.",
            "Fish live in water.",
            "Rabbits are soft.",
            "Horses are strong.",
            "Turtles are slow.",
            "Snakes are scary.",
            "Monkeys are funny.",
            "Elephants are huge.",
            "Lions are kings of the jungle.",
            "Penguins live in cold places.",
            "Dolphins are smart.",
            "Whales are the biggest.",
            "Bears are very strong.",
            "Giraffes have long necks.",
            "Zebras are black and white.",
            "Kangaroos jump very high.",
            "Owls are wise.",
            "Butterflies are beautiful.",
            "Bees make honey.",
            "Ants are tiny.",
            "Spiders have eight legs.",
            "Frogs can jump.",
            "Cows give us milk.",
            "Chickens lay eggs.",
            "Sheep give us wool.",
            "Pigs are pink.",
            "I love my pet.",
            "My dog is my best friend.",
            "I feed my cat every day.",
            "I walk my dog in the park.",
            "My cat likes to sleep.",
            "My bird can sing.",
            "I love to play with animals.",
            "Animals need love too.",
            "Be kind to animals.",
            "I want a puppy!",
            "My pet is very cute.",
            "Animals are amazing!",
            "I love all animals!"
        ],
        "dialogues": [
            {"lines": ["Person A: Do you have a pet?", "Person B: Yes, I have a dog.", "Person A: What's its name?", "Person B: His name is Max."]},
            {"lines": ["Person A: I love cats!", "Person B: Me too! They're so cute.", "Person A: How many cats do you have?", "Person B: I have two cats."]},
            {"lines": ["Person A: What's your favorite animal?", "Person B: I love dolphins.", "Person A: They are smart!", "Person B: Yes, and they're friendly."]},
            {"lines": ["Person A: Can I pet your dog?", "Person B: Yes, he's friendly.", "Person A: He's so cute!", "Person B: Thank you! He loves people."]},
            {"lines": ["Person A: Do you like birds?", "Person B: Yes, they're beautiful.", "Person A: Do you have any?", "Person B: Yes, a parrot named Polly."]},
            {"lines": ["Person A: I want to get a pet.", "Person B: What kind?", "Person A: I'm thinking about a cat.", "Person B: Cats are great pets!"]},
            {"lines": ["Person A: What animals do you see in the zoo?", "Person B: Lions, elephants, and giraffes.", "Person A: Which one is your favorite?", "Person B: I love the elephants!"]},
            {"lines": ["Person A: Do you like snakes?", "Person B: No, I'm scared of them.", "Person A: They're interesting though.", "Person B: Maybe, but from far away!"]},
            {"lines": ["Person A: How do you take care of your dog?", "Person B: I feed him and walk him.", "Person A: How often do you walk him?", "Person B: Every morning and evening."]},
            {"lines": ["Person A: What's the name of your cat?", "Person B: Her name is Luna.", "Person A: That's a pretty name!", "Person B: Thank you! She's a pretty cat."]}
        ]
    }
}


class PracticeGenerator:
    def __init__(self, output_dir="audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_sentence_audio(self, topic_id, sentence_num, sentence, voice):
        """Generate audio for a single sentence with specific voice."""
        import edge_tts
        
        filename = f"sentence_{sentence_num:02d}.mp3"
        filepath = self.output_dir / topic_id / filename
        
        try:
            communicate = edge_tts.Communicate(sentence, voice)
            await communicate.save(str(filepath))
            return filename
        except Exception as e:
            print(f"  Error generating {filename}: {e}")
            return None
    
    async def generate_dialogue_audio(self, topic_id, dialogue_num, lines):
        """Generate audio for a dialogue with two voices."""
        import edge_tts
        import tempfile
        import os
        
        filename = f"dialogue_{dialogue_num:02d}.mp3"
        filepath = self.output_dir / topic_id / filename
        
        temp_files = []
        voices_used = []
        
        try:
            # Create temporary audio files for each line
            for i, line in enumerate(lines):
                temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                temp_files.append(temp_file.name)
                
                if line.startswith("Person A:"):
                    voice = DIALOGUE_VOICES["A"]
                    text = line.replace("Person A:", "").strip()
                else:
                    voice = DIALOGUE_VOICES["B"]
                    text = line.replace("Person B:", "").strip()
                
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(temp_file.name)
                voices_used.append(voice.split('-')[-1].replace('Neural', ''))
            
            # Concatenate all audio files
            import subprocess
            
            # Create concat file
            concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            for tf in temp_files:
                concat_file.write(f"file '{tf}'\n")
            concat_file.close()
            
            # Use ffmpeg to concatenate
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_file.name, "-c", "copy", str(filepath)
            ], capture_output=True, check=True)
            
            # Cleanup temp files
            os.unlink(concat_file.name)
            for tf in temp_files:
                os.unlink(tf)
            
            return filename
            
        except Exception as e:
            print(f"  Error generating dialogue {dialogue_num}: {e}")
            # Cleanup on error
            for tf in temp_files:
                if os.path.exists(tf):
                    os.unlink(tf)
            return None
    
    async def generate_topic(self, topic_id, topic_data):
        """Generate all audio for a topic."""
        print(f"\n{'='*50}")
        print(f"Generating: {topic_id.upper()}")
        print(f"Topic: {topic_data['name']}")
        print(f"  Sentences: {len(topic_data['sentences'])}")
        print(f"  Dialogues: {len(topic_data['dialogues'])}")
        print(f"{'='*50}")
        
        # Create output directory
        topic_dir = self.output_dir / topic_id
        topic_dir.mkdir(exist_ok=True)
        
        # Generate sentence audio with different voices
        sentence_files = []
        for i, sentence in enumerate(topic_data["sentences"], 1):
            voice = SENTENCE_VOICES[(i - 1) % len(SENTENCE_VOICES)]
            print(f"  Generating sentence {i}/50 with voice: {voice.split('-')[-1].replace('Neural', '')}")
            filename = await self.generate_sentence_audio(topic_id, i, sentence, voice)
            if filename:
                sentence_files.append({
                    "text": sentence,
                    "file": f"{topic_id}/{filename}",
                    "voice": voice
                })
        
        # Generate dialogue audio
        dialogue_files = []
        for i, dialogue in enumerate(topic_data["dialogues"], 1):
            print(f"  Generating dialogue {i}/10 (two voices)")
            filename = await self.generate_dialogue_audio(topic_id, i, dialogue["lines"])
            if filename:
                dialogue_files.append({
                    "lines": dialogue["lines"],
                    "file": f"{topic_id}/{filename}"
                })
        
        return {
            "sentences": sentence_files,
            "dialogues": dialogue_files
        }
    
    async def generate_all(self):
        """Generate practice audio for all topics."""
        all_results = {}
        
        for topic_id, topic_data in PRACTICE_TOPICS.items():
            result = await self.generate_topic(topic_id, topic_data)
            all_results[topic_id] = {
                "name": topic_data["name"],
                "sentences": result["sentences"],
                "dialogues": result["dialogues"]
            }
        
        # Save practice structure
        structure_file = self.output_dir / "practice_structure.json"
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        # Save topics list for HTML player
        topics_list = [{"id": k, "name": v["name"]} for k, v in PRACTICE_TOPICS.items()]
        topics_file = self.output_dir / "practice_topics.json"
        with open(topics_file, 'w', encoding='utf-8') as f:
            json.dump(topics_list, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*50}")
        print(f"Practice generation complete!")
        print(f"Audio files saved to: {self.output_dir}")
        print(f"Practice structure saved to: {structure_file}")
        print(f"Topics list saved to: {topics_file}")
        print(f"{'='*50}")
        
        return all_results


async def main():
    generator = PracticeGenerator()
    await generator.generate_all()


if __name__ == "__main__":
    asyncio.run(main())
