# content_generation_agent/pipeline.py
"""
Defines the overall multi-agent pipeline architecture.

This file imports all the individual agents and composes them into a series of
sequential, parallel, and looping workflows. The final `root_agent` is the
single entry point for the entire content generation process.
"""
from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent

# Import agent definitions
from .agents import writers, editors, research, utility
from . import constants as K

# --- Define Reusable Write-Review-Approve Loops ---

blog_creation_loop = LoopAgent(
    name="BlogCreationLoop",
    sub_agents=[
        writers.blog_post_writer_agent,
        editors.blog_qa_editor_agent,
        utility.CheckCompletionAgent(name="BlogCompletionChecker", approval_key=K.STATE_BLOG_APPROVED),
    ],
    max_iterations=3,
)

linkedin_creation_loop = LoopAgent(
    name="LinkedInCreationLoop",
    sub_agents=[
        writers.linkedin_post_writer_agent,
        editors.linkedin_qa_editor_agent,
        utility.CheckCompletionAgent(name="LinkedInCompletionChecker", approval_key=K.STATE_LINKEDIN_APPROVED),
    ],
    max_iterations=3,
)

podcast_creation_loop = LoopAgent(
    name="PodcastCreationLoop",
    sub_agents=[
        writers.podcast_script_writer_agent,
        editors.podcast_qa_editor_agent,
        utility.CheckCompletionAgent(name="PodcastCompletionChecker", approval_key=K.STATE_PODCAST_APPROVED),
    ],
    max_iterations=3,
)

x_creation_loop = LoopAgent(
    name="XCreationLoop",
    sub_agents=[
        writers.x_post_writer_agent,
        editors.x_qa_editor_agent,
        utility.CheckCompletionAgent(name="XCompletionChecker", approval_key=K.STATE_X_POST_APPROVED),
    ],
    max_iterations=3,
)

threads_creation_loop = LoopAgent(
    name="ThreadsCreationLoop",
    sub_agents=[
        writers.threads_post_writer_agent,
        editors.threads_qa_editor_agent,
        utility.CheckCompletionAgent(name="ThreadsCompletionChecker", approval_key=K.STATE_THREADS_POST_APPROVED),
    ],
    max_iterations=3,
)

image_prompt_creation_loop = LoopAgent(
    name="ImagePromptCreationLoop",
    sub_agents=[
        writers.image_prompt_generator_agent,
        editors.image_prompt_validator_agent,
        utility.CheckCompletionAgent(name="ImagePromptCompletionChecker", approval_key=K.STATE_IMAGE_PROMPT_APPROVED),
    ],
    max_iterations=3,
)

# --- Define High-Level Pipelines ---

# Pipeline for creating the image (prompt loop -> generation)
image_creation_pipeline = SequentialAgent(
    name="FullImageCreationPipeline",
    sub_agents=[image_prompt_creation_loop, utility.image_generator_agent],
)

# Parallel agent to create all text/image content simultaneously
parallel_creation_agent = ParallelAgent(
    name="ParallelCreationAgent",
    sub_agents=[
        blog_creation_loop,
        linkedin_creation_loop,
        podcast_creation_loop,
        x_creation_loop,
        threads_creation_loop,
        image_creation_pipeline,
    ],
)

# Pipeline for iterative research (manage query -> search -> aggregate)
research_loop = LoopAgent(
    name="IterativeResearchLoop",
    sub_agents=[
        SequentialAgent(
            name="ResearchIteration",
            sub_agents=[
                utility.ResearchQueryManager(name="QueryManager"),
                research.single_search_agent,
                research.dossier_aggregator_agent,
            ],
        )
    ],
    max_iterations=5, # Allow for up to 5 search queries
)

# --- Assemble the Master Pipeline ---

content_pipeline_agent = SequentialAgent(
    name="ContentPipelineAgent",
    sub_agents=[
        # 1. Define strategy and extract search terms
        research.strategy_agent,
        research.query_extractor_agent,
        # 2. Execute research loop to build the dossier
        research_loop,
        # 3. Create all content in parallel
        parallel_creation_agent,
        # 4. Generate audio from the final podcast script
        utility.audio_producer_agent,
        # 5. Synthesize the final report for the user
        utility.synthesis_agent,
    ]
)

# The final, top-level agent that is exposed to the ADK framework.
root_agent = SequentialAgent(
    name="MasterOrchestrator",
    sub_agents=[
        utility.entry_point_agent, # Captures the initial user query
        content_pipeline_agent    # Runs the entire content factory
    ]
)