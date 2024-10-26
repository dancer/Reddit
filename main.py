import praw
import re
from random import randint, uniform, choice
from time import sleep, time
from praw.exceptions import RedditAPIException
from comment import GeneratorCommentOllama
from textblob import TextBlob
import json
import requests
from collections import Counter
from datetime import datetime, timedelta
import feedparser
import secret
try:
    with open('successful_comments.json', 'r') as f:
        SUCCESS_PATTERNS = json.load(f)
except FileNotFoundError:
    SUCCESS_PATTERNS = {'patterns': [], 'topics': {}, 'trends': []}

AI_TOPICS = {
    'machine_learning': ['neural network', 'deep learning', 'training', 'model'],
    'nlp': ['language model', 'nlp', 'text', 'gpt', 'token'],
    'computer_vision': ['vision', 'image', 'detection', 'recognition'],
    'reinforcement_learning': ['rl', 'agent', 'environment', 'reward'],
    'ethics': ['bias', 'fairness', 'ethics', 'responsible ai']
}

AI_SUBREDDITS = [
    "artificial",
    "MachineLearning", 
    "OpenAI",
    "GPT3",
    "LocalLLaMA",
    "MLQuestions",
    "deeplearning",
    "computervision",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

def get_github_trending_ai():
    try:
        response = requests.get('https://api.github.com/search/repositories?q=topic:artificial-intelligence&sort=stars&order=desc')
        if response.status_code == 200:
            return [repo['name'] for repo in response.json()['items'][:5]]
    except Exception as e:
        print(f"Error fetching GitHub trends: {e}")
    return []

def get_arxiv_papers():
    try:
        url = 'http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=lastUpdatedDate&sortOrder=descending&max_results=50'
        response = requests.get(url)
        feed = feedparser.parse(response.text)
        papers = []
        for entry in feed.entries:
            papers.append({
                'title': entry.title,
                'summary': entry.summary,
                'link': entry.link
            })
        return papers
    except Exception as e:
        print(f"Error fetching arXiv papers: {e}")
    return []

def get_ai_news():
    try:
        response = requests.get(f'https://newsapi.org/v2/everything?q=artificial+intelligence&apiKey={secret.NEWS_API_KEY}')
        if response.status_code == 200:
            return [article['title'] for article in response.json()['articles'][:5]]
    except Exception as e:
        print(f"Error fetching AI news: {e}")
    return []

def update_ai_trends():
    trends = {
        'github': get_github_trending_ai(),
        'papers': get_arxiv_papers(),
        'news': get_ai_news()
    }
    with open('ai_trends.json', 'w') as f:
        json.dump(trends, f)
    return trends

def analyze_post_sentiment(title, text):
    combined_text = f"{title} {text}"
    analysis = TextBlob(combined_text)
    return analysis.sentiment.polarity > 0

def track_successful_comments(reddit, min_score=5):
    successful_patterns = []
    for comment in reddit.user.me().comments.new(limit=100):
        if comment.score >= min_score:
            successful_patterns.append({
                'text': comment.body,
                'score': comment.score,
                'subreddit': comment.subreddit.display_name
            })
    
    with open('successful_comments.json', 'w') as f:
        json.dump({'patterns': successful_patterns}, f)
    return successful_patterns

def categorize_ai_topic(text):
    text = text.lower()
    topic_scores = {}
    for topic, keywords in AI_TOPICS.items():
        score = sum(keyword in text for keyword in keywords)
        topic_scores[topic] = score
    return max(topic_scores.items(), key=lambda x: x[1])[0]

def discover_ai_subreddits(reddit, base_subreddits):
    discovered_subreddits = set(base_subreddits)
    subreddit_stats = {}
    
    for subreddit_name in base_subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            subreddit_stats[subreddit_name] = {
                'subscribers': subreddit.subscribers,
                'active_users': subreddit.active_user_count
            }
            
            related = subreddit.description.lower()
            potential_subs = re.findall(r'/r/([a-zA-Z0-9_]+)', related)
            for sub in potential_subs:
                if any(ai_term in sub.lower() for ai_term in ['ai', 'ml', 'deep', 'neural', 'machine', 'gpt', 'llm']):
                    discovered_subreddits.add(sub)
        except Exception as e:
            print(f"Error discovering subreddits: {e}")
            continue
    
    active_subs = [sub for sub, stats in subreddit_stats.items() 
                  if stats['subscribers'] > 1000 and stats['active_users'] > 10]
    
    return list(set(active_subs + list(discovered_subreddits)))


def is_post_mature(submission, min_hours=1):
    post_age = time() - submission.created_utc
    return post_age > (min_hours * 3600)

def get_trending_topics(reddit, commented_posts, subreddits):
    trending_topics = []
    subreddits_str = '+'.join(subreddits)
    for submission in reddit.subreddit(subreddits_str).hot(limit=500):
        if submission.is_self and not submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            if submission.id not in commented_posts and is_post_mature(submission):
                trending_topics.append(submission)
    return trending_topics

def extract_text_title(submission):
    return submission.title

def extract_text_content(submission):
    return submission.selftext

def extract_comment_content_and_upvotes(submission):
    submission.comments.replace_more(limit=0)
    comments = submission.comments.list()[:5]
    return [(comment.body, comment.score) for comment in comments]

def generate_comment(chat_llm, title, post_text, comments, topic_category, ai_trends):
    try:
        comment = chat_llm.generate_comment(title, post_text, comments, topic_category, ai_trends)
        return comment.strip('"').strip("'")
    except Exception as e:
        print(f"Error generating comment: {e}")
        return ""

def get_commented_posts(reddit):
    commented_posts = set()
    try:
        for comment in reddit.user.me().comments.new(limit=1000):
            commented_posts.add(comment.submission.id)
    except Exception as e:
        print(f"Error retrieving comments: {e}")
    return commented_posts

def pause_randomly():
    sleep_duration = uniform(60, 120) 
    print(f"Taking a short break for {sleep_duration:.0f} seconds")
    sleep(sleep_duration)

def delete_negative_comments(reddit):
    try:
        for comment in reddit.user.me().comments.new(limit=None):
            if comment.score < 0:
                print(f"Deleting comment with ID {comment.id} and score {comment.score}")
                comment.delete()
    except Exception as e:
        print(f"Error deleting comments: {e}")

def main():
    user_agent = choice(USER_AGENTS)
    reddit = praw.Reddit(
        client_id=secret.REDDIT_CLIENT_ID,
        client_secret=secret.REDDIT_CLIENT_SECRET,
        username=secret.REDDIT_USERNAME,
        password=secret.REDDIT_PASSWORD,
        user_agent=user_agent,
    )
    
    commented_posts = get_commented_posts(reddit)
    all_subreddits = discover_ai_subreddits(reddit, AI_SUBREDDITS)
    generator_post = GeneratorCommentOllama(model_name="llama3.2")
    
    print(f"Starting to monitor {len(all_subreddits)} AI-related subreddits")
    
    ai_trends = update_ai_trends()
    last_trend_update = datetime.now()
    
    with open("commented_post_links.txt", "a") as file:
        while True:
            if datetime.now() - last_trend_update > timedelta(hours=6):
                ai_trends = update_ai_trends()
                last_trend_update = datetime.now()
            
            trending_topics = get_trending_topics(reddit, commented_posts, all_subreddits)
            
            for submission in trending_topics:
                post_title = extract_text_title(submission)
                text_content = extract_text_content(submission)
                
                if not analyze_post_sentiment(post_title, text_content):
                    print(f"Skipping negative post: {post_title}")
                    continue
                
                topic_category = categorize_ai_topic(f"{post_title} {text_content}")
                comment_content_and_upvotes = extract_comment_content_and_upvotes(submission)
                comment = generate_comment(generator_post, post_title, text_content, 
                                        comment_content_and_upvotes, topic_category, ai_trends)
                
                if not comment:
                    continue
                    
                exit = False
                while not exit:
                    try:
                        response = submission.reply(comment)
                        file.write(f"{response.submission.url}\n")
                        exit = True
                    except RedditAPIException as e:
                        if e.error_type == "RATELIMIT":
                            sleep(int(e.message.split(" ")[-5]) * 60)
                        elif e.error_type == "THREAD_LOCKED":
                            print("Thread locked. Skipping.")
                            exit = True
                        else:
                            print(e.error_type)
                            exit = True
                            
                print(f"Replied to '{submission.title}' in r/{submission.subreddit} with '{comment}'")
                commented_posts.add(submission.id)
                
                if randint(1, 30) == 1:
                    delete_negative_comments(reddit)
                    track_successful_comments(reddit)
                
                sleep(randint(60, 120))

if __name__ == "__main__":
    main()

