from fastapi import FastAPI
import logging

# 1. Initialize the FastAPI app (Vercel looks for this variable)
app = FastAPI()

# 2. Move your original marketing automation logic inside this function
def run_marketing_automation():
    logging.info("Starting automation task...")
    
    # 💥 PASTE YOUR ORIGINAL CODE HERE 💥
    # (The code that reads data, processes messages, etc.)
    
    return {"status": "success", "message": "Automation tasks completed."}

# 3. Create a default landing page route
@app.get("/")
def home():
    return {
        "message": "Marketing Automation API is live!",
        "endpoints": {
            "trigger_tasks": "/run"
        }
    }

# 4. Create an endpoint to trigger your automation
@app.get("/run")
def trigger_tasks():
    try:
        result = run_marketing_automation()
        return result
    except Exception as e:
        logging.error(f"Automation failed: {str(e)}")
        return {"status": "failed", "error": str(e)}
