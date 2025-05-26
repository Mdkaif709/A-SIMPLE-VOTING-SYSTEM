import tkinter as tk
from tkinter import ttk, messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Data Setup ---
candidates = {
    1: "Jagan",
    2: "Pavan",
    3: "CBN"
}

areas = [
    "Kadapa", "PDTR", "Madanapalle", "Nellore", "Kurnool", "Srikakulam",
    "Vizag", "Guntur", "Vijayawada", "Anantapur", "Tirupati", "Chittoor",
    "Rajahmundry", "Eluru", "Ongole", "Machilipatnam", "Kakinada"
]

users = {}
old_people = []
user_votes = {}
votes = {1: 0, 2: 0, 3: 0}
default_password = "1234"

# Generate 100 users and simulate votes
for i in range(1, 101):
    age = random.randint(10, 100)
    area = random.choice(areas)
    eligible = age >= 18
    voted = False
    voted_for = None
    if age >= 60:
        old_people.append({
            "name": f"User{i}",
            "age": age,
            "address": area
        })
    if eligible:
        if random.random() < 0.6:
            voted_for = 1
        else:
            voted_for = random.choice([2, 3])
        votes[voted_for] += 1
        user_votes[i] = voted_for
        voted = True
    users[i] = {
        "name": f"User{i}",
        "password": default_password,
        "address": area,
        "age": age,
        "eligible": eligible,
        "voted": voted,
        "voted_for": voted_for
    }

# --- Helper Functions ---
def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f'{width}x{height}+{x}+{y}')

# --- Pie Chart Function ---
def create_pie_chart(votes):
    vote_counts = [votes[1], votes[2], votes[3]]
    labels = [candidates[1], candidates[2], candidates[3]]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(vote_counts, labels=labels, autopct='%1.1f%%', startangle=90,
           colors=['#3498db', '#e74c3c', '#2ecc71'])
    ax.axis('equal')
    return fig

# --- GUI Functions ---
def validate_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    if not username.startswith("User") or not username[4:].isdigit():
        messagebox.showerror("Error", "Username must be in format: User1, User2, etc.")
        return
    try:
        user_id = int(username.replace("User", ""))
        if user_id in users and users[user_id]["password"] == password:
            open_results_interface(user_id)
        else:
            messagebox.showerror("Error", "Incorrect username or password.")
    except:
        messagebox.showerror("Error", "Invalid user ID.")

def clear_fields():
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

def on_enter_key(event=None):
    validate_login()

def logout(result_window):
    result_window.destroy()
    clear_fields()
    root.deiconify()

def open_results_interface(user_id):
    root.withdraw()
    result_window = tk.Toplevel()
    result_window.title("Andhra Pradesh Voting Results")
    center_window(result_window, 1100, 750)
    result_window.configure(bg="#f1f6ff")

    # Title
    tk.Label(result_window, text="Election Commission of India - Andhra Pradesh Voting Results",
             font=("Helvetica", 18, "bold"), bg="#1c2b4d", fg="white",
             pady=10).pack(fill="x")
    tk.Label(result_window, text=f"Welcome, {users[user_id]['name']}",
             font=("Arial", 14, "bold"), bg="#f1f6ff").pack(pady=10)

    # Scrollable Frame
    content_frame = tk.Frame(result_window, bg="#f1f6ff")
    content_frame.pack(fill="both", expand=True, padx=20)
    canvas = tk.Canvas(content_frame, bg="#f1f6ff", highlightthickness=0)
    scrollbar = ttk.Scrollbar(content_frame, orient="vertical",
                              command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f1f6ff")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Result Summary
    winner = max(votes, key=votes.get)
    winning_name = candidates[winner]
    result_text = f"Winner: {winning_name} with {votes[winner]} votes\n"
    winning_areas = set()
    for uid, cid in user_votes.items():
        if cid == winner:
            winning_areas.add(users[uid]["address"])
    area_text = f"{winning_name} won in the following area(s):\n" + \
                '\n'.join(f"• {area}" for area in sorted(winning_areas))
    tk.Label(scrollable_frame, text=result_text, font=("Arial", 14),
             justify="left", anchor="w", bg="#f1f6ff", fg="#0d3b66").pack(anchor="w", pady=(10, 0))
    tk.Label(scrollable_frame, text=area_text, font=("Arial", 12),
             justify="left", anchor="w", bg="#f1f6ff", fg="#333").pack(anchor="w", pady=(0, 10))

    # Pie Chart
    fig = create_pie_chart(votes)
    canvas_widget = FigureCanvasTkAgg(fig, master=scrollable_frame)
    canvas_widget.draw()
    canvas_widget.get_tk_widget().pack(pady=20)

    # --- Toggle Table Selection ---
    def show_voter_summary():
        senior_frame.pack_forget()
        voter_frame.pack(fill="both", expand=True)

    def show_senior_citizens():
        voter_frame.pack_forget()
        senior_frame.pack(fill="both", expand=True)

    toggle_frame = tk.Frame(scrollable_frame, bg="#f1f6ff")
    toggle_frame.pack(pady=10)
    tk.Label(toggle_frame, text="Select Data to View:", font=("Arial", 12, "bold"),
             bg="#f1f6ff").pack(side="left", padx=10)
    tk.Button(toggle_frame, text="Voter Summary", command=show_voter_summary,
              bg="#3498db", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
    tk.Button(toggle_frame, text="Senior Citizens", command=show_senior_citizens,
              bg="#2ecc71", fg="white", font=("Arial", 12)).pack(side="left", padx=5)

    # --- Voter Summary Table ---
    voter_frame = tk.Frame(scrollable_frame, bg="#f1f6ff")
    table_label = tk.Label(voter_frame, text="Voter Summary", font=("Arial", 14, "bold"),
                           bg="#f1f6ff", fg="#0d3b66")
    table_label.pack(pady=5)
    table_inner_frame = tk.Frame(voter_frame, bg="#f1f6ff")
    table_inner_frame.pack(fill="both", expand=True)
    cols = ("Name", "Age", "Address", "Eligible", "Voted For")
    tree = ttk.Treeview(table_inner_frame, columns=cols, show="headings", height=12)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")
    for uid, u in users.items():
        tree.insert("", "end", values=(
            u["name"], u["age"], u["address"],
            "Yes" if u["eligible"] else "No",
            candidates[u["voted_for"]] if u["voted"] else "No"
        ))
    scrollbar_y = ttk.Scrollbar(table_inner_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar_y.set)
    scrollbar_y.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)

    # --- Senior Citizens Table ---
    senior_frame = tk.Frame(scrollable_frame, bg="#f1f6ff")
    senior_label = tk.Label(senior_frame, text="Senior Citizens (Age 60+)",
                            font=("Arial", 14, "bold"), bg="#f1f6ff", fg="#0d3b66")
    senior_label.pack(pady=(10, 5))
    senior_inner_frame = tk.Frame(senior_frame, bg="#f1f6ff")
    senior_inner_frame.pack(fill="both", expand=True)
    senior_cols = ("Name", "Age", "Address")
    senior_tree = ttk.Treeview(senior_inner_frame, columns=senior_cols, show="headings", height=10)
    for col in senior_cols:
        senior_tree.heading(col, text=col)
        senior_tree.column(col, anchor="center", width=180)
    for person in old_people:
        senior_tree.insert("", "end", values=(person["name"], person["age"], person["address"]))
    senior_scrollbar_y = ttk.Scrollbar(senior_inner_frame, orient="vertical", command=senior_tree.yview)
    senior_tree.configure(yscroll=senior_scrollbar_y.set)
    senior_scrollbar_y.pack(side="right", fill="y")
    senior_tree.pack(fill="both", expand=True)

    # Initially show voter summary
    show_voter_summary()

    # Logout Button
    logout_button = tk.Button(result_window, text="Logout", command=lambda: logout(result_window),
                              bg="#f1f6ff", fg="#0d3b66", font=("Arial", 14))
    logout_button.pack(pady=20)

# --- Main Login Window ---
root = tk.Tk()
root.title("Voting System - Login")
center_window(root, 400, 350)
root.configure(bg="#f1f6ff")

# Login Interface
tk.Label(root, text="Login to View Results", font=("Helvetica", 18, "bold"),
         bg="#f1f6ff", fg="#0d3b66").pack(pady=20)
username_label = tk.Label(root, text="Username", font=("Arial", 12),
                          bg="#f1f6ff", fg="#333")
username_label.pack(pady=(10, 5))
username_entry = tk.Entry(root, font=("Arial", 14), width=25)
username_entry.pack(pady=(0, 5))
password_label = tk.Label(root, text="Password", font=("Arial", 12),
                          bg="#f1f6ff", fg="#333")
password_label.pack(pady=(0, 5))
password_entry = tk.Entry(root, font=("Arial", 14), show="*", width=25)
password_entry.pack(pady=(0, 20))
show_pass_var = tk.BooleanVar()


def toggle_password():
    password_entry.config(show="" if show_pass_var.get() else "*")


show_pass_check = tk.Checkbutton(root, text="Show Password",
                                 variable=show_pass_var, command=toggle_password, bg="#f1f6ff", fg="#0d3b66",
                                 font=("Arial", 10))
show_pass_check.pack()
login_button = tk.Button(root, text="Login", command=validate_login,
                         bg="#3498db", fg="white", font=("Arial", 14), width=20)
login_button.pack(pady=10)
clear_button = tk.Button(root, text="Clear", command=clear_fields,
                         bg="#f1f6ff", fg="#0d3b66", font=("Arial", 14))
clear_button.pack(pady=5)
root.bind('<Return>', on_enter_key)

root.mainloop()
