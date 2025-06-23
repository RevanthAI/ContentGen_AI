# content_generation_agent/constants.py
"""
Centralized definition of all state keys used throughout the agent system.

This approach prevents typos and makes it easy to track what parts of the
session state are being used by which agents.
"""

# --- Core State Keys ---
STATE_USER_QUERY = "user_query"
STATE_CONTENT_BRIEF = "content_brief"
STATE_RESEARCH_DOSSIER = "research_dossier"

# --- Content Draft & Feedback Keys ---
STATE_BLOG_DRAFT = "blog_draft"
STATE_BLOG_FEEDBACK = "blog_feedback"
STATE_LINKEDIN_DRAFT = "linkedin_draft"
STATE_LINKEDIN_FEEDBACK = "linkedin_feedback"
STATE_PODCAST_SCRIPT = "podcast_draft"
STATE_PODCAST_FEEDBACK = "podcast_feedback"
STATE_X_POST_DRAFT = "x_post_draft"
STATE_X_POST_FEEDBACK = "x_post_feedback"
STATE_THREADS_POST_DRAFT = "threads_post_draft"
STATE_THREADS_POST_FEEDBACK = "threads_post_feedback"
STATE_IMAGE_PROMPT = "image_prompt"
STATE_IMAGE_PROMPT_FEEDBACK = "image_prompt_feedback"

# --- Loop Control / Approval Flags ---
STATE_BLOG_APPROVED = "blog_is_approved"
STATE_LINKEDIN_APPROVED = "linkedin_is_approved"
STATE_PODCAST_APPROVED = "podcast_is_approved"
STATE_X_POST_APPROVED = "x_post_is_approved"
STATE_THREADS_POST_APPROVED = "threads_post_is_approved"
STATE_IMAGE_PROMPT_APPROVED = "image_prompt_is_approved"

# --- Media Generation Status ---
STATE_IMAGE_GENERATION_STATUS = "image_generation_status"
STATE_AUDIO_GENERATION_STATUS = "audio_generation_status"

# --- Research Loop State ---
STATE_SEARCH_QUERIES_LIST = "search_queries_list"
STATE_CURRENT_SEARCH_QUERY = "current_search_query"
STATE_SINGLE_SEARCH_RESULT = "single_search_result"

# --- Model Configuration ---
GEMINI_MODEL = "gemini-2.0-flash" # Use a more recent model if available