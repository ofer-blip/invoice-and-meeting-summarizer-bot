import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.cloud import firestore
import config

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

# Initialize Firestore Client (auto-detects GCP credentials from Cloud Run)
db = firestore.Client(database='default')

def get_flow():
    # Will need the redirect_uri to be set by the Flask request
    return Flow.from_client_secrets_file(
        config.CREDENTIALS_FILE,
        scopes=SCOPES
    )

def get_all_active_users():
    """Returns a list of email strings for all active users."""
    try:
        users_ref = db.collection('users').where('isActive', '==', True).stream()
        return [doc.id for doc in users_ref]
    except Exception as e:
        print(f"Firestore fallback (not initialized?): {e}")
        return []

def get_credentials_for_user(email):
    """Fetches credentials from Firestore for the given user, refreshing if necessary."""
    doc_ref = db.collection('users').document(email)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    
    data = doc.to_dict()
    token_json = data.get('token_json')
    if not token_json:
        return None
    
    creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
    
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                save_credentials_for_user(email, creds)
            except Exception:
                return None
    return creds

def save_credentials_for_user(email, creds):
    """Saves valid credentials to Firestore."""
    doc_ref = db.collection('users').document(email)
    token_json = creds.to_json()
    
    # Initialize categories if they don't exist
    doc = doc_ref.get()
    data = {'email': email, 'token_json': token_json, 'isActive': True}
    if not doc.exists or 'categories' not in doc.to_dict():
        data['categories'] = [{"name": "כללי", "prompt": ""}] # Default category
        
    doc_ref.set(data, merge=True)

def get_user_categories(email):
    """Get the list of custom categories for a user (list of dicts)."""
    doc_ref = db.collection('users').document(email)
    doc = doc_ref.get()
    if doc.exists:
        raw_categories = doc.to_dict().get('categories', [])
        # Backwards compatibility check: if it's a list of strings, convert to dicts
        normalized = []
        for c in raw_categories:
            if isinstance(c, str):
                normalized.append({"name": c, "prompt": "", "transcribe": False})
            elif isinstance(c, dict):
                c['transcribe'] = c.get('transcribe', False)
                normalized.append(c)
        return normalized
    return []

def update_user_categories(email, categories):
    """Updates the list of categories (dicts) for a user."""
    doc_ref = db.collection('users').document(email)
    doc_ref.set({'categories': categories}, merge=True)

def get_google_credentials():
    """Legacy method for backwards compatibility with single-user execution."""
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, SCOPES)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
            
    # Try active users from DB as fallback
    active_users = get_all_active_users()
    if active_users:
        return get_credentials_for_user(active_users[0])
        
    return None

def get_all_users_admin():
    """Fetches all users with their billing data for the admin panel."""
    users = []
    docs = db.collection('users').stream()
    for doc in docs:
        data = doc.to_dict()
        users.append({
            "email": doc.id,
            "minutes_used": data.get("minutes_used", 0),
            "minutes_limit": data.get("minutes_limit", 30),
            "num_uses": data.get("num_uses", 0), # Default 30 min trial
            "is_active": data.get("is_active", True)
        })
    return users

def update_user_billing(email, minutes_limit, is_active):
    """Admin updates user billing configuration."""
    db.collection('users').document(email).set({
        "minutes_limit": minutes_limit,
        "is_active": is_active
    }, merge=True)

def get_user_billing(email):
    """Gets current billing status for a user."""
    doc = db.collection('users').document(email).get()
    if doc.exists:
        data = doc.to_dict()
        return {
            "minutes_used": data.get("minutes_used", 0),
            "minutes_limit": data.get("minutes_limit", 30),
            "num_uses": data.get("num_uses", 0),
            "is_active": data.get("is_active", True)
        }
    return {"minutes_used": 0, "minutes_limit": 30, "is_active": True}

def increment_user_minutes(email, minutes_to_add):
    """Increments the used minutes counter for a user."""
    doc_ref = db.collection('users').document(email)
    doc = doc_ref.get()
    current = doc.to_dict().get("minutes_used", 0) if doc.exists else 0
    doc_ref.set({"minutes_used": current + minutes_to_add}, merge=True)
