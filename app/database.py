import sqlite3
from app.config import Config

"""Establishes a connection to the SQLite database using the configured path."""
def get_db_connection():
    # Connecting to the on-disk database listed in the Config class
    conn = sqlite3.connect(Config.DATABASE_PATH)

    # Row factory allows us to access columns by name like a dictionary: row['title']
    conn.row_factory = sqlite3.Row
    return conn

"""Creates the necessary tables if they do not exist yet."""
def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create the tasks table with explicit structured constraints
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT,
            priority TEXT CHECK(priority IN ('High', 'Medium', 'Low')) DEFAULT 'Medium',
            status TEXT CHECK(status IN ('Pending', 'Completed')) DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

"""Inserts a new task into the database. Exposed as an agent tool."""
def add_task(title: str, summary: str, priority: str = "Medium") -> str:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, summary, priority) VALUES (?, ?, ?)",
            (title, summary, priority)
        )
        conn.commit()
        conn.close()
        return f"Success: Task '{title}' added with {priority} priority."
    except Exception as e:
        return f"Error adding task: {str(e)}"

"""Retrieves all tasks sorted by priority hierarchy. Exposed as an agent tool."""
def get_all_tasks() -> str:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sort using a custom CASE statement so High priority appears first
        cursor.execute('''
            SELECT * FROM tasks 
            ORDER BY 
                CASE priority 
                    WHEN 'High' THEN 1 
                    WHEN 'Medium' THEN 2 
                    WHEN 'Low' THEN 3 
                END, created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "The task list is currently empty."
            
        # Format the output into a clean string representation for the LLM to read easily
        result = "Current Task List:\n"
        for row in rows:
            result += f"- [{row['priority']}] {row['title']}: {row['summary']} ({row['status']})\n"
        return result
    except Exception as e:
        return f"Error retrieving tasks: {str(e)}"