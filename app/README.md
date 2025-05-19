# Expense Tracker

A comprehensive web application to track personal expenses, income, and manage your financial life.

## Features

- **Dashboard**: View financial summary, recent expenses, and income
- **Expense Management**: Add, view, and delete expenses with categories
- **Income Tracking**: Record and manage income sources
- **Receipt Upload**: Upload and view receipts/screenshots for expenses
- **Monthly Reports**: View detailed financial reports by month
- **Category Management**: Create and manage expense categories
- **Fixed Expenses**: Track recurring monthly expenses (EMIs, SIPs, etc.)
- **Data Visualization**: Charts for expense distribution and monthly comparisons

## Default Setup

The application comes pre-configured with:

- **Income**: Salary (₹20,000)
- **Fixed Expenses**:
  - Laptop EMI (₹5,060)
  - Education Loan (₹5,724)
  - Monthly SIP (₹1,000)
  - Monthly Bus Pass (₹1,000)
- **Default Categories**: Food, Transportation, Housing, Utilities, Entertainment, Shopping, Health, Education, EMI, SIP, Travel, Miscellaneous

## Installation

### Option 1: Quick Setup (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/expense-tracker.git
   cd expense-tracker
   ```

2. Run the setup script:
   ```
   ./setup.sh
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

### Option 2: Manual Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/expense-tracker.git
   cd expense-tracker
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create uploads directory:
   ```
   mkdir -p static/uploads
   ```

5. Initialize the database:
   ```
   python -c "from app import init_db; init_db()"
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

## Usage

1. **Add Expenses**: Click "Add Expense" in the navigation bar, fill in the details, and optionally upload a receipt
2. **Add Income**: Click "Add Income" in the navigation bar and enter the income details
3. **View Reports**: Navigate to "Monthly Report" to see detailed financial data for specific months
4. **Manage Categories**: Add or delete expense categories from the "Categories" page
5. **View Receipts**: Click on the receipt icon next to an expense to view the uploaded receipt/screenshot

## Technologies Used

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Data Visualization**: Chart.js

## Deployment

### GitHub Repository Setup

1. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Enter a repository name (e.g., "expense-tracker")
   - Choose public or private visibility
   - Click "Create repository"

2. Connect your local repository to GitHub:
   ```
   git remote add origin https://github.com/yourusername/expense-tracker.git
   git push -u origin main
   ```

### Heroku Deployment

1. Create a Heroku account if you don't have one: https://signup.heroku.com/

2. Install the Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

3. Login to Heroku:
   ```
   heroku login
   ```

4. Create a new Heroku app:
   ```
   heroku create your-expense-tracker
   ```

5. Push to Heroku:
   ```
   git push heroku main
   ```

6. Open your app:
   ```
   heroku open
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.