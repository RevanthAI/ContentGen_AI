# content_generation_agent/agents/research.py
"""
Defines agents responsible for the research phase of the pipeline.

This includes creating a strategy, extracting search queries, performing
the searches, and aggregating the results into a cohesive dossier.
"""
from google.adk.agents import LlmAgent
from google.adk.tools import google_search, agent_tool
from .. import constants as K

strategy_agent = LlmAgent(
    name="StrategyAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a Content Strategist. Based on the user's query in state key {{{K.STATE_USER_QUERY}}}, create a structured 'Content Brief'.
    Your brief MUST be a single JSON object containing:
    - "topic": A clear, concise topic title.
    - "audience": The target audience (e.g., 'technical developers', 'business executives').
    - "goal": The primary goal of the content (e.g., 'inform', 'persuade').
    - "tone": The desired tone (e.g., 'professional', 'casual').
    - "keywords": An array of 3-5 relevant SEO keywords.
    - "search_queries": An array of 2 distinct, high-quality Google search query strings.
    Output ONLY the JSON object.
    """,
    output_key=K.STATE_CONTENT_BRIEF,
)

query_extractor_agent = LlmAgent(
    name="QueryExtractorAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a data parsing agent.
    Read the JSON from {{{K.STATE_CONTENT_BRIEF}}}.
    Extract the value of the "search_queries" key.
    Output ONLY the list of queries as a JSON array of strings.
    """,
    output_key=K.STATE_SEARCH_QUERIES_LIST,
)

research_agent = LlmAgent(
    name="ResearchAgent",
    model=K.GEMINI_MODEL,
    instruction="You are a research assistant. Use the Google Search tool to find information based on the user's query.",
    tools=[google_search],
)

single_search_agent = LlmAgent(
    name="SingleSearchAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""Your task is to perform research for a single query using the `ResearchAgent` tool.
    The query is in the state key {{{K.STATE_CURRENT_SEARCH_QUERY}}}.
    Call the `ResearchAgent` tool with this query and output ONLY the direct result.
    """,
    tools=[agent_tool.AgentTool(agent=research_agent)],
    output_key=K.STATE_SINGLE_SEARCH_RESULT,
)

dossier_aggregator_agent = LlmAgent(
    name="DossierAggregatorAgent",
    model=K.GEMINI_MODEL,
    instruction=f"""You are a silent data processing unit. Your SOLE function is to merge research findings.

    **Inputs (from state):**
    - Existing Dossier: {{{K.STATE_RESEARCH_DOSSIER}?}}
    - Latest Search Result: {{{K.STATE_SINGLE_SEARCH_RESULT}}}

    **Task:**
    Append the new search result to the existing dossier. Summarize and structure the combined information into a clear, updated Research Dossier, removing duplicates.

    **CRITICAL:** Output ONLY the updated Research Dossier text. No conversational filler.
    """,
    output_key=K.STATE_RESEARCH_DOSSIER,
)