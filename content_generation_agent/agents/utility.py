# content_generation_agent/agents/utility.py
"""
Defines utility agents and custom agent classes.

This includes specialized BaseAgents for controlling loops and simple LlmAgents
whose sole purpose is to execute a specific tool.
"""
import logging
import json
from typing import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from .. import constants as K
from .. import tools

class CheckCompletionAgent(BaseAgent):
    """A custom agent that checks a specific state key to terminate a loop."""
    approval_key: str

    def __init__(self, name: str, approval_key: str):
        super().__init__(name=name, approval_key=approval_key)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        should_escalate = ctx.session.state.get(self.approval_key, False)
        if should_escalate:
            logging.info(f"🔎 [{self.name}] Detected '{self.approval_key}' is True. Escalating to stop loop.")
        yield Event(author=self.name, actions=EventActions(escalate=should_escalate))

class ResearchQueryManager(BaseAgent):
    """A custom agent that manages the list of search queries for the research loop."""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        queries_data = ctx.session.state.get(K.STATE_SEARCH_QUERIES_LIST, [])
        queries = []
        if isinstance(queries_data, str):
            try: queries = json.loads(queries_data.strip("```json\n").strip())
            except json.JSONDecodeError: logging.error(f"[QueryManager] Could not decode: {queries_data}")
        elif isinstance(queries_data, list):
            queries = queries_data

        if not queries:
            logging.info("🔎 [QueryManager] Query list is empty. Escalating to stop loop.")
            yield Event(author=self.name, actions=EventActions(escalate=True))
            return

        current_query = queries.pop(0)
        logging.info(f"🔎 [QueryManager] Next query: '{current_query}'. {len(queries)} remaining.")
        yield Event(author=self.name, actions=EventActions(
            state_delta={
                K.STATE_CURRENT_SEARCH_QUERY: current_query,
                K.STATE_SEARCH_QUERIES_LIST: queries,
            }
        ))

image_generator_agent = LlmAgent(
    name="ImageGeneratorAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a silent automation unit. Your only job is to take the final, approved image prompt from state key {{{K.STATE_IMAGE_PROMPT}}} and execute the `generate_images_tool`.
    You MUST call the tool with this prompt.
    """,
    tools=[tools.generate_images_tool],
    output_key=K.STATE_IMAGE_GENERATION_STATUS,
)

audio_producer_agent = LlmAgent(
    name="AudioProducerAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a robotics process automation (RPA) unit. Your single function is to execute the `generate_podcast_audio_tool`.

    The script to process is in state key: {{{K.STATE_PODCAST_SCRIPT}}}.
    You MUST check if the script is present and not empty, then call the tool with the full script text.
    Your job is only to call the tool.
    """,
    tools=[tools.generate_podcast_audio_tool],
    output_key=K.STATE_AUDIO_GENERATION_STATUS,
)

synthesis_agent = LlmAgent(
    name="SynthesisAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are the Final Packager. Assemble all final approved content and status into a clean, human-readable markdown report for the user.
    You MUST use the exact headings and markers provided below.

    ---
    **BLOG_POST_START**
    ## Generated Blog Post
    {{{K.STATE_BLOG_DRAFT}}}
    **BLOG_POST_END**
    ---
    **LINKEDIN_POST_START**
    ## Generated LinkedIn Post
    {{{K.STATE_LINKEDIN_DRAFT}}}
    **LINKEDIN_POST_END**
    ---
    **X_POST_START**
    ## Generated X (Twitter) Post
    {{{K.STATE_X_POST_DRAFT}}}
    **X_POST_END**
    ---
    **THREADS_POST_START**
    ## Generated Threads Post
    {{{K.STATE_THREADS_POST_DRAFT}}}
    **THREADS_POST_END**
    ---
    **PODCAST_SCRIPT_START**
    ## Generated Podcast Script
    {{{K.STATE_PODCAST_SCRIPT}}}
    **PODCAST_SCRIPT_END**
    ---
    **IMAGE_PROMPT_START**
    ## Final Approved Image Prompt
    The following prompt was used to generate the images:
    "{{{K.STATE_IMAGE_PROMPT}}}"
    **IMAGE_PROMPT_END**
    ---
    **MEDIA_STATUS_START**
    ## Media Generation Status
    - **Podcast Audio:** Based on the status report `{{{K.STATE_AUDIO_GENERATION_STATUS}?}}`, confirm if "podcast_episode.wav" was created successfully or if an error occurred.
    - **Generated Images:** Based on the status report `{{{K.STATE_IMAGE_GENERATION_STATUS}?}}`, confirm if the 4 images were created successfully or if an error occurred.
    **MEDIA_STATUS_END**
    ---
    """,
)

entry_point_agent = LlmAgent(
    name="QueryCaptureAgent",
    model=K.GEMINI_MODEL,
    instruction="You are a routing agent. Your only job is to save the user's query.",
    output_key=K.STATE_USER_QUERY
)