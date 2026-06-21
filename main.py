"""
Marketing Automation Script
============================
Automates Email and WhatsApp marketing campaigns
using contact data from an Excel spreadsheet.

Features:
- Email sending via SMTP (Gmail)
- WhatsApp sending via pywhatkit
- Anti-spam protection (batch delays + micro delays)
- Message personalization
- Full logging and result tracking
- Output results to Excel

Usage:
    1. Fill in contacts.xlsx with your data
    2. Set up .env file with your credentials
    3. Run: python main.py
    
Author: Marketing Automation Tool
"""

import sys
import time
import pandas as pd
from datetime import datetime

# Import our modules
from config import INPUT_FILE, OUTPUT_FILE
from logger_setup import setup_logger
from email_sender import send_email
from whatsapp_sender import send_whatsapp_messages, validate_phone


def load_contacts(filepath, logger):
    """
    Load and validate contacts from Excel file.
    
    Expected columns: Name, Email, Phone_Number, Email_Message, WA_Message
    
    Args:
        filepath (str): Path to Excel file
        logger: Logger instance
    
    Returns:
        pandas.DataFrame: Validated contact data
    """
    
    try:
        df = pd.read_excel(filepath, engine="openpyxl")
        logger.info(f"LOADED      | {len(df)} contacts from '{filepath}'")
        
    except FileNotFoundError:
        logger.error(f"FILE ERROR  | '{filepath}' not found!")
        logger.error(f"FILE ERROR  | Create '{filepath}' with columns: "
                     f"Name, Email, Phone_Number, Email_Message, WA_Message")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"FILE ERROR  | Cannot read '{filepath}': {str(e)}")
        sys.exit(1)
    
    # Check required columns exist
    required_columns = ["Name", "Email", "Phone_Number", "Email_Message", "WA_Message"]
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        logger.error(f"FILE ERROR  | Missing columns: {missing}")
        logger.error(f"FILE ERROR  | Your Excel must have: {required_columns}")
        sys.exit(1)
    
    # Remove completely empty rows
    df = df.dropna(how="all")
    
    # Fill NaN with empty string for message columns
    df["Email_Message"] = df["Email_Message"].fillna("")
    df["WA_Message"] = df["WA_Message"].fillna("")
    df["Name"] = df["Name"].fillna("Friend")
    
    logger.info(f"VALIDATED   | {len(df)} valid contacts ready")
    
    return df


def run_email_campaign(df, logger):
    """
    Run email campaign for all contacts.
    
    Args:
        df (pandas.DataFrame): Contact data
        logger: Logger instance
    
    Returns:
        list: Email status for each contact
    """
    
    results = []
    total = len(df)
    
    logger.info("=" * 60)
    logger.info("EMAIL CAMPAIGN STARTING")
    logger.info("=" * 60)
    
    for index, row in df.iterrows():
        name = str(row["Name"])
        email = str(row["Email"]).strip()
        message = str(row["Email_Message"])
        
        # Skip if no email address
        if not email or email == "nan" or "@" not in email:
            logger.warning(f"SKIP EMAIL  | No valid email for {name}")
            results.append("Skipped")
            continue
        
        # Skip if no message
        if not message or message.strip() == "" or message == "nan":
            logger.warning(f"SKIP EMAIL  | No message for {name}")
            results.append("Skipped")
            continue
        
        # Send the email
        success = send_email(name, email, message, logger)
        results.append("Sent" if success else "Failed")
        
        # Small delay between emails (2 seconds)
        time.sleep(2)
    
    sent = results.count("Sent")
    failed = results.count("Failed")
    skipped = results.count("Skipped")
    
    logger.info(f"EMAIL DONE  | Sent: {sent} | Failed: {failed} | Skipped: {skipped}")
    
    return results


def run_whatsapp_campaign(df, logger):
    """
    Run WhatsApp campaign for all contacts.
    
    Args:
        df (pandas.DataFrame): Contact data
        logger: Logger instance
    
    Returns:
        list: WhatsApp status for each contact
    """
    
    logger.info("=" * 60)
    logger.info("WHATSAPP CAMPAIGN STARTING")
    logger.info("=" * 60)
    
    # Build contacts list for WhatsApp sender
    wa_contacts = []
    skip_indices = []
    
    for index, row in df.iterrows():
        name = str(row["Name"])
        phone = row["Phone_Number"]
        message = str(row["WA_Message"])
        
        # Skip if no phone
        if pd.isna(phone) or str(phone).strip() == "":
            logger.warning(f"SKIP WA     | No phone number for {name}")
            skip_indices.append(index)
            continue
        
        # Skip if no message
        if not message or message.strip() == "" or message == "nan":
            logger.warning(f"SKIP WA     | No message for {name}")
            skip_indices.append(index)
            continue
        
        wa_contacts.append({
            "name": name,
            "phone": phone,
            "message": message,
            "index": index
        })
    
    # Send all WhatsApp messages with anti-spam protection
    if wa_contacts:
        wa_results = send_whatsapp_messages(wa_contacts, logger)
    else:
        logger.warning("SKIP WA     | No valid WhatsApp contacts found")
        wa_results = []
    
    # Build results list matching DataFrame order
    results = ["Skipped"] * len(df)
    
    for i, contact in enumerate(wa_contacts):
        if i < len(wa_results):
            results[contact["index"]] = wa_results[i]["status"]
    
    return results


def save_results(df, email_results, wa_results, logger):
    """
    Save campaign results to Excel file.
    
    Args:
        df (pandas.DataFrame): Original contact data
        email_results (list): Email send status
        wa_results (list): WhatsApp send status
        logger: Logger instance
    """
    
    try:
        # Add result columns
        results_df = df.copy()
        results_df["Email_Status"] = email_results
        results_df["WhatsApp_Status"] = wa_results
        results_df["Campaign_Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to Excel
        results_df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
        logger.info(f"RESULTS     | Saved to '{OUTPUT_FILE}'")
        
    except Exception as e:
        logger.error(f"SAVE ERROR  | Cannot save results: {str(e)}")


def main():
    """
    Main function — orchestrates the entire campaign.
    """
    
    # Set up logging
    logger = setup_logger()
    
    logger.info("=" * 60)
    logger.info("MARKETING AUTOMATION CAMPAIGN")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Load contacts from Excel
    df = load_contacts(INPUT_FILE, logger)
    
    # Show preview
    logger.info(f"PREVIEW     | First 3 contacts:")
    for i, row in df.head(3).iterrows():
        logger.info(f"             | {row['Name']} | {row['Email']} | {row['Phone_Number']}")
    
    # Ask user what to run
    print("\n" + "=" * 50)
    print("MARKETING AUTOMATION CAMPAIGN")
    print("=" * 50)
    print(f"\nLoaded {len(df)} contacts from '{INPUT_FILE}'")
    print("\nWhat would you like to run?")
    print("  1 → Email campaign only")
    print("  2 → WhatsApp campaign only")
    print("  3 → Both Email + WhatsApp")
    print("  0 → Exit")
    
    choice = input("\nEnter your choice (0/1/2/3): ").strip()
    
    email_results = ["Not Run"] * len(df)
    wa_results = ["Not Run"] * len(df)
    
    if choice == "1":
        email_results = run_email_campaign(df, logger)
        
    elif choice == "2":
        print("\n⚠️  IMPORTANT: WhatsApp Web must be open and logged in!")
        print("   Open https://web.whatsapp.com in your browser first.")
        input("\n   Press Enter when WhatsApp Web is ready...")
        wa_results = run_whatsapp_campaign(df, logger)
        
    elif choice == "3":
        # Run email first
        email_results = run_email_campaign(df, logger)
        
        # Then WhatsApp
        print("\n⚠️  IMPORTANT: WhatsApp Web must be open and logged in!")
        print("   Open https://web.whatsapp.com in your browser first.")
        input("\n   Press Enter when WhatsApp Web is ready...")
        wa_results = run_whatsapp_campaign(df, logger)
        
    elif choice == "0":
        logger.info("CANCELLED   | User exited")
        sys.exit(0)
        
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)
    
    # Save results to Excel
    save_results(df, email_results, wa_results, logger)
    
    # Final summary
    logger.info("=" * 60)
    logger.info("CAMPAIGN COMPLETE")
    logger.info(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Results saved to: {OUTPUT_FILE}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
