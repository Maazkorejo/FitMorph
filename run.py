import uvicorn
import os
import sys

def main():
    print("=" * 60)
    print("           FITMORPH ATHLETIC INTELLIGENCE ENGINE           ")
    print("   Adaptive Periodization, Injury Shield & Vision AI Coach ")
    print("=" * 60)

    # 1. Check if database exists; if not, automatically seed
    db_file = "fitmorph.db"
    if not os.path.exists(db_file):
        print("[Setup] Database not found. Initializing and seeding database...")
        from seed_data import seed_database
        seed_database()
        print("[Setup] Seed complete.")
    else:
        print("[Setup] SQLite database verified.")

    # 2. Ensure directories exist
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    print("[Ready] Server starting at http://127.0.0.1:8000")
    print("[Docs]  Interactive Swagger UI: http://127.0.0.1:8000/docs")
    print("[Health] API Status endpoint:   http://127.0.0.1:8000/health")
    print("=" * 60)

    # 3. Launch Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
