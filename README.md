# 📚 Library Management System

A comprehensive **Library Management System** built with Python for college Software Engineering project.

## 🛠️ Technologies Used

| Technology | Purpose |
|-----------|---------|
| **Python 3** | Core programming language |
| **Tkinter** | GUI framework (built-in with Python) |
| **SQLite3** | Database engine (built-in with Python) |

> **Note:** No external packages required! Uses only Python standard library.

## ✨ Features

### 📊 Dashboard
- Real-time statistics (total books, members, issued, overdue)
- Recent transaction history
- Visual stat cards with color coding

### 📖 Book Management
- Add, Edit, Delete books
- Search by title, author, ISBN, or category
- Track quantity and availability

### 👥 Member Management
- Add, Edit, Delete members
- Member types: Student, Faculty, Staff, Guest
- Search by name, email, or phone

### 📤 Issue Books
- Search and select books
- Search and select members
- Automatic due date calculation (14 days)
- Prevents duplicate issues

### 📥 Return Books
- View all currently issued books
- Automatic fine calculation (₹2/day for overdue)
- Overdue highlighting in red

### 📋 Transaction History
- Complete record of all issues and returns
- Fine tracking

### ⚠️ Overdue Tracking
- List of all overdue books
- Days overdue counter
- Estimated fine calculation

## 🚀 How to Run

1. Make sure Python 3.x is installed on your system
2. Open terminal/command prompt
3. Navigate to the project folder:
   ```
   cd library_management
   ```
4. Run the application:
   ```
   python main.py
   ```

## 📁 Project Structure

```
library_management/
├── main.py          # Main application (GUI + logic)
├── database.py      # Database operations (SQLite)
├── library.db       # Database file (auto-created)
└── README.md        # Project documentation
```

## 📐 Database Schema

### Books Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto) |
| title | TEXT | Book title |
| author | TEXT | Author name |
| isbn | TEXT | ISBN (unique) |
| publisher | TEXT | Publisher name |
| year | INTEGER | Publication year |
| category | TEXT | Book category |
| quantity | INTEGER | Total copies |
| available | INTEGER | Available copies |

### Members Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto) |
| name | TEXT | Member name |
| email | TEXT | Email address |
| phone | TEXT | Phone number |
| address | TEXT | Address |
| member_type | TEXT | Student/Faculty/Staff/Guest |
| join_date | TEXT | Date of joining |

### Transactions Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto) |
| book_id | INTEGER | Foreign key → Books |
| member_id | INTEGER | Foreign key → Members |
| issue_date | TEXT | Date of issue |
| due_date | TEXT | Return deadline |
| return_date | TEXT | Actual return date |
| fine | REAL | Fine amount (₹) |
| status | TEXT | Issued / Returned |

## 📸 Screenshots

The application features a modern dark-themed interface with:
- Sidebar navigation with hover effects
- Dashboard with colored stat cards
- Searchable data tables
- Modal dialogs for add/edit operations

## 👨‍💻 Developed By

**[Your Name]** — B.Tech Software Engineering Project

---
*Built with ❤️ using Python*
