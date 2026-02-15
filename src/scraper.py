import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import time
import json

class InfoHubScraper:
    def __init__(self):
        self.base_url = "https://infohub.rs.ge/ka"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_page_links(self, url):
        """გვერდიდან ყველა ლინკის მოძიება"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = set()
            
            # ვეძებთ ყველა ქართულ გვერდს
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(self.base_url, href)
                
                # მხოლოდ infohub.rs.ge/ka ლინკები
                if full_url.startswith(self.base_url) and full_url != self.base_url:
                    links.add(full_url)
            
            return list(links)
        
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return []
    
    def scrape_page_content(self, url):
        """გვერდიდან ტექსტის ამოღება"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ვშლით script, style, nav, footer ტეგებს
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            # ძირითადი კონტენტის მოძიება
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
            
            # ტექსტის გაწმენდა
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            # Title-ის მოძიება
            title = soup.find('h1')
            title = title.get_text(strip=True) if title else url.split('/')[-1]
            
            return {
                'url': url,
                'title': title,
                'content': text
            }
        
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape_all(self, max_pages=50):
        """საიტის სკრეიპინგი"""
        print("🚀 Starting scraping process...")
        print(f"Base URL: {self.base_url}\n")
        
        # ვიწყებთ მთავარი გვერდიდან
        to_visit = [self.base_url]
        visited = set()
        all_content = []
        
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            
            if url in visited:
                continue
            
            print(f"[{len(visited)+1}/{max_pages}] Scraping: {url}")
            visited.add(url)
            
            # ვიღებთ კონტენტს
            content = self.scrape_page_content(url)
            
            if content and content['content']:
                all_content.append(content)
                print(f"  ✓ Extracted {len(content['content'])} characters")
                
                # ვინახავთ ცალკე ფაილში
                filename = f"page_{len(all_content):03d}.txt"
                filepath = os.path.join('data', 'raw', filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"URL: {content['url']}\n")
                    f.write(f"Title: {content['title']}\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(content['content'])
            
            # ვეძებთ ახალ ლინკებს
            new_links = self.get_page_links(url)
            for link in new_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)
            
            # თავაზიანად ველოდებით (1 წამი გვერდებს შორის)
            time.sleep(1)
        
        # ვინახავთ metadata-ს
        metadata_file = os.path.join('data', 'raw', 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(all_content, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Scraping completed!")
        print(f"📄 Scraped {len(all_content)} pages")
        print(f"💾 Saved to data/raw/")
        
        return all_content

def main():
    # საქაღალდის შექმნა
    os.makedirs('data/raw', exist_ok=True)
    
    # Scraper-ის გაშვება
    scraper = InfoHubScraper()
    results = scraper.scrape_all(max_pages=50)
    
    print(f"\n🎉 Done! Scraped {len(results)} pages")

if __name__ == "__main__":
    main()