"""
Library Management System - Database Module

Handles all SQLite database operations including CRUD for books,
members, and transactions (issue/return).
"""

import sqlite3
import os
from datetime import datetime, timedelta

# Database file path (same directory as this script)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")

# Fine rate per day for late returns (in ₹)
FINE_PER_DAY = 2.0

# Default loan period in days
LOAN_PERIOD_DAYS = 14


def get_connection():
    """Create and return a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """
    Create all required tables if they don't exist.
    Called once when the application starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Books table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            publisher TEXT,
            year INTEGER,
            category TEXT,
            quantity INTEGER DEFAULT 1,
            available INTEGER DEFAULT 1,
            added_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Members table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            member_type TEXT DEFAULT 'Student',
            join_date TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)

    # Transactions table (issue/return records)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            fine REAL DEFAULT 0.0,
            status TEXT DEFAULT 'Issued',
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (member_id) REFERENCES members(id)
        )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  BOOK OPERATIONS
# ─────────────────────────────────────────────

def add_book(title, author, isbn, publisher, year, category, quantity):
    """Add a new book to the library."""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO books (title, author, isbn, publisher, year, category, quantity, available)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, author, isbn, publisher, year, category, quantity, quantity)
        )
        conn.commit()
        return True, "Book added successfully!"
    except sqlite3.IntegrityError:
        return False, "A book with this ISBN already exists."
    finally:
        conn.close()


def update_book(book_id, title, author, isbn, publisher, year, category, quantity):
    """Update an existing book's details."""
    conn = get_connection()
    try:
        # Get current book info to adjust available count
        current = conn.execute("SELECT quantity, available FROM books WHERE id = ?", (book_id,)).fetchone()
        if current:
            issued = current["quantity"] - current["available"]
            new_available = max(0, quantity - issued)
        else:
            new_available = quantity

        conn.execute(
            """UPDATE books SET title=?, author=?, isbn=?, publisher=?, year=?, 
               category=?, quantity=?, available=? WHERE id=?""",
            (title, author, isbn, publisher, year, category, quantity, new_available, book_id)
        )
        conn.commit()
        return True, "Book updated successfully!"
    except sqlite3.IntegrityError:
        return False, "A book with this ISBN already exists."
    finally:
        conn.close()


def delete_book(book_id):
    """Delete a book from the library."""
    conn = get_connection()
    # Check if the book has active transactions
    active = conn.execute(
        "SELECT COUNT(*) as cnt FROM transactions WHERE book_id = ? AND status = 'Issued'",
        (book_id,)
    ).fetchone()
    if active["cnt"] > 0:
        conn.close()
        return False, "Cannot delete: This book has active issues."
    conn.execute("DELETE FROM transactions WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return True, "Book deleted successfully!"


def search_books(keyword=""):
    """Search books by title, author, ISBN, or category."""
    conn = get_connection()
    if keyword:
        rows = conn.execute(
            """SELECT * FROM books WHERE title LIKE ? OR author LIKE ? 
               OR isbn LIKE ? OR category LIKE ? ORDER BY title""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_book(book_id):
    """Get a single book by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    return dict(row) if row else None




def add_member(name, email, phone, address, member_type):
    """Add a new library member."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO members (name, email, phone, address, member_type)
           VALUES (?, ?, ?, ?, ?)""",
        (name, email, phone, address, member_type)
    )
    conn.commit()
    conn.close()
    return True, "Member added successfully!"


def update_member(member_id, name, email, phone, address, member_type):
    """Update an existing member's details."""
    conn = get_connection()
    conn.execute(
        """UPDATE members SET name=?, email=?, phone=?, address=?, member_type=? WHERE id=?""",
        (name, email, phone, address, member_type, member_id)
    )
    conn.commit()
    conn.close()
    return True, "Member updated successfully!"


def delete_member(member_id):
    """Delete a member from the library."""
    conn = get_connection()
    active = conn.execute(
        "SELECT COUNT(*) as cnt FROM transactions WHERE member_id = ? AND status = 'Issued'",
        (member_id,)
    ).fetchone()
    if active["cnt"] > 0:
        conn.close()
        return False, "Cannot delete: This member has unreturned books."
    conn.execute("DELETE FROM transactions WHERE member_id = ?", (member_id,))
    conn.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()
    return True, "Member deleted successfully!"


def search_members(keyword=""):
    """Search members by name, email, or phone."""
    conn = get_connection()
    if keyword:
        rows = conn.execute(
            """SELECT * FROM members WHERE is_active = 1 AND 
               (name LIKE ? OR email LIKE ? OR phone LIKE ?) ORDER BY name""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM members WHERE is_active = 1 ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_member(member_id):
    """Get a single member by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
    conn.close()
    return dict(row) if row else None



def issue_book(book_id, member_id):
    """Issue a book to a member."""
    conn = get_connection()

    # Check book availability
    book = conn.execute("SELECT available FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        conn.close()
        return False, "Book not found."
    if book["available"] <= 0:
        conn.close()
        return False, "No copies available for this book."

    # Check if member already has this book
    existing = conn.execute(
        "SELECT COUNT(*) as cnt FROM transactions WHERE book_id=? AND member_id=? AND status='Issued'",
        (book_id, member_id)
    ).fetchone()
    if existing["cnt"] > 0:
        conn.close()
        return False, "This member already has a copy of this book."

    issue_date = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=LOAN_PERIOD_DAYS)).strftime("%Y-%m-%d")

    conn.execute(
        """INSERT INTO transactions (book_id, member_id, issue_date, due_date, status)
           VALUES (?, ?, ?, ?, 'Issued')""",
        (book_id, member_id, issue_date, due_date)
    )
    conn.execute("UPDATE books SET available = available - 1 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return True, f"Book issued successfully! Due date: {due_date}"


def return_book(transaction_id):
    """Return a book and calculate fine if overdue."""
    conn = get_connection()

    txn = conn.execute("SELECT * FROM transactions WHERE id = ? AND status = 'Issued'",
                       (transaction_id,)).fetchone()
    if not txn:
        conn.close()
        return False, "Transaction not found or book already returned.", 0.0

    return_date = datetime.now().strftime("%Y-%m-%d")
    due_date = datetime.strptime(txn["due_date"], "%Y-%m-%d")
    today = datetime.now()

    fine = 0.0
    if today > due_date:
        overdue_days = (today - due_date).days
        fine = overdue_days * FINE_PER_DAY

    conn.execute(
        "UPDATE transactions SET return_date=?, fine=?, status='Returned' WHERE id=?",
        (return_date, fine, transaction_id)
    )
    conn.execute("UPDATE books SET available = available + 1 WHERE id = ?", (txn["book_id"],))
    conn.commit()
    conn.close()

    if fine > 0:
        return True, f"Book returned. Overdue fine: ₹{fine:.2f}", fine
    return True, "Book returned successfully! No fine.", 0.0


def get_issued_books():
    """Get all currently issued books with member and book details."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.id as txn_id, t.issue_date, t.due_date, 
               b.title as book_title, b.id as book_id,
               m.name as member_name, m.id as member_id
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id
        WHERE t.status = 'Issued'
        ORDER BY t.due_date
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_transactions():
    """Get all transactions with details."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.id as txn_id, t.issue_date, t.due_date, t.return_date, t.fine, t.status,
               b.title as book_title, b.id as book_id,
               m.name as member_name, m.id as member_id
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id
        ORDER BY t.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]



def get_dashboard_stats():
    """Get summary statistics for the dashboard."""
    conn = get_connection()

    total_books = conn.execute("SELECT COALESCE(SUM(quantity), 0) as cnt FROM books").fetchone()["cnt"]
    total_titles = conn.execute("SELECT COUNT(*) as cnt FROM books").fetchone()["cnt"]
    total_members = conn.execute("SELECT COUNT(*) as cnt FROM members WHERE is_active = 1").fetchone()["cnt"]
    books_issued = conn.execute(
        "SELECT COUNT(*) as cnt FROM transactions WHERE status = 'Issued'"
    ).fetchone()["cnt"]
    overdue = conn.execute(
        "SELECT COUNT(*) as cnt FROM transactions WHERE status = 'Issued' AND due_date < date('now')"
    ).fetchone()["cnt"]
    total_fines = conn.execute(
        "SELECT COALESCE(SUM(fine), 0) as total FROM transactions"
    ).fetchone()["total"]

    conn.close()
    return {
        "total_books": total_books,
        "total_titles": total_titles,
        "total_members": total_members,
        "books_issued": books_issued,
        "overdue_books": overdue,
        "total_fines": total_fines
    }


def get_recent_transactions(limit=10):
    """Get the most recent transactions for the dashboard."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.id as txn_id, t.issue_date, t.due_date, t.return_date, t.status,
               b.title as book_title, m.name as member_name
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id
        ORDER BY t.id DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_overdue_books():
    """Get all overdue books."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.id as txn_id, t.issue_date, t.due_date,
               b.title as book_title, b.id as book_id,
               m.name as member_name, m.id as member_id,
               CAST(julianday(date('now')) - julianday(t.due_date) AS INTEGER) as overdue_days
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id
        WHERE t.status = 'Issued' AND t.due_date < date('now')
        ORDER BY t.due_date
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Insert sample data for demonstration
def insert_sample_data():
    """Insert sample books and members for demonstration purposes."""
    conn = get_connection()

    # Check if data already exists
    count = conn.execute("SELECT COUNT(*) as cnt FROM books").fetchone()["cnt"]
    if count > 0:
        conn.close()
        return

    # Sample books
    sample_books = [
        ("Introduction to Algorithms", "Thomas H. Cormen", "978-0262033848", "MIT Press", 2009, "Computer Science", 5),
        ("Clean Code", "Robert C. Martin", "978-0132350884", "Prentice Hall", 2008, "Software Engineering", 3),
        ("The C Programming Language", "Brian W. Kernighan", "978-0131103627", "Prentice Hall", 1988, "Programming", 4),
        ("Database System Concepts", "Abraham Silberschatz", "978-0078022159", "McGraw-Hill", 2019, "Database", 3),
        ("Operating System Concepts", "Abraham Silberschatz", "978-1119800361", "Wiley", 2021, "Operating Systems", 4),
        ("Computer Networks", "Andrew S. Tanenbaum", "978-0132126953", "Pearson", 2010, "Networking", 3),
        ("Artificial Intelligence: A Modern Approach", "Stuart Russell", "978-0134610993", "Pearson", 2020, "AI/ML", 2),
        ("Design Patterns", "Erich Gamma", "978-0201633610", "Addison-Wesley", 1994, "Software Engineering", 3),
        ("Python Crash Course", "Eric Matthes", "978-1593279288", "No Starch Press", 2019, "Programming", 5),
        ("Data Structures and Algorithms in Python", "Michael T. Goodrich", "978-1118290279", "Wiley", 2013, "Data Structures", 4),
        ("Digital Logic and Computer Design", "M. Morris Mano", "978-8131714508", "Pearson", 2007, "Digital Electronics", 3),
        ("Discrete Mathematics and Its Applications", "Kenneth H. Rosen", "978-0073383095", "McGraw-Hill", 2011, "Mathematics", 4),
    ]

    for book in sample_books:
        conn.execute(
            "INSERT INTO books (title, author, isbn, publisher, year, category, quantity, available) VALUES (?,?,?,?,?,?,?,?)",
            (*book, book[6])
        )

    # Sample members
    sample_members = [
        ("Aarav Sharma", "aarav.sharma@college.edu", "9876543210", "Room 101, Boys Hostel", "Student"),
        ("Priya Patel", "priya.patel@college.edu", "9876543211", "Room 205, Girls Hostel", "Student"),
        ("Rahul Kumar", "rahul.kumar@college.edu", "9876543212", "Room 302, Boys Hostel", "Student"),
        ("Sneha Reddy", "sneha.reddy@college.edu", "9876543213", "Room 107, Girls Hostel", "Student"),
        ("Dr. Amit Verma", "amit.verma@college.edu", "9876543214", "Faculty Block A", "Faculty"),
        ("Neha Gupta", "neha.gupta@college.edu", "9876543215", "Room 201, Girls Hostel", "Student"),
        ("Vikram Singh", "vikram.singh@college.edu", "9876543216", "Room 405, Boys Hostel", "Student"),
        ("Prof. Sunita Joshi", "sunita.joshi@college.edu", "9876543217", "Faculty Block B", "Faculty"),
    ]

    for member in sample_members:
        conn.execute(
            "INSERT INTO members (name, email, phone, address, member_type) VALUES (?,?,?,?,?)",
            member
        )

    # Sample transactions (issue/return/overdue data)
    from datetime import datetime, timedelta
    today = datetime.now()

    sample_transactions = [
        # (book_id, member_id, issue_date, due_date, return_date, fine, status)
        # ── Overdue books (issued in the past, past due date, NOT returned) ──
        (1, 1, (today - timedelta(days=30)).strftime("%Y-%m-%d"),
               (today - timedelta(days=16)).strftime("%Y-%m-%d"),
               None, 0.0, "Issued"),  # 16 days overdue
        (3, 2, (today - timedelta(days=25)).strftime("%Y-%m-%d"),
               (today - timedelta(days=11)).strftime("%Y-%m-%d"),
               None, 0.0, "Issued"),  # 11 days overdue
        (5, 4, (today - timedelta(days=20)).strftime("%Y-%m-%d"),
               (today - timedelta(days=6)).strftime("%Y-%m-%d"),
               None, 0.0, "Issued"),  # 6 days overdue
        (7, 6, (today - timedelta(days=22)).strftime("%Y-%m-%d"),
               (today - timedelta(days=8)).strftime("%Y-%m-%d"),
               None, 0.0, "Issued"),  # 8 days overdue

        # ── Currently issued (not overdue yet) ──
        (2, 3, (today - timedelta(days=5)).strftime("%Y-%m-%d"),
               (today + timedelta(days=9)).strftime("%Y-%m-%d"),
               None, 0.0, "Issued"),  # Due in 9 days
        (4, 5, (today - timedelta(days=3)).strftime("%Y-%m-%d"),
               (today + timedelta(days=11)).strftime("%Y-%m-%d"),
               None, 0.0, "Issued"),  # Due in 11 days
        (9, 7, (today - timedelta(days=7)).strftime("%Y-%m-%d"),
               (today + timedelta(days=7)).strftime("%Y-%m-%d"),
               None, 0.0, "Issued"),  # Due in 7 days

        # ── Already returned books (some with fines) ──
        (6, 1, (today - timedelta(days=40)).strftime("%Y-%m-%d"),
               (today - timedelta(days=26)).strftime("%Y-%m-%d"),
               (today - timedelta(days=20)).strftime("%Y-%m-%d"),
               12.0, "Returned"),  # Returned 6 days late, fine ₹12
        (8, 3, (today - timedelta(days=35)).strftime("%Y-%m-%d"),
               (today - timedelta(days=21)).strftime("%Y-%m-%d"),
               (today - timedelta(days=21)).strftime("%Y-%m-%d"),
               0.0, "Returned"),  # Returned on time
        (10, 2, (today - timedelta(days=50)).strftime("%Y-%m-%d"),
                (today - timedelta(days=36)).strftime("%Y-%m-%d"),
                (today - timedelta(days=30)).strftime("%Y-%m-%d"),
                12.0, "Returned"),  # Returned 6 days late, fine ₹12
        (11, 8, (today - timedelta(days=28)).strftime("%Y-%m-%d"),
                (today - timedelta(days=14)).strftime("%Y-%m-%d"),
                (today - timedelta(days=12)).strftime("%Y-%m-%d"),
                4.0, "Returned"),  # Returned 2 days late, fine ₹4
        (12, 5, (today - timedelta(days=15)).strftime("%Y-%m-%d"),
                (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                (today - timedelta(days=2)).strftime("%Y-%m-%d"),
                0.0, "Returned"),  # Returned 1 day early
    ]

    for txn in sample_transactions:
        book_id, member_id, issue_date, due_date, return_date, fine, status = txn
        conn.execute(
            """INSERT INTO transactions (book_id, member_id, issue_date, due_date, return_date, fine, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (book_id, member_id, issue_date, due_date, return_date, fine, status)
        )
        # Decrement available count for currently issued books
        if status == "Issued":
            conn.execute("UPDATE books SET available = available - 1 WHERE id = ?", (book_id,))

    conn.commit()
    conn.close()

