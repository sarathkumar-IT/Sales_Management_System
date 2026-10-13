import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import mysql.connector
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load .env from the same folder as this file
load_dotenv(Path(__file__).parent / ".env")

# Page Configuration
st.set_page_config(
    page_title="Sales Management System", page_icon="📊", layout="wide"
)


# --- DATABASE CONNECTION & SETUP ---
def init_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

def ensure_payment_splits_table():
    conn = init_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_splits (
                payment_id INT AUTO_INCREMENT PRIMARY KEY,
                payment_date DATE,
                amount_paid DECIMAL(10,2),
                payment_method VARCHAR(50),
                sale_id INT
            )
        """)
        conn.commit()
    except Exception as e:
        st.error(f"Error creating payment_splits table: {e}")
    finally:
        cursor.close()
        conn.close()


# Run table check on startup
ensure_payment_splits_table()


def run_query(query, params=None, fetch=True):
    conn = init_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.branch_id = None

# New Sale Form State Initialization
if "ns_student_name" not in st.session_state:
    st.session_state.ns_student_name = ""
if "ns_mobile_number" not in st.session_state:
    st.session_state.ns_mobile_number = ""
if "ns_gross_sales" not in st.session_state:
    st.session_state.ns_gross_sales = 0.0
if "ns_received_amount" not in st.session_state:
    st.session_state.ns_received_amount = 0.0
if "ns_joining_date" not in st.session_state:
    st.session_state.ns_joining_date = datetime.today()

# Payment Split Form State Initialization
if "ps_collected_amount" not in st.session_state:
    st.session_state.ps_collected_amount = 0.0
if "ps_payment_date" not in st.session_state:
    st.session_state.ps_payment_date = datetime.today()

# --- HANDLE FORM RESETS BEFORE WIDGET INSTANTIATION ---
if st.session_state.get("reset_ns", False):
    st.session_state.ns_student_name = ""
    st.session_state.ns_mobile_number = ""
    st.session_state.ns_gross_sales = 0.0
    st.session_state.ns_received_amount = 0.0
    st.session_state.ns_joining_date = datetime.today()
    st.session_state.reset_ns = False

if st.session_state.get("reset_ps", False):
    st.session_state.ps_collected_amount = 0.0
    st.session_state.ps_payment_date = datetime.today()
    st.session_state.reset_ps = False


# --- CALLBACK FUNCTIONS ---
def clear_new_sale_fields():
    st.session_state.reset_ns = True


def clear_payment_split_fields():
    st.session_state.reset_ps = True


# --- LOGIN MODULE ---
def login_page():
    st.title("Sales Management System")
    st.subheader("Welcome to the Login Portal")
    st.info("Please login with your credentials to access the sales reports")

    with st.form("login_form"):
        username = st.text_input("Username", value="")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            users = run_query(query, (username, password))

            if users and len(users) > 0:
                user = users[0]
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]  # Expecting 'Super Admin' or 'Admin'[cite: 3]
                
                # --- BULLETPROOF BRANCH RESOLUTION ---
                b_id = user.get("branch_id")
                if pd.isna(b_id) or b_id is None:
                    uname_lower = user["username"].lower()
                    branch_res = run_query("SELECT branch_id, branch_name FROM branches")
                    if branch_res:
                        for b in branch_res:
                            if b["branch_name"].lower() in uname_lower:
                                b_id = b["branch_id"]
                                break
                
                st.session_state.branch_id = int(b_id) if not pd.isna(b_id) and b_id is not None else None
                # ------------------------------------

                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid Username or Password. Please try again.")


# --- MAIN DASHBOARD VIEW ---
def main_dashboard():
    # --- SIDEBAR NAVIGATION ---
    st.sidebar.title("Navigation")
    st.sidebar.caption("Go to")

    # Dynamic navigation: Hide Advanced SQL Engine from regular Admins
    nav_options = ["🔴 Dashboard & Reports", "➕ Data Entry Workspace"]
    if st.session_state.role == "Super Admin":
        nav_options.append("🔍 Advanced SQL Engine")

    page = st.sidebar.radio(label="", options=nav_options)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"👤 **User:** `{st.session_state.username}`")
    st.sidebar.markdown(f"🔑 **Role:** `{st.session_state.role}`")
    if st.session_state.branch_id:
        st.sidebar.markdown(f"🏢 **Branch ID:** `{st.session_state.branch_id}`")

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.branch_id = None
        st.rerun()

    # --- 1. DASHBOARD & REPORTS PAGE ---
    if page == "🔴 Dashboard & Reports":
        st.title("📈 Student Enrollment Dashboard")

        # STRICTLY RESTRICT BASE QUERY TO BRANCH IF USER IS AN ADMIN
        if st.session_state.role == "Admin" and st.session_state.branch_id:
            base_query = f"""
                SELECT 
                    cs.sale_id,
                    cs.branch_id,
                    b.branch_name,
                    cs.date,
                    cs.name,
                    cs.mobile_number,
                    cs.product_name,
                    cs.gross_sales,
                    cs.received_amount,
                    cs.pending_amount,
                    cs.status
                FROM customer_sales cs
                LEFT JOIN branches b ON cs.branch_id = b.branch_id
                WHERE cs.branch_id = {st.session_state.branch_id}
            """
        else:
            base_query = """
                SELECT 
                    cs.sale_id,
                    cs.branch_id,
                    b.branch_name,
                    cs.date,
                    cs.name,
                    cs.mobile_number,
                    cs.product_name,
                    cs.gross_sales,
                    cs.received_amount,
                    cs.pending_amount,
                    cs.status
                FROM customer_sales cs
                LEFT JOIN branches b ON cs.branch_id = b.branch_id
            """
        raw_data = run_query(base_query)

        if raw_data:
            df = pd.DataFrame(raw_data)
            df["date"] = pd.to_datetime(df["date"])

            st.subheader("🔍 Filter Controls")
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)

            if st.session_state.role == "Admin":
                assigned_branch_row = run_query("SELECT branch_name FROM branches WHERE branch_id = %s", (st.session_state.branch_id,))
                branch_name_display = assigned_branch_row[0]["branch_name"] if assigned_branch_row else "Assigned Branch"
                branch_options = [branch_name_display]
            else:
                branch_options = ["All"] + list(df["branch_name"].dropna().unique())

            product_options = ["All"] + list(df["product_name"].dropna().unique())

            with f_col1:
                if st.session_state.role == "Admin":
                    selected_branch = st.selectbox("Branch Name", options=branch_options, disabled=True)
                else:
                    selected_branch = st.selectbox("Branch Name", options=branch_options)
            with f_col2:
                selected_product = st.selectbox("Product Name", options=product_options)
            with f_col3:
                min_date = df["date"].min().date() if not df.empty else datetime(2024, 1, 1).date()
                start_date = st.date_input("Start Date", value=min_date)
            with f_col4:
                max_date = df["date"].max().date() if not df.empty else datetime(2024, 12, 30).date()
                end_date = st.date_input("End Date", value=max_date)

            st.markdown("---")

            filtered_df = df.copy()
            if st.session_state.role != "Admin" and selected_branch != "All":
                filtered_df = filtered_df[filtered_df["branch_name"] == selected_branch]
            if selected_product != "All":
                filtered_df = filtered_df[filtered_df["product_name"] == selected_product]
            filtered_df = filtered_df[
                (filtered_df["date"].dt.date >= start_date)
                & (filtered_df["date"].dt.date <= end_date)
            ]

            total_gross = filtered_df["gross_sales"].sum() if not filtered_df.empty else 0.0
            total_received = filtered_df["received_amount"].sum() if not filtered_df.empty else 0.0
            total_pending = filtered_df["pending_amount"].sum() if not filtered_df.empty else 0.0
            pending_pct = (total_pending / total_gross * 100) if total_gross > 0 else 0.0

            st.subheader("💵 Financial Summary")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric(label="Overall Revenue (Gross)", value=f"₹{total_gross:,.2f}")
            kpi2.metric(label="Total Received Amount", value=f"₹{total_received:,.2f}")
            kpi3.metric(label="Total Pending Amount", value=f"₹{total_pending:,.2f}")
            kpi4.metric(label="Pending Collection Pct", value=f"{pending_pct:.1f}%")

            st.markdown("---")
            st.subheader("📋 Branch Course Records Summary")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No sales data available in the database for your branch scope.")

    # --- 2. DATA ENTRY WORKSPACE PAGE ---
    elif page == "➕ Data Entry Workspace":
        st.title("🛠️ Operations Record Creator")

        tab1, tab2 = st.tabs(["Add New Sales Entry", "Log Payment Split Details"])

        with tab1:
            st.subheader("New Sale Generation")

            branches_data = run_query("SELECT branch_id, branch_name FROM branches")
            branch_dict = {b["branch_name"]: b["branch_id"] for b in branches_data} if branches_data else {}

            with st.form("new_sale_form"):
                col1, col2 = st.columns(2)

                with col1:
                    # Lock branch selection automatically if user is an Admin
                    if st.session_state.role == "Admin":
                        assigned_branch_name = "Assigned Branch"
                        if branches_data:
                            for b in branches_data:
                                if b["branch_id"] == st.session_state.branch_id:
                                    assigned_branch_name = b["branch_name"]
                                    break
                        selected_branch_name = st.selectbox(
                            "Select Target Branch",
                            options=[assigned_branch_name],
                            disabled=True,
                            key="ns_branch_locked"
                        )
                    else:
                        selected_branch_name = st.selectbox(
                            "Select Target Branch",
                            options=list(branch_dict.keys()) if branch_dict else ["Default Branch"],
                            key="ns_branch",
                        )

                    student_name = st.text_input("Student Name", key="ns_student_name")
                    mobile_number = st.text_input("Mobile Number", key="ns_mobile_number")
                    gross_sales = st.number_input(
                        "Gross Sales Amount (₹)",
                        min_value=0.0,
                        format="%.2f",
                        key="ns_gross_sales",
                    )

                with col2:
                    # Explicit default course options based on user screenshot + dynamic merging
                    default_courses = ["AI", "BA", "BI", "DA", "DS", "FSD", "ML", "SQL"]
                    courses_data = run_query("SELECT DISTINCT product_name FROM customer_sales WHERE product_name IS NOT NULL")
                    db_courses = [c["product_name"] for c in courses_data] if courses_data else []
                    
                    # Combine and deduplicate
                    course_options = sorted(list(set(default_courses + db_courses)))

                    course_name = st.selectbox(
                        "Select Course Name",
                        options=course_options,
                        key="ns_course_name",
                    )
                    joining_date = st.date_input("Joining Date", key="ns_joining_date")
                    received_amount = st.number_input(
                        "Received Amount (₹)",
                        min_value=0.0,
                        format="%.2f",
                        key="ns_received_amount",
                    )
                    initial_status = st.selectbox(
                        "Initial Order Status",
                        options=["open", "close"],
                        key="ns_initial_status",
                    )

                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    submit_sale = st.form_submit_button("Submit Sales Entry", use_container_width=True)
                with btn_col2:
                    clear_sale = st.form_submit_button(
                        "Clear Form",
                        use_container_width=True,
                        on_click=clear_new_sale_fields,
                    )

                if submit_sale:
                    if not student_name or not mobile_number:
                        st.warning("Please fill in the student name and mobile number.")
                    else:
                        # ENFORCE ADMIN BRANCH ID SECURELY
                        if st.session_state.role == "Admin":
                            branch_id = st.session_state.branch_id
                        else:
                            branch_id = branch_dict.get(selected_branch_name, 1) if branch_dict else 1

                        pending_amount = gross_sales - received_amount

                        insert_query = """
                            INSERT INTO customer_sales 
                            (branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, pending_amount, status) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        params = (
                            branch_id,
                            joining_date,
                            student_name,
                            mobile_number,
                            course_name,
                            gross_sales,
                            received_amount,
                            pending_amount,
                            initial_status,
                        )

                        last_id = run_query(insert_query, params=params, fetch=False)
                        if last_id is not None:
                            st.session_state.reset_ns = True
                            st.toast(f"✅ Successfully added sale for {student_name}!", icon="🎉")
                            st.success(f"Successfully added new sales record for {student_name}!")
                            st.rerun()
                        else:
                            st.error("Failed to insert record into the database.")

        with tab2:
            st.subheader("Post Payment Installment Split")

            # STRICTLY FILTER PENDING SALES TO ONLY LOGGED-IN ADMIN'S BRANCH
            if st.session_state.role == "Admin" and st.session_state.branch_id:
                active_sales = run_query(
                    "SELECT sale_id, name, gross_sales, received_amount, pending_amount FROM customer_sales WHERE pending_amount > 0 AND branch_id = %s",
                    (st.session_state.branch_id,)
                )
            else:
                active_sales = run_query(
                    "SELECT sale_id, name, gross_sales, received_amount, pending_amount FROM customer_sales WHERE pending_amount > 0"
                )

            if active_sales:
                sale_options = {
                    f"ID {s['sale_id']} - {s['name']} (₹{s['pending_amount']} Pending)": s
                    for s in active_sales
                }

                with st.form("payment_split_form"):
                    selected_sale_label = st.selectbox(
                        "Select Target Active Sale ID Asset",
                        options=list(sale_options.keys()),
                        key="ps_sale_label",
                    )
                    payment_channel = st.selectbox(
                        "Payment Collection Channel",
                        options=["Cash", "UPI", "Bank Transfer", "Credit Card", "Debit Card"],
                        key="ps_payment_channel",
                    )
                    collected_amount = st.number_input(
                        "Collected Split Amount Balance (₹)",
                        min_value=0.0,
                        format="%.2f",
                        key="ps_collected_amount",
                    )
                    payment_date = st.date_input("Payment Date", key="ps_payment_date")

                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        submit_payment = st.form_submit_button(
                            "Apply Payment Allocation", use_container_width=True
                        )
                    with btn_col2:
                        clear_payment = st.form_submit_button(
                            "Clear Form",
                            use_container_width=True,
                            on_click=clear_payment_split_fields,
                        )

                    if submit_payment:
                        selected_sale = sale_options[selected_sale_label]
                        sale_id = selected_sale["sale_id"]
                        current_received = selected_sale["received_amount"]
                        gross = selected_sale["gross_sales"]

                        col_amount_dec = Decimal(str(collected_amount))
                        new_received = current_received + col_amount_dec
                        new_pending = gross - new_received
                        new_status = "close" if new_pending <= 0 else "open"

                        payment_insert_query = """
                            INSERT INTO payment_splits (payment_date, amount_paid, payment_method, sale_id) 
                            VALUES (%s, %s, %s, %s)
                        """
                        payment_params = (payment_date, col_amount_dec, payment_channel, sale_id)
                        run_query(payment_insert_query, params=payment_params, fetch=False)

                        update_query = """
                            UPDATE customer_sales 
                            SET received_amount = %s, pending_amount = %s, status = %s 
                            WHERE sale_id = %s
                        """
                        update_params = (new_received, max(Decimal("0.0"), new_pending), new_status, sale_id)
                        run_query(update_query, params=update_params, fetch=False)

                        st.session_state.reset_ps = True

                        st.toast(
                            f"✅ Payment of ₹{collected_amount:,.2f} logged & customer sales updated for Sale ID {sale_id}!",
                            icon="🎉",
                        )
                        st.success(f"Successfully allocated ₹{collected_amount:,.2f} for Sale ID {sale_id}!")
                        st.rerun()
            else:
                st.info("No active sales with pending balances found for your branch.")

    # --- 3. ADVANCED SQL ENGINE PAGE (Super Admin Only) ---
    elif page == "🔍 Advanced SQL Engine" and st.session_state.role == "Super Admin":
        st.title("💻 Live SQL Business Analytics Engine")
        st.write("Select and execute any of the 20 mandatory verification queries to audit records from your tables.")

        predefined_queries = {
            "1. Retrieve all records from the customer_sales table": {
                "tier": "Basic Queries",
                "query": "SELECT * FROM customer_sales",
            },
            "2. Retrieve all records from the branches table": {
                "tier": "Basic Queries",
                "query": "SELECT * FROM branches",
            },
            "3. Retrieve all records from the payment_splits table": {
                "tier": "Basic Queries",
                "query": "SELECT * FROM payment_splits",
            },
            "4. Display all sales with status = 'open'": {
                "tier": "Basic Queries",
                "query": "SELECT * FROM customer_sales WHERE status = 'open'",
            },
            "5. Retrieve all sales belonging to the Chennai branch": {
                "tier": "Basic Queries",
                "query": """
                    SELECT cs.* 
                    FROM customer_sales cs 
                    JOIN branches b ON cs.branch_id = b.branch_id 
                    WHERE b.branch_name = 'Chennai'
                """,
            },
            "6. Calculate the total gross sales across all branches": {
                "tier": "Aggregation Queries",
                "query": "SELECT SUM(gross_sales) AS total_gross_sales FROM customer_sales",
            },
            "7. Calculate the total received amount across all sales": {
                "tier": "Aggregation Queries",
                "query": "SELECT SUM(received_amount) AS total_received_amount FROM customer_sales",
            },
            "8. Calculate the total pending amount across all sales": {
                "tier": "Aggregation Queries",
                "query": "SELECT SUM(pending_amount) AS total_pending_amount FROM customer_sales",
            },
            "9. Count the total number of sales per branch": {
                "tier": "Aggregation Queries",
                "query": """
                    SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales 
                    FROM customer_sales cs 
                    LEFT JOIN branches b ON cs.branch_id = b.branch_id 
                    GROUP BY b.branch_name
                """,
            },
            "10. Find the average gross sales amount": {
                "tier": "Aggregation Queries",
                "query": "SELECT AVG(gross_sales) AS average_gross_sales FROM customer_sales",
            },
            "11. Retrieve sales details along with the branch name": {
                "tier": "Join-Based Queries",
                "query": """
                    SELECT cs.sale_id, cs.name, cs.product_name, cs.gross_sales, b.branch_name 
                    FROM customer_sales cs 
                    LEFT JOIN branches b ON cs.branch_id = b.branch_id
                """,
            },
            "12. Retrieve sales details along with total payment received (using payment_splits)": {
                "tier": "Join-Based Queries",
                "query": """
                    SELECT cs.sale_id, cs.name, cs.gross_sales, cs.received_amount, COALESCE(SUM(p.amount_paid), 0) AS total_paid_splits 
                    FROM customer_sales cs 
                    LEFT JOIN payment_splits p ON cs.sale_id = p.sale_id 
                    GROUP BY cs.sale_id, cs.name, cs.gross_sales, cs.received_amount
                """,
            },
            "13. Show branch-wise total gross sales (using JOIN & GROUP BY)": {
                "tier": "Join-Based Queries",
                "query": """
                    SELECT b.branch_name, SUM(cs.gross_sales) AS branch_total_gross 
                    FROM branches b 
                    LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id 
                    GROUP BY b.branch_name
                """,
            },
            "14. Display sales along with payment method used": {
                "tier": "Join-Based Queries",
                "query": """
                    SELECT cs.sale_id, cs.name, p.payment_method, p.amount_paid, p.payment_date 
                    FROM customer_sales cs 
                    JOIN payment_splits p ON cs.sale_id = p.sale_id
                """,
            },
            "15. Retrieve sales along with branch admin name": {
                "tier": "Join-Based Queries",
                "query": """
                    SELECT cs.sale_id, cs.name, b.branch_name, u.username AS branch_admin 
                    FROM customer_sales cs 
                    JOIN branches b ON cs.branch_id = b.branch_id 
                    LEFT JOIN users u ON b.branch_id = u.branch_id AND u.role = 'Admin'
                """,
            },
            "16. Find sales where the pending amount is greater than 5000": {
                "tier": "Financial Tracking Queries",
                "query": "SELECT * FROM customer_sales WHERE pending_amount > 5000",
            },
            "17. Retrieve top 3 highest gross sales": {
                "tier": "Financial Tracking Queries",
                "query": "SELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3",
            },
            "18. Find the branch with highest total gross sales": {
                "tier": "Financial Tracking Queries",
                "query": """
                    SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross 
                    FROM branches b 
                    JOIN customer_sales cs ON b.branch_id = cs.branch_id 
                    GROUP BY b.branch_name 
                    ORDER BY total_gross DESC 
                    LIMIT 1
                """,
            },
            "19. Retrieve monthly sales summary (group by month & year)": {
                "tier": "Financial Tracking Queries",
                "query": """
                    SELECT MONTH(date) AS sale_month, YEAR(date) AS sale_year, 
                           COUNT(sale_id) AS total_sales, 
                           SUM(gross_sales) AS monthly_gross 
                    FROM customer_sales 
                    GROUP BY YEAR(date), MONTH(date) 
                    ORDER BY sale_year DESC, sale_month DESC
                """,
            },
            "20. Calculate payment method-wise total collection (Cash / UPI / Card)": {
                "tier": "Financial Tracking Queries",
                "query": """
                    SELECT payment_method, SUM(amount_paid) AS total_collected 
                    FROM payment_splits 
                    GROUP BY payment_method
                """,
            },
        }

        selected_q_label = st.selectbox(
            "Choose Targeted Predefined Operational Query:",
            options=list(predefined_queries.keys()),
        )

        q_info = predefined_queries[selected_q_label]

        st.markdown(f"**Query Classification Tier:** `{q_info['tier']}`")
        st.code(q_info["query"], language="sql")

        if st.button("Execute Live Database Transaction", type="primary"):
            results = run_query(q_info["query"])
            if results is not None:
                if len(results) > 0:
                    res_df = pd.DataFrame(results)
                    st.success(f"Query executed successfully! Returned {len(res_df)} rows.")
                    st.dataframe(res_df, use_container_width=True)
                else:
                    st.info("Query executed successfully, but returned 0 rows.")


# --- CONTROLLER ROUTING ---
if not st.session_state.logged_in:
    login_page()
else:
    main_dashboard()
