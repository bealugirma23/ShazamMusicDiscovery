import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url: str = os.getenv('SUPABASE_URL')
key: str = os.getenv('SUPABASE_KEY')
print("url", url)
print("key", key)

supabaseInit: Client = create_client(url, key)

print("supabase initialized")