from app.models import Users, SharedUsers
from app import db

def search_user(username):
    """
    Search for a user by username.
    """
    return Users.query.filter(Users.username.ilike(f"%{username}%")).all()

def share_data(current_user, target_user):
    """
    Share data with another user by adding an entry to the SharedUsers table.
    """
    existing_entry = SharedUsers.query.filter_by(username=current_user, shared_username=target_user).first()
    if not existing_entry:
        new_shared_user = SharedUsers(username=current_user, shared_username=target_user)
        db.session.add(new_shared_user)
        db.session.commit()
        return True
    return False

def get_shared_with_me(username):
    """
    Fetch all users who shared their data with the current user.
    """
    return SharedUsers.query.filter_by(shared_username=username).all()