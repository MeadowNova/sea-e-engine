#!/usr/bin/env python3
"""
Quick script to exchange Etsy authorization code for tokens
"""

import os
import sys
import requests
import hashlib
import base64
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
from core.logger import setup_logger

# Load environment variables
load_dotenv()

# Set up logging
logger = setup_logger("etsy_token_exchange")

def generate_pkce_challenge():
    """Generate PKCE code verifier and challenge for OAuth 2.0."""
    # Generate code verifier (43-128 characters)
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Generate code challenge
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge

def exchange_code_for_tokens(authorization_code):
    """Exchange authorization code for access and refresh tokens."""
    api_key = os.getenv("ETSY_API_KEY")

    if not api_key:
        logger.error("ETSY_API_KEY not found in environment")
        return None

    # Try to read code verifier from file
    try:
        with open('.etsy_code_verifier', 'r') as f:
            code_verifier = f.read().strip()
        logger.info("✅ Code verifier loaded from file")
    except FileNotFoundError:
        logger.error("❌ Code verifier not found. Please run: python auth/etsy_oauth_renewal.py")
        return None

    logger.info("Exchanging authorization code for tokens...")

    data = {
        "grant_type": "authorization_code",
        "client_id": api_key,
        "redirect_uri": "https://www.meadownova.com/callback",
        "code": authorization_code,
        "code_verifier": code_verifier
    }
    
    try:
        response = requests.post("https://api.etsy.com/v3/public/oauth/token", data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)
            
            logger.info("✅ Successfully obtained new tokens!")
            logger.info(f"Access token expires in: {expires_in} seconds")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in
            }
        else:
            logger.error(f"❌ Failed to exchange code for tokens: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Exception during token exchange: {e}")
        return None

def update_env_file(tokens):
    """Update .env file with new tokens."""
    logger.info("Updating .env file with new tokens...")
    
    env_path = Path(".env")
    
    try:
        # Read current .env file
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Update or add token lines
        updated_lines = []
        access_token_updated = False
        refresh_token_updated = False
        
        for line in lines:
            if line.startswith("ETSY_ACCESS_TOKEN="):
                updated_lines.append(f"ETSY_ACCESS_TOKEN={tokens['access_token']}\n")
                access_token_updated = True
            elif line.startswith("ETSY_REFRESH_TOKEN="):
                updated_lines.append(f"ETSY_REFRESH_TOKEN={tokens['refresh_token']}\n")
                refresh_token_updated = True
            else:
                updated_lines.append(line)
        
        # Add tokens if they weren't found in the file
        if not access_token_updated:
            updated_lines.append(f"ETSY_ACCESS_TOKEN={tokens['access_token']}\n")
        if not refresh_token_updated:
            updated_lines.append(f"ETSY_REFRESH_TOKEN={tokens['refresh_token']}\n")
        
        # Write updated .env file
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        logger.info("✅ .env file updated successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update .env file: {e}")
        return False

def main():
    """Main function."""
    logger.info("=" * 60)
    logger.info("ETSY TOKEN EXCHANGE")
    logger.info("=" * 60)
    
    # Your authorization code
    authorization_code = "B7INCgydpesEH3HENp6JGiN8Kw-G_kYpTECbHvjkKuxmeWFkdvzpPpqxDymIjOlnAPI02XEBxljH9dfXpvZUj-lvIvIk05HNtcqn"
    
    logger.info(f"Using authorization code: {authorization_code[:20]}...")
    
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(authorization_code)
    
    if tokens:
        # Update .env file
        if update_env_file(tokens):
            logger.info("🎉 Token exchange completed successfully!")
            logger.info("")
            logger.info("✅ New tokens have been saved to .env file")
            logger.info("✅ You can now test the Etsy authentication:")
            logger.info("   python auth/test_etsy_auth.py")
            logger.info("")
            logger.info("✅ Or test the full SEA-E engine:")
            logger.info("   python run_engine.py --list-manifests")
            return True
        else:
            logger.error("❌ Failed to save tokens to .env file")
            logger.info("📋 Manual update required:")
            logger.info(f"ETSY_ACCESS_TOKEN={tokens['access_token']}")
            logger.info(f"ETSY_REFRESH_TOKEN={tokens['refresh_token']}")
            return False
    else:
        logger.error("❌ Failed to obtain tokens")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
