from typing import List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from schemas.user_profile_model import UserProfile
from utils.age_utils import get_age_bracket, get_age_from_birth_date
from utils.request_utils import retry_with_backoff


def remove_prohibited_queries(queries: List[str]) -> List[str]:
    prohibited_queries = [
        "professional connections",
        "find collaborators",
        "business collaboration",
        "networking",
        "professional networking",
        "find a job",
        "job fairs",
        "job training",
        "career fair",
        "career fairs",
        "job fair",
        "job opportunities",
        "job search",
        "job openings",
        "improve skills",
        "career",
    ]
    return [query for query in queries if query not in prohibited_queries]


def get_search_keywords_for_event_sites(
    user_profile: UserProfile, model: BaseChatModel
) -> List[str]:
    """
    Generate search keywords based on user profile and model.

    Args:
        user_profile: UserProfile object containing user information
        model: BaseChatModel instance

    Returns:
        List of search keywords
    """

    lgbtq_section = (
        """
        4. LGBTQ+ QUERY:
        - Create one LGBTQ+ query (e.g. "LGBTQ+ events", "LGBTQ+ community", "LGBTQ+ support group", etc.)
    """
        if user_profile.sexual_orientation != "straight"
        else ""
    )

    single_non_lgbtq_section = (
        """
        5. SINGLE-SPECIFIC QUERY:
        - Create one single-specific query. Include the age bracket if relevant (e.g. "single events", "speed dating {age_bracket}", etc.)
    """
        if user_profile.relationship_status == "single"
        and user_profile.sexual_orientation == "straight"
        else ""
    )

    single_lgbtq_section = (
        """
        6. SINGLE-SPECIFIC QUERY:
        - Create one single-specific query (e.g. "{sexual_orientation} speed dating", "LGBTQ+ singles", etc.)
    """
        if user_profile.relationship_status == "single"
        and user_profile.sexual_orientation != "straight"
        else ""
    )

    extra_info_section = (
        """
        7. EXTRA INFO:
        The user's extra information is: {extra_info}
        - Use the user's extra information to create 1-2 queries. If there is nothing in the user's extra information that offers an opportunity for a new query, then don't include it in the output.
    """
        if user_profile.extra_info
        else ""
    )

    prompt_template = """
        You are a search query generator specialized in creating effective event discovery queries.

        IMPORTANT: Format your response ONLY as a comma-separated list of search queries with NO additional text or explanations. Limit the number of queries to 20.
        IMPORTANT: Examples (e.g.) are just for demonstration purposes. DO NOT follow them exactly. If the user has no interest in something that was provided in the examples, then do not include it in the output. The only exception is negative examples. If a negative example is provided, then under no circumstances should you include it in the output.

        The user's occupation is: {occupation}
        The user's extra information is: {extra_info}

        QUERY CREATION RULES:
        1. GOAL-BASED QUERIES:
        The user's goals are: {goals}
        - Create personalized queries for EACH goal
        - ONLY IF appropriate generate an EXTRA query (don't replace the original query) for a goal that will find other relevant events (e.g. "find a business partner" -> "pitch night", "make new friends" -> "community {age_bracket}").

        2. AGE-SPECIFIC QUERIES:
        - For social/community goals, ALWAYS include age bracket (e.g., "community {age_bracket}", "make friends {age_bracket}") but not for professional goals (e.g., "networking {age_bracket}" or "business partner {age_bracket}" are NOT good queries) nor for more general goals (e.g., "volunteering {age_bracket}", "yoga classes {age_bracket}", "running clubs {age_bracket}" are NOT good queries)

        3. GENDER-SPECIFIC QUERIES:
        The user's gender is: {gender}
        - Create one gender-specific query based on the user's gender (e.g. ladies only, men circles etc.)

        {lgbtq_section}

        {single_non_lgbtq_section}

        {single_lgbtq_section}

        {extra_info_section}

        8. INTEREST-BASED QUERIES:
        The user's interests are: {interests}
        - Keep all interest queries to 4 words or less
        - DO NOT include age bracket in interest queries, only include it in goal-based queries

        9. PROHIBITED TERMS:
        - NO generic terms (e.g. "events", "meetups", "community", "group", "gathering", "enthusiasts", "near me", "weekend") unless they are absolutely necessary
        - NO generic queries (e.g. "professional connections", "find collaborators", "business collaboration", "networking", "professional networking", "find a job", "job fairs", "job training")

        10. QUERY DIVERSITY:
        - Avoid overly similar queries that would return the same results. For example, repeating the same query with different variations of the same word
        - Focus on specificity and relevance

        EXAMPLE OUTPUT FORMAT (ONLY AS A GUIDE):
        "make friends {age_bracket}, find a business partner, tech startups, python coding, hiking outdoors, AI"
        - The above are just examples. DO NOT follow them exactly. Only use them as a guide.

        IMPORTANT:
        Examples are just that, examples. DO NOT follow them exactly. If the user has no interest in something that was provided in the examples, then do not include it in the output. The only exception is negative examples. If a negative example is provided, then under no circumstances should you include it in the output.
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | model
    response = retry_with_backoff(
        chain.invoke,
        max_retries=5,
        base_delay=2.0,
        input={
            "interests": user_profile.interests,
            "goals": user_profile.goals,
            "age_bracket": get_age_bracket(
                get_age_from_birth_date(user_profile.birth_date)
            ),
            "occupation": user_profile.occupation,
            "gender": user_profile.gender,
            "sexual_orientation": user_profile.sexual_orientation,
            "lgbtq_section": lgbtq_section,
            "single_non_lgbtq_section": single_non_lgbtq_section,
            "single_lgbtq_section": single_lgbtq_section,
            "extra_info_section": extra_info_section,
            "extra_info": user_profile.extra_info,
        },
    )

    response_str = (
        str(response.content) if hasattr(response, "content") else str(response)
    )

    keywords = [keyword.strip() for keyword in response_str.split(",")]
    keywords = list(dict.fromkeys(keywords))
    return remove_prohibited_queries(keywords)
