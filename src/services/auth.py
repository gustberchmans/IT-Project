import bcrypt
from firebase_admin import auth
from firebase_admin import firestore
from services.firebase import db

def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(password, hashed_password):
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def register_test_user(email, password, firstname, lastname):
    try:
        # Store the plain password directly
        user = auth.create_user(
            email=email,
            password=password  # Use the plain password for Firebase auth
        )
        
        # Store the plain password in Firestore
        db.collection('Users').document(user.uid).set({
            'email': email,
            'password': password,  # Store as plain string
            'firstname': firstname,
            'lastname': lastname,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        
        return {'success': True, 'user_id': user.uid}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def register_user(email, password, firstname, lastname):
    try:
        # Hash the password before storing it
        hashed_password = hash_password(password)
        
        user = auth.create_user(
            email=email,
            password=password  # You can still use the plain password for Firebase auth
        )
        
        # Store the hashed password in Firestore
        db.collection('Users').document(user.uid).set({
            'email': email,
            'password': hashed_password.decode('utf-8'),  # Store as string
            'firstname': firstname,
            'lastname': lastname,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        
        return {'success': True, 'user_id': user.uid}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        user_doc = db.collection('Users').document(user.uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            hashed_password = user_data.get('password').encode('utf-8')  # Get the stored hashed password
            
            if check_password(password, hashed_password):
                return {'success': True, 'user_id': user.uid}
            return {'success': False, 'error': 'Invalid password'}
        return {'success': False, 'error': 'User not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}



def login_test_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        user_doc = db.collection('Users').document(user.uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            stored_password = user_data.get('password')  # Get the stored password directly
            
            if password == stored_password:  # Direct comparison without hashing
                return {'success': True, 'user_id': user.uid}
            return {'success': False, 'error': 'Invalid password'}
        return {'success': False, 'error': 'User not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    