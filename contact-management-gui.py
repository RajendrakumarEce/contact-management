import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ContactManager:
    def __init__(self, master):
        self.master = master
        self.master.title("Contact Management System")
        self.master.geometry("600x400")
        self.master.configure(bg='#f0f0f0')

        self.create_db()
        self.create_widgets()

    def create_db(self):
        self.conn = sqlite3.connect('contacts.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS contacts
                         (id INTEGER PRIMARY KEY,
                          name TEXT,
                          phone TEXT,
                          email TEXT,
                          address TEXT)''')
        self.conn.commit()

    def create_widgets(self):
        # Notebook for different sections
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add Contact Tab
        self.add_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_frame, text="Add Contact")
        self.create_add_widgets()

        # View Contacts Tab
        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="View Contacts")
        self.create_view_widgets()

        # Search Contact Tab
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Search Contact")
        self.create_search_widgets()

    def create_add_widgets(self):
        labels = ["Name:", "Phone:", "Email:", "Address:"]
        self.add_entries = []

        for i, label in enumerate(labels):
            tk.Label(self.add_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = tk.Entry(self.add_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.add_entries.append(entry)

        add_button = tk.Button(self.add_frame, text="Add Contact", command=self.add_contact, bg='#4CAF50', fg='white')
        add_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def create_view_widgets(self):
        self.tree = ttk.Treeview(self.view_frame, columns=("Name", "Phone", "Email", "Address"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Address", text="Address")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        button_frame = tk.Frame(self.view_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        update_button = tk.Button(button_frame, text="Update", command=self.update_contact, bg='#2196F3', fg='white')
        update_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_contact, bg='#F44336', fg='white')
        delete_button.pack(side=tk.LEFT, padx=5)

        refresh_button = tk.Button(button_frame, text="Refresh", command=self.view_contacts, bg='#FF9800', fg='white')
        refresh_button.pack(side=tk.LEFT, padx=5)

    def create_search_widgets(self):
        tk.Label(self.search_frame, text="Search:").pack(padx=5, pady=5)
        self.search_entry = tk.Entry(self.search_frame, width=40)
        self.search_entry.pack(padx=5, pady=5)

        search_button = tk.Button(self.search_frame, text="Search", command=self.search_contact, bg='#9C27B0', fg='white')
        search_button.pack(pady=10)

        self.search_result = tk.Text(self.search_frame, height=10, width=50)
        self.search_result.pack(padx=5, pady=5)

    def add_contact(self):
        name, phone, email, address = [entry.get() for entry in self.add_entries]
        if name and phone:
            self.c.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
                           (name, phone, email, address))
            self.conn.commit()
            messagebox.showinfo("Success", "Contact added successfully!")
            for entry in self.add_entries:
                entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Name and Phone are required fields!")

    def view_contacts(self):
        self.tree.delete(*self.tree.get_children())
        self.c.execute("SELECT * FROM contacts")
        for row in self.c.fetchall():
            self.tree.insert("", tk.END, values=row[1:])

    def update_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a contact to update!")
            return
        values = self.tree.item(selected)['values']
        update_window = tk.Toplevel(self.master)
        update_window.title("Update Contact")
        labels = ["Name:", "Phone:", "Email:", "Address:"]
        entries = []
        for i, label in enumerate(labels):
            tk.Label(update_window, text=label).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = tk.Entry(update_window, width=40)
            entry.insert(0, values[i])
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)
        
        def save_update():
            new_values = [entry.get() for entry in entries]
            self.c.execute("UPDATE contacts SET name=?, phone=?, email=?, address=? WHERE name=? AND phone=?",
                           (*new_values, values[0], values[1]))
            self.conn.commit()
            messagebox.showinfo("Success", "Contact updated successfully!")
            update_window.destroy()
            self.view_contacts()

        save_button = tk.Button(update_window, text="Save", command=save_update, bg='#4CAF50', fg='white')
        save_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def delete_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a contact to delete!")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this contact?"):
            values = self.tree.item(selected)['values']
            self.c.execute("DELETE FROM contacts WHERE name=? AND phone=?", (values[0], values[1]))
            self.conn.commit()
            messagebox.showinfo("Success", "Contact deleted successfully!")
            self.view_contacts()

    def search_contact(self):
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showerror("Error", "Please enter a search term!")
            return
        self.c.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ?",
                       (f'%{search_term}%', f'%{search_term}%'))
        results = self.c.fetchall()
        self.search_result.delete(1.0, tk.END)
        if results:
            for row in results:
                self.search_result.insert(tk.END, f"Name: {row[1]}\nPhone: {row[2]}\nEmail: {row[3]}\nAddress: {row[4]}\n\n")
        else:
            self.search_result.insert(tk.END, "No results found.")

def main():
    root = tk.Tk()
    app = ContactManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
