from os import environ
from dotenv import load_dotenv
import sys

load_dotenv()

# ========================================
# ENVIRONMENT VARIABLES VALIDATION
# ========================================

def get_env_var(key, default="", var_type=str, required=True):
    """
    Safely get environment variable with validation
    """
    value = environ.get(key, default)
    
    if required and not value:
        print(f"❌ ERROR: '{key}' environment variable is missing!")
        print(f"Please set '{key}' in your hosting platform's environment variables.")
        return None
    
    # Convert to required type
    try:
        if var_type == int:
            return int(value) if value else None
        elif var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on') if value else False
        else:
            return value
    except ValueError:
        print(f"❌ ERROR: '{key}' has invalid format. Expected {var_type.__name__}")
        return None

# ========================================
# LOAD AND VALIDATE ALL VARIABLES
# ========================================

print("🔄 Loading configuration...")

API_ID = get_env_var("API_ID", var_type=int, required=True)
API_HASH = get_env_var("API_HASH", required=True)
BOT_TOKEN = get_env_var("BOT_TOKEN", required=True)
LOG_CHANNEL = get_env_var("LOG_CHANNEL", var_type=int, required=True)
ADMINS = get_env_var("ADMINS", var_type=int, required=True)
DB_URI = get_env_var("DB_URI", required=True)

# Optional variables
DB_NAME = get_env_var("DB_NAME", default="vjjoinrequestbot", required=False)
NEW_REQ_MODE = get_env_var("NEW_REQ_MODE", default="False", var_type=bool, required=False)

# ========================================
# FINAL VALIDATION CHECK
# ========================================

required_vars = {
    'API_ID': API_ID,
    'API_HASH': API_HASH,
    'BOT_TOKEN': BOT_TOKEN,
    'LOG_CHANNEL': LOG_CHANNEL,
    'ADMINS': ADMINS,
    'DB_URI': DB_URI
}

missing_vars = [key for key, value in required_vars.items() if value is None or value == ""]

if missing_vars:
    print("\n" + "="*50)
    print("❌ CONFIGURATION ERROR!")
    print("="*50)
    print(f"\n⚠️  Missing variables: {', '.join(missing_vars)}\n")
    print("📋 Required Environment Variables:")
    print("   • API_ID      - Get from https://my.telegram.org")
    print("   • API_HASH    - Get from https://my.telegram.org")
    print("   • BOT_TOKEN   - Get from @BotFather")
    print("   • LOG_CHANNEL - Channel ID (starts with -100)")
    print("   • ADMINS      - Your Telegram User ID")
    print("   • DB_URI      - MongoDB connection string")
    print("\n💡 Set these in your hosting platform's environment variables section.")
    print("="*50 + "\n")
    sys.exit(1)

# Additional validations
if API_ID and API_ID == 0:
    print("❌ ERROR: API_ID cannot be 0")
    sys.exit(1)

if BOT_TOKEN and not BOT_TOKEN.count(':') == 1:
    print("❌ ERROR: BOT_TOKEN format invalid (should be like: 123456:ABC-DEF1234)")
    sys.exit(1)

if LOG_CHANNEL and LOG_CHANNEL >= 0:
    print("⚠️  WARNING: LOG_CHANNEL should be negative (starting with -100)")
    print(f"   Current value: {LOG_CHANNEL}")

if DB_URI and not DB_URI.startswith(('mongodb://', 'mongodb+srv://')):
    print("⚠️  WARNING: DB_URI should start with 'mongodb://' or 'mongodb+srv://'")
    print("   Make sure your MongoDB connection string is correct")

# Success message
print("\n✅ All environment variables loaded successfully!")
print(f"   • API_ID: {API_ID}")
print(f"   • API_HASH: {'*' * len(API_HASH) if API_HASH else 'Not Set'}")
print(f"   • BOT_TOKEN: {BOT_TOKEN[:10]}...{'*' * 20}")
print(f"   • LOG_CHANNEL: {LOG_CHANNEL}")
print(f"   • ADMINS: {ADMINS}")
print(f"   • DB_NAME: {DB_NAME}")
print(f"   • NEW_REQ_MODE: {NEW_REQ_MODE}")
print(f"   • DB Connected: {'Yes' if DB_URI else 'No'}")
print("="*50 + "\n")
