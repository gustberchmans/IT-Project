import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from functools import lru_cache
import os
from datetime import datetime
from datetime import timedelta


current_dir = os.path.dirname(os.path.abspath(__file__))
service_account_path = os.path.join(current_dir, "../../serviceAccountKey.json")



try:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'it-projectv2.firebasestorage.app'  # Specify the storage bucket
    })
    print("------------------------------------------")
    print("Firebase app initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase app: {e}")

try:
    db = firestore.client()
    print("Firestore client initialized successfully.")
    print("------------------------------------------")
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

def load_progress(user_id):
    try:
        progress_ref = db.collection('progress').document(user_id)
        progress_doc = progress_ref.get()
        
        if progress_doc.exists:
            return progress_doc.to_dict()
        else:
            # Hier stellen we de structuur in met de verschillende levels voor elke difficulty
            progress_ref.set({
                'difficulty1': {
                    'd1l1': 0,
                    'd1l2': 0,
                    'd1l3': 0
                },
                'difficulty2': {
                    'd2l1': 0,
                    'd2l2': 0,
                    'd2l3': 0
                },
                'difficulty3': {
                    'd3l1': 0,
                    'd3l2': 0,
                    'd3l3': 0
                }
            })
            return {
                'difficulty1': {
                    'd1l1': 0,
                    'd1l2': 0,
                    'd1l3': 0
                },
                'difficulty2': {
                    'd2l1': 0,
                    'd2l2': 0,
                    'd2l3': 0
                },
                'difficulty3': {
                    'd3l1': 0,
                    'd3l2': 0,
                    'd3l3': 0
                }
            }
    except Exception as e:
        print(f"Error loading progress: {e}")
        return {
            'difficulty1': {
                'd1l1': 0,
                'd1l2': 0,
                'd1l3': 0
            },
            'difficulty2': {
                'd2l1': 0,
                'd2l2': 0,
                'd2l3': 0
            },
            'difficulty3': {
                'd3l1': 0,
                'd3l2': 0,
                'd3l3': 0
            }
        }

def update_progress(user_id, difficulty, level, progress):
    """
    Update the progress of a specific level for a user in Firestore.
    
    :param user_id: The ID of the user.
    :param difficulty: The difficulty level (e.g., 'difficulty1', 'difficulty2', 'difficulty3').
    :param level: The specific level within the difficulty (e.g., 'd1l1', 'd1l2').
    :param progress: The progress to set (typically 0 or 1 for unfinished/finished).
    """
    try:
        # Verkrijg het document van de gebruiker uit Firestore
        progress_ref = db.collection('progress').document(user_id)
        progress_doc = progress_ref.get()
        
        if progress_doc.exists:
            # Haal de bestaande data op
            data = progress_doc.to_dict()

            # Update de voortgang van het specifieke level binnen de juiste difficulty
            if difficulty in data:
                data[difficulty][level] = progress
            else:
                # Als de difficulty nog niet bestaat, voeg dan een nieuwe toe
                data[difficulty] = {level: progress}
            
            # Update het document in Firestore met de nieuwe data
            progress_ref.update(data)
            print("------------------------------------------")
            print(f"Progress for {difficulty} - {level} updated to {progress}")
            print("------------------------------------------")
        else:
            print("------------------------------------------")
            print(f"No data found for user {user_id}")
            print("------------------------------------------")
    except Exception as e:
        print("------------------------------------------")
        print(f"Error updating progress: {e}")
        print("------------------------------------------")

# Functie om streak bij te werken
def update_streak(user_id):
    try:
        streak_ref = db.collection('UserStreaks').document(user_id)
        streak_doc = streak_ref.get()

        if streak_doc.exists:
            data = streak_doc.to_dict()
            last_date = datetime.strptime(data.get('last_date', '2000-01-01'), '%Y-%m-%d').date()
            current_date = datetime.now().date()
            current_streak = data.get('streak', 0)

            # Bereken de dagenverschil
            days_difference = (current_date - last_date).days
            if days_difference > 1:
                current_streak = 0  # Reset streak
            elif days_difference == 1:
                current_streak += 1

            # Update de streak in Firestore
            streak_ref.update({
                'streak': current_streak,
                'last_date': current_date.strftime('%Y-%m-%d')
            })

            # Bereken de totale dagen sinds de eerste streak
            total_days = (current_date - datetime.strptime(data.get('first_date', '2000-01-01'), '%Y-%m-%d').date()).days

            return current_streak, total_days
        else:
            current_date = datetime.now().date()
            streak_ref.set({
                'streak': 0,
                'last_date': current_date.strftime('%Y-%m-%d'),
                'first_date': current_date.strftime('%Y-%m-%d')
            })

            return 0, 0  # Eerste keer voor de gebruiker
    except Exception as e:
        print(f"Error updating streak: {e}")
        return 0, 0

# Functie om de streak van een gebruiker op te halen
def get_streak(user_id):
    try:
        # Haal de streakgegevens op van de gebruiker
        streak_ref = db.collection('UserStreaks').document(user_id)
        streak_doc = streak_ref.get()

        if streak_doc.exists:
            data = streak_doc.to_dict()
            current_streak = data.get('streak', 0)
            print(f"Current streak for {user_id}: {current_streak}")
            return current_streak
        else:
            print(f"No streak data found for user {user_id}.")
            return 0
    except Exception as e:
        print(f"Error getting streak: {e}")
        return 0

from datetime import timedelta
from firebase_admin import storage

from datetime import timedelta
from firebase_admin import storage

def get_videos():
    try:
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix='videos/')  # Adjust prefix if needed
        videos = []

        seen_files = set()  # Track already processed video names

        for blob in blobs:
            # Exclude placeholder folders and ensure no duplicates
            if not blob.name.endswith('/') and blob.name not in seen_files:
                seen_files.add(blob.name)  # Add the file name to the seen set

                # Generate a signed URL valid for 24 hours
                url = blob.generate_signed_url(
                    expiration=timedelta(seconds=86400),  # Valid for 24 hours
                    method='GET'
                )
                videos.append(url)
        print("------------------------------------------")
        print(videos)  # Debug: Print the generated URLs
        return videos  # Return the list of URLs
    except Exception as e:
        print("------------------------------------------")
        print(f"Error getting videos: {e}")
        print("------------------------------------------")
        return None  # Return None in case of an error




  