import tkinter as tk
from tkinter import ttk, messagebox
import random
import sqlite3
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DB_NAME = "voting.db"
DEFAULT_PASSWORD = "1234"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("DROP TABLE IF EXISTS users")
    except:
        pass
    c.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        age INTEGER NOT NULL,
        address TEXT NOT NULL,
        eligible INTEGER NOT NULL DEFAULT 0,
        voted_for INTEGER NOT NULL DEFAULT 0,
        is_senior_citizen INTEGER NOT NULL DEFAULT 0
    )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_users_eligible ON users(eligible)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_users_voted_for ON users(voted_for)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_users_senior ON users(is_senior_citizen)")
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def seed_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        conn.close()
        print("ℹ️ Database already contains data")
        return
    areas = ["Kadapa", "PDTR", "Madanapalle", "Nellore", "Kurnool", "Vizag", "Guntur", "Vijayawada", "Tirupati", "Anantapur"]
    print("📊 Seeding database with 100 users...")
    for i in range(1, 101):
        age = random.randint(10, 90)
        area = random.choice(areas)
        eligible = 1 if age >= 18 else 0
        is_senior = 1 if age >= 60 else 0
        voted_for = 0
        if eligible:
            voted_for = random.choices([1, 2, 3], weights=[60, 25, 15], k=1)[0]
        c.execute("INSERT INTO users (id, name, password, age, address, eligible, voted_for, is_senior_citizen) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (i, f"User{i}", DEFAULT_PASSWORD, age, area, eligible, voted_for, is_senior))
    conn.commit()
    conn.close()
    print("✅ Database seeded successfully!")

def center_window(win, w, h):
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def get_vote_counts():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    counts = {1: 0, 2: 0, 3: 0}
    c.execute("SELECT voted_for FROM users WHERE voted_for != 0")
    for (v,) in c.fetchall():
        counts[v] += 1
    conn.close()
    return counts

def get_voting_statistics():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE eligible = 1")
    eligible = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE voted_for != 0")
    voted = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_senior_citizen = 1")
    senior = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_senior_citizen = 1 AND voted_for != 0")
    senior_voted = c.fetchone()[0]
    conn.close()
    return {
        'total_users': total,
        'eligible_voters': eligible,
        'votes_cast': voted,
        'turnout_percentage': (voted / eligible * 100) if eligible > 0 else 0,
        'senior_citizens': senior,
        'senior_voted': senior_voted
    }

def create_pie_chart(votes):
    fig, ax = plt.subplots(figsize=(5, 5))
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    ax.pie(votes.values(), labels=["Jagan", "Pavan", "CBN"], autopct="%1.1f%%", startangle=90, colors=colors, explode=(0.05, 0.05, 0.05), shadow=True)
    ax.axis("equal")
    ax.set_title("Vote Distribution", fontsize=14, fontweight='bold')
    return fig

def validate_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    if not username.startswith("User") or not username[4:].isdigit():
        messagebox.showerror("Error", "Username must be User1, User2, etc.")
        return
    user_id = int(username.replace("User", ""))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=? AND password=?", (user_id, password))
    user = c.fetchone()
    conn.close()
    if user:
        open_results()
    else:
        messagebox.showerror("Login Failed", "Wrong username or password!")

def on_enter_key(event):
    validate_login()

def open_results():
    root.withdraw()
    win = tk.Toplevel()
    win.title("Voting Results - Election Commission of India")
    center_window(win, 1200, 800)
    win.configure(bg='#f0f0f0')
    win.resizable(True, True)

    main_canvas = tk.Canvas(win, bg='#f0f0f0', highlightthickness=0)
    main_canvas.pack(side="left", fill="both", expand=True)
    main_scrollbar = ttk.Scrollbar(win, orient="vertical", command=main_canvas.yview)
    main_scrollbar.pack(side="right", fill="y")
    main_canvas.configure(yscrollcommand=main_scrollbar.set)
    content_frame = tk.Frame(main_canvas, bg='#f0f0f0')
    canvas_window = main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def configure_scroll(event=None):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        main_canvas.itemconfig(canvas_window, width=main_canvas.winfo_width())

    content_frame.bind("<Configure>", configure_scroll)
    main_canvas.bind("<Configure>", configure_scroll)

    def on_mousewheel(event):
        main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    main_canvas.bind("<Enter>", lambda e: main_canvas.bind_all("<MouseWheel>", on_mousewheel))
    main_canvas.bind("<Leave>", lambda e: main_canvas.unbind_all("<MouseWheel>"))

    header_frame = tk.Frame(content_frame, bg='#2c3e50', height=70)
    header_frame.pack(fill='x')
    header_frame.pack_propagate(False)
    tk.Label(header_frame, text="🗳️ Election Commission of India - AP Results", font=("Arial", 20, "bold"), bg='#2c3e50', fg='white').pack(pady=20)

    stats = get_voting_statistics()
    stats_frame = tk.Frame(content_frame, bg='#ecf0f1', height=50)
    stats_frame.pack(fill='x', pady=10, padx=20)
    stats_frame.pack_propagate(False)
    stats_text = f"Total Users: {stats['total_users']} | Eligible: {stats['eligible_voters']} | Voted: {stats['votes_cast']} | Turnout: {stats['turnout_percentage']:.1f}% | Seniors: {stats['senior_citizens']}"
    tk.Label(stats_frame, text=stats_text, font=("Arial", 12, "bold"), bg='#ecf0f1', fg='#2c3e50').pack(pady=12)

    chart_frame = tk.Frame(content_frame, bg='white', relief='solid', borderwidth=1)
    chart_frame.pack(fill='x', padx=20, pady=10)
    votes = get_vote_counts()
    fig = create_pie_chart(votes)
    canvas_chart = FigureCanvasTkAgg(fig, chart_frame)
    canvas_chart.draw()
    canvas_chart.get_tk_widget().pack(pady=10)

    summary_frame = tk.Frame(content_frame, bg='#f0f0f0')
    summary_frame.pack(fill='x', padx=20, pady=10)
    candidates = [("Jagan", votes[1], '#FF6B6B'), ("Pavan", votes[2], '#4ECDC4'), ("CBN", votes[3], '#45B7D1')]
    for name, count, color in candidates:
        card = tk.Frame(summary_frame, bg=color, relief='raised', borderwidth=2)
        card.pack(side='left', expand=True, fill='both', padx=10, pady=5)
        tk.Label(card, text=name, font=("Arial", 16, "bold"), bg=color, fg='white').pack(pady=10)
        tk.Label(card, text=f"{count} Votes", font=("Arial", 14), bg=color, fg='white').pack(pady=5)
        percentage = (count / sum(votes.values()) * 100) if sum(votes.values()) > 0 else 0
        tk.Label(card, text=f"{percentage:.1f}%", font=("Arial", 12, "bold"), bg=color, fg='white').pack(pady=10)

    table_frame = tk.Frame(content_frame, bg='#f0f0f0')
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)
    tk.Label(table_frame, text="📋 Complete Voter Details", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=10)
    table_container = tk.Frame(table_frame, bg='white', relief='solid', borderwidth=2, height=400)
    table_container.pack(fill="both", expand=True)
    table_container.pack_propagate(False)

    cols = ("ID", "Name", "Age", "Area", "Eligible", "Senior", "Voted For")
    tree = ttk.Treeview(table_container, columns=cols, show="headings", selectmode='browse')
    table_v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    table_v_scrollbar.pack(side="right", fill="y")
    table_h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)
    table_h_scrollbar.pack(side="bottom", fill="x")
    tree.configure(yscrollcommand=table_v_scrollbar.set, xscrollcommand=table_h_scrollbar.set)

    tree.column("ID", width=70, anchor="center")
    tree.column("Name", width=130, anchor="center")
    tree.column("Age", width=80, anchor="center")
    tree.column("Area", width=150, anchor="center")
    tree.column("Eligible", width=110, anchor="center")
    tree.column("Senior", width=130, anchor="center")
    tree.column("Voted For", width=130, anchor="center")
    for col in cols:
        tree.heading(col, text=col, anchor="center")

    # FIXED: Changed table header styling for maximum visibility
    style = ttk.Style()
    style.theme_use('clam')  # Use clam theme for better control
    
    # Main table row styling
    style.configure("Treeview", 
                    background="white", 
                    foreground="black", 
                    rowheight=28, 
                    font=('Arial', 10),
                    fieldbackground="white")
    style.map('Treeview', background=[('selected', '#3498db')], 
              foreground=[('selected', 'white')])
    
    # Table header styling with high contrast
    style.configure("Treeview.Heading", 
                    font=('Arial', 12, 'bold'), 
                    background='#2c3e50',  # Dark blue-gray background
                    foreground='#ffffff',   # Pure white text
                    relief='raised',
                    borderwidth=3,
                    padding=5)
    style.map("Treeview.Heading",
              background=[('active', '#34495e')],
              foreground=[('active', '#ffffff')],
              relief=[('active', 'sunken')])

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, age, address, eligible, is_senior_citizen, voted_for FROM users ORDER BY id")
    row_count = 0
    for row in c.fetchall():
        tags = ('evenrow',) if row_count % 2 == 0 else ('oddrow',)
        tree.insert("", "end", values=(row[0], row[1], row[2], row[3], "✓ Yes" if row[4] else "✗ No", "👴 Yes" if row[5] else "✗ No", ["-", "Jagan", "Pavan", "CBN"][row[6]]), tags=tags)
        row_count += 1
    conn.close()
    tree.tag_configure('evenrow', background='#f8f9fa')
    tree.tag_configure('oddrow', background='white')
    tree.pack(fill="both", expand=True, side="left")

    senior_frame = tk.Frame(content_frame, bg='#f0f0f0')
    senior_frame.pack(fill="both", expand=True, padx=20, pady=10)
    senior_header = tk.Frame(senior_frame, bg='#9b59b6', height=50)
    senior_header.pack(fill='x')
    senior_header.pack_propagate(False)
    tk.Label(senior_header, text="👴 Senior Citizens (Age 60+)", font=("Arial", 16, "bold"), bg='#9b59b6', fg='white').pack(pady=12)

    senior_stats_frame = tk.Frame(senior_frame, bg='#e8daef', height=40)
    senior_stats_frame.pack(fill='x')
    senior_stats_frame.pack_propagate(False)
    senior_stats_text = f"Total: {stats['senior_citizens']} | Voted: {stats['senior_voted']} | Turnout: {(stats['senior_voted']/stats['senior_citizens']*100 if stats['senior_citizens'] > 0 else 0):.1f}%"
    tk.Label(senior_stats_frame, text=senior_stats_text, font=("Arial", 11, "bold"), bg='#e8daef', fg='#6c3483').pack(pady=10)

    senior_container = tk.Frame(senior_frame, bg='white', relief='solid', borderwidth=2, height=300)
    senior_container.pack(fill="both", expand=True, pady=10)
    senior_container.pack_propagate(False)
    senior_cols = ("ID", "Name", "Age", "Area", "Voted For")
    senior_tree = ttk.Treeview(senior_container, columns=senior_cols, show="headings", selectmode='browse')
    senior_v = ttk.Scrollbar(senior_container, orient="vertical", command=senior_tree.yview)
    senior_v.pack(side="right", fill="y")
    senior_h = ttk.Scrollbar(senior_container, orient="horizontal", command=senior_tree.xview)
    senior_h.pack(side="bottom", fill="x")
    senior_tree.configure(yscrollcommand=senior_v.set, xscrollcommand=senior_h.set)

    senior_tree.column("ID", width=100, anchor="center")
    senior_tree.column("Name", width=150, anchor="center")
    senior_tree.column("Age", width=100, anchor="center")
    senior_tree.column("Area", width=180, anchor="center")
    senior_tree.column("Voted For", width=150, anchor="center")
    for col in senior_cols:
        senior_tree.heading(col, text=col, anchor="center")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, age, address, voted_for FROM users WHERE is_senior_citizen = 1 ORDER BY age DESC")
    senior_row = 0
    for row in c.fetchall():
        tags = ('senior_even',) if senior_row % 2 == 0 else ('senior_odd',)
        senior_tree.insert("", "end", values=(row[0], row[1], f"{row[2]} years", row[3], ["-", "Jagan", "Pavan", "CBN"][row[4]]), tags=tags)
        senior_row += 1
    conn.close()
    senior_tree.tag_configure('senior_even', background='#f4ecf7')
    senior_tree.tag_configure('senior_odd', background='#ebdef0')
    senior_tree.pack(fill="both", expand=True, side="left")

    button_frame = tk.Frame(content_frame, bg='#f0f0f0', height=90)
    button_frame.pack(fill='x', pady=20)
    button_frame.pack_propagate(False)
    button_container = tk.Frame(button_frame, bg='#f0f0f0')
    button_container.pack(expand=True)

    tk.Button(button_container, text="🔄 Refresh Data", command=lambda: refresh_results(win), font=("Arial", 13, "bold"), bg='#27ae60', fg='white', padx=50, pady=15, cursor='hand2', relief='raised', borderwidth=3, activebackground='#229954').pack(side="left", padx=20)
    tk.Button(button_container, text="🚪 Logout", command=lambda: logout(win), font=("Arial", 13, "bold"), bg='#e74c3c', fg='white', padx=50, pady=15, cursor='hand2', relief='raised', borderwidth=3, activebackground='#c0392b').pack(side="left", padx=20)

    content_frame.update_idletasks()
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))

def refresh_results(win):
    logout(win)
    open_results()

def logout(win):
    win.destroy()
    root.deiconify()
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    username_entry.focus()

if __name__ == "__main__":
    print("=" * 60)
    print("VOTING MANAGEMENT SYSTEM")
    print("=" * 60)
    init_db()
    seed_data()
    print("\n" + "=" * 60)
    print("✅ APPLICATION READY!")
    print("Login: User1 to User100 | Password: 1234")
    print("=" * 60 + "\n")

    root = tk.Tk()
    root.title("Voting System Login")
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    center_window(root, 450, 350)
    root.configure(bg='#ecf0f1')
    root.update()
    root.deiconify()

    tk.Label(root, text="🗳️ Voting System", font=("Arial", 22, "bold"), bg='#ecf0f1', fg='#2c3e50').pack(pady=20)
    tk.Label(root, text="Login to View Results", font=("Arial", 14), bg='#ecf0f1', fg='#7f8c8d').pack(pady=5)

    form_frame = tk.Frame(root, bg='#ecf0f1')
    form_frame.pack(pady=20)
    tk.Label(form_frame, text="Username:", font=("Arial", 12), bg='#ecf0f1').grid(row=0, column=0, sticky='w', pady=10)
    username_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
    username_entry.grid(row=0, column=1, pady=10, padx=10)
    username_entry.bind('<Return>', on_enter_key)
    username_entry.focus()

    tk.Label(form_frame, text="Password:", font=("Arial", 12), bg='#ecf0f1').grid(row=1, column=0, sticky='w', pady=10)
    password_entry = tk.Entry(form_frame, show="●", font=("Arial", 12), width=25)
    password_entry.grid(row=1, column=1, pady=10, padx=10)
    password_entry.bind('<Return>', on_enter_key)

    tk.Button(root, text="🔐 Login", width=20, font=("Arial", 12, "bold"), command=validate_login, bg='#3498db', fg='white', padx=10, pady=8, cursor='hand2').pack(pady=15)
    tk.Label(root, text="Credentials: User1-User100 | Password: 1234", font=("Arial", 9), bg='#ecf0f1', fg='#95a5a6').pack(pady=5)

    root.mainloop()
    
