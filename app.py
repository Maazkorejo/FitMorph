import os
import gradio as gr
from main import app as fastapi_app
from seed_data import seed_database

# 0. ZeroGPU compatibility if running on Hugging Face ZeroGPU hardware
try:
    import spaces
    @spaces.GPU
    def init_gpu():
        return True
    init_gpu()
    print("[Setup] Hugging Face ZeroGPU initialized.")
except Exception:
    pass

# 1. Initialize and seed SQLite database if not present
if not os.path.exists("fitmorph.db"):
    print("[Setup] Database not found. Initializing and seeding...")
    seed_database()
    print("[Setup] Database seeded successfully.")

# 2. Ensure upload and report directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# 3. Mount full-viewport responsive FitMorph application into Gradio
with gr.Blocks(title="FitMorph — Adaptive Fitness Intelligence", fill_height=True) as demo:
    gr.HTML("""
    <style>
      .gradio-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; background: #0A0D12 !important; }
      footer { display: none !important; }
    </style>
    <iframe src="/app-view" style="position:fixed; top:0; left:0; width:100vw; height:100vh; border:none; margin:0; padding:0; z-index:999999;"></iframe>
    """)

# Mount Gradio at root of FastAPI application
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    demo.launch()
