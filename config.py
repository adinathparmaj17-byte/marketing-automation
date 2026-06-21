"""
Configuration file for marketing automation.
Store all settings here. NEVER hardcode passwords in main code.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# EMAIL SETTINGS
# ============================================
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")       # your-email@gmail.com
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")      # app password (not regular password)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "Hello from Our Team!")

# ============================================
# WHATSAPP SETTINGS
# ============================================
# Batch size: how many messages before long pause
WA_BATCH_SIZE = 5

# Long pause after every batch (in seconds)
# 60 seconds = 1 minute
WA_BATCH_DELAY = 60

# Random micro delay between each message (in seconds)
# Script will wait random time between these two values
WA_MICRO_DELAY_MIN = 5
WA_MICRO_DELAY_MAX = 12

# ============================================
# FILE SETTINGS
# ============================================
INPUT_FILE = "contacts.xlsx"
OUTPUT_FILE = "campaign_results.xlsx"
LOG_FILE = "campaign.log"
