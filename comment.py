from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import random

class GeneratorCommentOllama:
    def __init__(self, model_name="llama3.2"):
        self.llm = OllamaLLM(model=model_name)

    def _preprocess_template_string(self, template_string: str) -> str:
        return template_string

    def generate_comment(self, title: str, post_text: str, comments: list[tuple[str, int]], topic_category: str = None, ai_trends: dict = None) -> str:
        prompt_template = """
        Title: {title}
        Text: {post_text}
        Comments: {comments}
        Topic Category: {topic_category}
        Current AI Trends: {ai_trends}

        Create a witty, AI-focused comment that directly relates to the post's content above. Your comment should:
        1. Reference specific details from the post's title or text
        2. Use AI/ML concepts that are relevant to the post's topic category
        3. Build upon the existing discussion
        4. Stay focused on the post's main subject
        5. Reference relevant current AI trends when appropriate
        6. Maintain technical accuracy while being entertaining

        Your comment should be between 5-20 words and directly address the post's content.
        """

        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm | StrOutputParser()
        output = chain.invoke({
            "title": title,
            "post_text": post_text,
            "comments": comments,
            "topic_category": topic_category or "general AI",
            "ai_trends": str(ai_trends) if ai_trends else "No current trends data"
        })
        return output.strip('"').strip("'")
