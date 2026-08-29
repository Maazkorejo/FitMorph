import os
import uvicorn
import gradio as gr
from main import app as fastapi_app
from seed_data import seed_database

# 1. Initialize and seed SQLite database if not present
if not os.path.exists("fitmorph.db"):
    print("[Setup] Database not found. Initializing and seeding...")
    seed_database()
    print("[Setup] Database seeded successfully.")

# 2. Ensure upload and report directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# 3. Mount Gradio to FastAPI so Hugging Face Spaces recognizes it natively,
# while serving our full FitMorph custom athletic web app at the root (/) and /static
with gr.Blocks(title="FitMorph") as demo:
    gr.HTML("<meta http-equiv='refresh' content='0; url=/'>")

app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    print(f"[Ready] FitMorph running on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
