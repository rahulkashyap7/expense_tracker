import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import uuid

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# Initialize database
db = SQLAlchemy(app)

# Define models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    expenses = db.relationship('Expense', backref='category', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    receipt_filename = db.Column(db.String(255))
    is_fixed = db.Column(db.Boolean, default=False)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_month_year_choices():
    expenses = Expense.query.order_by(Expense.date).all()
    incomes = Income.query.order_by(Income.date).all()
    
    dates = set()
    for expense in expenses:
        dates.add((expense.date.month, expense.date.year))
    for income in incomes:
        dates.add((income.date.month, income.date.year))
    
    # If no data, add current month/year
    if not dates:
        today = datetime.today()
        dates.add((today.month, today.year))
    
    # Sort by year, then month
    return sorted(list(dates), key=lambda x: (x[1], x[0]))

# Routes
@app.route('/')
def index():
    # Get recent expenses
    recent_expenses = Expense.query.order_by(Expense.date.desc()).limit(5).all()
    
    # Get recent incomes
    recent_incomes = Income.query.order_by(Income.date.desc()).limit(5).all()
    
    # Get total income, expenses, and remaining
    total_income = db.session.query(db.func.sum(Income.amount)).scalar() or 0
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    remaining = total_income - total_expenses
    
    # Get expenses by category for chart
    expenses_by_category = db.session.query(
        Category.name, db.func.sum(Expense.amount)
    ).join(Expense).group_by(Category.name).all()
    
    # Get monthly expenses and incomes for chart
    today = datetime.today()
    current_year = today.year
    
    monthly_data = []
    for month in range(1, 13):
        month_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
            db.extract('month', Expense.date) == month,
            db.extract('year', Expense.date) == current_year
        ).scalar() or 0
        
        month_incomes = db.session.query(db.func.sum(Income.amount)).filter(
            db.extract('month', Income.date) == month,
            db.extract('year', Income.date) == current_year
        ).scalar() or 0
        
        monthly_data.append({
            'month': month,
            'expenses': month_expenses,
            'incomes': month_incomes
        })
    
    return render_template(
        'index.html',
        recent_expenses=recent_expenses,
        recent_incomes=recent_incomes,
        total_income=total_income,
        total_expenses=total_expenses,
        remaining=remaining,
        expenses_by_category=expenses_by_category,
        monthly_data=monthly_data,
        today=datetime.today().strftime('%Y-%m-%d')
    )

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    categories = Category.query.order_by(Category.name).all()
    
    if request.method == 'POST':
        amount = float(request.form['amount'])
        description = request.form['description']
        date_str = request.form['date']
        category_id = int(request.form['category'])
        is_fixed = 'is_fixed' in request.form
        
        # Parse date
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Handle file upload
        receipt_filename = None
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                
                # Save file
                file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], unique_filename))
                receipt_filename = unique_filename
        
        # Create expense
        expense = Expense(
            amount=amount,
            description=description,
            date=date,
            category_id=category_id,
            receipt_filename=receipt_filename,
            is_fixed=is_fixed
        )
        
        db.session.add(expense)
        db.session.commit()
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_expense.html', categories=categories, today=datetime.today().strftime('%Y-%m-%d'))

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        description = request.form['description']
        date_str = request.form['date']
        
        # Parse date
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Create income
        income = Income(
            amount=amount,
            description=description,
            date=date
        )
        
        db.session.add(income)
        db.session.commit()
        
        flash('Income added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_income.html', today=datetime.today().strftime('%Y-%m-%d'))

@app.route('/monthly_report', methods=['GET', 'POST'])
def monthly_report():
    month_year_choices = get_month_year_choices()
    
    # Default to current month/year
    today = datetime.today()
    selected_month = request.args.get('month', today.month, type=int)
    selected_year = request.args.get('year', today.year, type=int)
    
    # Get expenses for selected month/year
    expenses = Expense.query.filter(
        db.extract('month', Expense.date) == selected_month,
        db.extract('year', Expense.date) == selected_year
    ).order_by(Expense.date.desc()).all()
    
    # Get incomes for selected month/year
    incomes = Income.query.filter(
        db.extract('month', Income.date) == selected_month,
        db.extract('year', Income.date) == selected_year
    ).order_by(Income.date.desc()).all()
    
    # Get totals
    total_income = sum(income.amount for income in incomes)
    total_expenses = sum(expense.amount for expense in expenses)
    remaining = total_income - total_expenses
    
    # Get expenses by category for chart
    expenses_by_category = db.session.query(
        Category.name, db.func.sum(Expense.amount)
    ).join(Expense).filter(
        db.extract('month', Expense.date) == selected_month,
        db.extract('year', Expense.date) == selected_year
    ).group_by(Category.name).all()
    
    return render_template(
        'monthly_report.html',
        expenses=expenses,
        incomes=incomes,
        total_income=total_income,
        total_expenses=total_expenses,
        remaining=remaining,
        expenses_by_category=expenses_by_category,
        month_year_choices=month_year_choices,
        selected_month=selected_month,
        selected_year=selected_year,
        month_name=datetime(2000, selected_month, 1).strftime('%B')
    )

@app.route('/manage_categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        name = request.form['name']
        
        # Check if category already exists
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category:
            flash('Category already exists!', 'danger')
        else:
            category = Category(name=name)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
        
        return redirect(url_for('manage_categories'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('manage_categories.html', categories=categories)

@app.route('/delete_category/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Check if category has expenses
    if category.expenses:
        flash('Cannot delete category with expenses!', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    
    return redirect(url_for('manage_categories'))

@app.route('/delete_expense/<int:id>', methods=['POST'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    
    # Delete receipt file if exists
    if expense.receipt_filename:
        try:
            os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], expense.receipt_filename))
        except:
            pass
    
    db.session.delete(expense)
    db.session.commit()
    
    flash('Expense deleted successfully!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/delete_income/<int:id>', methods=['POST'])
def delete_income(id):
    income = Income.query.get_or_404(id)
    
    db.session.delete(income)
    db.session.commit()
    
    flash('Income deleted successfully!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/view_receipt/<filename>')
def view_receipt(filename):
    return render_template('view_receipt.html', filename=filename)

# Initialize database with default data
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add default categories if they don't exist
        default_categories = [
            'Food', 'Transportation', 'Housing', 'Utilities', 
            'Entertainment', 'Shopping', 'Health', 'Education',
            'EMI', 'SIP', 'Travel', 'Miscellaneous'
        ]
        
        for category_name in default_categories:
            if not Category.query.filter_by(name=category_name).first():
                category = Category(name=category_name)
                db.session.add(category)
        
        # Add default income (salary)
        if not Income.query.first():
            income = Income(
                amount=20000,
                description='Salary',
                date=datetime.today().date()
            )
            db.session.add(income)
        
        # Add fixed expenses
        if not Expense.query.filter_by(is_fixed=True).first():
            # Get category IDs
            emi_category = Category.query.filter_by(name='EMI').first()
            education_category = Category.query.filter_by(name='Education').first()
            sip_category = Category.query.filter_by(name='SIP').first()
            travel_category = Category.query.filter_by(name='Travel').first()
            
            # Add laptop EMI
            if emi_category:
                expense = Expense(
                    amount=5060,
                    description='Laptop EMI',
                    date=datetime.today().date(),
                    category_id=emi_category.id,
                    is_fixed=True
                )
                db.session.add(expense)
            
            # Add education loan
            if education_category:
                expense = Expense(
                    amount=5724,
                    description='Education Loan',
                    date=datetime.today().date(),
                    category_id=education_category.id,
                    is_fixed=True
                )
                db.session.add(expense)
            
            # Add SIP
            if sip_category:
                expense = Expense(
                    amount=1000,
                    description='Monthly SIP',
                    date=datetime.today().date(),
                    category_id=sip_category.id,
                    is_fixed=True
                )
                db.session.add(expense)
            
            # Add bus pass
            if travel_category:
                expense = Expense(
                    amount=1000,
                    description='Monthly Bus Pass',
                    date=datetime.today().date(),
                    category_id=travel_category.id,
                    is_fixed=True
                )
                db.session.add(expense)
        
        db.session.commit()

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Run app
    app.run(host='0.0.0.0', port=8080, debug=True)