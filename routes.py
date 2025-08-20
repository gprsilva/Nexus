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
        flash('Nome de usuário ou senha inválidos', 'danger')
    
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
        flash('Cadastro realizado com sucesso!', 'success')
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
                flash('Nome de usuário já está sendo usado. Escolha outro.', 'danger')
                return render_template('edit_profile.html', form=form)
        
        # Check if email is already taken by another user
        if form.email.data != current_user.email:
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Email já está cadastrado. Escolha outro.', 'danger')
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
        flash('Seu perfil foi atualizado!', 'success')
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
        
        # Handle file uploads
        if form.image.data:
            try:
                image_file = save_picture(form.image.data, 'projects', (800, 600))
                project.image = image_file
            except Exception as e:
                flash('Erro ao fazer upload da imagem', 'danger')
        
        if form.video.data:
            try:
                video_file = save_picture(form.video.data, 'videos')
                project.video = video_file
            except Exception as e:
                flash('Erro ao fazer upload do vídeo', 'danger')
        
        db.session.add(project)
        db.session.commit()
        flash('Projeto criado com sucesso!', 'success')
        return redirect(url_for('project_detail', id=project.id))
    
    return render_template('create_project.html', form=form)

@app.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    form = CommentForm()
    
    # Get comments
    comments = project.comments.order_by(Comment.created_at.desc()).all()
    
    # Check if current user liked this project
    user_liked = False
    if current_user.is_authenticated:
        user_liked = project.is_liked_by(current_user)
    
    return render_template('project_detail.html', project=project, form=form, 
                         comments=comments, user_liked=user_liked)

# Like/Unlike functionality
@app.route('/toggle_like/<int:project_id>', methods=['POST'])
@login_required
def toggle_like(project_id):
    project = Project.query.get_or_404(project_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, project_id=project_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        like = Like(user_id=current_user.id, project_id=project_id)
        db.session.add(like)
        liked = True
        # Create notification
        if project.user != current_user:
            create_notification(
                project.user, 'like', 
                f'{current_user.display_name} curtiu seu projeto "{project.title}"',
                related_user=current_user, project=project
            )
    
    db.session.commit()
    return jsonify({'liked': liked, 'like_count': project.get_like_count()})

# Comment functionality  
@app.route('/add_comment/<int:project_id>', methods=['POST'])
@login_required
def add_comment(project_id):
    project = Project.query.get_or_404(project_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            project_id=project_id
        )
        db.session.add(comment)
        
        # Create notification
        if project.user != current_user:
            create_notification(
                project.user, 'comment', 
                f'{current_user.display_name} comentou no seu projeto "{project.title}"',
                related_user=current_user, project=project
            )
        
        db.session.commit()
        flash('Comentário adicionado!', 'success')
    
    return redirect(url_for('project_detail', id=project_id))

# Follow/Unfollow functionality
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash('Você não pode seguir a si mesmo!', 'warning')
        return redirect(url_for('profile', username=username))
    
    current_user.follow(user)
    db.session.commit()
    
    # Create notification
    create_notification(
        user, 'follow',
        f'{current_user.display_name} começou a seguir você',
        related_user=current_user
    )
    
    flash(f'Agora você está seguindo {user.display_name}!', 'success')
    return redirect(url_for('profile', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user == current_user:
        flash('Você não pode deixar de seguir a si mesmo!', 'warning')
        return redirect(url_for('profile', username=username))
    
    current_user.unfollow(user)
    db.session.commit()
    flash(f'Você não está mais seguindo {user.display_name}.', 'info')
    return redirect(url_for('profile', username=username))

# Notifications
@app.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    notifications = current_user.notifications.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Mark all as read
    current_user.notifications.filter_by(read=False).update({Notification.read: True})
    db.session.commit()
    
    return render_template('notifications.html', notifications=notifications)

# Feed
@app.route('/feed')
@login_required  
def feed():
    page = request.args.get('page', 1, type=int)
    
    # Get projects from followed users
    followed_projects = Project.query.join(
        User.followed, (User.followed.c.followed_id == Project.user_id)
    ).filter(
        User.followed.c.follower_id == current_user.id,
        Project.is_published == True
    ).order_by(Project.created_at.desc())
    
    # Include current user's projects
    own_projects = current_user.projects.filter_by(is_published=True)
    
    # Combine and paginate
    all_projects = followed_projects.union(own_projects).order_by(Project.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('feed.html', projects=all_projects)

# Followers/Following pages
@app.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    followers = User.query.join(
        User.followed, (User.followed.c.follower_id == User.id)
    ).filter(User.followed.c.followed_id == user.id).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('followers.html', user=user, users=followers)

@app.route('/following/<username>')  
def following(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    following = User.query.join(
        User.followed, (User.followed.c.followed_id == User.id)
    ).filter(User.followed.c.follower_id == user.id).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('following.html', user=user, users=following)

# Project editing and deletion routes
@app.route('/project/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    
    if project.user != current_user:
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
            try:
                image_file = save_picture(form.image.data, 'projects', (800, 600))
                project.image = image_file
            except Exception as e:
                flash('Erro ao fazer upload da imagem', 'danger')
        
        if form.video.data:
            try:
                video_file = save_picture(form.video.data, 'videos')
                project.video = video_file
            except Exception as e:
                flash('Erro ao fazer upload do vídeo', 'danger')
        
        db.session.commit()
        flash('Projeto atualizado com sucesso!', 'success')
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
    
    return render_template('edit_project.html', form=form, project=project)

@app.route('/project/<int:id>/delete', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    
    if project.user != current_user:
        abort(403)
    
    db.session.delete(project)
    db.session.commit()
    flash('Projeto excluído com sucesso!', 'success')
    return redirect(url_for('profile', username=current_user.username))

# Configure upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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