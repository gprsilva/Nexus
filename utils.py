import os
import secrets
from PIL import Image
from flask import current_app
from models import Notification, db

def save_picture(form_picture, folder, size=None):
    """Save uploaded picture to the uploads folder"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    # Create folder if it doesn't exist
    folder_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(folder_path, exist_ok=True)
    
    picture_path = os.path.join(folder_path, picture_fn)
    
    if size and f_ext.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
        # Resize image if size is specified and it's an image
        img = Image.open(form_picture)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        img.save(picture_path)
    else:
        # Save original file
        form_picture.save(picture_path)
    
    return f"{folder}/{picture_fn}"

def create_notification(user, notification_type, message, related_user=None, project=None):
    """Create a new notification for a user"""
    notification = Notification()
    notification.user_id = user.id
    notification.type = notification_type
    notification.message = message
    if related_user:
        notification.related_user_id = related_user.id
    if project:
        notification.project_id = project.id
    db.session.add(notification)
    db.session.commit()

def get_file_url(filename):
    """Get URL for uploaded file"""
    if filename:
        return f"/uploads/{filename}"
    return None
