#!/usr/bin/env python3
"""
Interactive setup script for Zoho Desk Call Ticket Processor
"""

import os
from pathlib import Path

def setup():
    """Interactive setup for credentials."""
    print("=" * 60)
    print("🎫 Zoho Desk Call Ticket Processor - Setup")
    print("=" * 60)
    print()
    
    # Check if .env already exists
    env_path = Path(".env")
    if env_path.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (yes/no): ").strip().lower()
        if overwrite != "yes":
            print("❌ Setup cancelled.")
            return
    
    print("📋 Please provide your credentials:")
    print()
    
    # Exotel credentials
    print("--- Exotel Configuration ---")
    exotel_sid = input("Exotel SID: ").strip()
    exotel_key = input("Exotel API Key: ").strip()
    exotel_token = input("Exotel API Token: ").strip()
    print()
    
    # Deepgram
    print("--- Deepgram Configuration ---")
    deepgram_key = input("Deepgram API Key: ").strip()
    print()
    
    # OpenAI (optional)
    print("--- OpenAI Configuration (Optional - press Enter to skip) ---")
    openai_key = input("OpenAI API Key (or leave empty): ").strip()
    print()
    
    # Zoho Desk
    print("--- Zoho Desk Configuration ---")
    print("See README.md for how to get these credentials")
    zoho_org_id = input("Organization ID: ").strip()
    zoho_access_token = input("Access Token: ").strip()
    zoho_refresh_token = input("Refresh Token: ").strip()
    zoho_client_id = input("Client ID: ").strip()
    zoho_client_secret = input("Client Secret: ").strip()
    zoho_department_id = input("Department ID: ").strip()
    print()
    
    # Optional settings
    print("--- Optional Settings (press Enter for defaults) ---")
    api_domain = input("API Domain [https://desk.zoho.com]: ").strip() or "https://desk.zoho.com"
    priority = input("Default Priority [Medium]: ").strip() or "Medium"
    auto_create = input("Auto-create contacts? [true]: ").strip() or "true"
    print()
    
    # Create .env file
    env_content = f"""# Exotel API Configuration
EXOTEL_SID={exotel_sid}
EXOTEL_API_KEY={exotel_key}
EXOTEL_API_TOKEN={exotel_token}

# Deepgram API Configuration
DEEPGRAM_API_KEY={deepgram_key}

# OpenAI API Configuration (Optional)
OPENAI_API_KEY={openai_key}

# Zoho Desk Configuration
ZOHO_DESK_ENABLED=true
ZOHO_DESK_ORG_ID={zoho_org_id}
ZOHO_DESK_ACCESS_TOKEN={zoho_access_token}
ZOHO_DESK_REFRESH_TOKEN={zoho_refresh_token}
ZOHO_DESK_CLIENT_ID={zoho_client_id}
ZOHO_DESK_CLIENT_SECRET={zoho_client_secret}
ZOHO_DESK_DEPARTMENT_ID={zoho_department_id}
ZOHO_DESK_API_DOMAIN={api_domain}
ZOHO_DESK_DEFAULT_PRIORITY={priority}
ZOHO_DESK_AUTO_CREATE_CONTACT={auto_create}
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("=" * 60)
    print("✅ Configuration saved to .env!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("1. Review agents_config.json and add your agents")
    print("2. Run: start.bat")
    print("3. Check zoho_processor.log for activity")
    print()
    print("🎉 Setup complete!")
    print()

if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

