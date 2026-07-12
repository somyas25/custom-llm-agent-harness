# app/tools.py
import os
import json
import urllib.request
from typing import Optional
from app.database import add_task, get_all_tasks

# Read the internal Mailpit container destination provided by Docker Compose
MAILPIT_URL = os.getenv("MAILPIT_API_URL", "http://localhost:8025/api/v1")

def search_and_fetch_emails(sender_filter: Optional[str] = None, limit: int = 5) -> str:
    """
    Fetches live unread messages from the mailbox API endpoint.
    Use this tool whenever the user asks to 'check emails', 'list messages', 
    or check for correspondence from a specific person.

    Args:
        sender_filter: Optional string to filter emails by sender email or name.
        limit: The maximum number of recent emails to return. Defaults to 5.
    """
    print(f" -> [Tool Execute] search_and_fetch_emails(sender_filter={sender_filter}, limit={limit})")
    
    # Mailpit REST API endpoint for pulling messages
    # Documentation reference: /api/v1/messages?limit=X
    api_endpoint = f"{MAILPIT_URL}/messages?limit={limit}"
    
    try:
        # Perform a clean, framework-free HTTP GET request to the Mailpit container
        with urllib.request.urlopen(api_endpoint, timeout=5) as response:
            if response.status != 200:
                return "Error: Unable to connect to the email server gateway."
                
            data = json.loads(response.read().decode())
            messages = data.get("messages", [])
            
        if not messages:
            return "Your inbox is completely empty. No unread messages found."
            
        # Process and filter the network payloads
        output = f"Retrieved {len(messages)} recent messages from server:\n"
        matched_count = 0
        
        for msg in messages:
            sender = msg.get("From", {}).get("Address", "Unknown")
            name = msg.get("From", {}).get("Name", "")
            full_sender_string = f"{name} <{sender}>"
            subject = msg.get("Subject", "(No Subject)")
            msg_id = msg.get("ID")
            
            # Apply dynamic sender filtering if requested by Gemini
            if sender_filter and (sender_filter.lower() not in full_sender_string.lower() and sender_filter.lower() not in subject.lower()):
                continue
                
            # To extract the raw text Body, Mailpit requires a separate quick lookup per message ID
            body_endpoint = f"{MAILPIT_URL}/message/{msg_id}"
            try:
                with urllib.request.urlopen(body_endpoint, timeout=2) as body_resp:
                    body_data = json.loads(body_resp.read().decode())
                    body_content = body_data.get("Snippet", body_data.get("Text", ""))
            except Exception:
                body_content = "[Could not parse message body contents]"
                
            output += f"--- Email ID: {msg_id} ---\n"
            output += f"From: {full_sender_string}\n"
            output += f"Subject: {subject}\n"
            output += f"Body: {body_content}\n\n"
            matched_count += 1

        if matched_count == 0 and sender_filter:
            return f"Found emails in the inbox, but none matched your sender filter: '{sender_filter}'."
            
        return output

    except Exception as e:
        return f"Tool Execution System Failure: Failed to connect to email API. Details: {str(e)}"

def create_task_from_email(title: str, summary: str, priority: str) -> str:
    """Adds an actionable item to the customer's prioritized task list database."""
    return add_task(title, summary, priority)

def view_current_task_list() -> str:
    """Retrieves a formatted table of all currently tracked tasks sorted by priority."""
    return get_all_tasks()