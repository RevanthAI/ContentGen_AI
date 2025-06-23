# content_generation_agent/agents/editors.py
"""
Defines the Quality Assurance (QA) agents.

These agents review the drafts produced by the writer agents against a set of
guidelines. They either provide specific, actionable feedback for revision or,
if the content is perfect, call an 'approve' tool to signal completion.
"""
from google.adk.agents import LlmAgent
from .. import constants as K
from .. import tools

# Each QA agent follows the same pattern:
# 1. Review a draft against a checklist.
# 2. If changes are needed, output ONLY the feedback text.
# 3. If the draft is perfect, output ONLY a call to the corresponding approval tool.

blog_qa_editor_agent = LlmAgent(
    name="Blog_QA_EditorAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a meticulous Quality Assurance Editor. Review the blog draft.

    **Inputs (from session state):**
    - Content Brief: {{{K.STATE_CONTENT_BRIEF}}}
    - Blog Post Draft: {{{K.STATE_BLOG_DRAFT}}}

    **Task:**
    Review the draft against our style guide (Markdown formatting, catchy title, short paragraphs, clarity, tone).
    - **IF changes are needed:** Output ONLY actionable feedback.
    - **IF the draft is perfect:** Call the `approve_blog_content` tool.
    """,
    tools=[tools.approve_blog_content],
    output_key=K.STATE_BLOG_FEEDBACK,
)

linkedin_qa_editor_agent = LlmAgent(
    name="LinkedIn_QA_EditorAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a sharp Social Media Content Reviewer for LinkedIn.

    **Inputs (from session state):**
    - Content Brief: {{{K.STATE_CONTENT_BRIEF}}}
    - LinkedIn Post Draft: {{{K.STATE_LINKEDIN_DRAFT}}}

    **Task:**
    Review the draft against LinkedIn best practices (powerful hook, scannability, emojis, hashtags, CTA).
    - **IF changes are needed:** Output ONLY actionable feedback.
    - **IF the draft is perfect:** Call the `approve_linkedin_content` tool.
    """,
    tools=[tools.approve_linkedin_content],
    output_key=K.STATE_LINKEDIN_FEEDBACK,
)

podcast_qa_editor_agent = LlmAgent(
    name="Podcast_QA_EditorAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a podcast producer and quality editor.

    **Input (from session state):**
    - Podcast Script: {{{K.STATE_PODCAST_SCRIPT}}}

    **Task:**
    Review the script for conversational flow, clarity, and correct formatting ("Alex:", "Ben:").
    - **IF changes are needed:** Output ONLY actionable feedback.
    - **IF the script is excellent:** Call the `approve_podcast_content` tool.
    """,
    tools=[tools.approve_podcast_content],
    output_key=K.STATE_PODCAST_FEEDBACK,
)

x_qa_editor_agent = LlmAgent(
    name="X_QA_EditorAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a content moderator for X. Review the draft post for platform-readiness.

    **Input (from session state):**
    - X Post Draft: {{{K.STATE_X_POST_DRAFT}}}

    **Task:**
    Check for conciseness (<280 chars), impact, and proper use of hashtags.
    - **IF changes are needed:** Output ONLY actionable feedback.
    - **IF the draft is perfect:** Call the `approve_x_post` tool.
    """,
    tools=[tools.approve_x_post],
    output_key=K.STATE_X_POST_FEEDBACK,
)

threads_qa_editor_agent = LlmAgent(
    name="Threads_QA_EditorAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a community engagement specialist. Review the draft Threads post.

    **Input (from session state):**
    - Threads Post Draft: {{{K.STATE_THREADS_POST_DRAFT}}}

    **Task:**
    Check that the post is conversational and likely to spark discussion.
    - **IF changes are needed:** Output ONLY actionable feedback.
    - **IF the draft is perfect:** Call the `approve_threads_post` tool.
    """,
    tools=[tools.approve_threads_post],
    output_key=K.STATE_THREADS_POST_FEEDBACK,
)

image_prompt_validator_agent = LlmAgent(
    name="ImagePromptValidatorAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a strict AI Art Director. Validate the image prompt for quality.

    **Input (from session state):**
    - Image Prompt: {{{K.STATE_IMAGE_PROMPT}}}

    **Task:**
    Assess the prompt: Is it descriptive, unambiguous, concise, and safe for work?
    - **IF changes are needed:** Output ONLY actionable feedback.
    - **IF the prompt is excellent:** Call the `approve_image_prompt` tool.
    """,
    tools=[tools.approve_image_prompt],
    output_key=K.STATE_IMAGE_PROMPT_FEEDBACK,
)