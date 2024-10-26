
# AI Subreddit Engagement Bot

An intelligent bot that engages with AI-focused communities on Reddit by generating contextually relevant comments using local LLMs. The bot automatically discovers AI-related subreddits, tracks trending topics, and maintains high-quality interactions to contribute to discussions in an engaging and meaningful way.

---

## Features

- **Smart Subreddit Discovery**: Automatically identifies and engages with AI-focused communities.
- **Real-time AI Trend Monitoring**:
  - Tracks latest papers from arXiv
  - Finds trending GitHub repositories
  - Keeps up with current AI news
- **Intelligent Comment Generation**:
  - Generates topic-aware responses
  - Includes sentiment analysis
  - Ensures technical accuracy
  - Engages naturally with users
- **Quality Control**:
  - Removes low-performing comments automatically
  - Tracks successful comment patterns
  - Optimizes for better engagement

---

## Requirements

- Python 3.8+
- Ollama with `llama3.2` model
- Reddit API credentials
- News API key

---

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/ai-reddit-bot.git
    cd reddit-ai-bot
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Configuration**:
   Open `secret.py` with your API credentials:
    ```python
    REDDIT_CLIENT_ID = "client-id"
    REDDIT_CLIENT_SECRET = "client-secret"
    REDDIT_USERNAME = "username"
    REDDIT_PASSWORD = "password"
    NEWS_API_KEY = "newsapi-key"
    ```

---

## Usage

To run the bot, execute:
```bash
python main.py
```

---

## Configuration Options

- **Subreddit Discovery**: Adjust parameters in `AI_SUBREDDITS`.
- **Topic Categories**: Modify topics in `AI_TOPICS`.
- **Comment Generation**: Configure templates in `comment.py`.
- **Timing & Rate Limits**: Set custom limits for better control.

---

## Contributing

1. Fork the repository.
2. Create your feature branch.
3. Commit your changes.
4. Push to the branch.
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License - feel free to use and modify as needed.

---

## Acknowledgments

**Made with ❤️ by [dxd](https://x.com/dxd)**
Leveraging **Ollama**, **LangChain**, and the **Reddit API via PRAW**.
