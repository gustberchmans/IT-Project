import firebase_admin
from firebase_admin import credentials, firestore, auth
from functools import lru_cache
import os

# Get the directory containing the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Create absolute path to serviceAccountKey.json
service_account_path = os.path.join(current_dir, "serviceAccountKey.json")

# Initialize Firebase Admin with your service account credentials
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred)

# Initialize Firestore with caching
db = firestore.client()

# Cache for user session
_current_user = None

@lru_cache(maxsize=128)
def get_user_data(user_id):
    """Cached function to get user data"""
    return db.collection('Users').document(user_id).get().to_dict()

def set_current_user(user_id):
    global _current_user
    _current_user = user_id

def get_current_user():
    return _current_user

def is_authenticated():
    return _current_user is not None

def logout():
    global _current_user
    _current_user = None
    get_user_data.cache_clear()  # Clear cache on logout

def verify_user(email, password):
    """
    Verify user credentials against Firebase
    Returns: (bool, str) - (success, message)
    """
    try:
        users_ref = db.collection('Users')
        # Query for user with matching email
        query = users_ref.where('email', '==', email).limit(1).get()
        
        if not query:
            return False, "User not found"
            
        user = next(iter(query), None)
        if not user:
            return False, "Invalid email or password"
            
        user_data = user.to_dict()
        
        if user_data['password'] != password:
            return False, "Invalid email or password"
        
        # Set current user on successful login
        set_current_user(user.id)
        return True, user.id
        
    except Exception as e:
        return False, f"Login error: {str(e)}"

@lru_cache(maxsize=128)
def get_user_progress(user_id):
    """Get user's learning progress from Firestore with caching"""
    try:
        user_doc = db.collection('Users').document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return user_data.get('progress', {})
        return {}
    except Exception:
        return {}
