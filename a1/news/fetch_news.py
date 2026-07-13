#!/usr/bin/env python3
"""
Fetch news from VOA Learning English RSS feed.
Uses original VOA audio (already A1 level).
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
            
            # Get audio URL from enclosure
            enclosure = item.find('enclosure')
            audio_url = enclosure.get('url') if enclosure is not None else ''
            
            # Clean title (remove date suffix)
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


def select_best_articles(articles, count=5):
    """Select the best articles for A1 learners."""
    scored = []
    for article in articles:
        score = 0
        
        # Shorter titles are better for A1
        if len(article['title']) < 60:
            score += 2
        elif len(article['title']) < 80:
            score += 1
        
        # Prefer recent articles
        if '2026' in article['pub_date'] or '2025' in article['pub_date']:
            score += 1
        
        # Known easy topics for A1
        easy_topics = ['bridge', 'city', 'food', 'dog', 'cat', 'school', 'weather',
                      'barber', 'record', 'gold', 'history', 'design']
        title_lower = article['title'].lower()
        for topic in easy_topics:
            if topic in title_lower:
                score += 1
                break
        
        # Prefer shorter duration (easier for A1)
        if article['duration']:
            try:
                parts = article['duration'].split(':')
                minutes = int(parts[0]) if len(parts) > 0 else 0
                if minutes <= 3:
                    score += 2
                elif minutes <= 5:
                    score += 1
            except:
                pass
        
        scored.append((score, article))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    
    return [article for _, article in scored[:count]]


def parse_date(date_str):
    """Parse RSS date format to readable format."""
    try:
        # Format: "Fri, 14 Mar 2025 13:19:43 +0000"
        date_str = re.sub(r'\s+\+\d{4}$', '', date_str)
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")
        return dt.strftime("%B %d, %Y")
    except:
        return date_str


def main():
    print("Fetching VOA Learning English RSS feed...")
    articles = fetch_rss()
    
    if not articles:
        print("No articles found!")
        return
    
    print(f"Found {len(articles)} articles")
    
    # Select best 5 articles
    selected = select_best_articles(articles, count=5)
    print(f"Selected {len(selected)} articles for A1 level")
    
    news_data = {
        "source": "VOA Learning English",
        "source_url": "https://learningenglish.voanews.com",
        "last_updated": datetime.now().isoformat(),
        "articles": []
    }
    
    for i, article in enumerate(selected):
        news_article = {
            "id": f"news_{i+1:03d}",
            "title": article['title'],
            "date": parse_date(article['pub_date']),
            "link": article['link'],
            "audio_url": article['audio_url'],
            "duration": article['duration']
        }
        news_data['articles'].append(news_article)
        print(f"  [{i+1}] {article['title']} ({article['duration']})")
    
    # Save to news.json
    output_path = 'news.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(news_data['articles'])} articles to {output_path}")
    print("Audio will be streamed directly from VOA (no need to generate)")


if __name__ == '__main__':
    main()
