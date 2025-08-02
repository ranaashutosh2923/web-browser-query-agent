# Web Browser Query Agent 🤖

An intelligent AI-powered web search agent that classifies queries, performs similarity searches, and provides comprehensive summarized results from automated web scraping.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

## 🌟 Overview

This project implements a sophisticated web browser query agent that intelligently processes user queries through a multi-layered AI pipeline. It demonstrates modern software architecture, AI integration, and full-stack development capabilities.

## 🚀 Key Features

### 🧠 **Intelligent Query Processing**
- **Query Classification**: Uses Google Gemini LLM to validate and classify search queries
- **Similarity Detection**: Vector embeddings with ChromaDB to find semantically similar past queries
- **Smart Caching**: Redis-based caching system for lightning-fast retrieval of similar queries

### 🌐 **Advanced Web Scraping**
- **Multi-Platform Search**: Automated scraping from Google and DuckDuckGo with intelligent fallbacks
- **Playwright Integration**: Robust browser automation handling dynamic content
- **Content Extraction**: Intelligent parsing and cleaning of web content

### 🤖 **AI-Powered Summarization**
- **Content Synthesis**: Gemini AI creates comprehensive summaries from multiple sources
- **Context-Aware**: Summaries tailored to the original user query
- **Source Attribution**: Proper citation and linking to original sources

### 💻 **Dual Interface Design**
- **CLI Interface**: Full-featured command-line interface for developers
- **Web Application**: Modern, responsive web interface with dark/light themes
- **Real-time Processing**: Live status updates and interactive feedback

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │    │  Query Classifier │    │ Similarity Search│
│  (CLI or Web)   │───▶│   (Gemini LLM)   │───▶│   (ChromaDB)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                          │
┌─────────────────┐    ┌──────────────────┐              │
│ Content Summary │    │   Web Scraper    │              │
│   (Gemini AI)   │◀───│   (Playwright)   │◀─────────────┘
└─────────────────┘    └──────────────────┘              │
          │                       │                      │
          ▼                       ▼                      ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Final Response │    │   Redis Cache    │    │  Vector Storage │
│   (User Output) │    │   (Fast Access)  │    │   (Future Use)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Requirements

### System Requirements
- **Python**: 3.11 or higher
- **Operating System**: Windows 11 (tested), Linux, macOS
- **Memory**: Minimum 4GB RAM
- **Storage**: 2GB free space

### External Services
- **Google Gemini API**: For query classification and content summarization
- **Redis Server**: For caching and performance optimization

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ranaashutosh2923/web-browser-query-agent.git
cd web-browser-query-agent
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 4. Configure Environment Variables
```bash
# Create .env file
cp .env.example .env
```

Edit `.env` file with your configuration:
```env
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Search Configuration
SIMILARITY_THRESHOLD=0.8
MAX_SCRAPE_PAGES=5
SCRAPE_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
```

### 5. Start Redis Server
```bash
# Windows (if installed):
redis-server

# Docker alternative:
docker run -d -p 6379:6379 redis:alpine

# Or install Redis for Windows:
# https://github.com/MicrosoftArchive/redis/releases
```

## 🚀 Usage

### Command Line Interface
```bash
# Interactive mode
python cli.py --interactive

# Single query
python cli.py "Best places to visit in Delhi"

# System status
python cli.py --status
```

### Web Application
```bash
# Start web server
python main.py --mode api

# Access web interface
# http://localhost:5000
```

### Test Mode
```bash
# Run example queries
python main.py --mode test
```

## 💡 Example Queries

### Valid Queries ✅
```
"Best places to visit in Delhi"
"How to learn Python programming"
"What is machine learning"
"Climate change effects on agriculture"
"Top restaurants in New York City"
```

### Invalid Queries ❌
```
"walk my pet, add apples to grocery"  → "This is not a valid query."
"call mom, buy milk, wash car"        → "This is not a valid query."
```

## 📁 Project Structure

```
web_query_agent/
├── 📄 README.md                    # Project documentation
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment template
├── 📄 .gitignore                   # Git ignore rules
├── 🐍 main.py                      # Main application entry
├── 🖥️  cli.py                       # Command-line interface
├── ⚙️  config.py                    # Configuration management
├── 📁 services/                    # Core business logic
│   ├── 🐍 __init__.py              # Package initialization
│   ├── 🧠 query_classifier.py      # LLM query validation
│   ├── 🔍 similarity_search.py     # Vector similarity search
│   ├── 🌐 web_scraper.py          # Web content scraping
│   ├── 💾 cache_manager.py         # Redis cache operations
│   └── 📝 content_summarizer.py    # AI content summarization
├── 📁 api/                         # Flask web API
│   ├── 🐍 __init__.py              # API package init
│   └── 🛣️  routes.py                # API endpoints
├── 📁 templates/                   # HTML templates
│   └── 🌐 index.html              # Web interface
└── 📁 static/                      # Frontend assets
    ├── 📁 css/
    │   └── 🎨 style.css            # Responsive styling
    └── 📁 js/
        └── ⚡ app.js               # Frontend JavaScript
```

## 🔧 Technical Implementation

### Query Processing Pipeline

1. **Input Validation** → Query received via CLI or web interface
2. **Classification** → Gemini LLM determines if query is valid for web search
3. **Similarity Check** → ChromaDB vector search for semantically similar past queries
4. **Cache Lookup** → Redis check for existing results from similar queries
5. **Web Scraping** → Playwright automation scrapes top 5 results from Google/DuckDuckGo
6. **Content Processing** → BeautifulSoup cleans and extracts meaningful content
7. **AI Summarization** → Gemini creates comprehensive summary from all sources
8. **Caching & Storage** → Results cached in Redis and query vectors stored in ChromaDB
9. **Response Delivery** → Formatted response sent to user interface

### Key Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend Framework** | Flask | REST API and web server |
| **AI/ML Services** | Google Gemini API | Query classification & summarization |
| **Vector Database** | ChromaDB | Similarity search & embeddings |
| **Caching Layer** | Redis | Performance optimization |
| **Web Scraping** | Playwright + BeautifulSoup | Content extraction |
| **Frontend** | HTML5, CSS3, JavaScript | Modern web interface |
| **Package Management** | pip + venv | Dependency management |

## 🎯 Requirements Compliance

This project fully satisfies :

### ✅ Minimum Requirement
- **Architecture Explanation**: Complete system flowchart and detailed documentation
- **Internal Working**: Comprehensive breakdown of all components and their interactions

### ✅ Good to Have  
- **Working CLI Prototype**: Full-featured command-line interface with interactive mode
- **Query Classification**: "walk my pet, add apples to grocery" → "This is not a valid query."
- **Similarity Detection**: Queries like "Best places to visit in Delhi" and "Top tourist attractions in Delhi" are treated as similar

### ✅ Stretch Goal
- **Complete Web Application**: Modern responsive frontend with backend API
- **Production Architecture**: Scalable, maintainable codebase with proper separation of concerns

## 🧪 Testing

### Manual Testing
```bash
# Test query classification
python cli.py "Best restaurants in Mumbai"        # Valid
python cli.py "walk dog, buy groceries, call mom" # Invalid

# Test similarity search
python cli.py "Places to visit in Delhi"          # First query
python cli.py "Top Delhi tourist attractions"     # Should find similarity

# Test web scraping
python cli.py "Python programming tutorials"      # Should scrape and summarize

# Test system status
python cli.py --status                           # System health check
```

### Web Interface Testing
1. Start web server: `python main.py --mode api`
2. Navigate to: `http://localhost:5000`
3. Test various query types and system features
4. Verify responsive design and theme switching

## 🚀 Performance

- **Query Classification**: ~2-3 seconds (Gemini API)
- **Similarity Search**: ~0.5 seconds (ChromaDB local)
- **Cache Retrieval**: ~0.1 seconds (Redis)
- **Web Scraping**: ~15-30 seconds (depends on sites)
- **Content Summarization**: ~3-5 seconds (Gemini API)

**Total Processing Time**: 5-40 seconds depending on cache status and content complexity

## 🔒 Security Features

- **Environment Variables**: Sensitive data stored in `.env` files
- **API Key Protection**: Keys never committed to version control
- **Input Validation**: Comprehensive query sanitization
- **Error Handling**: Graceful failure modes prevent information leakage
- **Rate Limiting**: Built-in delays for respectful web scraping

## 📊 Monitoring & Logging

- **System Status API**: Real-time component health monitoring
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Cache Statistics**: Redis performance metrics
- **Query Analytics**: Processing time and success rate tracking

## 🛣️ Roadmap

### Phase 1 (Current) ✅
- [x] Core query processing pipeline
- [x] CLI and web interfaces
- [x] Basic caching and similarity search

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for all functions
- Include type hints where appropriate

## 👨‍💻 Author

**Ashutosh Rana**
- Showcasing modern AI application development
- Demonstrating full-stack capabilities and system design

## 🙏 Acknowledgments

- **Google Gemini**: For powerful AI capabilities
- **Playwright Team**: For robust web automation tools
- **Open Source Community**: For the amazing tools and libraries

---

*Demonstrating modern AI application development, system architecture, and full-stack engineering capabilities.*
