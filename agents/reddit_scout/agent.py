import os
from typing import Dict, List
import praw
from prawcore import PrawcoreException

from google.adk.agents import Agent
from dotenv import load_dotenv
load_dotenv()

def get_reddit_news(subreddit: str, limit: int = 5) -> Dict[str, List[str]]:
    """
    Fetches the top post titles from a given subreddit.

    Args:
        subreddit: Name of the subreddit (e.g. "springboot", "java", without "r/").
        limit: Maximum number of posts to retrieve (default: 5).

    Returns:
        A dict mapping the subreddit to its list of post titles,
        or an error message if something went wrong.
    """
    # Load credentials
    client_id     = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent    = os.getenv("REDDIT_USER_AGENT")

    if not all((client_id, client_secret, user_agent)):
        return {subreddit: ["Error: Missing Reddit API credentials."]}

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            check_for_async=False
        )
        # Validate subreddit exists
        reddit.subreddits.search_by_name(subreddit, exact=True)

        posts = reddit.subreddit(subreddit).hot(limit=limit)
        titles = [p.title for p in posts]

        if not titles:
            return {subreddit: [f"No hot posts found in r/{subreddit}."]}

        return {subreddit: titles}

    except PrawcoreException as e:
        return {subreddit: [f"API error accessing r/{subreddit}: {e}"]}

    except Exception as e:
        return {subreddit: [f"Unexpected error: {e}"]}

# Define the Agent
agent = Agent(
    name="spring_ai_developer_scout",
    description="A Spring AI Developer Scout specializing in Spring Boot, Spring Cloud, and AI integration topics.",
    model="gemini-1.5-flash-latest",
    instruction=(
        "You are the Spring AI Developer Scout. Your task is to fetch and summarize Spring-related AI development news from Reddit. "
        "1. **Identify Intent:** Determine if the user asks about Spring Boot, Spring Cloud, or Spring AI integration. "
        "2. **Determine Subreddit:** Identify which subreddit(s) to check or default to 'springboot' if none are provided. "
        "3. **Synthesize Output:** Take the exact list of titles returned by the tool."
        "4. **Format Response:** Present the information as a concise, bulleted list. Clearly state which subreddit(s) the information came from. If the tool indicates an error or an unknown subreddit, report that message directly."
        "5. **MUST CALL TOOL:** You **MUST** call the `get_reddit_news` tool with the identified subreddit(s). Do NOT generate summaries without calling the tool first."
    ),
    tools=[get_reddit_news],
)