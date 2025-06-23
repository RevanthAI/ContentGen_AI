# content_generation_agent/tools.py
"""
Defines all tools that can be called by LlmAgents.

This includes approval tools that set state flags to terminate loops,
and I/O tools for generating images and audio.
"""
import logging
import os
import wave
import io
import json # <--- Import the json library
import traceback
from typing import Dict, List # We can still use these for internal type hints

from google.adk.tools import ToolContext
from google.genai import types as genai_types
from google import genai
from vertexai.preview.vision_models import ImageGenerationModel

from . import constants

# --- Approval Tools ---
# These tools now correctly return a simple `str` for reliable model parsing.

def approve_blog_content(tool_context: ToolContext) -> str:
    """Call this function ONLY when the blog post draft is approved."""
    logging.info(f"✅ [{tool_context.agent_name}] approved BLOG content.")
    tool_context.state[constants.STATE_BLOG_APPROVED] = True
    return "Blog content approved."

def approve_linkedin_content(tool_context: ToolContext) -> str:
    """Call this function ONLY when the LinkedIn post draft is approved."""
    logging.info(f"✅ [{tool_context.agent_name}] approved LINKEDIN content.")
    tool_context.state[constants.STATE_LINKEDIN_APPROVED] = True
    return "LinkedIn content approved."

def approve_podcast_content(tool_context: ToolContext) -> str:
    """Call this function ONLY when the podcast script is approved."""
    logging.info(f"✅ [{tool_context.agent_name}] approved PODCAST script.")
    tool_context.state[constants.STATE_PODCAST_APPROVED] = True
    return "Podcast script approved."

def approve_x_post(tool_context: ToolContext) -> str:
    """Call this function ONLY when the X (Twitter) post is approved."""
    logging.info(f"✅ [{tool_context.agent_name}] approved X POST.")
    tool_context.state[constants.STATE_X_POST_APPROVED] = True
    return "X (Twitter) post approved."

def approve_threads_post(tool_context: ToolContext) -> str:
    """Call this function ONLY when the Threads post is approved."""
    logging.info(f"✅ [{tool_context.agent_name}] approved THREADS post.")
    tool_context.state[constants.STATE_THREADS_POST_APPROVED] = True
    return "Threads post approved."

def approve_image_prompt(tool_context: ToolContext) -> str:
    """Call this function ONLY when the image prompt is approved."""
    logging.info(f"✅ [{tool_context.agent_name}] approved IMAGE PROMPT.")
    tool_context.state[constants.STATE_IMAGE_PROMPT_APPROVED] = True
    return "Image prompt approved."


# --- Media Generation Tools ---

async def generate_images_tool(prompt: str, tool_context: ToolContext) -> str: 
    """Generates 4 images using Vertex AI's Imagen model and saves them as artifacts."""
    try:
        logging.info(f"🎨 [Imagen Tool] Generating 4 images for prompt: '{prompt[:70]}...'")
        imagen_model = ImageGenerationModel.from_pretrained("imagen-4.0-fast-generate-preview-06-06")
        image_response = imagen_model.generate_images(
            prompt=prompt, number_of_images=4, aspect_ratio="16:9", add_watermark=False
        )

        list_of_generated_images = image_response.images
        if not list_of_generated_images:
            raise ValueError("Imagen API did not return any images.")

        for i, img in enumerate(list_of_generated_images):
            artifact_filename = f"generated_image_{i+1}.png"
            image_artifact_part = genai_types.Part.from_bytes(data=img._image_bytes, mime_type="image/png")
            version = await tool_context.save_artifact(filename=artifact_filename, artifact=image_artifact_part)
            logging.info(f"✅ [Imagen Tool] Saved '{artifact_filename}' as version {version}.")

        status_report = {"status": "success", "images_generated": len(list_of_generated_images)}
        return json.dumps(status_report) # <--- FIX 2: Return a JSON string

    except Exception as e:
        logging.error(f"❌ [Imagen Tool] Error: {e}\n{traceback.format_exc()}")
        status_report = {"status": "error", "message": str(e)}
        return json.dumps(status_report) # <--- FIX 2: Return a JSON string

async def generate_podcast_audio_tool(script_text: str, tool_context: ToolContext) -> str: 
    """Generates multi-speaker audio from a script using Gemini TTS and saves it as a WAV artifact."""
    try:
        logging.info("🎙️ [TTS Tool] Generating multi-speaker audio...")
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'), vertexai=False)
        tts_model = "gemini-2.5-flash-preview-tts"

        response = client.models.generate_content(
            model=tts_model,
            contents=script_text,
            config=genai_types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=genai_types.SpeechConfig(
                    multi_speaker_voice_config=genai_types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            genai_types.SpeakerVoiceConfig(speaker='Alex', voice_config=genai_types.VoiceConfig(prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(voice_name='Kore'))),
                            genai_types.SpeakerVoiceConfig(speaker='Ben', voice_config=genai_types.VoiceConfig(prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(voice_name='Puck'))),
                        ]
                    )
                )
            )
        )

        raw_audio_bytes = response.candidates[0].content.parts[0].inline_data.data
        if not raw_audio_bytes:
            raise ValueError("TTS API did not return audio content.")

        with io.BytesIO() as in_memory_file:
            with wave.open(in_memory_file, 'wb') as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
                wf.writeframes(raw_audio_bytes)
            wav_file_bytes = in_memory_file.getvalue()
        
        audio_artifact_part = genai_types.Part.from_bytes(data=wav_file_bytes, mime_type="audio/wav")
        version = await tool_context.save_artifact(filename="podcast_episode.wav", artifact=audio_artifact_part)
        
        logging.info(f"✅ [TTS Tool] Saved artifact 'podcast_episode.wav' as version {version}.")
        status_report = {"status": "success", "artifact_name": "podcast_episode.wav", "version": version}
        return json.dumps(status_report) # <--- FIX 2: Return a JSON string

    except Exception as e:
        logging.error(f"❌ [TTS Tool] Error: {e}\n{traceback.format_exc()}")
        status_report = {"status": "error", "message": str(e)}
        return json.dumps(status_report) # <--- FIX 2: Return a JSON string