import firebase_admin
from firebase_admin import auth
from firebase_admin import firestore
from firebase_config import db

def register_user(email, password, firstname, lastname):
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password
        )
        
        # Store additional user data in Firestore
        db.collection('Users').document(user.uid).set({
            'email': email,
            'password': password,
            'firstname': firstname,
            'lastname': lastname,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        
        return {'success': True, 'user_id': user.uid}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def login_user(email, password):
    try:
        # Verify user credentials
        user = auth.get_user_by_email(email)
        user_doc = db.collection('Users').document(user.uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            if user_data.get('password') == password:
                return {'success': True, 'user_id': user.uid}
            return {'success': False, 'error': 'Invalid password'}
        return {'success': False, 'error': 'User not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)} 