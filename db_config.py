import sqlite3

# Connect to the database (or create if not exists)
conn = sqlite3.connect('agent_memory.db', check_same_thread=False)
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        user_query TEXT NOT NULL,
        agent_response TEXT NOT NULL,
        addresses TEXT,
        demands TEXT,
        plan_output TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Save a conversation
def save_conversation(user_id, user_query, agent_response, addresses=None, demands=None, plan_output=None):
    cursor.execute('''
        INSERT INTO conversations (
            user_id, user_query, agent_response, addresses, demands,
            plan_output
        )
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        user_query,
        agent_response,
        str(addresses) if addresses else None,
        str(demands) if demands else None,
        plan_output
    ))
    conn.commit()

# Retrieve conversations
def get_user_conversations(user_id, n=5):
    cursor.execute('''
        SELECT user_query, agent_response, plan_output FROM conversations
        WHERE user_id = ?
        ORDER BY timestamp DESC LIMIT ?
    ''', (user_id, n))
    
    rows = cursor.fetchall()
    context = ''
    for user_query, agent_response, plan_output in rows:
        context += f"\nUser: {user_query}\n"
        context += f"Agent: {agent_response}\n"
        context += f"Plan Output: {plan_output}\n"
    
    return context

# Example usage
# save_conversation("Where should I deliver order 1 last?", "Sure, I’ll optimize it accordingly.")
# conversations = get_all_conversations()
# for convo in conversations:
#     print(convo)
