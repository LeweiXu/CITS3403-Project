from app.models import Users, SharedUsers
from app import db
from flask import flash, render_template, jsonify, redirect, url_for
from app.helpers.entries_functions import get_entries
from app.helpers.activities_functions import get_activities
from app.helpers.analysis_functions import get_analysis_page
from app.forms import ShareWithUserForm, DeleteSharedUserForm, ViewSharedDataForm

def share_data_handler(username):
    # Fetch users who shared their data with the current user
    shared_with_me = SharedUsers.query.filter_by(shared_username=username).all()
    # Fetch users you have shared your data with
    shared_with = SharedUsers.query.filter_by(username=username).all()

    delete_shared_user_forms = {user.shared_username: DeleteSharedUserForm(target_user=user.shared_username) for user in shared_with}
    view_shared_data_forms = {
        (user.username, dtype): ViewSharedDataForm(
            target_user=user.username,
            data_type=dtype
        )
        for user in shared_with_me
        for dtype in ['analysis', 'activities', 'history']
    }
    share_with_user_form = ShareWithUserForm()
    
    return render_template('sharedata.html', 
                            shared_with_me=shared_with_me, 
                            shared_with=shared_with,
                            delete_shared_user_forms=delete_shared_user_forms,
                            share_with_user_form=share_with_user_form,
                            view_shared_data_forms=view_shared_data_forms
    )

def search_users(request):
    """
    Fetch users whose usernames match the query.
    """
    query = request.args.get('query', '')
    matching_users = Users.query.filter(Users.username.ilike(f"%{query}%")).all()
    if matching_users:
        return jsonify([user.username for user in matching_users])
    return jsonify([])

def view_shared_data_handler(username, request, form):
    target_user = form.target_user.data
    data_type = form.data_type.data
    # Check if the target_user has shared their data with the current user
    shared_entry = SharedUsers.query.filter_by(username=target_user, shared_username=username).first()
    if not shared_entry:
        flash('You do not have permission to view this user’s data.', 'danger')
        return redirect(url_for('main.sharedata'))

    if data_type == 'analysis':
        result = get_analysis_page(target_user)
    if data_type == 'activities':
        result = get_activities(target_user, request)
    elif data_type == 'history':
        result = get_entries(target_user, request)

    return result

def delete_shared_user_handler(username, form):
    target_user = form.target_user.data
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
    return redirect(url_for('main.sharedata'))

def share_with_user_handler(username, form):
    target_user = form.target_user.data
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
    return redirect(url_for('main.sharedata'))