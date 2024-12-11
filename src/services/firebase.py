import firebase_admin
from firebase_admin import credentials, firestore, auth
from functools import lru_cache
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
service_account_path = os.path.join(current_dir, "../../serviceAccountKey.json")

try:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
    print("Firebase app initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase app: {e}")

try:
    db = firestore.client()
    print("Firestore client initialized successfully.")
except Exception as e:
    print(f"Error initializing Firestore client: {e}")

_current_user = None

@lru_cache(maxsize=128)
def get_user_data(user_id):
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
    get_user_data.cache_clear()

def verify_user(email, password):
    try:
        users_ref = db.collection('Users')
        query = users_ref.where('email', '==', email).limit(1).get()
        
        if not query:
            return False, "User not found"
            
        user = next(iter(query), None)
        if not user:
            return False, "Invalid email or password"
            
        user_data = user.to_dict()
        
        if user_data['password'] != password:
            return False, "Invalid email or password"
        
        set_current_user(user.id)
        return True, user.id
        
    except Exception as e:
        return False, f"Login error: {str(e)}"

def add_score(user_id, score, quiz_id, total_questions):
    # Reference to the scores collection
    db.collection('scores').document(user_id).set({
        'user_id': user_id,  # Foreign key reference to the users collection
        'score': score,
        'quiz_id': quiz_id,  # Optional: to identify which quiz the score is for
        'timestamp': firestore.SERVER_TIMESTAMP,
        'total_questions': total_questions
    })

  