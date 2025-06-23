import gradio as gr
import requests
import uuid
import json
import re
import logging
import time
import tempfile
import base64
import os
from typing import Dict, List, Any, Generator

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://127.0.0.1:8000"
APP_NAME = "content_generation_agent"  # This must match your agent's directory name
GRADIO_SERVER_PORT = int(os.environ.get("PORT", 7860))

# --- UI Helper Functions ---

def parse_final_report(report_text: str) -> Dict[str, str]:
    """Parses the structured markdown report from the SynthesisAgent."""
    if not report_text: return {}
    
    def find_block(key: str) -> str:
        match = re.search(rf"{key.upper()}_START\s*(.*?)\s*{key.upper()}_END", report_text, re.DOTALL)
        return match.group(1).strip() if match else ""

    return {
        "blog": find_block("blog_post"),
        "linkedin": find_block("linkedin_post"),
        "x_post": find_block("x_post"),
        "threads_post": find_block("threads_post"),
        "podcast": find_block("podcast_script"),
        "image_prompt": find_block("image_prompt"),
        "media_status": find_block("media_status"),
    }

def create_new_session():
    """Creates a new user/session with the ADK server."""
    user_id = f"gradio-user-{uuid.uuid4()}"
    session_id = f"gradio-session-{uuid.uuid4()}"
    url = f"{API_BASE_URL}/apps/{APP_NAME}/users/{user_id}/sessions/{session_id}"
    try:
        response = requests.post(url, json={})
        response.raise_for_status()
        logger.info(f"Created new session: {session_id}")
        return user_id, session_id, f"✅ **Active Session:** `{session_id}`"
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create session: {e}")
        return None, None, "❌ **Connection Error:** Could not connect to ADK server."

def stream_agent_events(payload: dict) -> Generator[Dict, None, None]:
    """Streams Server-Sent Events from the ADK's /run_sse endpoint."""
    try:
        with requests.post(f"{API_BASE_URL}/run_sse", json=payload, stream=True, timeout=600) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line.startswith(b'data:'):
                    try:
                        yield json.loads(line.decode('utf-8')[5:])
                    except json.JSONDecodeError:
                        pass
    except requests.exceptions.RequestException as e:
        yield {"error": f"Connection to server failed: {e}"}

def fetch_media_artifacts(user_id: str, session_id: str):
    """Fetches generated image and audio artifacts from the ADK server."""
    log_updates = ""
    # Fetch Images
    image_filepaths = []
    log_updates += "\n* 🖼️ Fetching generated image artifacts..."
    for i in range(1, 5):
        artifact_name = f"generated_image_{i}.png"
        url = f"{API_BASE_URL}/apps/{APP_NAME}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}"
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                b64_data = response.json()['inlineData']['data']
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(base64.urlsafe_b64decode(b64_data))
                    image_filepaths.append(tmp.name)
                log_updates += f"\n  - ✅ Loaded `{artifact_name}`"
            else:
                log_updates += f"\n  - ⚠️ Could not load `{artifact_name}` (Status: {response.status_code})"
        except Exception as e:
            log_updates += f"\n  - ❌ Error loading `{artifact_name}`: {e}"
    
    # Fetch Audio
    audio_filepath = None
    log_updates += "\n* 🔊 Fetching audio artifact..."
    url = f"{API_BASE_URL}/apps/{APP_NAME}/users/{user_id}/sessions/{session_id}/artifacts/podcast_episode.wav"
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            b64_data = response.json()['inlineData']['data']
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(base64.urlsafe_b64decode(b64_data))
                audio_filepath = tmp.name
            log_updates += "\n* ✅ **Audio Loaded Successfully!**"
        else:
            log_updates += f"\n* ⚠️ **Warning:** Could not fetch audio (Status: {response.status_code})."
    except Exception as e:
        log_updates += f"\n* ❌ **Error:** Failed to process audio artifact: {e}."
        
    return image_filepaths, audio_filepath, log_updates

# --- Main Gradio Pipeline Function ---

def run_content_pipeline(user_query: str, user_id: str, session_id: str):
    """The main function driving the Gradio UI updates."""
    # Initialize UI state
    ui_state = {
        "blog": "", "linkedin": "", "x_post": "", "threads_post": "", "podcast": "", "audio": None, "images": [],
        "execution_log": "### Agent Execution Flow\n", "tabs": gr.Tabs(selected=0), "raw_json": [], "strategy_brief": {},
        "search_queries": "", "research_results": "", "dossier": "", "image_prompt": ""
    }
    yield list(ui_state.values())

    if not session_id:
        ui_state["execution_log"] += "\n* ❌ **Error:** Please create a session first."
        yield list(ui_state.values())
        return

    # Start the agent pipeline
    run_payload = {"app_name": APP_NAME, "user_id": user_id, "session_id": session_id, "new_message": {"role": "user", "parts": [{"text": user_query}]}}
    processed_authors = set()

    # Stream events and update UI in real-time
    for event in stream_agent_events(run_payload):
        ui_state["raw_json"].append(event)
        if event.get("error"):
            ui_state["execution_log"] += f"\n* ❌ **STREAM ERROR:** {event['error']}"
            yield list(ui_state.values())
            return

        author = event.get('author')
        if author and author not in processed_authors:
            ui_state["execution_log"] += f"\n* **Agent:** `{author}` is active..."
            processed_authors.add(author)

        # Update content from state deltas
        state_delta = event.get("actions", {}).get("stateDelta", {})
        if state_delta:
            key_map = {
                "image_prompt": "image_prompt", "blog_draft": "blog", "linkedin_draft": "linkedin",
                "x_post_draft": "x_post", "threads_post_draft": "threads_post", "podcast_draft": "podcast",
                "research_dossier": "dossier"
            }
            for key, ui_key in key_map.items():
                if key in state_delta:
                    ui_state[ui_key] = state_delta[key]
            
            if "content_brief" in state_delta:
                try: ui_state["strategy_brief"] = json.loads(re.sub(r'```json\n|\n```', '', state_delta["content_brief"]).strip())
                except json.JSONDecodeError: pass
        
        # Parse final report
        if event.get('author') == "SynthesisAgent" and event.get('is_final_response'):
            ui_state["execution_log"] += "\n* ✅ **Final Report Generated**"
            parsed_report = parse_final_report(event['content']['parts'][0]['text'])
            ui_state.update(parsed_report)
        
        yield list(ui_state.values())

    # After stream, fetch generated media artifacts
    images, audio, log_updates = fetch_media_artifacts(user_id, session_id)
    ui_state["images"] = images
    ui_state["audio"] = audio
    ui_state["execution_log"] += log_updates
    ui_state["execution_log"] += "\n\n🏁 **Pipeline Complete!**"
    yield list(ui_state.values())


# --- Gradio UI Definition ---
# (The Gradio UI block remains largely the same, as it was already well-structured)
with gr.Blocks(theme=gr.themes.Default(primary_hue="blue", secondary_hue="sky"), css="footer {display: none !important}") as demo:
    gr.Markdown("# 🤖 ADK Multi-Agent Content Factory")
    user_id_state, session_id_state = gr.State(), gr.State()
    with gr.Row():
        with gr.Column(scale=1, min_width=350):
            gr.Markdown("### ⚙️ Controls & Status")
            new_session_button = gr.Button("➕ New Session", variant="secondary")
            session_status_text = gr.Markdown("🔴 **No Active Session**")
            gr.Markdown("### 📝 Agent Execution Log")
            execution_log_output = gr.Markdown("Awaiting pipeline start...")
        with gr.Column(scale=3):
            gr.Markdown(
                """
                ### How to Use:
                1. Click **➕ New Session** to start.
                2. Enter a content topic below.
                3. Click **Generate Content ✨** and watch the agents work!
                """
            )
            query_input = gr.Textbox(label="Enter your content topic", placeholder="e.g., 'The future of AI'", interactive=False)
            submit_button = gr.Button("Generate Content ✨", variant="primary", interactive=False)
            output_tabs = gr.Tabs(elem_id="output_tabs")
            with output_tabs:
                with gr.TabItem("📝 Blog Post", id=0): blog_output = gr.Markdown()
                with gr.TabItem("🔗 LinkedIn Post", id=1): linkedin_output = gr.Markdown()
                with gr.TabItem("🐦 X (Twitter) Post", id=2): x_output = gr.Markdown()
                with gr.TabItem("🧵 Threads Post", id=3): threads_output = gr.Markdown()
                with gr.TabItem("▶️ Podcast Script", id=4): podcast_output = gr.Markdown()
                with gr.TabItem("🖼️ Generated Images", id=5):
                    image_gallery = gr.Gallery(label="Generated Images", columns=2, height="auto")
                with gr.TabItem("🎤 Podcast Audio", id=6): audio_output = gr.Audio(label="Generated Podcast Episode", type="filepath")
                with gr.TabItem("🔬 Behind the Scenes", id=7):
                    with gr.Accordion("Content Strategy & Research", open=True):
                        gr.Markdown("#### Content Brief"); strategy_brief_output = gr.Json()
                        gr.Markdown("#### Final Research Dossier"); dossier_output = gr.Markdown()
                        gr.Markdown("#### Final Image Prompt"); image_prompt_output = gr.Markdown()

    with gr.Accordion("Raw Server Response (Events JSON)", open=False): raw_json_output = gr.Json()

    def handle_new_session_ui(uid, sid): return (gr.Textbox(interactive=True), gr.Button(interactive=True), {}) if uid and sid else (gr.Textbox(interactive=False), gr.Button(interactive=False), {})
    new_session_button.click(fn=create_new_session, outputs=[user_id_state, session_id_state, session_status_text]).then(
        fn=handle_new_session_ui, inputs=[user_id_state, session_id_state], outputs=[query_input, submit_button, raw_json_output])
    
    submit_button.click(fn=run_content_pipeline, inputs=[query_input, user_id_state, session_id_state],
        outputs=[ blog_output, linkedin_output, x_output, threads_output, podcast_output, audio_output, image_gallery,
                  execution_log_output, output_tabs, raw_json_output, strategy_brief_output, 
                  gr.Markdown(), gr.Markdown(), dossier_output, image_prompt_output ]) # Empty markdown to match outputs list

if __name__ == "__main__":
    logger.info(f"Starting Gradio server on http://0.0.0.0:{GRADIO_SERVER_PORT}")
    demo.launch(server_name="0.0.0.0", server_port=GRADIO_SERVER_PORT)