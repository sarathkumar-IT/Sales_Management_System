# Sales Management System

A multi-branch Sales Management System built with MySQL, Python, and Streamlit. Features role-based login, sales entry, payment splits, and MySQL triggers that automatically maintain received and pending balances.

## Features
- Login and logout with Super Admin and Admin roles
- Admins see only their own branch; Super Admin sees all branches
- Sales entry with student, course and branch details
- Payment split tracking with automatic pending balance and open/close status
- Dashboard with filters and KPIs: revenue, received, pending and pending %
- 20 predefined SQL queries for Super Admin (basic, aggregation, join and financial tracking)

## Tech Stack
MySQL, Python 3.13, Streamlit, pandas, python-dotenv

## Database
Tables: `branches`, `customer_sales`, `users`, `payment_splits`

Run the SQL scripts in this order:
1. `Table Creation.sql`
2. `Rename Column.sql`
3. `Imported sample data.csv files
4. `Modified Triggers.sql`

## Setup
1. Install MySQL and create the `sales_management_system` database using the scripts above.
2. Copy `.env.example` to `.env` and fill in your MySQL details.
3. Install the packages:
```
   pip install -r requirements.txt
```
4. Run the app:
```
   python -m streamlit run Sales_Management_App.py
```

## Project Files
- `Sales_Management_App.py` - Streamlit application
- `.env.example` - template for database settings (never commit your real `.env`)
- `requirements.txt` - Python dependencies

## Author
Sarath
