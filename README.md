# Recon

An AI-powered web application that helps you prepare for networking calls by analyzing LinkedIn profiles and generating smart conversation starters.

## 🚀 Features

- **LinkedIn Profile Analysis**: Scrape and analyze LinkedIn profiles or search by name
- **Activity Aggregation**: Find recent public activities, news mentions, and blog posts
- **Smart Question Generation**: AI-generated conversation starters based on profile analysis
- **Modern Chat Interface**: Beautiful, responsive UI built with Next.js and Tailwind CSS
- **Multi-Agent Architecture**: Separate agents for scraping, aggregation, and LLM processing

## 🏗️ Architecture

```
[User Input (LinkedIn URL or name)]
        ↓
[Scraper Agent]
        ↓
[Activity Aggregator Agent]
        ↓
[LLM Summary + Question Generation Agent]
        ↓
[Formatted Output in Chat Interface]
```

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - Modern Python web framework
- **OpenAI GPT-4** - LLM for summary and question generation
- **SerpAPI** - Web search functionality
- **Perplexity API** - Enhanced search capabilities
- **BeautifulSoup4** - Web scraping

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- API keys for OpenAI, SerpAPI, and Perplexity (optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Recon
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SERPAPI_KEY=your_serpapi_key_here
   PERPLEXITY_API_KEY=your_perplexity_api_key_here
   ```

## 🚀 Running the Application

### Development Mode

1. **Start the backend server**
   ```bash
   cd backend
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the frontend development server**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`

### Production Mode

1. **Build the frontend**
   ```bash
   npm run build
   npm start
   ```

2. **Run the backend with uvicorn**
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## 🔧 Configuration

### API Keys

- **OpenAI API Key**: Required for LLM functionality. Get it from [OpenAI Platform](https://platform.openai.com/)
- **SerpAPI Key**: Optional, for enhanced web search. Get it from [SerpAPI](https://serpapi.com/)
- **Perplexity API Key**: Optional, for enhanced search. Get it from [Perplexity](https://www.perplexity.ai/)

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM | Yes |
| `SERPAPI_KEY` | SerpAPI key for web search | No |
| `PERPLEXITY_API_KEY` | Perplexity API key | No |

## 📱 Usage

1. Open the application in your browser
2. Enter a LinkedIn URL or person's name in the chat interface
3. Wait for the AI to analyze the profile and recent activities
4. Receive a conversational summary and smart networking questions
5. Use the generated questions as conversation starters for your networking call

## 🤖 How It Works

### 1. Scraper Agent
- Accepts LinkedIn URLs or names
- Attempts to scrape LinkedIn profiles (with fallback to search)
- Extracts basic profile information (name, headline, about)

### 2. Activity Aggregator
- Searches for recent public activities using Perplexity/SerpAPI
- Finds news mentions, blog posts, conference talks
- Aggregates recent professional activities

### 3. LLM Agent
- Processes profile data and activities
- Generates conversational summary
- Creates 5 smart networking questions
- Uses OpenAI GPT-4 for natural language generation

## 🔒 Privacy & Security

- No profile data is stored permanently
- API calls are made securely with proper error handling
- LinkedIn scraping respects robots.txt and rate limits
- All sensitive data is handled via environment variables

## 🧪 Testing

The application includes fallback mock data for testing without API keys:

- Mock LinkedIn profile data
- Mock activity data
- Mock LLM responses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check that all API keys are properly configured
2. Ensure all dependencies are installed
3. Check the browser console and server logs for errors
4. Open an issue on GitHub

## 🚀 Future Enhancements

- [ ] GitHub profile integration
- [ ] Twitter/X profile analysis
- [ ] Conference schedule integration
- [ ] Email template generation
- [ ] Meeting scheduling integration
- [ ] Advanced analytics dashboard 