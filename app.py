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

# 4. Route serving index.html with iframe headers
@fastapi_app.get("/app-view")
def app_view():
    from fastapi.responses import FileResponse
    index_path = os.path.join(os.path.dirname(__file__), "app", "static", "index.html")
    response = FileResponse(index_path)
    response.headers["X-Frame-Options"] = "ALLOWALL"
    response.headers["Content-Security-Policy"] = "frame-ancestors *"
    return response

# 5. Embed full responsive FitMorph application inside Gradio Space
with gr.Blocks(title="FitMorph — Adaptive Fitness Intelligence", fill_height=True) as demo:
    gr.HTML('''
    <style>
      .gradio-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
      footer { display: none !important; }
    </style>
    <iframe src="/app-view" style="position:fixed; top:0; left:0; width:100vw; height:100vh; border:none; margin:0; padding:0; z-index:999999;"></iframe>
    ''')

app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")
demo.app = app

if __name__ == "__main__":
    demo.launch()
