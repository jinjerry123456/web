from flask import Blueprint, render_template, flash, redirect, url_for
from flask import request, abort, jsonify, current_app
from flask_paginate import Pagination, get_page_args
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Course, Tag, Comment
# from app.models import favorites
from app.forms import LoginForm, RegistrationForm, CourseForm, EditUserForm
from app.forms import CreateCourseForm, CommentForm, ChangePasswordForm
from functools import wraps
from .kmp import kmp_search
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)


# log route
@main.route('/some_route')
def some_route():
    current_app.logger.info(f'{current_user.username} accessed some_route')
    current_app.logger.info('This is an informational log message.')
    current_app.logger.error('This is an error log message.')
    current_app.logger.warning('This is a warning log message.')
    return 'Some route'


# function to check if the user is a manager
def role_required(*required_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_app.logger.info(
                f'Checking role for user {current_user.username}')
            if not current_user.is_authenticated:
                current_app.logger.warning(
                    f'User {current_user.username} is not authenticated')
                abort(403)
            if current_user.role not in required_roles:
                current_app.logger.warning(
                    f'User {current_user.username} does not have '
                    f'required roles: {required_roles}')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# the home page


@main.route('/')
def index():
    current_app.logger.info('Entering index')
    # the search query
    query = request.args.get('q', '')
    courses = Course.query.order_by(Course.created_at.desc()).limit(6).all()
    # if there is a search query
    if query:
        # search the courses
        matching_courses = []
        for course in courses:
            # use the KMP search algorithm
            if (kmp_search(course.title.lower(), query.lower()) or
                    kmp_search(course.description.lower(), query.lower())):
                matching_courses.append(course)
        return render_template('index.html', courses=matching_courses,
                               query=query)

    else:
        # get the latest 6 courses
        courses = Course.query.order_by(
            Course.created_at.desc()).limit(6).all()
    current_app.logger.info('Exiting index')
    return render_template('index.html', courses=courses, query=query)

# log page


@main.route('/logs')
@login_required
@role_required('manager')
def view_logs():
    # current_app.logger.info('Entering view_logs')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    start_line = (page - 1) * per_page

    try:
        with open('app_logs.txt', 'r') as file:
            lines = file.readlines()
        if start_line >= len(lines):
            logs = "No more logs available."
        else:
            logs = ''.join(lines[start_line:start_line + per_page])

        total_logs = len(lines)
        total_pages = (total_logs // per_page) + \
            (1 if total_logs % per_page > 0 else 0)

    except FileNotFoundError:
        logs = "No log file found."
        total_pages = 0

    return render_template('log.html', logs=logs, page=page,
                           total_pages=total_pages)


# login and register page
@main.route('/login', methods=['GET', 'POST'])
def login_register():
    current_app.logger.info('Entering login_register')
    if current_user.is_authenticated:
        current_app.logger.info(
            'User already authenticated, redirecting to index')
        return redirect(url_for('main.index'))

    login_form = LoginForm()
    register_form = RegistrationForm()

    if login_form.validate_on_submit() and 'login' in request.form:
        user = User.query.filter_by(username=login_form.username.data).first()
        # check if the user exists and the password is correct
        if user and user.check_password(login_form.password.data):
            login_user(user)
            current_app.logger.info(
                f'User {user.username} logged in successfully.')
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            current_app.logger.info('Exiting login_register')
            return redirect(next_page or url_for('main.index'))
        else:
            current_app.logger.warning(
                f'Failed login for username: {login_form.username.data}.')
            flash('Invalid username or password', 'danger')

    if register_form.validate_on_submit() and 'register' in request.form:
        # check if the username already exists
        user = User.query.filter_by(
            username=register_form.username.data).first()
        email = User.query.filter_by(email=register_form.email.data).first()
        if user:
            flash('Username already exists', 'danger')
        elif email:
            flash('Email already exists', 'danger')
        else:
            user = User(username=register_form.username.data,
                        email=register_form.email.data,
                        role=register_form.role.data)
            user.set_password(register_form.password.data)
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f'New user {user.username} registered.')
            flash('Registration successful! Please log in.', 'success')
            current_app.logger.info('Exiting login_register')
            return redirect(url_for('main.login_register'))
    else:
        if 'register' in request.form:
            flash('Registration failed. Please check errors.', 'danger')

    current_app.logger.info('Exiting login_register')
    return render_template('login.html', login_form=login_form,
                           register_form=register_form)


# change password
@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash,
                                   form.old_password.data):
            flash('Old password is incorrect', 'danger')
        else:
            current_user.password_hash = generate_password_hash(
                form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('main.index'))
    return render_template('change_password.html', form=form)


# the logout function
@main.route('/logout')
@login_required
def logout():
    current_app.logger.info(f'User {current_user.username} logged out.')
    logout_user()
    return redirect(url_for('main.index'))


# the course page
@main.route('/courses')
def courses():
    current_app.logger.info('Entering courses')
    # get the selected tags from the query string
    tag_ids = request.args.getlist('tag')
    page = request.args.get('page', 1, type=int)

    # if tags are selected, filter courses by tags
    if tag_ids:
        tag_ids = [int(tag_id) for tag_id in tag_ids]
        # use 'any' method to filter courses that have any of the selected tags
        courses = Course.query.filter(Course.tags.any(
            Tag.id.in_(tag_ids))).paginate(page=page, per_page=9)
    else:
        courses = Course.query.paginate(page=page, per_page=9)

    tags = Tag.query.all()
    current_app.logger.info('Exiting courses')
    return render_template('courses.html',
                           courses=courses,
                           tags=tags,
                           selected_tags=tag_ids if tag_ids else [])


# the course detail page
@main.route('/course/<int:course_id>', methods=['GET', 'POST'])
def course_detail(course_id):
    current_app.logger.info(
        f'Entering course_detail for course_id: {course_id}')
    course = Course.query.get_or_404(course_id)
    form = CommentForm()
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(course_id=course_id).paginate(
        page=page, per_page=5, error_out=False)

    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(content=form.content.data,
                              user_id=current_user.id, course_id=course.id)
            db.session.add(comment)
            db.session.commit()
            flash('Your comment has been added.', 'success')
        else:
            flash('You need to be logged in to comment.', 'danger')
        current_app.logger.info('Exiting course_detail')
        return redirect(url_for('main.course_detail', course_id=course.id))
    current_app.logger.info('Exiting course_detail')
    return render_template('course_detail.html', course=course, form=form,
                           comments=comments)

# add comment


@main.route('/course/<int:course_id>/add_comment', methods=['POST'])
@login_required
def add_comment(course_id):
    current_app.logger.info(f'Entering add_comment for course_id: {course_id}')
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data,
                          user_id=current_user.id, course_id=course_id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added.', 'success')
    else:
        flash('Failed to add comment.', 'danger')
    current_app.logger.info('Exiting add_comment')
    return redirect(url_for('main.course_detail', course_id=course_id))

# my courses page


@main.route('/my-courses')
@login_required
def my_courses():
    current_app.logger.info('Entering my_courses')
    page = request.args.get('page', 1, type=int)
    courses = current_user.favorited_courses.paginate(page=page, per_page=6)
    current_app.logger.info('Exiting my_courses')
    return render_template('my_courses.html', courses=courses)

# favorite the course


@main.route('/course/<int:course_id>/add_favorite', methods=['POST'])
@login_required
def add_favorite(course_id):
    current_app.logger.info(
        f'Entering add_favorite for course_id: {course_id}')
    course = Course.query.get_or_404(course_id)
    if course not in current_user.favorited_courses:
        current_user.favorited_courses.append(course)
        db.session.commit()
        flash('Course has been added to your favorites!', 'success')
    else:
        flash('This course is already in your favorites!', 'info')
    current_app.logger.info('Exiting add_favorite')
    return redirect(url_for('main.course_detail', course_id=course.id))

# remove the course from favorites


@main.route('/course/<int:course_id>/remove_favorite', methods=['POST'])
@login_required
def remove_favorite(course_id):
    current_app.logger.info(
        f'Entering remove_favorite for course_id: {course_id}')
    course = Course.query.get_or_404(course_id)
    if course in current_user.favorited_courses:
        current_user.favorited_courses.remove(course)
        db.session.commit()
        flash('Course has been removed from your favorites.', 'success')
    else:
        flash('This course is not in your favorites.', 'info')
    current_app.logger.info('Exiting remove_favorite')
    return redirect(url_for('main.course_detail', course_id=course.id))


# like the course
@main.route('/course/<int:course_id>/toggle_like', methods=['POST'])
@login_required
def toggle_like(course_id):
    current_app.logger.info(f'Entering toggle_like for course_id: {course_id}')
    course = Course.query.get_or_404(course_id)
    if current_user in course.liked_by:
        course.liked_by.remove(current_user)
        course.likes_count -= 1
        liked = False
    else:
        course.liked_by.append(current_user)
        course.likes_count += 1
        liked = True
    db.session.commit()
    current_app.logger.info('Exiting toggle_like')
    return jsonify({
        'success': True,
        'likes_count': course.likes_count,
        'liked': liked,
        'new_url': url_for('main.toggle_like', course_id=course_id)
    })


# manager page-------------------------------------
# manage the user
@main.route('/user_record')
@role_required('manager')
def user_record():
    current_app.logger.info('Entering user_record')
    # setting the pagination
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')
    per_page = 10
    total = User.query.count()
    users = User.query.offset(offset).limit(per_page).all()
    pagination = Pagination(page=page, total=total,
                            per_page=per_page, css_framework='bootstrap4')
    current_app.logger.info('Exiting user_record')
    return render_template('user_record.html', users=users,
                           pagination=pagination)

# delete the user


@main.route('/delete_user/<int:user_id>', methods=['POST'])
@role_required('manager')
def delete_user(user_id):
    current_app.logger.info(f'Entering delete_user for user_id: {user_id}')
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted successfully.', 'success')
    current_app.logger.info('Exiting delete_user')
    return redirect(url_for('main.user_record'))

# edit the user


@main.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@role_required('manager')
def edit_user(user_id):
    current_app.logger.info(f'Entering edit_user for user_id: {user_id}')
    # get the user
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    if form.validate_on_submit():
        # Check if the username or email is already taken by another user
        existing_user = User.query.filter(
            (User.username == form.username.data) | (
                User.email == form.email.data)).filter(
                    User.id != user_id).first()
        if existing_user:
            flash(
                'Username or email already exists.', 'danger')
            current_app.logger.info('Username or email already exists.')
        else:
            user.username = form.username.data
            user.email = form.email.data
            user.role = form.role.data
            db.session.commit()
            flash('User information updated successfully.', 'success')
            current_app.logger.info('Exiting edit_user')
            return redirect(url_for('main.user_record'))

    # pre-populate the form with the user data
    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role
    current_app.logger.info('Exiting edit_user')
    return render_template('edit_user.html', form=form, user=user)

# create the course


@main.route('/create_course', methods=['GET', 'POST'])
@login_required
@role_required('manager', 'teacher')
def create_course():
    current_app.logger.info('Entering create_course')
    form = CreateCourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            video_url=form.video_url.data,
            image_url=form.image_url.data,
        )
        for tag in form.tag.data:
            course.tags.append(tag)

        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        current_app.logger.info('Exiting create_course')
        return redirect(url_for('main.create_course'))
        # when submit the form, the page will be redirected to the course_list
    elif request.method == 'POST':
        flash('Error creating course. Please check the errors.', 'danger')

    current_app.logger.info('Exiting create_course')
    return render_template('create_course.html', form=form)


# course list
@main.route('/course_record', methods=['GET'])
@role_required('manager')
def course_record():
    current_app.logger.info('Entering course_record')
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Course.query.paginate(
        page=page, per_page=per_page, error_out=False)
    courses = pagination.items
    current_app.logger.info('Exiting course_record')
    return render_template('course_record.html', courses=courses,
                           pagination=pagination)

# edit the course


@main.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
@role_required('manager')
def edit_course(course_id):
    current_app.logger.info(f'Entering edit_course for course_id: {course_id}')
    course = Course.query.get_or_404(course_id)
    # fill the form with the course data
    form = CourseForm(obj=course)
    if request.method == 'GET':
        form.tag.data = course.tags

    if form.validate_on_submit():
        # update the course data
        course.title = form.title.data
        course.description = form.description.data
        course.video_url = form.video_url.data
        course.image_url = form.image_url.data
        course.tags = []
        for tag in form.tag.data:
            course.tags.append(tag)
        db.session.commit()
        flash('Course updated successfully!', 'success')
        current_app.logger.info('Exiting edit_course')
        return redirect(url_for('main.course_record'))
    current_app.logger.info('Exiting edit_course')
    return render_template('edit_course.html', form=form, course=course)

# comment page


@main.route('/comments/<int:course_id>', methods=['GET'])
def course_comments(course_id):
    current_app.logger.info(
        f'Entering course_comments for course_id: {course_id}')
    # get the course
    course = Course.query.get_or_404(course_id)
    # get the comments
    comments = Comment.query.filter_by(course_id=course.id).all()
    current_app.logger.info('Exiting course_comments')
    return render_template('course_comments.html', course=course,
                           comments=comments)


# delete the comment
@main.route('/delete_comment/<int:comment_id>', methods=['POST'])
@role_required('manager')
def delete_comment(comment_id):
    current_app.logger.info(
        f'Entering delete_comment for comment_id: {comment_id}')
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully!', 'success')
    current_app.logger.info('Exiting delete_comment')
    return redirect(url_for('main.course_comments',
                            course_id=comment.course_id))


# delete the course
@main.route('/delete_course/<int:course_id>', methods=['POST'])
@role_required('manager')
def delete_course(course_id):
    current_app.logger.info(
        f'Entering delete_course for course_id: {course_id}')
    course = Course.query.get_or_404(course_id)
    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting course: {str(e)}', 'danger')
    current_app.logger.info('Exiting delete_course')
    return redirect(url_for('main.course_record'))
