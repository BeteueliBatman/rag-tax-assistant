import os
import json
import re
from pathlib import Path
from typing import List, Dict

class TextProcessor:
    def __init__(self, chunk_size=800, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """ტექსტის გაწმენდა"""
        # მრავალჯერადი ხაზის გადატანები
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # ზედმეტი სიცარიელეები
        text = re.sub(r' {2,}', ' ', text)
        
        # სტრიქონის გაწმენდა
        text = text.strip()
        
        return text
    
    def split_into_chunks(self, text: str) -> List[str]:
        """ტექსტის chunks-ად დაყოფა"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # თუ ბოლოში ვართ
            if end >= len(text):
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break
            
            # ვეძებთ წერტილს რომ არ გავწყვიტოთ წინადადება
            chunk_end = end
            for separator in ['. ', '! ', '? ', '\n\n', '\n']:
                pos = text.rfind(separator, start, end)
                if pos != -1 and pos > start:
                    chunk_end = pos + len(separator)
                    break
            
            chunk_text = text[start:chunk_end].strip()
            if chunk_text:
                chunks.append(chunk_text)
            
            start = chunk_end - self.chunk_overlap
            if start < 0:
                start = chunk_end
        
        return chunks
    
    def process_all_files(self):
        """ყველა ფაილის დამუშავება"""
        print("📝 Processing text files...")
        
        raw_dir = Path('data/raw')
        processed_dir = Path('data/processed')
        processed_dir.mkdir(exist_ok=True)
        
        # ვტვირთავთ metadata-ს
        metadata_file = raw_dir / 'metadata.json'
        if not metadata_file.exists():
            print("❌ Error: metadata.json not found!")
            print("   Please run: python src/scraper.py first")
            return []
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        all_chunks = []
        chunk_id = 0
        
        for i, doc in enumerate(metadata):
            print(f"\n[{i+1}/{len(metadata)}] Processing: {doc['title'][:50]}...")
            
            # ვკითხულობთ ფაილს
            filename = f"page_{i+1:03d}.txt"
            filepath = raw_dir / filename
            
            if not filepath.exists():
                print(f"  ⚠ File not found: {filename}")
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ვწმენდთ
            cleaned_text = self.clean_text(content)
            
            # ვყოფთ chunks-ად
            chunks = self.split_into_chunks(cleaned_text)
            
            print(f"  ✓ Created {len(chunks)} chunks")
            
            # ვამატებთ metadata-ს
            for j, chunk_text in enumerate(chunks):
                all_chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'source': doc['url'],
                    'title': doc['title'],
                    'chunk_index': j,
                    'total_chunks': len(chunks)
                })
                chunk_id += 1
        
        # ვინახავთ chunks-ს
        chunks_file = processed_dir / 'chunks.json'
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Processing completed!")
        print(f"📦 Total chunks: {len(all_chunks)}")
        print(f"💾 Saved to: {chunks_file}")
        
        return all_chunks

def main():
    processor = TextProcessor(chunk_size=800, chunk_overlap=200)
    chunks = processor.process_all_files()
    
    if chunks:
        # სტატისტიკა
        total_chars = sum(len(chunk['text']) for chunk in chunks)
        avg_chunk_size = total_chars / len(chunks) if chunks else 0
        
        print(f"\n📊 Statistics:")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Total characters: {total_chars:,}")
        print(f"   Average chunk size: {avg_chunk_size:.0f} characters")

if __name__ == "__main__":
    main()