from app.models import Users, SharedUsers
from app import db
from flask import flash, jsonify

def share_data_handler(username, request):
    """
    Handle sharing and deleting shared data entries.
    """
    if request.method == 'POST':
        if 'target_user' in request.form:
            # Handle sharing data with another user
            target_user = request.form.get('target_user')
            if target_user:
                # Check if the target user exists in the Users table
                user_exists = Users.query.filter_by(username=target_user).first()
                if user_exists:
                    # Check if the sharing entry already exists
                    existing_entry = SharedUsers.query.filter_by(username=username, shared_username=target_user).first()
                    if not existing_entry:
                        # Add the tuple (username, target_user) to the SharedUsers table
                        new_shared_user = SharedUsers(username=username, shared_username=target_user)
                        db.session.add(new_shared_user)
                        db.session.commit()
                        flash(f'Data shared with {target_user} successfully.', 'success')
                    else:
                        flash(f'You have already shared your data with {target_user}.', 'info')
                else:
                    flash(f'User {target_user} does not exist.', 'danger')
        elif 'delete_user' in request.form:
            # Handle deleting a shared user
            target_user = request.form.get('delete_user')
            print(f"Deleting shared user: {target_user}")
            if target_user:
                # Find the shared user entry
                shared_user_entry = SharedUsers.query.filter_by(username=username, shared_username=target_user).first()
                if shared_user_entry:
                    db.session.delete(shared_user_entry)
                    db.session.commit()
                    flash(f'Shared data with {target_user} has been removed.', 'success')
                else:
                    flash(f'No shared data found with {target_user}.', 'danger')
            else:
                flash('Invalid user specified.', 'danger')

    # Fetch users who shared their data with the current user
    shared_with_me = SharedUsers.query.filter_by(shared_username=username).all()
    # Fetch users you have shared your data with
    shared_with = SharedUsers.query.filter_by(username=username).all()

    return shared_with_me, shared_with

def search_users(query):
    """
    Fetch users whose usernames match the query.
    """
    matching_users = Users.query.filter(Users.username.ilike(f"%{query}%")).all()
    return [user.username for user in matching_users]