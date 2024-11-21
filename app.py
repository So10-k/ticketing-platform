from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='open')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report_problem', methods=['POST'])
def report_problem():
    if 'user_id' not in session:
        flash('Please log in to report a problem.', 'danger')
        return redirect(url_for('login'))
    title = request.form['title']
    description = request.form['description']
    new_ticket = Ticket(title=title, description=description, created_by=session['user_id'])
    db.session.add(new_ticket)
    db.session.commit()
    flash('Problem reported successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username already exists.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Please check your credentials and try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/create_ticket', methods=['GET', 'POST'])
def create_ticket():
    if 'user_id' not in session:
        flash('Please log in to create a ticket.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_ticket = Ticket(title=title, description=description, created_by=session['user_id'])
        db.session.add(new_ticket)
        db.session.commit()
        flash('Ticket created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create_ticket.html')

@app.route('/tickets')
def view_tickets():
    if 'user_id' not in session:
        flash('Please log in to view tickets.', 'danger')
        return redirect(url_for('login'))
    if session.get('user_role') == 'it_support':
        tickets = Ticket.query.all()
    else:
        tickets = Ticket.query.filter_by(created_by=session['user_id']).all()
    return render_template('tickets.html', tickets=tickets)

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    tickets = Ticket.query.all()
    users = User.query.all()
    return render_template('admin.html', tickets=tickets, users=users)

@app.route('/assign_ticket/<int:ticket_id>', methods=['POST'])
def assign_ticket(ticket_id):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    user_id = request.form['user_id']
    ticket = Ticket.query.get(ticket_id)
    ticket.assigned_to = user_id
    ticket.status = 'assigned'
    db.session.commit()
    flash('Ticket assigned successfully!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/update_ticket/<int:ticket_id>', methods=['POST'])
def update_ticket(ticket_id):
    if 'user_id' not in session or session.get('user_role') != 'it_support':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    status = request.form['status']
    ticket = Ticket.query.get(ticket_id)
    ticket.status = status
    db.session.commit()
    flash('Ticket status updated successfully!', 'success')
    return redirect(url_for('view_tickets'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create a default admin user
        default_username = 'admin'
        default_password = 'password'
        if not User.query.filter_by(username=default_username).first():
            hashed_password = generate_password_hash(default_password, method='sha256')
            new_user = User(username=default_username, password=hashed_password, role='admin')
            db.session.add(new_user)
            db.session.commit()
    app.run(debug=True)