#!/usr/bin/env python3
"""
Fetch headlines from Formosa News (english.ftvnews.com.tw)
Extracts title, summary, image, URL, and date for each article.
"""

import json
import re
from pathlib import Path
from urllib.request import urlopen, Request
from html.parser import HTMLParser


class FTVNewsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.articles = []
        self.current_article = None
        self.in_article = False
        self.in_title = False
        self.in_summary = False
        self.in_date = False
        self.capture_text = False
        self.current_text = ""
        self.tag_stack = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        href = attrs_dict.get('href', '')
        cls = attrs_dict.get('class', '')
        
        # Detect article links (pattern: /news/YYYYMMDD...)
        if tag == 'a' and re.match(r'/news/\d{8}\w+', href):
            if not self.in_article:
                self.in_article = True
                self.current_article = {
                    'url': f'https://english.ftvnews.com.tw{href}',
                    'title': '',
                    'summary': '',
                    'date': '',
                    'image': ''
                }
        
        # Detect title (h2 tag inside article link)
        if self.in_article and tag == 'h2':
            self.in_title = True
            self.current_text = ""
            
        # Detect summary (h3 tag inside article link)
        if self.in_article and tag == 'h3':
            self.in_summary = True
            self.current_text = ""
            
        # Detect date (#### tag)
        if self.in_article and tag == 'h4':
            self.in_date = True
            self.current_text = ""
            
        # Detect image
        if self.in_article and tag == 'img':
            src = attrs_dict.get('src', '')
            if src and 'cdn.ftvnews' in src:
                self.current_article['image'] = src
    
    def handle_endtag(self, tag):
        if tag == 'h2' and self.in_title:
            self.in_title = False
            if self.current_article:
                self.current_article['title'] = self.current_text.strip()
                
        if tag == 'h3' and self.in_summary:
            self.in_summary = False
            if self.current_article:
                self.current_article['summary'] = self.current_text.strip()
                
        if tag == 'h4' and self.in_date:
            self.in_date = False
            if self.current_article:
                # Extract date from text like "2026-07-15"
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', self.current_text)
                if date_match:
                    self.current_article['date'] = date_match.group()
                    
        if tag == 'a' and self.in_article:
            if self.current_article and self.current_article.get('title'):
                self.articles.append(self.current_article)
            self.current_article = None
            self.in_article = False
    
    def handle_data(self, data):
        if self.in_title or self.in_summary or self.in_date:
            self.current_text += data


def fetch_ftv_news(max_articles=10):
    """Fetch latest headlines from FTV News."""
    url = "https://english.ftvnews.com.tw/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    req = Request(url, headers=headers)
    
    try:
        with urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []
    
    # Parse HTML
    parser = FTVNewsParser()
    parser.feed(html)
    
    # Deduplicate by URL and limit
    seen_urls = set()
    articles = []
    for article in parser.articles:
        if article['url'] not in seen_urls and article.get('title'):
            seen_urls.add(article['url'])
            articles.append(article)
            if len(articles) >= max_articles:
                break
    
    return articles


def main():
    print("Fetching headlines from Formosa News...")
    articles = fetch_ftv_news(max_articles=10)
    
    if not articles:
        print("No articles found!")
        return
    
    print(f"\nFound {len(articles)} articles:\n")
    
    output_file = Path(__file__).parent / "news_raw.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. [{article.get('date', 'N/A')}] {article['title'][:60]}...")
        if article.get('summary'):
            print(f"   Summary: {article['summary'][:80]}...")
        print()
    
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()
