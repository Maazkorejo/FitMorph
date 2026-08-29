import os
import uvicorn
import urllib.request
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

# 2. Ensure storage and asset directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# 3. Ensure high-resolution brand and fitness imagery are hydrated from GitHub CDN
img_dir = os.path.join(os.path.dirname(__file__), "app", "static", "img")
os.makedirs(img_dir, exist_ok=True)
cdn_base = "https://raw.githubusercontent.com/Maazkorejo/FitMorph/main/app/static/img"
for img_name in ["logo.jpg", "hero_gym.jpg", "hero_cardio.jpg", "hero_scan.jpg"]:
    local_path = os.path.join(img_dir, img_name)
    if not os.path.exists(local_path) or os.path.getsize(local_path) < 1000:
        try:
            print(f"[Assets] Hydrating {img_name} from GitHub CDN...")
            urllib.request.urlretrieve(f"{cdn_base}/{img_name}", local_path)
            print(f"[Assets] {img_name} loaded successfully.")
        except Exception as e:
            print(f"[Assets] Note on {img_name}: {e}")

# 4. Mount our custom FastAPI app with Gradio and launch via Gradio's managed server
with gr.Blocks(title="FitMorph — Adaptive Fitness Intelligence") as demo:
    gr.HTML("<meta http-equiv='refresh' content='0; url=/'>")

app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")
demo.app = app

if __name__ == "__main__":
    demo.launch()
