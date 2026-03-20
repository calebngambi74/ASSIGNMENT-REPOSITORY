from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from data_structures import StudentManager

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize the student manager
student_manager = StudentManager()

# Simple user credentials with profile data (in production, use a database with hashed passwords)
USERS = {
    'admin': {
        'password': 'admin123',
        'name': 'Admin User',
        'email': 'admin@studentms.com'
    },
    'user': {
        'password': 'user123',
        'name': 'Regular User',
        'email': 'user@studentms.com'
    }
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS and USERS[username]['password'] == password:
            session['username'] = username
            session['name'] = USERS[username]['name']
            session['email'] = USERS[username]['email']
            flash(f'Welcome back, {USERS[username]["name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('name', None)
    session.pop('email', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = session['username']
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            new_name = request.form['name']
            new_email = request.form['email']
            new_username = request.form['username']
            
            # Check if new username already exists (and it's not the current user)
            if new_username != username and new_username in USERS:
                flash('Username already exists!', 'error')
            else:
                # Update user data
                user_data = USERS[username]
                
                # If username changed, move data to new key
                if new_username != username:
                    USERS[new_username] = user_data
                    del USERS[username]
                    session['username'] = new_username
                
                # Update profile data
                USERS[new_username]['name'] = new_name
                USERS[new_username]['email'] = new_email
                session['name'] = new_name
                session['email'] = new_email
                
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('profile'))
        
        elif action == 'change_password':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            
            if USERS[username]['password'] != current_password:
                flash('Current password is incorrect!', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match!', 'error')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters long!', 'error')
            else:
                USERS[username]['password'] = new_password
                flash('Password changed successfully!', 'success')
                return redirect(url_for('profile'))
    
    user_data = {
        'username': username,
        'name': USERS[username]['name'],
        'email': USERS[username]['email']
    }
    
    return render_template('profile.html', user=user_data)

@app.route('/')
@login_required
def index():
    students = student_manager.get_all_students()
    queue_count = len(student_manager.get_registration_queue())
    return render_template('index.html', students=students, queue_count=queue_count)

@app.route('/students')
@login_required
def students():
    all_students = student_manager.get_all_students()
    return render_template('students.html', students=all_students)

@app.route('/student/<student_id>')
@login_required
def view_student(student_id):
    student = student_manager.search_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('students'))
    return render_template('view_student.html', student=student)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        program = request.form['program']
        year = request.form['year']
        
        if student_manager.add_student(student_id, name, program, year):
            flash('Student added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Student ID already exists!', 'error')
    
    return render_template('add_student.html')

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search_student():
    student = None
    if request.method == 'POST':
        student_id = request.form['student_id']
        student = student_manager.search_student(student_id)
        if not student:
            flash('Student not found!', 'error')
    
    return render_template('search_student.html', student=student)

@app.route('/update/<student_id>', methods=['GET', 'POST'])
@login_required
def update_student(student_id):
    if request.method == 'POST':
        name = request.form['name']
        program = request.form['program']
        year = request.form['year']
        
        if student_manager.update_student(student_id, name, program, year):
            flash('Student updated successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Student not found!', 'error')
    
    student = student_manager.search_student(student_id)
    return render_template('update_student.html', student=student)

@app.route('/delete/<student_id>')
@login_required
def delete_student(student_id):
    if student_manager.delete_student(student_id):
        flash('Student deleted successfully!', 'success')
    else:
        flash('Student not found!', 'error')
    return redirect(url_for('index'))

@app.route('/undo')
@login_required
def undo_delete():
    if student_manager.undo_delete():
        flash('Delete operation undone!', 'success')
    else:
        flash('No delete operation to undo!', 'error')
    return redirect(url_for('index'))

@app.route('/queue')
@login_required
def view_queue():
    queue_items = student_manager.get_registration_queue()
    return render_template('queue.html', queue_items=queue_items)

@app.route('/queue/add', methods=['POST'])
@login_required
def add_to_queue():
    student_id = request.form['student_id']
    student_manager.add_to_registration_queue(student_id)
    flash('Added to registration queue!', 'success')
    return redirect(url_for('view_queue'))

@app.route('/queue/process')
@login_required
def process_queue():
    processed = student_manager.process_registration_queue()
    if processed:
        flash(f'Processed registration for Student ID: {processed}', 'success')
    else:
        flash('Queue is empty!', 'error')
    return redirect(url_for('view_queue'))

if __name__ == '__main__':
    app.run(debug=True)
