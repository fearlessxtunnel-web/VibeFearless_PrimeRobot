import time

chat_queues = {}
progress_tasks = {}
active_clients = {}
paused_chats = set()
user_command_history = {}
bot_start_time = time.time()
ASSISTANT_ID = None
ASSISTANT_USERNAME = None
