import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """
    Initializes and returns a Supabase client using credentials from environment variables.
    """
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY not found in environment variables.")
    
    return create_client(url, key)

if __name__ == "__main__":
    # Test connection
    try:
        client = get_supabase_client()
        print("Successfully connected to Supabase.")
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}")
