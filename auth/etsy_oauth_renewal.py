#!/usr/bin/env python3
"""
Etsy OAuth 2.0 Token Renewal Script
==================================

This script helps you renew your Etsy OAuth tokens by guiding you through
the OAuth 2.0 authorization flow to get fresh access and refresh tokens.

Requirements:
- ETSY_API_KEY and ETSY_API_SECRET in .env file
- Web browser access
- Etsy developer account with app configured

Usage:
    python auth/etsy_oauth_renewal.py
"""

import os
import sys
import requests
import urllib.parse
import secrets
import hashlib
import base64
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
from core.logger import setup_logger

# Load environment variables
load_dotenv()

# Set up logging
logger = setup_logger("etsy_oauth_renewal")


class EtsyOAuthRenewal:
    """Helper class for Etsy OAuth 2.0 token renewal."""
    
    def __init__(self):
        """Initialize with credentials from environment."""
        self.api_key = os.getenv("ETSY_API_KEY")
        self.api_secret = os.getenv("ETSY_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            raise ValueError("ETSY_API_KEY and ETSY_API_SECRET must be set in .env file")
        
        # OAuth 2.0 configuration with your custom callback URL
        self.redirect_uri = "https://www.meadownova.com/callback"
        self.auth_url = "https://www.etsy.com/oauth/connect"
        self.token_url = "https://api.etsy.com/v3/public/oauth/token"
        
        # Required scopes for SEA-E functionality
        self.scopes = [
            "listings_r",      # Read listings
            "listings_w",      # Write listings
            "shops_r",         # Read shop info
            "profile_r",       # Read profile
            "billing_r"        # Read billing (for shop verification)
        ]
    
    def generate_pkce_challenge(self):
        """Generate PKCE code verifier and challenge for OAuth 2.0."""
        # Generate code verifier (43-128 characters)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    def get_authorization_url(self):
        """Generate the authorization URL for OAuth flow."""
        code_verifier, code_challenge = self.generate_pkce_challenge()

        # Store code verifier for later use
        self.code_verifier = code_verifier

        # Save code verifier to file for later use
        with open('.etsy_code_verifier', 'w') as f:
            f.write(code_verifier)
        
        # Build authorization URL
        params = {
            "response_type": "code",
            "client_id": self.api_key,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": secrets.token_urlsafe(32),  # CSRF protection
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        auth_url = f"{self.auth_url}?" + urllib.parse.urlencode(params)
        return auth_url
    
    def exchange_code_for_tokens(self, authorization_code):
        """Exchange authorization code for access and refresh tokens."""
        logger.info("Exchanging authorization code for tokens...")

        # Try to read code verifier from file if not in memory
        if not hasattr(self, 'code_verifier'):
            try:
                with open('.etsy_code_verifier', 'r') as f:
                    self.code_verifier = f.read().strip()
                logger.info("✅ Code verifier loaded from file")
            except FileNotFoundError:
                logger.error("❌ Code verifier not found. Please run the authorization flow again.")
                return None

        data = {
            "grant_type": "authorization_code",
            "client_id": self.api_key,
            "redirect_uri": self.redirect_uri,
            "code": authorization_code,
            "code_verifier": self.code_verifier
        }
        
        try:
            response = requests.post(self.token_url, data=data, timeout=30)
            
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
    
    def update_env_file(self, tokens):
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
    """Main function to run the OAuth renewal process."""
    logger.info("=" * 60)
    logger.info("ETSY OAUTH 2.0 TOKEN RENEWAL")
    logger.info("=" * 60)
    
    try:
        # Initialize OAuth helper
        oauth = EtsyOAuthRenewal()
        
        # Step 1: Generate authorization URL
        logger.info("🔗 Generating authorization URL...")
        auth_url = oauth.get_authorization_url()
        
        logger.info("📋 AUTHORIZATION REQUIRED:")
        logger.info("1. Click the link below or copy it to your browser")
        logger.info("2. Log in to your Etsy account")
        logger.info("3. Authorize the application")
        logger.info("4. You'll be redirected to: https://www.meadownova.com/callback?code=...")
        logger.info("5. Copy the 'code' parameter from the URL")
        logger.info("")
        logger.info(f"🌐 Authorization URL:")
        logger.info(f"{auth_url}")
        logger.info("")
        
        # Try to open browser automatically
        try:
            webbrowser.open(auth_url)
            logger.info("✅ Browser opened automatically")
        except:
            logger.info("⚠️ Could not open browser automatically - please copy the URL manually")
        
        logger.info("")
        
        # Step 2: Get authorization code from user
        print("After authorizing the app, you'll be redirected to your callback URL.")
        print("The URL will look like: https://www.meadownova.com/callback?code=AUTHORIZATION_CODE&state=...")
        print("")

        authorization_code = input("📝 Enter the authorization code from the URL: ").strip()
        
        if not authorization_code:
            logger.error("❌ No authorization code provided")
            return False
        
        # Step 3: Exchange code for tokens
        tokens = oauth.exchange_code_for_tokens(authorization_code)
        
        if not tokens:
            logger.error("❌ Failed to obtain tokens")
            return False
        
        # Step 4: Update .env file
        if oauth.update_env_file(tokens):
            logger.info("🎉 OAuth renewal completed successfully!")
            logger.info("")
            logger.info("✅ New tokens have been saved to .env file")
            logger.info("✅ You can now run the Etsy authentication test:")
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
            
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
    finally:
        logger.info("=" * 60)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
