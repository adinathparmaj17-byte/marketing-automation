"""
WhatsApp sending module.
Uses pywhatkit to send messages via WhatsApp Web.
Implements anti-spam measures: batch delays + micro delays + personalization.
"""

import time
import random
import pywhatkit
from config import (
    WA_BATCH_SIZE,
    WA_BATCH_DELAY,
    WA_MICRO_DELAY_MIN,
    WA_MICRO_DELAY_MAX,
)


def validate_phone(phone):
    """
    Validate and clean phone number.
    Must start with country code (e.g., +91 for India).
    
    Args:
        phone: Raw phone number from Excel
    
    Returns:
        str or None: Cleaned phone number or None if invalid
    """
    
    if phone is None:
        return None
    
    # Convert to string and clean
    phone = str(phone).strip()
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Add + if missing
    if not phone.startswith("+"):
        # Assume India (+91) if no country code
        # Change this for your country
        if len(phone) == 10:
            phone = "+91" + phone
        else:
            phone = "+" + phone
    
    # Basic validation: must have at least 10 digits after +
    digits_only = phone.replace("+", "")
    if not digits_only.isdigit() or len(digits_only) < 10:
        return None
    
    return phone


def send_whatsapp_messages(contacts_list, logger):
    """
    Send WhatsApp messages with anti-spam protection.
    
    Implements:
    - Batch sending (5 messages per batch)
    - 1 minute pause between batches
    - Random 5-12 second delay between each message
    - Name personalization to avoid identical messages
    
    Args:
        contacts_list (list): List of dicts with keys: name, phone, message
        logger: Logger instance
    
    Returns:
        list: Results with status for each contact
    """
    
    results = []
    batch_count = 0
    total = len(contacts_list)
    
    logger.info(f"WHATSAPP    | Starting campaign for {total} contacts")
    logger.info(f"WHATSAPP    | Batch size: {WA_BATCH_SIZE} | "
                f"Batch delay: {WA_BATCH_DELAY}s | "
                f"Micro delay: {WA_MICRO_DELAY_MIN}-{WA_MICRO_DELAY_MAX}s")
    
    for i, contact in enumerate(contacts_list, 1):
        name = contact["name"]
        phone = contact["phone"]
        message = contact["message"]
        
        # Validate phone number
        clean_phone = validate_phone(phone)
        if clean_phone is None:
            logger.warning(f"SKIP WA     | Invalid phone for {name}: '{phone}'")
            results.append({
                "name": name,
                "phone": phone,
                "status": "Failed",
                "reason": "Invalid phone number"
            })
            continue
        
        # Validate message
        if not message or str(message).strip() == "":
            logger.warning(f"SKIP WA     | Empty message for {name}")
            results.append({
                "name": name,
                "phone": clean_phone,
                "status": "Failed",
                "reason": "Empty message"
            })
            continue
        
        # Personalize message — replace {name} with actual name
        # This makes each message unique (anti-spam measure)
        personalized_msg = str(message).replace("{name}", str(name))
        
        # Add slight random variation to further avoid spam detection
        greetings = ["Hi", "Hello", "Hey", "Dear"]
        random_greeting = random.choice(greetings)
        personalized_msg = f"{random_greeting} {name},\n\n{personalized_msg}"
        
        try:
            logger.info(f"SENDING WA  | [{i}/{total}] To: {clean_phone} | Name: {name}")
            
            # Send message using pywhatkit
            # wait_time=15: waits 15 seconds for WhatsApp Web to load
            # tab_close=True: closes the tab after sending
            # close_time=3: waits 3 seconds before closing tab
            pywhatkit.sendwhatmsg_instantly(
                phone_no=clean_phone,
                message=personalized_msg,
                wait_time=15,
                tab_close=True,
                close_time=3
            )
            
            logger.info(f"WA SENT     | [{i}/{total}] To: {clean_phone} | Name: {name}")
            results.append({
                "name": name,
                "phone": clean_phone,
                "status": "Sent",
                "reason": "Success"
            })
            
        except Exception as e:
            logger.error(f"WA FAIL     | [{i}/{total}] To: {clean_phone} | Error: {str(e)}")
            results.append({
                "name": name,
                "phone": clean_phone,
                "status": "Failed",
                "reason": str(e)
            })
        
        # ========================================
        # ANTI-SPAM DELAYS
        # ========================================
        
        batch_count += 1
        
        # Check if batch is complete
        if batch_count >= WA_BATCH_SIZE and i < total:
            # BATCH DELAY — 1 minute pause after every 5 messages
            logger.info(f"BATCH PAUSE | Completed batch of {WA_BATCH_SIZE}. "
                        f"Waiting {WA_BATCH_DELAY} seconds...")
            time.sleep(WA_BATCH_DELAY)
            batch_count = 0
            logger.info(f"BATCH PAUSE | Resuming...")
            
        elif i < total:
            # MICRO DELAY — random 5-12 second pause between each message
            micro_delay = random.uniform(WA_MICRO_DELAY_MIN, WA_MICRO_DELAY_MAX)
            logger.info(f"MICRO DELAY | Waiting {micro_delay:.1f} seconds...")
            time.sleep(micro_delay)
    
    # Summary
    sent = sum(1 for r in results if r["status"] == "Sent")
    failed = sum(1 for r in results if r["status"] == "Failed")
    logger.info(f"WA COMPLETE | Sent: {sent} | Failed: {failed} | Total: {total}")
    
    return results
