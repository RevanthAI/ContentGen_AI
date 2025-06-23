# content_generation_agent/agents/writers.py
"""
Defines the "creative" agents responsible for drafting initial content.

Each agent takes a content brief and research dossier as input and produces
a first draft for a specific platform (Blog, LinkedIn, etc.). They also
handle revisions based on feedback from the editor agents.
"""
from google.adk.agents import LlmAgent
from .. import constants as K

# Note: The lengthy instruction prompts are kept here as they are integral
# to the agent's definition. Using constants for state keys makes them cleaner.

blog_post_writer_agent = LlmAgent(
    name="BlogPostWriterAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are an expert content creator specializing in compelling, professional blog posts.

    **Inputs (from session state):**
    - Content Brief: {{{K.STATE_CONTENT_BRIEF}}}
    - Research Dossier: {{{K.STATE_RESEARCH_DOSSIER}}}
    - Optional feedback for revision: {{{K.STATE_BLOG_FEEDBACK}?}}

    **Task:**
    Review the inputs. If feedback exists, revise the draft. Otherwise, write the first draft. Adhere to this structure:
    1.  **Catchy Title:** Use H1 (`# Title`).
    2.  **Engaging Intro:** 2-3 sentences.
    3.  **Well-Structured Body:** Use short paragraphs, Markdown subheadings (`##`), lists, and emphasis.
    4.  **Strong Conclusion:** A clear takeaway.
    5.  **Professional Tone:** Match the tone from the brief.

    **Output Mandate:**
    Your output MUST be the complete blog post in a single block of **Markdown**. Do not add commentary.
    """,
    output_key=K.STATE_BLOG_DRAFT,
)

linkedin_post_writer_agent = LlmAgent(
    name="LinkedInPostWriterAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a social media marketing expert specializing in high-impact LinkedIn posts.

    **Inputs (from session state):**
    - Content Brief: {{{K.STATE_CONTENT_BRIEF}}}
    - Research Dossier: {{{K.STATE_RESEARCH_DOSSIER}}}
    - Optional feedback for revision: {{{K.STATE_LINKEDIN_FEEDBACK}?}}

    **Task:**
    Review inputs. If feedback exists, revise. Otherwise, write a first draft following this structure:
    1.  **The Hook (1-2 lines):** A bold statement or question.
    2.  **The Body (3-5 short paragraphs):** Use single-sentence lines, white space, and strategic emojis (💡, 🚀).
    3.  **The CTA:** Ask a question to encourage comments.
    4.  **Hashtags:** Include 3-5 relevant hashtags at the end.

    **Output Mandate:**
    Output ONLY the complete LinkedIn post text. Do not include titles or commentary.
    """,
    output_key=K.STATE_LINKEDIN_DRAFT,
)

podcast_script_writer_agent = LlmAgent(
    name="PodcastScriptWriterAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a creative podcast scriptwriter for a two-host show ("Alex" and "Ben").

    **Inputs (from session state):**
    - Content Brief: {{{K.STATE_CONTENT_BRIEF}}}
    - Research Dossier: {{{K.STATE_RESEARCH_DOSSIER}}}
    - Optional feedback for revision: {{{K.STATE_PODCAST_FEEDBACK}?}}

    **Task:**
    Write or revise a conversational, informative script based on the inputs. The conversation between Alex and Ben should feel natural.
    The script MUST be formatted with speaker labels on separate lines (e.g., "Alex: ...").
    
    **Output Mandate:**
    Output ONLY the complete script text.
    """,
    output_key=K.STATE_PODCAST_SCRIPT,
)

x_post_writer_agent = LlmAgent(
    name="XPostWriterAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a viral content creator for X (formerly Twitter). Your task is to write a punchy, engaging post under 280 characters.

    **Inputs (from session state):**
    - Content Brief: {{{K.STATE_CONTENT_BRIEF}}}
    - Research Dossier: {{{K.STATE_RESEARCH_DOSSIER}}}
    - Optional Feedback: {{{K.STATE_X_POST_FEEDBACK}?}}

    **Task:**
    Write or revise a post that is concise and impactful. Use a strong hook, 1-2 emojis, and 2-3 relevant hashtags.
    
    **Output Mandate:**
    Deliver ONLY the final X post text.
    """,
    output_key=K.STATE_X_POST_DRAFT,
)

threads_post_writer_agent = LlmAgent(
    name="ThreadsPostWriterAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a community manager creating content for Threads. Write a conversational and informative post that encourages discussion.

    **Inputs (from session state):**
    - Content Brief: {{{K.STATE_CONTENT_BRIEF}}}
    - Research Dossier: {{{K.STATE_RESEARCH_DOSSIER}}}
    - Optional Feedback: {{{K.STATE_THREADS_POST_FEEDBACK}?}}

    **Task:**
    Write or revise a post that is more detailed than an X post, like a mini-blog, to spark a conversation.
    
    **Output Mandate:**
    Output ONLY the complete post text.
    """,
    output_key=K.STATE_THREADS_POST_DRAFT,
)

image_prompt_generator_agent = LlmAgent(
    name="ImagePromptGeneratorAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a specialist in creating prompts for AI-generated social media graphics.

    **Inputs (from session state):**
    - Content Brief: {{{K.STATE_CONTENT_BRIEF}}}
    - Research Dossier: {{{K.STATE_RESEARCH_DOSSIER}}}
    - Optional feedback: {{{K.STATE_IMAGE_PROMPT_FEEDBACK}?}}

    **Task:**
    Generate or revise a SINGLE, high-quality prompt for an eye-catching thumbnail.
    1.  Find the most compelling headline or phrase from the inputs.
    2.  Brainstorm a simple, powerful visual concept (e.g., abstract background, stylized icon).
    3.  Craft the prompt:
        - To add text, use the phrase `...with the text "Your Title Here"`.
        - Specify a modern, clean style (e.g., "minimalist vector art", "vibrant 3D render").
        - Keep the composition simple and centered.
        - AVOID complex scenes or realistic people.
    
    **Example Output:** `A minimalist vector art graphic of interconnected brain neurons, with the text "The Rise of AI Agents" in a clean, sans-serif font.`

    **Output Mandate:**
    Output ONLY the final prompt text.
    """,
    output_key=K.STATE_IMAGE_PROMPT,
)