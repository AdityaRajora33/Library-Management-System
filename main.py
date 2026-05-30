"""
╔══════════════════════════════════════════════════════════════╗
║          LIBRARY MANAGEMENT SYSTEM  v2.0                     ║
║          Python + Tkinter + SQLite                           ║
║          College Project - Software Engineering              ║
╚══════════════════════════════════════════════════════════════╝

A comprehensive Library Management System with:
  • Dashboard with real-time statistics
  • Book Management (Add / Edit / Delete / Search)
  • Member Management (Add / Edit / Delete / Search)
  • Issue & Return Books with automatic fine calculation
  • Transaction History & Overdue tracking
  • Enhanced hover effects & warm beige-brown UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from datetime import datetime
import database as db

# ─────────────────────────────────────────────
#  COLOR SCHEME & THEME CONFIGURATION
#  Warm Beige & Brown Theme - Approachable UI
# ─────────────────────────────────────────────
COLORS = {
    "bg_main":       "#f5ebe0",       # Main background – warm cream
    "bg_sidebar":    "#4a2c2a",       # Sidebar background – dark espresso brown
    "bg_card":       "#fff8f0",       # Card background – warm off-white
    "bg_input":      "#f0e4d4",       # Input field background – light beige
    "bg_hover_side": "#6b4332",       # Sidebar hover – lighter brown
    "accent":        "#c17f3e",       # Primary accent – warm amber
    "accent_light":  "#d4a35a",       # Light accent – golden
    "accent_green":  "#6a9b5a",       # Success – olive green
    "accent_orange": "#d4883a",       # Warning – warm orange
    "accent_red":    "#c0392b",       # Danger – warm red
    "accent_blue":   "#5b7ea8",       # Info – dusty blue
    "text_primary":  "#3c2415",       # Primary text – dark brown
    "text_secondary":"#7a6552",       # Secondary text – medium brown
    "text_muted":    "#a89580",       # Muted text – light brown
    "text_on_dark":  "#f5ebe0",       # Text on dark backgrounds
    "border":        "#ddd0c0",       # Border color – tan
    "table_stripe":  "#f8f0e5",       # Table alternate row – light beige
    "sidebar_active":"#7a4a30",       # Active nav item bg
    "table_header":  "#e8dac8",       # Table header bg
    "overdue_bg":    "#fde8e8",       # Overdue row background
    "overdue_fg":    "#c0392b",       # Overdue text
}

# Font sizes
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 16, "bold")
FONT_SUBHEADING = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI", 11, "bold")
FONT_SIDEBAR = ("Segoe UI", 12)
FONT_STAT_NUMBER = ("Segoe UI", 28, "bold")
FONT_STAT_LABEL = ("Segoe UI", 10)

# ─────────────────────────────────────────────
#  LOGIN CREDENTIALS
#  Change these to update the application's login
# ─────────────────────────────────────────────
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin@123"

class LibraryApp(tk.Tk):
    """Main application window for the Library Management System."""

    def __init__(self):
        super().__init__()

        # ── Window Setup ──
        self.title("📚 Library Management System")
        self.geometry("1280x720")
        self.minsize(1100, 650)
        self.configure(bg=COLORS["bg_main"])

        # Try to set icon (ignore if not available)
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        # ── Initialize Database ──
        db.initialize_database()
        db.insert_sample_data()

        # ── Apply Custom Theme ──
        self._setup_styles()

        # ── Build Layout ──
        self.current_page = None
        self.show_login_page()

    # ─────────────────────────────────────────
    #  THEME & STYLES
    # ─────────────────────────────────────────
    def _setup_styles(self):
        """Configure ttk styles for the beige-brown theme."""
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Treeview (table) styling
        self.style.configure("Custom.Treeview",
                             background=COLORS["bg_card"],
                             foreground=COLORS["text_primary"],
                             fieldbackground=COLORS["bg_card"],
                             borderwidth=0,
                             font=FONT_SMALL,
                             rowheight=32)
        self.style.configure("Custom.Treeview.Heading",
                             background=COLORS["table_header"],
                             foreground=COLORS["text_primary"],
                             font=("Segoe UI", 10, "bold"),
                             borderwidth=0)
        self.style.map("Custom.Treeview",
                       background=[("selected", COLORS["accent"])],
                       foreground=[("selected", "#ffffff")])

        # Scrollbar styling
        self.style.configure("Custom.Vertical.TScrollbar",
                             background=COLORS["border"],
                             troughcolor=COLORS["bg_card"],
                             borderwidth=0,
                             arrowsize=12)

    # ─────────────────────────────────────────
    #  SIDEBAR
    # ─────────────────────────────────────────
    def _build_sidebar(self):
        """Build the left sidebar navigation."""
        self.sidebar = tk.Frame(self, bg=COLORS["bg_sidebar"], width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App title / logo area
        logo_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"], pady=20)
        logo_frame.pack(fill="x")

        tk.Label(logo_frame, text="📚", font=("Segoe UI", 36),
                 bg=COLORS["bg_sidebar"], fg=COLORS["accent_light"]).pack()
        tk.Label(logo_frame, text="LIBRARY", font=("Segoe UI", 18, "bold"),
                 bg=COLORS["bg_sidebar"], fg=COLORS["text_on_dark"]).pack()
        tk.Label(logo_frame, text="Management System", font=FONT_SMALL,
                 bg=COLORS["bg_sidebar"], fg=COLORS["accent_light"]).pack()

        # Divider
        tk.Frame(self.sidebar, bg=COLORS["accent"], height=2).pack(fill="x", padx=20, pady=10)

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("📊", "Dashboard",    self.show_dashboard),
            ("📖", "Books",        self.show_books),
            ("👥", "Members",      self.show_members),
            ("📤", "Issue Book",   self.show_issue),
            ("📥", "Return Book",  self.show_return),
            ("📋", "Transactions", self.show_transactions),
            ("⚠️", "Overdue",      self.show_overdue),
        ]

        for icon, label, command in nav_items:
            btn = self._create_nav_button(icon, label, command)
            self.nav_buttons[label] = btn

        # Footer
        tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"]).pack(fill="both", expand=True)
        tk.Label(self.sidebar, text="v2.0 • Python Project",
                 font=("Segoe UI", 9), bg=COLORS["bg_sidebar"],
                 fg=COLORS["accent_light"]).pack(side="bottom", pady=15)

    def _create_nav_button(self, icon, label, command):
        """Create a styled sidebar navigation button with stable hover."""
        btn_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"], cursor="hand2")
        btn_frame.pack(fill="x", padx=12, pady=2)

        # Left accent bar (hidden by default)
        accent_bar = tk.Frame(btn_frame, bg=COLORS["bg_sidebar"], width=4)
        accent_bar.pack(side="left", fill="y")

        btn_label = tk.Label(
            btn_frame, text=f"  {icon}  {label}", font=FONT_SIDEBAR,
            bg=COLORS["bg_sidebar"], fg=COLORS["text_on_dark"],
            anchor="w", padx=10, pady=10
        )
        btn_label.pack(fill="x", side="left", expand=True)

        def on_enter(e):
            if self.current_page != label:
                btn_frame.configure(bg=COLORS["bg_hover_side"])
                btn_label.configure(bg=COLORS["bg_hover_side"], fg="#ffffff")
                accent_bar.configure(bg=COLORS["accent"])

        def on_leave(e):
            if self.current_page != label:
                btn_frame.configure(bg=COLORS["bg_sidebar"])
                btn_label.configure(bg=COLORS["bg_sidebar"], fg=COLORS["text_on_dark"])
                accent_bar.configure(bg=COLORS["bg_sidebar"])

        def on_click(e):
            command()

        for widget in (btn_frame, btn_label, accent_bar):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        return (btn_frame, btn_label, accent_bar)

    def _set_active_nav(self, label):
        """Highlight the active navigation button."""
        for name, (frame, lbl, bar) in self.nav_buttons.items():
            if name == label:
                frame.configure(bg=COLORS["sidebar_active"])
                lbl.configure(bg=COLORS["sidebar_active"], fg="#ffffff")
                bar.configure(bg=COLORS["accent"])
            else:
                frame.configure(bg=COLORS["bg_sidebar"])
                lbl.configure(bg=COLORS["bg_sidebar"], fg=COLORS["text_on_dark"])
                bar.configure(bg=COLORS["bg_sidebar"])
        self.current_page = label

    # ─────────────────────────────────────────
    #  MAIN CONTENT AREA
    # ─────────────────────────────────────────
    def _build_main_area(self):
        """Build the main content area on the right."""
        self.main_area = tk.Frame(self, bg=COLORS["bg_main"])
        self.main_area.pack(side="right", fill="both", expand=True)

    def _clear_main(self):
        """Remove all widgets from the main content area."""
        for widget in self.main_area.winfo_children():
            widget.destroy()

    # ─────────────────────────────────────────
    #  HELPER WIDGETS AND LOGIN
    # ─────────────────────────────────────────
    def show_login_page(self):
        """Display the secure login page."""
        self.login_frame = tk.Frame(self, bg=COLORS["bg_main"])
        self.login_frame.pack(fill="both", expand=True)

        center_frame = tk.Frame(self.login_frame, bg=COLORS["bg_main"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(center_frame, bg=COLORS["bg_card"],
                        highlightbackground=COLORS["border"],
                        highlightthickness=1)
        card.pack(padx=20, pady=20, ipadx=40, ipady=30)

        tk.Label(card, text="📚", font=("Segoe UI", 48),
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=(10, 0))
        tk.Label(card, text="Library Management", font=FONT_TITLE,
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack()
        tk.Label(card, text="Please login to access the system", font=FONT_BODY,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(pady=(5, 30))

        tk.Label(card, text="Username", font=FONT_BODY,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w", padx=30)
        user_entry = tk.Entry(card, font=FONT_BODY, bg=COLORS["bg_input"],
                              fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                              relief="flat", highlightthickness=1,
                              highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"])
        user_entry.pack(fill="x", padx=30, pady=(5, 15), ipady=6)

        tk.Label(card, text="Password", font=FONT_BODY,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(anchor="w", padx=30)
        pwd_entry = tk.Entry(card, font=FONT_BODY, bg=COLORS["bg_input"],
                             fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                             relief="flat", highlightthickness=1,
                             highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"],
                             show="*")
        pwd_entry.pack(fill="x", padx=30, pady=(5, 30), ipady=6)

        def attempt_login(e=None):
            username = user_entry.get().strip()
            password = pwd_entry.get().strip()

            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                self.login_frame.destroy()
                self._build_sidebar()
                self._build_main_area()
                self.show_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.", parent=self)

        user_entry.bind("<Return>", attempt_login)
        pwd_entry.bind("<Return>", attempt_login)

        btn = tk.Button(
            card, text="🔒 Login", command=attempt_login,
            font=FONT_BUTTON, bg=COLORS["accent"], fg="#ffffff",
            activebackground=COLORS["accent_light"],
            activeforeground="#ffffff",
            relief="flat", cursor="hand2"
        )
        btn.pack(fill="x", padx=30, pady=(0, 20), ipady=6)

    def _make_header(self, parent, title, subtitle=""):
        """Create a page header with title and optional subtitle."""
        header = tk.Frame(parent, bg=COLORS["bg_main"])
        header.pack(fill="x", padx=30, pady=(25, 5))
        tk.Label(header, text=title, font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor="w")
        if subtitle:
            tk.Label(header, text=subtitle, font=FONT_BODY,
                     bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 0))
        return header

    def _make_card(self, parent, **pack_opts):
        """Create a styled card frame."""
        card = tk.Frame(parent, bg=COLORS["bg_card"],
                        highlightbackground=COLORS["border"],
                        highlightthickness=1)
        card.pack(fill="both", padx=30, pady=10, **pack_opts)
        return card

    def _make_button(self, parent, text, command, color=None, width=14):
        """Create a styled button without complex hover checks for stability."""
        if color is None:
            color = COLORS["accent"]

        # Use white text on dark buttons, dark text on light buttons
        fg_color = "#ffffff"

        btn = tk.Button(
            parent, text=text, command=command,
            font=FONT_BUTTON, bg=color, fg=fg_color,
            activebackground=self._darken_color(color, 20),
            activeforeground="#ffffff",
            relief="flat", cursor="hand2", width=width, pady=6,
            bd=0
        )

        return btn

    def _darken_color(self, hex_color, amount=25):
        """Darken a hex color by a given amount."""
        try:
            hex_color = hex_color.lstrip('#')
            r = max(0, int(hex_color[0:2], 16) - amount)
            g = max(0, int(hex_color[2:4], 16) - amount)
            b = max(0, int(hex_color[4:6], 16) - amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color

    def _make_entry(self, parent, placeholder=""):
        """Create a styled entry field."""
        entry = tk.Entry(
            parent, font=FONT_BODY, bg=COLORS["bg_input"],
            fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
            relief="flat", highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=COLORS["text_muted"])

            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, "end")
                    entry.config(fg=COLORS["text_primary"])

            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=COLORS["text_muted"])

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        return entry

    def _make_label_entry(self, parent, label_text, row, col=0, width=30, placeholder=""):
        """Create a label + entry pair in a grid layout."""
        tk.Label(parent, text=label_text, font=FONT_BODY,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                 anchor="w").grid(row=row, column=col, sticky="w", padx=15, pady=(10, 2))
        entry = self._make_entry(parent, placeholder)
        entry.config(width=width)
        entry.grid(row=row, column=col + 1, sticky="ew", padx=15, pady=(10, 2), ipady=5)
        return entry

    def _make_treeview(self, parent, columns, heights=15):
        """Create a styled Treeview with scrollbar (no row hover — stable)."""
        tree_frame = tk.Frame(parent, bg=COLORS["bg_card"])
        tree_frame.pack(fill="both", expand=True, padx=15, pady=10)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", style="Custom.Vertical.TScrollbar")
        scroll_y.pack(side="right", fill="y")

        tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings",
            style="Custom.Treeview", height=heights,
            yscrollcommand=scroll_y.set
        )
        scroll_y.config(command=tree.yview)

        for col in columns:
            tree.heading(col, text=col, anchor="w")
            tree.column(col, anchor="w", minwidth=60, width=120)

        tree.pack(fill="both", expand=True)

        # Alternate row colors (stable tags, no hover swapping)
        tree.tag_configure("oddrow", background=COLORS["table_stripe"])
        tree.tag_configure("evenrow", background=COLORS["bg_card"])
        tree.tag_configure("overdue", background=COLORS["overdue_bg"], foreground=COLORS["overdue_fg"])

        return tree

    # ═══════════════════════════════════════════
    #  PAGE: DASHBOARD
    # ═══════════════════════════════════════════
    def show_dashboard(self):
        """Display the dashboard with statistics and recent activity."""
        self._clear_main()
        self._set_active_nav("Dashboard")
        self._make_header(self.main_area, "📊 Dashboard", "Overview of library statistics")

        stats = db.get_dashboard_stats()

        # ── Stats Cards ──
        cards_frame = tk.Frame(self.main_area, bg=COLORS["bg_main"])
        cards_frame.pack(fill="x", padx=30, pady=10)

        stat_data = [
            ("📚", "Total Books", str(stats["total_books"]), COLORS["accent"]),
            ("📖", "Unique Titles", str(stats["total_titles"]), COLORS["accent_blue"]),
            ("👥", "Members", str(stats["total_members"]), COLORS["accent_green"]),
            ("📤", "Issued", str(stats["books_issued"]), COLORS["accent_orange"]),
            ("⚠️", "Overdue", str(stats["overdue_books"]), COLORS["accent_red"]),
            ("💰", "Fines", f"₹{stats['total_fines']:.0f}", COLORS["accent_light"]),
        ]

        for i, (icon, label, value, color) in enumerate(stat_data):
            card = tk.Frame(cards_frame, bg=COLORS["bg_card"],
                            highlightbackground=COLORS["border"], highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=6, pady=5, ipadx=10, ipady=10)
            cards_frame.columnconfigure(i, weight=1)

            # Color bar on top
            tk.Frame(card, bg=color, height=4).pack(fill="x")
            tk.Label(card, text=icon, font=("Segoe UI", 20),
                     bg=COLORS["bg_card"], fg=color).pack(pady=(10, 0))
            tk.Label(card, text=value, font=FONT_STAT_NUMBER,
                     bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack()
            tk.Label(card, text=label, font=FONT_STAT_LABEL,
                     bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(pady=(0, 10))

        # ── Recent Transactions ──
        recent_card = self._make_card(self.main_area, expand=True)
        tk.Label(recent_card, text="📋 Recent Transactions", font=FONT_SUBHEADING,
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(anchor="w", padx=15, pady=(15, 5))

        cols = ("S.No", "Book", "Member", "Issue Date", "Due Date", "Status")
        tree = self._make_treeview(recent_card, cols)
        tree.column("S.No", width=50)
        tree.column("Status", width=80)

        recent = db.get_recent_transactions(15)
        for i, txn in enumerate(recent):
            tag = "oddrow" if i % 2 else "evenrow"
            tree.insert("", "end", values=(
                i + 1, txn["book_title"][:35], txn["member_name"],
                txn["issue_date"], txn["due_date"], txn["status"]
            ), tags=(tag,))

    # ═══════════════════════════════════════════
    #  PAGE: BOOKS MANAGEMENT
    # ═══════════════════════════════════════════
    def show_books(self):
        """Display the books management page."""
        self._clear_main()
        self._set_active_nav("Books")
        self._make_header(self.main_area, "📖 Books Management", "Add, edit, search, and remove books")

        # ── Search Bar ──
        search_frame = tk.Frame(self.main_area, bg=COLORS["bg_main"])
        search_frame.pack(fill="x", padx=30, pady=(10, 0))

        self.book_search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame, textvariable=self.book_search_var,
            font=FONT_BODY, bg=COLORS["bg_input"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"], relief="flat", width=40,
            highlightthickness=1, highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )
        search_entry.pack(side="left", ipady=6, padx=(0, 10))
        search_entry.insert(0, "🔍 Search books...")
        search_entry.bind("<FocusIn>", lambda e: (search_entry.delete(0, "end") if search_entry.get().startswith("🔍") else None))
        search_entry.bind("<KeyRelease>", lambda e: self._refresh_books_table())

        btn_frame = tk.Frame(search_frame, bg=COLORS["bg_main"])
        btn_frame.pack(side="right")

        self._make_button(btn_frame, "➕ Add Book", self._show_add_book_dialog,
                          COLORS["accent_green"], width=12).pack(side="left", padx=4)
        self._make_button(btn_frame, "✏️ Edit", self._show_edit_book_dialog,
                          COLORS["accent_blue"], width=10).pack(side="left", padx=4)
        self._make_button(btn_frame, "🗑️ Delete", self._delete_selected_book,
                          COLORS["accent_red"], width=10).pack(side="left", padx=4)

        # ── Books Table ──
        table_card = self._make_card(self.main_area, expand=True)
        cols = ("S.No", "Title", "Author", "ISBN", "Publisher", "Year", "Category", "Qty", "Available")
        self.books_tree = self._make_treeview(table_card, cols)
        self.books_tree.column("S.No", width=50)
        self.books_tree.column("Title", width=200)
        self.books_tree.column("Author", width=150)
        self.books_tree.column("ISBN", width=130)
        self.books_tree.column("Publisher", width=120)
        self.books_tree.column("Year", width=60)
        self.books_tree.column("Category", width=120)
        self.books_tree.column("Qty", width=45)
        self.books_tree.column("Available", width=70)

        self._books_id_map = {}
        self._refresh_books_table()

    def _refresh_books_table(self):
        """Refresh the books table with current data."""
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)

        keyword = self.book_search_var.get()
        if keyword.startswith("🔍"):
            keyword = ""
        books = db.search_books(keyword)

        self._books_id_map = {}
        for i, b in enumerate(books):
            sno = i + 1
            tag = "oddrow" if i % 2 else "evenrow"
            item_id = self.books_tree.insert("", "end", values=(
                sno, b["title"], b["author"], b["isbn"] or "",
                b["publisher"] or "", b["year"] or "", b["category"] or "",
                b["quantity"], b["available"]
            ), tags=(tag,))
            self._books_id_map[item_id] = b["id"]

    def _get_selected_book_id(self):
        """Get the actual DB ID of the selected book."""
        selected = self.books_tree.selection()
        if not selected:
            return None, None
        item_id = selected[0]
        db_id = self._books_id_map.get(item_id)
        values = self.books_tree.item(item_id, "values")
        return db_id, values

    def _show_add_book_dialog(self):
        """Show a dialog to add a new book."""
        dialog = tk.Toplevel(self)
        dialog.title("Add New Book")
        dialog.geometry("500x520")
        dialog.configure(bg=COLORS["bg_card"])
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="📖 Add New Book", font=FONT_HEADING,
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(pady=(20, 10))

        form = tk.Frame(dialog, bg=COLORS["bg_card"])
        form.pack(fill="both", padx=20)

        entries = {}
        fields = [("Title *", "title"), ("Author *", "author"), ("ISBN", "isbn"),
                  ("Publisher", "publisher"), ("Year", "year"),
                  ("Category", "category"), ("Quantity *", "quantity")]

        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label, font=FONT_BODY,
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
                row=i, column=0, sticky="w", padx=10, pady=8)
            e = tk.Entry(form, font=FONT_BODY, bg=COLORS["bg_input"],
                         fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                         relief="flat", width=30, highlightthickness=1,
                         highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"])
            e.grid(row=i, column=1, padx=10, pady=8, ipady=4)
            entries[key] = e

        entries["quantity"].insert(0, "1")

        def save():
            title = entries["title"].get().strip()
            author = entries["author"].get().strip()
            isbn = entries["isbn"].get().strip()
            publisher = entries["publisher"].get().strip()
            try:
                year = int(entries["year"].get().strip()) if entries["year"].get().strip() else None
            except ValueError:
                messagebox.showerror("Error", "Year must be a number.", parent=dialog)
                return
            category = entries["category"].get().strip()
            try:
                quantity = int(entries["quantity"].get().strip())
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a number.", parent=dialog)
                return

            if not title or not author:
                messagebox.showerror("Error", "Title and Author are required.", parent=dialog)
                return

            success, msg = db.add_book(title, author, isbn, publisher, year, category, quantity)
            if success:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self._refresh_books_table()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_card"])
        btn_frame.pack(pady=20)
        self._make_button(btn_frame, "💾 Save Book", save, COLORS["accent_green"]).pack(side="left", padx=5)
        self._make_button(btn_frame, "Cancel", dialog.destroy, COLORS["accent_red"], width=10).pack(side="left", padx=5)

    def _show_edit_book_dialog(self):
        """Show a dialog to edit the selected book."""
        db_id, values = self._get_selected_book_id()
        if db_id is None:
            messagebox.showwarning("Warning", "Please select a book to edit.")
            return

        book = db.get_book(db_id)
        if not book:
            messagebox.showerror("Error", "Book not found.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Edit Book")
        dialog.geometry("500x520")
        dialog.configure(bg=COLORS["bg_card"])
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="✏️ Edit Book", font=FONT_HEADING,
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(pady=(20, 10))

        form = tk.Frame(dialog, bg=COLORS["bg_card"])
        form.pack(fill="both", padx=20)

        entries = {}
        fields = [("Title *", "title"), ("Author *", "author"), ("ISBN", "isbn"),
                  ("Publisher", "publisher"), ("Year", "year"),
                  ("Category", "category"), ("Quantity *", "quantity")]

        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label, font=FONT_BODY,
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
                row=i, column=0, sticky="w", padx=10, pady=8)
            e = tk.Entry(form, font=FONT_BODY, bg=COLORS["bg_input"],
                         fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                         relief="flat", width=30, highlightthickness=1,
                         highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"])
            e.grid(row=i, column=1, padx=10, pady=8, ipady=4)
            val = book.get(key, "")
            if val is not None:
                e.insert(0, str(val))
            entries[key] = e

        def save():
            title = entries["title"].get().strip()
            author = entries["author"].get().strip()
            isbn = entries["isbn"].get().strip()
            publisher = entries["publisher"].get().strip()
            try:
                year = int(entries["year"].get().strip()) if entries["year"].get().strip() else None
            except ValueError:
                messagebox.showerror("Error", "Year must be a number.", parent=dialog)
                return
            category = entries["category"].get().strip()
            try:
                quantity = int(entries["quantity"].get().strip())
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a number.", parent=dialog)
                return
            if not title or not author:
                messagebox.showerror("Error", "Title and Author are required.", parent=dialog)
                return

            success, msg = db.update_book(db_id, title, author, isbn, publisher, year, category, quantity)
            if success:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self._refresh_books_table()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_card"])
        btn_frame.pack(pady=20)
        self._make_button(btn_frame, "💾 Update", save, COLORS["accent_blue"]).pack(side="left", padx=5)
        self._make_button(btn_frame, "Cancel", dialog.destroy, COLORS["accent_red"], width=10).pack(side="left", padx=5)

    def _delete_selected_book(self):
        """Delete the selected book after confirmation."""
        db_id, values = self._get_selected_book_id()
        if db_id is None:
            messagebox.showwarning("Warning", "Please select a book to delete.")
            return

        title = values[1]

        if messagebox.askyesno("Confirm Delete", f"Delete book '{title}'?\nThis action cannot be undone."):
            success, msg = db.delete_book(db_id)
            if success:
                messagebox.showinfo("Success", msg)
                self._refresh_books_table()
            else:
                messagebox.showerror("Error", msg)

    # ═══════════════════════════════════════════
    #  PAGE: MEMBERS MANAGEMENT
    # ═══════════════════════════════════════════
    def show_members(self):
        """Display the members management page."""
        self._clear_main()
        self._set_active_nav("Members")
        self._make_header(self.main_area, "👥 Members Management", "Manage library members")

        # ── Search Bar ──
        search_frame = tk.Frame(self.main_area, bg=COLORS["bg_main"])
        search_frame.pack(fill="x", padx=30, pady=(10, 0))

        self.member_search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame, textvariable=self.member_search_var,
            font=FONT_BODY, bg=COLORS["bg_input"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"], relief="flat", width=40,
            highlightthickness=1, highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )
        search_entry.pack(side="left", ipady=6, padx=(0, 10))
        search_entry.insert(0, "🔍 Search members...")
        search_entry.bind("<FocusIn>", lambda e: (search_entry.delete(0, "end") if search_entry.get().startswith("🔍") else None))
        search_entry.bind("<KeyRelease>", lambda e: self._refresh_members_table())

        btn_frame = tk.Frame(search_frame, bg=COLORS["bg_main"])
        btn_frame.pack(side="right")

        self._make_button(btn_frame, "➕ Add Member", self._show_add_member_dialog,
                          COLORS["accent_green"], width=14).pack(side="left", padx=4)
        self._make_button(btn_frame, "✏️ Edit", self._show_edit_member_dialog,
                          COLORS["accent_blue"], width=10).pack(side="left", padx=4)
        self._make_button(btn_frame, "🗑️ Delete", self._delete_selected_member,
                          COLORS["accent_red"], width=10).pack(side="left", padx=4)

        # ── Members Table ──
        table_card = self._make_card(self.main_area, expand=True)
        cols = ("S.No", "Name", "Email", "Phone", "Address", "Type", "Joined")
        self.members_tree = self._make_treeview(table_card, cols)
        self.members_tree.column("S.No", width=50)
        self.members_tree.column("Name", width=160)
        self.members_tree.column("Email", width=200)
        self.members_tree.column("Phone", width=120)
        self.members_tree.column("Address", width=180)
        self.members_tree.column("Type", width=80)
        self.members_tree.column("Joined", width=100)

        self._members_id_map = {}
        self._refresh_members_table()

    def _refresh_members_table(self):
        """Refresh the members table."""
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)

        keyword = self.member_search_var.get()
        if keyword.startswith("🔍"):
            keyword = ""
        members = db.search_members(keyword)

        self._members_id_map = {}
        for i, m in enumerate(members):
            sno = i + 1
            tag = "oddrow" if i % 2 else "evenrow"
            join_date = m["join_date"][:10] if m["join_date"] else ""
            item_id = self.members_tree.insert("", "end", values=(
                sno, m["name"], m["email"] or "", m["phone"] or "",
                m["address"] or "", m["member_type"], join_date
            ), tags=(tag,))
            self._members_id_map[item_id] = m["id"]

    def _get_selected_member_id(self):
        """Get the actual DB ID of the selected member."""
        selected = self.members_tree.selection()
        if not selected:
            return None, None
        item_id = selected[0]
        db_id = self._members_id_map.get(item_id)
        values = self.members_tree.item(item_id, "values")
        return db_id, values

    def _show_add_member_dialog(self):
        """Show dialog to add a new member."""
        dialog = tk.Toplevel(self)
        dialog.title("Add New Member")
        dialog.geometry("500x450")
        dialog.configure(bg=COLORS["bg_card"])
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="👤 Add New Member", font=FONT_HEADING,
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(pady=(20, 10))

        form = tk.Frame(dialog, bg=COLORS["bg_card"])
        form.pack(fill="both", padx=20)

        entries = {}
        fields = [("Name *", "name"), ("Email", "email"), ("Phone", "phone"),
                  ("Address", "address")]

        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label, font=FONT_BODY,
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
                row=i, column=0, sticky="w", padx=10, pady=8)
            e = tk.Entry(form, font=FONT_BODY, bg=COLORS["bg_input"],
                         fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                         relief="flat", width=30, highlightthickness=1,
                         highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"])
            e.grid(row=i, column=1, padx=10, pady=8, ipady=4)
            entries[key] = e

        # Member Type dropdown
        tk.Label(form, text="Type", font=FONT_BODY,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
            row=4, column=0, sticky="w", padx=10, pady=8)
        type_var = tk.StringVar(value="Student")
        type_combo = ttk.Combobox(form, textvariable=type_var,
                                  values=["Student", "Faculty", "Staff", "Guest"],
                                  font=FONT_BODY, state="readonly", width=28)
        type_combo.grid(row=4, column=1, padx=10, pady=8)

        def save():
            name = entries["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required.", parent=dialog)
                return
            email = entries["email"].get().strip()
            phone = entries["phone"].get().strip()
            address = entries["address"].get().strip()
            member_type = type_var.get()

            success, msg = db.add_member(name, email, phone, address, member_type)
            if success:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self._refresh_members_table()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_card"])
        btn_frame.pack(pady=20)
        self._make_button(btn_frame, "💾 Save", save, COLORS["accent_green"]).pack(side="left", padx=5)
        self._make_button(btn_frame, "Cancel", dialog.destroy, COLORS["accent_red"], width=10).pack(side="left", padx=5)

    def _show_edit_member_dialog(self):
        """Show dialog to edit the selected member."""
        db_id, values = self._get_selected_member_id()
        if db_id is None:
            messagebox.showwarning("Warning", "Please select a member to edit.")
            return

        member = db.get_member(db_id)
        if not member:
            messagebox.showerror("Error", "Member not found.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Edit Member")
        dialog.geometry("500x450")
        dialog.configure(bg=COLORS["bg_card"])
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="✏️ Edit Member", font=FONT_HEADING,
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(pady=(20, 10))

        form = tk.Frame(dialog, bg=COLORS["bg_card"])
        form.pack(fill="both", padx=20)

        entries = {}
        fields = [("Name *", "name"), ("Email", "email"), ("Phone", "phone"),
                  ("Address", "address")]

        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label, font=FONT_BODY,
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
                row=i, column=0, sticky="w", padx=10, pady=8)
            e = tk.Entry(form, font=FONT_BODY, bg=COLORS["bg_input"],
                         fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                         relief="flat", width=30, highlightthickness=1,
                         highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"])
            e.grid(row=i, column=1, padx=10, pady=8, ipady=4)
            val = member.get(key, "")
            if val:
                e.insert(0, str(val))
            entries[key] = e

        tk.Label(form, text="Type", font=FONT_BODY,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
            row=4, column=0, sticky="w", padx=10, pady=8)
        type_var = tk.StringVar(value=member.get("member_type", "Student"))
        type_combo = ttk.Combobox(form, textvariable=type_var,
                                  values=["Student", "Faculty", "Staff", "Guest"],
                                  font=FONT_BODY, state="readonly", width=28)
        type_combo.grid(row=4, column=1, padx=10, pady=8)

        def save():
            name = entries["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required.", parent=dialog)
                return

            success, msg = db.update_member(
                db_id, name, entries["email"].get().strip(),
                entries["phone"].get().strip(), entries["address"].get().strip(),
                type_var.get()
            )
            if success:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self._refresh_members_table()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_card"])
        btn_frame.pack(pady=20)
        self._make_button(btn_frame, "💾 Update", save, COLORS["accent_blue"]).pack(side="left", padx=5)
        self._make_button(btn_frame, "Cancel", dialog.destroy, COLORS["accent_red"], width=10).pack(side="left", padx=5)

    def _delete_selected_member(self):
        """Delete the selected member."""
        db_id, values = self._get_selected_member_id()
        if db_id is None:
            messagebox.showwarning("Warning", "Please select a member to delete.")
            return

        name = values[1]

        if messagebox.askyesno("Confirm Delete", f"Delete member '{name}'?\nThis action cannot be undone."):
            success, msg = db.delete_member(db_id)
            if success:
                messagebox.showinfo("Success", msg)
                self._refresh_members_table()
            else:
                messagebox.showerror("Error", msg)

    # ═══════════════════════════════════════════
    #  PAGE: ISSUE BOOK
    # ═══════════════════════════════════════════
    def show_issue(self):
        """Display the issue book page."""
        self._clear_main()
        self._set_active_nav("Issue Book")
        self._make_header(self.main_area, "📤 Issue Book", "Issue a book to a library member")

        card = self._make_card(self.main_area)

        form = tk.Frame(card, bg=COLORS["bg_card"])
        form.pack(fill="x", padx=20, pady=20)

        # ── Book Selection ──
        tk.Label(form, text="Select Book:", font=FONT_SUBHEADING,
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))

        tk.Label(form, text="Search Book", font=FONT_BODY,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
            row=1, column=0, sticky="w", padx=10, pady=5)

        book_search = tk.Entry(form, font=FONT_BODY, bg=COLORS["bg_input"],
                               fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                               relief="flat", width=40, highlightthickness=1,
                               highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"])
        book_search.grid(row=1, column=1, padx=10, pady=5, ipady=4)

        book_list_frame = tk.Frame(form, bg=COLORS["bg_card"])
        book_list_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        book_listbox = tk.Listbox(book_list_frame, font=FONT_BODY, bg=COLORS["bg_input"],
                                  fg=COLORS["text_primary"], selectbackground=COLORS["accent"],
                                  selectforeground="#ffffff",
                                  relief="flat", height=5, width=60,
                                  highlightthickness=1, highlightbackground=COLORS["border"],
                                  cursor="hand2")
        book_listbox.pack(fill="x")

        self._issue_books_data = db.search_books()
        for b in self._issue_books_data:
            status = f"(Avail: {b['available']}/{b['quantity']})"
            book_listbox.insert("end", f"[{b['id']}] {b['title']} - {b['author']} {status}")

        def filter_books(e):
            keyword = book_search.get().strip()
            book_listbox.delete(0, "end")
            self._issue_books_data = db.search_books(keyword)
            for b in self._issue_books_data:
                status = f"(Avail: {b['available']}/{b['quantity']})"
                book_listbox.insert("end", f"[{b['id']}] {b['title']} - {b['author']} {status}")

        book_search.bind("<KeyRelease>", filter_books)

        # Divider
        tk.Frame(form, bg=COLORS["accent"], height=1).grid(row=3, column=0, columnspan=2,
                                                            sticky="ew", padx=10, pady=15)

        # ── Member Selection ──
        tk.Label(form, text="Select Member:", font=FONT_SUBHEADING,
                 bg=COLORS["bg_card"], fg=COLORS["accent"]).grid(
            row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))

        tk.Label(form, text="Search Member", font=FONT_BODY,
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).grid(
            row=5, column=0, sticky="w", padx=10, pady=5)

        member_search = tk.Entry(form, font=FONT_BODY, bg=COLORS["bg_input"],
                                 fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                                 relief="flat", width=40, highlightthickness=1,
                                 highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"])
        member_search.grid(row=5, column=1, padx=10, pady=5, ipady=4)

        member_list_frame = tk.Frame(form, bg=COLORS["bg_card"])
        member_list_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        member_listbox = tk.Listbox(member_list_frame, font=FONT_BODY, bg=COLORS["bg_input"],
                                    fg=COLORS["text_primary"], selectbackground=COLORS["accent"],
                                    selectforeground="#ffffff",
                                    relief="flat", height=4, width=60,
                                    highlightthickness=1, highlightbackground=COLORS["border"],
                                    cursor="hand2")
        member_listbox.pack(fill="x")

        self._issue_members_data = db.search_members()
        for m in self._issue_members_data:
            member_listbox.insert("end", f"[{m['id']}] {m['name']} ({m['member_type']}) - {m['phone'] or 'N/A'}")

        def filter_members(e):
            keyword = member_search.get().strip()
            member_listbox.delete(0, "end")
            self._issue_members_data = db.search_members(keyword)
            for m in self._issue_members_data:
                member_listbox.insert("end", f"[{m['id']}] {m['name']} ({m['member_type']}) - {m['phone'] or 'N/A'}")

        member_search.bind("<KeyRelease>", filter_members)

        # ── Issue Button ──
        def issue():
            book_sel = book_listbox.curselection()
            member_sel = member_listbox.curselection()

            if not book_sel:
                messagebox.showwarning("Warning", "Please select a book.")
                return
            if not member_sel:
                messagebox.showwarning("Warning", "Please select a member.")
                return

            book = self._issue_books_data[book_sel[0]]
            member = self._issue_members_data[member_sel[0]]

            if messagebox.askyesno("Confirm Issue",
                                   f"Issue '{book['title']}' to {member['name']}?"):
                success, msg = db.issue_book(book["id"], member["id"])
                if success:
                    messagebox.showinfo("Success", msg)
                    self.show_issue()  # Refresh
                else:
                    messagebox.showerror("Error", msg)

        btn_frame = tk.Frame(card, bg=COLORS["bg_card"])
        btn_frame.pack(pady=(5, 20))
        self._make_button(btn_frame, "📤 Issue Book", issue,
                          COLORS["accent_green"], width=18).pack()

    # ═══════════════════════════════════════════
    #  PAGE: RETURN BOOK
    # ═══════════════════════════════════════════
    def show_return(self):
        """Display the return book page with overdue warnings."""
        self._clear_main()
        self._set_active_nav("Return Book")
        self._make_header(self.main_area, "📥 Return Book", "Return an issued book and calculate fines")

        # Info banner for overdue
        overdue_count = db.get_dashboard_stats()["overdue_books"]
        if overdue_count > 0:
            warning_frame = tk.Frame(self.main_area, bg=COLORS["overdue_bg"],
                                     highlightbackground=COLORS["accent_red"], highlightthickness=1)
            warning_frame.pack(fill="x", padx=30, pady=(5, 0))
            tk.Label(warning_frame,
                     text=f"  ⚠️  {overdue_count} book(s) are OVERDUE! Fines accumulating at ₹{db.FINE_PER_DAY}/day.",
                     font=("Segoe UI", 11, "bold"), bg=COLORS["overdue_bg"],
                     fg=COLORS["accent_red"], anchor="w", pady=8, padx=10).pack(fill="x")

        card = self._make_card(self.main_area, expand=True)

        tk.Label(card, text="Currently Issued Books", font=FONT_SUBHEADING,
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(
            anchor="w", padx=15, pady=(15, 5))

        cols = ("S.No", "Book", "Member", "Issue Date", "Due Date", "Status", "Est. Fine")
        self.return_tree = self._make_treeview(card, cols)
        self.return_tree.column("S.No", width=50)
        self.return_tree.column("Book", width=200)
        self.return_tree.column("Member", width=140)
        self.return_tree.column("Issue Date", width=100)
        self.return_tree.column("Due Date", width=100)
        self.return_tree.column("Status", width=90)
        self.return_tree.column("Est. Fine", width=80)

        issued = db.get_issued_books()
        today = datetime.now().strftime("%Y-%m-%d")
        self._return_txn_ids = {}
        for i, txn in enumerate(issued):
            is_overdue = txn["due_date"] < today
            tag = "overdue" if is_overdue else ("oddrow" if i % 2 else "evenrow")
            status = "⚠️ OVERDUE" if is_overdue else "✅ Active"

            fine_str = "—"
            if is_overdue:
                due = datetime.strptime(txn["due_date"], "%Y-%m-%d")
                days_over = (datetime.now() - due).days
                fine_str = f"₹{days_over * db.FINE_PER_DAY:.0f}"

            item_id = self.return_tree.insert("", "end", values=(
                i + 1, txn["book_title"][:35], txn["member_name"],
                txn["issue_date"], txn["due_date"], status, fine_str
            ), tags=(tag,))
            self._return_txn_ids[item_id] = txn["txn_id"]

        # Return Button
        btn_frame = tk.Frame(card, bg=COLORS["bg_card"])
        btn_frame.pack(pady=15)

        def return_selected():
            selected = self.return_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a transaction to return.")
                return

            item_id = selected[0]
            txn_id = self._return_txn_ids.get(item_id)
            values = self.return_tree.item(item_id, "values")
            book = values[1]
            member = values[2]

            if messagebox.askyesno("Confirm Return",
                                   f"Return '{book}' from {member}?"):
                success, msg, fine = db.return_book(txn_id)
                if success:
                    messagebox.showinfo("Success", msg)
                    self.show_return()  # Refresh
                else:
                    messagebox.showerror("Error", msg)

        self._make_button(btn_frame, "📥 Return Selected Book", return_selected,
                          COLORS["accent_blue"], width=22).pack()

    # ═══════════════════════════════════════════
    #  PAGE: TRANSACTION HISTORY
    # ═══════════════════════════════════════════
    def show_transactions(self):
        """Display all transactions."""
        self._clear_main()
        self._set_active_nav("Transactions")
        self._make_header(self.main_area, "📋 Transaction History", "Complete record of all issues and returns")

        card = self._make_card(self.main_area, expand=True)
        cols = ("S.No", "Book", "Member", "Issue Date", "Due Date", "Return Date", "Fine (₹)", "Status")
        tree = self._make_treeview(card, cols)
        tree.column("S.No", width=50)
        tree.column("Book", width=200)
        tree.column("Member", width=130)
        tree.column("Issue Date", width=90)
        tree.column("Due Date", width=90)
        tree.column("Return Date", width=90)
        tree.column("Fine (₹)", width=70)
        tree.column("Status", width=80)

        transactions = db.get_all_transactions()
        for i, txn in enumerate(transactions):
            tag = "oddrow" if i % 2 else "evenrow"
            tree.insert("", "end", values=(
                i + 1, txn["book_title"][:30], txn["member_name"],
                txn["issue_date"], txn["due_date"],
                txn["return_date"] or "—",
                f"₹{txn['fine']:.0f}" if txn["fine"] else "—",
                txn["status"]
            ), tags=(tag,))

    # ═══════════════════════════════════════════
    #  PAGE: OVERDUE BOOKS
    # ═══════════════════════════════════════════
    def show_overdue(self):
        """Display overdue books with return option."""
        self._clear_main()
        self._set_active_nav("Overdue")
        self._make_header(self.main_area, "⚠️ Overdue Books", "Books that are past their due date")

        card = self._make_card(self.main_area, expand=True)
        cols = ("S.No", "Book", "Member", "Issue Date", "Due Date", "Days Overdue", "Est. Fine")
        tree = self._make_treeview(card, cols)
        tree.column("S.No", width=50)
        tree.column("Book", width=200)
        tree.column("Member", width=140)
        tree.column("Issue Date", width=100)
        tree.column("Due Date", width=100)
        tree.column("Days Overdue", width=100)
        tree.column("Est. Fine", width=80)

        overdue = db.get_overdue_books()

        if not overdue:
            tk.Label(card, text="✅ No overdue books! All books are returned on time.",
                     font=FONT_HEADING, bg=COLORS["bg_card"],
                     fg=COLORS["accent_green"]).pack(pady=50)
        else:
            self._overdue_txn_ids = {}
            for i, txn in enumerate(overdue):
                days = int(txn["overdue_days"])
                fine = days * db.FINE_PER_DAY
                tag = "overdue"
                item_id = tree.insert("", "end", values=(
                    i + 1, txn["book_title"][:35], txn["member_name"],
                    txn["issue_date"], txn["due_date"],
                    f"{days} days", f"₹{fine:.0f}"
                ), tags=(tag,))
                self._overdue_txn_ids[item_id] = txn["txn_id"]

            # Summary + Return button
            bottom_frame = tk.Frame(card, bg=COLORS["bg_card"])
            bottom_frame.pack(fill="x", padx=15, pady=10)

            total_fine = sum(int(t["overdue_days"]) * db.FINE_PER_DAY for t in overdue)
            tk.Label(bottom_frame,
                     text=f"Total overdue: {len(overdue)} books  •  Estimated fines: ₹{total_fine:.0f}",
                     font=FONT_BODY, bg=COLORS["bg_card"],
                     fg=COLORS["accent_red"]).pack(side="left")

            def return_overdue():
                selected = tree.selection()
                if not selected:
                    messagebox.showwarning("Warning", "Please select an overdue book to return.")
                    return

                item_id = selected[0]
                txn_id = self._overdue_txn_ids.get(item_id)
                values = tree.item(item_id, "values")
                book = values[1]
                member = values[2]

                if messagebox.askyesno("Confirm Return",
                                       f"Return overdue book '{book}' from {member}?\n"
                                       f"Fine will be calculated automatically."):
                    success, msg, fine = db.return_book(txn_id)
                    if success:
                        messagebox.showinfo("Book Returned", msg)
                        self.show_overdue()  # Refresh
                    else:
                        messagebox.showerror("Error", msg)

            self._make_button(bottom_frame, "📥 Return Selected", return_overdue,
                              COLORS["accent_red"], width=18).pack(side="right")


# ─────────────────────────────────────────────
#  APPLICATION ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
