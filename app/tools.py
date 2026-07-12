# app/tools.py
from app.database import add_task, get_all_tasks

def fetch_unread_emails() -> str:
    """
    Simulates fetching recent unread emails from the user's inbox.
    Use this tool at the start of the triage cycle to find out what requests have come in.
    """
    # Simulated email box payload
    mock_inbox = [
        {
            "id": "msg_001",
            "sender": "landlord@apartments.com",
            "subject": "Urgent: Lease Renewal Notice",
            "body": "Hi, your current lease expires soon. Please sign the renewal paperwork and update your renter's insurance details by Friday at 5 PM."
        },
        {
            "id": "msg_002",
            "sender": "ai-weekly-newsletter@media.io",
            "subject": "Top 10 Agent Trends for 2026",
            "body": "In this week's edition, we explore how frameworkless agent harnesses are changing the way production engineering is approached..."
        },
        {
            "id": "msg_003",
            "sender": "team-lead@company.com",
            "subject": "Code Review: Merge Request #412",
            "body": "Can you take a look at the open merge request for the Docker container update when you have a moment? No immediate rush, sometime before Monday is fine."
        }
    ]
    
    # Format the data into an easy-to-read layout for the LLM context window
    output = "Unread Emails:\n"
    for email in mock_inbox:
        output += f"--- Email ID: {email['id']} ---\n"
        output += f"From: {email['sender']}\n"
        output += f"Subject: {email['subject']}\n"
        output += f"Body: {email['body']}\n\n"
        
    return output

def create_task_from_email(title: str, summary: str, priority: str) -> str:
    """
    Adds a verified actionable item to the customer's prioritized task list database.
    Use this tool when an email contains an explicit request, task, or deadline.
    
    Args:
        title: A brief, clear title for the task (e.g., 'Sign apartment lease renewal').
        summary: A concise description of what needs to be done and its deadline.
        priority: The urgency level. Must be exactly 'High', 'Medium', or 'Low'.
    """
    # This calls our safe, parameterized SQLite function from app/database.py
    return add_task(title, summary, priority)

def view_current_task_list() -> str:
    """
    Retrieves a formatted table of all currently tracked tasks sorted by priority.
    Use this to see if a task already exists or to show the user their list.
    """
    return get_all_tasks()