import os
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, send_from_directory
from flask_login import login_user, current_user, logout_user, login_required
from urllib.parse import urlparse as url_parse
from app import app, db
from models import User, Project, Like, Comment, Notification
from forms import LoginForm, RegistrationForm, EditProfileForm, ProjectForm, CommentForm
from utils import save_picture, create_notification, get_file_url

# Serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    """Homepage - shows recent and popular projects"""
    page = request.args.get('page', 1, type=int)
    projects = Project.query.filter_by(is_published=True).order_by(Project.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)
    
    # Get popular projects (most liked in last 30 days)
    popular_projects = Project.query.filter_by(is_published=True).join(Like).group_by(Project.id).order_by(db.func.count(Like.id).desc()).limit(6).all()
    
    return render_template('index.html', projects=projects, popular_projects=popular_projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    projects = user.projects.filter_by(is_published=True).order_by(Project.created_at.desc()).paginate(
        page=page, per_page=9, error_out=False)
    
    return render_template('profile.html', user=user, projects=projects)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # Check if username is already taken by another user
        if form.username.data != current_user.username:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username already taken. Please choose a different one.', 'danger')
                return render_template('edit_profile.html', form=form)
        
        # Check if email is already taken by another user
        if form.email.data != current_user.email:
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Email already registered. Please choose a different one.', 'danger')
                return render_template('edit_profile.html', form=form)
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.website = form.website.data
        current_user.github_username = form.github_username.data
        current_user.linkedin_profile = form.linkedin_profile.data
        
        if form.profile_image.data:
            picture_file = save_picture(form.profile_image.data, 'profile_pics', (300, 300))
            current_user.profile_image = picture_file
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.bio.data = current_user.bio
        form.location.data = current_user.location
        form.website.data = current_user.website
        form.github_username.data = current_user.github_username
        form.linkedin_profile.data = current_user.linkedin_profile
    
    return render_template('edit_profile.html', form=form)

@app.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project()
        project.title = form.title.data
        project.description = form.description.data
        project.content = form.content.data
        project.category = form.category.data
        project.tags = form.tags.data
        project.github_link = form.github_link.data
        project.demo_link = form.demo_link.data
        project.is_published = form.is_published.data
        project.user_id = current_user.id
        
        if form.image.data:
            picture_file = save_picture(form.image.data, 'project_images', (800, 600))
            project.image = picture_file
        
        if form.video.data:
            video_file = save_picture(form.video.data, 'project_videos')
            project.video = video_file
        
        db.session.add(project)
        db.session.commit()
        
        status = "published" if project.is_published else "saved as draft"
        flash(f'Your project has been {status}!', 'success')
        return redirect(url_for('project_detail', id=project.id))
    
    return render_template('create_project.html', form=form, legend='New Project')

@app.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    
    # Check if user can view this project
    if not project.is_published and (not current_user.is_authenticated or project.author != current_user):
        abort(403)
    
    form = CommentForm()
    comments = project.comments.order_by(Comment.created_at.desc()).all()
    
    return render_template('project_detail.html', project=project, form=form, comments=comments)

@app.route('/project/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    
    if project.author != current_user:
        abort(403)
    
    form = ProjectForm()
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.content = form.content.data
        project.category = form.category.data
        project.tags = form.tags.data
        project.github_link = form.github_link.data
        project.demo_link = form.demo_link.data
        project.is_published = form.is_published.data
        
        if form.image.data:
            picture_file = save_picture(form.image.data, 'project_images', (800, 600))
            project.image = picture_file
        
        if form.video.data:
            video_file = save_picture(form.video.data, 'project_videos')
            project.video = video_file
        
        db.session.commit()
        flash('Your project has been updated!', 'success')
        return redirect(url_for('project_detail', id=project.id))
    
    elif request.method == 'GET':
        form.title.data = project.title
        form.description.data = project.description
        form.content.data = project.content
        form.category.data = project.category
        form.tags.data = project.tags
        form.github_link.data = project.github_link
        form.demo_link.data = project.demo_link
        form.is_published.data = project.is_published
    
    return render_template('edit_project.html', form=form, project=project, legend='Edit Project')

@app.route('/project/<int:id>/delete', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    
    if project.author != current_user:
        abort(403)
    
    db.session.delete(project)
    db.session.commit()
    flash('Your project has been deleted!', 'success')
    return redirect(url_for('profile', username=current_user.username))

@app.route('/like_project/<int:id>', methods=['POST'])
@login_required
def like_project(id):
    project = Project.query.get_or_404(id)
    
    if not project.is_published:
        abort(403)
    
    existing_like = Like.query.filter_by(user=current_user, project=project).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        liked = False
    else:
        # Like
        like = Like()
        like.user_id = current_user.id
        like.project_id = project.id
        db.session.add(like)
        liked = True
        
        # Create notification for project author
        if project.author != current_user:
            message = f"{current_user.username} liked your project '{project.title}'"
            create_notification(project.author, 'like', message, current_user, project)
    
    db.session.commit()
    
    return jsonify({
        'liked': liked,
        'like_count': project.get_like_count()
    })

@app.route('/add_comment/<int:id>', methods=['POST'])
@login_required
def add_comment(id):
    project = Project.query.get_or_404(id)
    
    if not project.is_published:
        abort(403)
    
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment()
        comment.content = form.content.data
        comment.user_id = current_user.id
        comment.project_id = project.id
        db.session.add(comment)
        
        # Create notification for project author
        if project.author != current_user:
            message = f"{current_user.username} commented on your project '{project.title}'"
            create_notification(project.author, 'comment', message, current_user, project)
        
        db.session.commit()
        flash('Your comment has been added!', 'success')
    
    return redirect(url_for('project_detail', id=id))

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.', 'warning')
        return redirect(url_for('index'))
    
    if user == current_user:
        flash('You cannot follow yourself!', 'warning')
        return redirect(url_for('profile', username=username))
    
    current_user.follow(user)
    db.session.commit()
    
    # Create notification
    message = f"{current_user.username} started following you"
    create_notification(user, 'follow', message, current_user)
    
    flash(f'You are now following {username}!', 'success')
    return redirect(url_for('profile', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.', 'warning')
        return redirect(url_for('index'))
    
    if user == current_user:
        flash('You cannot unfollow yourself!', 'warning')
        return redirect(url_for('profile', username=username))
    
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are no longer following {username}.', 'info')
    return redirect(url_for('profile', username=username))

@app.route('/feed')
@login_required
def feed():
    """Feed showing projects from followed users"""
    page = request.args.get('page', 1, type=int)
    
    # Get projects from followed users
    followed_users = current_user.followed.all()
    followed_ids = [user.id for user in followed_users] + [current_user.id]
    
    projects = Project.query.filter(
        Project.user_id.in_(followed_ids),
        Project.is_published == True
    ).order_by(Project.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('feed.html', projects=projects)

@app.route('/notifications')
@login_required
def notifications():
    """User notifications page"""
    page = request.args.get('page', 1, type=int)
    notifications = current_user.notifications.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Mark all notifications as read
    current_user.notifications.filter_by(read=False).update({'read': True})
    db.session.commit()
    
    return render_template('notifications.html', notifications=notifications)

@app.route('/following/<username>')
def following(username):
    """Show users that this user is following"""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    following_users = user.followed.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('following.html', user=user, following_users=following_users)

@app.route('/followers/<username>')
def followers(username):
    """Show users that follow this user"""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    followers_users = user.followers.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('followers.html', user=user, followers_users=followers_users)

@app.route('/search')
def search():
    """Search for projects and users"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        # Search projects
        projects = Project.query.filter(
            Project.is_published == True,
            db.or_(
                Project.title.contains(query),
                Project.description.contains(query),
                Project.tags.contains(query)
            )
        ).order_by(Project.created_at.desc()).paginate(
            page=page, per_page=12, error_out=False)
        
        # Search users
        users = User.query.filter(
            db.or_(
                User.username.contains(query),
                User.first_name.contains(query),
                User.last_name.contains(query)
            )
        ).limit(10).all()
    else:
        projects = None
        users = []
    
    return render_template('search.html', projects=projects, users=users, query=query)

# Error handlers
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
