# საგადასახადო RAG ასისტენტი

RAG (Retrieval-Augmented Generation) აგენტი საქართველოს საგადასახადო და საბაჟო ინფორმაციისთვის.

## პროექტის აღწერა

სისტემა უპასუხებს ქართულად დასმულ კითხვებს საგადასახადო და საბაჟო საკითხებზე, infohub.rs.ge საიტიდან მოპოვებული დოკუმენტების საფუძველზე. სისტემა იყენებს RAG არქიტექტურას სემანტიკური ძებნისთვის და ყოველთვის მიუთითებს წყაროს.

## ტექნოლოგიები

- Python 3.13
- LangChain
- ChromaDB (Vector Database)
- Sentence Transformers (paraphrase-multilingual-MiniLM-L12-v2)
- Groq API (llama-3.3-70b-versatile)
- Gradio (Web Interface)
- BeautifulSoup4 (Web Scraping)

## სისტემის მოთხოვნები

- Python 3.13.x (არა 3.14)
- 4GB+ RAM
- Internet კავშირი (API-სთვის)

## ინსტალაცია

### 1. Repository-ს კლონირება

```bash
git clone https://github.com/your-username/rag-tax-assistant.git
cd rag-tax-assistant
```

### 2. Virtual Environment

```bash
python -m venv venv

# Windows:
venv\Scripts\activate.bat

# Mac/Linux:
source venv/bin/activate
```

### 3. დამოკიდებულებების დაინსტალირება

```bash
pip install -r requirements.txt
```

### 4. API Key კონფიგურაცია

შექმენით `.env` ფაილი root დირექტორიაში:

```
GROQ_API_KEY=your_api_key_here
```

Groq API Key-ის მისაღებად:
1. გადადით https://console.groq.com/
2. შექმენით ანგარიში
3. API Keys → Create API Key

## გამოყენება

### მონაცემების მომზადება (ერთხელ)

```bash
# 1. Web Scraping
python src/scraper.py

# 2. ტექსტის დამუშავება
python src/text_processor.py

# 3. Vector Store-ის აგება
python src/vector_store.py
```

### აპლიკაციის გაშვება

#### Gradio Web Interface:
```bash
python src/app.py
```

გაიხსნება http://127.0.0.1:7860

#### Terminal Mode:
```bash
python src/rag_pipeline.py
```

## პროექტის სტრუქტურა

```
rag-tax-assistant/
├── src/
│   ├── scraper.py          # Web scraping
│   ├── text_processor.py   # ტექსტის დამუშავება
│   ├── vector_store.py     # Vector database
│   ├── rag_pipeline.py     # RAG ლოგიკა
│   └── app.py              # Gradio interface
├── data/
│   ├── raw/                # Scraped documents
│   ├── processed/          # Processed chunks
│   └── chroma_db/          # Vector database
├── .env                    # API keys
├── .gitignore
├── requirements.txt
└── README.md
```

## ფუნქციონალობა

- ქართული ენის სრული მხარდაჭერა
- Semantic search სემანტიკური ძებნით
- წყაროების ავტომატური მითითება
- Web-based interface
- Interactive terminal mode
- Multilingual embeddings

## გაუმჯობესებები და განვითარება

შესაძლო გაუმჯობესებები:
- დოკუმენტების ბაზის გაფართოება
- მოდელის fine-tuning ქართულ დომენზე
- Cache მექანიზმი ხშირი კითხვებისთვის
- მონაცემების პერიოდული განახლება

## პრობლემების გადაჭრა

### ChromaDB Error
თუ Chrome DB-ს შეცდომა გამოდის, დარწმუნდით რომ Python 3.13.x არის დაინსტალირებული (არა 3.14).

### API Rate Limit
Groq-ის უფასო tier-ზე შეზღუდვები არსებობს. Rate limit-ის გადაჭრისთვის გამოიყენეთ retry logic-ი ან გადახედეთ API plan-ს.

### Memory Issues
Vector Store-ის აგებისას დიდი RAM საჭიროა. თუ პრობლემა გაქვთ, შეამცირეთ batch_size `vector_store.py`-ში.

## დამატებითი ინფორმაცია

დეტალური დოკუმენტაციისთვის გადახედეთ source code-ის კომენტარებს.