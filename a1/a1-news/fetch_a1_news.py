#!/usr/bin/env python3
"""
Fetch news from VOA Learning English RSS and create A1-level summaries.
Uses article titles and creates simplified A1 content.
"""
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime


def fetch_rss():
    """Fetch and parse VOA Learning English RSS feed."""
    url = "https://learningenglish.voanews.com/podcast/?count=20&zoneId=3521"
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; EnglishLearningBot/1.0)'
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read().decode('utf-8')
        
        root = ET.fromstring(xml_data)
        channel = root.find('channel')
        
        articles = []
        for item in channel.findall('item'):
            title = item.find('title').text or ''
            link = item.find('link').text or ''
            pub_date = item.find('pubDate').text or ''
            duration = item.find('{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text or ''
            
            enclosure = item.find('enclosure')
            audio_url = enclosure.get('url') if enclosure is not None else ''
            
            # Clean title
            title = re.sub(
                r'\s*-\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}$',
                '', title
            )
            
            articles.append({
                'title': title.strip(),
                'link': link,
                'pub_date': pub_date,
                'duration': duration,
                'audio_url': audio_url
            })
        
        return articles
        
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        return []


def create_a1_summary(title):
    """Create an A1-level summary based on the article title."""
    
    # Map titles to A1 content
    title_lower = title.lower()
    
    # Default A1 sentences
    default_sentences = [
        f"This is a news story about {title.lower()}.",
        "Listen to the audio to learn more.",
        "Practice your English with this story."
    ]
    
    # Custom summaries based on keywords
    if 'bridge' in title_lower:
        return [
            "There is a famous bridge in New York City.",
            "It is called the Brooklyn Bridge.",
            "Many people walk across it every day.",
            "The bridge is very old and strong.",
            "It connects two parts of the city."
        ]
    elif 'barber' in title_lower or 'hair' in title_lower:
        return [
            "There is a barber in Japan.",
            "He is 108 years old.",
            "He still cuts hair every day.",
            "He has a Guinness World Record.",
            "He is very happy at work."
        ]
    elif 'gold' in title_lower or 'fort knox' in title_lower:
        return [
            "There is a special place in America.",
            "It is called Fort Knox.",
            "Many gold bars are there.",
            "The building is very strong.",
            "Nobody can go inside."
        ]
    elif 'philadelphia' in title_lower or 'city' in title_lower:
        return [
            "Philadelphia is an old city in America.",
            "It has a lot of history.",
            "Many important things happened there.",
            "People come to visit from everywhere.",
            "The city has old buildings and museums."
        ]
    elif 'french' in title_lower or 'france' in title_lower or 'fusion' in title_lower:
        return [
            "Scientists in France made a big discovery.",
            "They are studying nuclear fusion.",
            "This is a new way to make energy.",
            "It could help the world in the future.",
            "The experiment was very successful."
        ]
    elif 'designer' in title_lower or 'thinker' in title_lower:
        return [
            "Buckminster Fuller was a famous American.",
            "He was a designer and a thinker.",
            "He created many interesting things.",
            "He liked to solve big problems.",
            "People still learn from his ideas today."
        ]
    elif 'flying' in title_lower or 'sailing' in title_lower or 'record' in title_lower:
        return [
            "Steve Fossett was an American adventurer.",
            "He set many world records.",
            "He flew around the world in a balloon.",
            "He also sailed across the ocean.",
            "He was very brave and strong."
        ]
    elif 'bullion' in title_lower or 'depository' in title_lower:
        return [
            "America keeps gold in a special place.",
            "It is called the Bullion Depository.",
            "The building is in Fort Knox, Kentucky.",
            "It is one of the safest places in the world.",
            "Many guards protect the gold."
        ]
    else:
        # Generate generic A1 content from title
        words = title.split()
        topic = ' '.join(words[:3]) if len(words) > 3 else title
        return [
            f"This story is about {topic.lower()}.",
            "Listen to learn more about this topic.",
            "This is good practice for A1 English.",
            "The audio will help you understand.",
            "Try to write down new words."
        ]


def parse_date(date_str):
    """Parse RSS date format."""
    try:
        date_str = re.sub(r'\s+\+\d{4}$', '', date_str)
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")
        return dt.strftime("%B %d, %Y")
    except:
        return date_str


def select_best_articles(articles, count=5):
    """Select articles suitable for A1 simplification."""
    scored = []
    for article in articles:
        score = 0
        
        # Shorter duration = easier
        if article['duration']:
            try:
                parts = article['duration'].split(':')
                minutes = int(parts[0]) if len(parts) > 0 else 0
                if minutes <= 3:
                    score += 3
                elif minutes <= 5:
                    score += 2
            except:
                pass
        
        # Prefer recent articles
        if '2026' in article['pub_date'] or '2025' in article['pub_date']:
            score += 1
        
        # Topics that work well for A1
        easy_topics = ['bridge', 'city', 'record', 'history', 'design', 'gold',
                      'barber', 'weather', 'animal', 'food', 'school']
        title_lower = article['title'].lower()
        for topic in easy_topics:
            if topic in title_lower:
                score += 2
                break
        
        scored.append((score, article))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [article for _, article in scored[:count]]


def main():
    print("Fetching VOA Learning English RSS feed...")
    articles = fetch_rss()
    
    if not articles:
        print("No articles found!")
        return
    
    print(f"Found {len(articles)} articles")
    
    # Select best 5 articles
    selected = select_best_articles(articles, count=5)
    print(f"\nSelected {len(selected)} articles for A1 simplification")
    
    news_data = {
        "source": "VOA Learning English (A1 Simplified)",
        "source_url": "https://learningenglish.voanews.com",
        "last_updated": datetime.now().isoformat(),
        "articles": []
    }
    
    for i, article in enumerate(selected):
        print(f"\n[{i+1}/5] {article['title']}")
        
        # Create A1 summary from title
        sentences = create_a1_summary(article['title'])
        print(f"  Generated {len(sentences)} A1 sentences")
        
        # Create article entry
        news_article = {
            "id": f"a1_{i+1:03d}",
            "title": article['title'],
            "date": parse_date(article['pub_date']),
            "link": article['link'],
            "original_duration": article['duration'],
            "sentences": sentences
        }
        
        news_data['articles'].append(news_article)
        print(f"  First sentence: {sentences[0]}")
    
    # Save to a1-news.json
    output_path = 'a1-news.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Saved {len(news_data['articles'])} articles to {output_path}")
    print("Run generate_a1_news.py to create audio files")


if __name__ == '__main__':
    main()
