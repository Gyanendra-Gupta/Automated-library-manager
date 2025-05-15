# Automated Book Lending and Return System manages books and borrowers in a library using Python.
# It tracks due dates, sends email reminders, generates PDF reports, and shows borrowing 
# trends with simple charts.

import tkinter as tk
from tkinter import messagebox
import sqlite3
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

conn = sqlite3.connect('library.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    due_date TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS borrowers (
    borrower_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    book_id INTEGER,
    borrow_date TEXT,
    return_date TEXT,
    FOREIGN KEY (book_id) REFERENCES books (book_id)
)
''')
conn.commit()

root = tk.Tk()
root.title("Library Manager")
root.geometry("500x400")

def add_book():
    title = entry_title.get()
    author = entry_author.get()
    due_date = entry_due_date.get()
    if title and author and due_date:
        c.execute('INSERT INTO books (title, author, due_date) VALUES (?, ?, ?)', (title, author, due_date))
        conn.commit()
        messagebox.showinfo("Success", "Book added successfully!")
        update_books_list()
    else:
        messagebox.showwarning("Input Error", "Please fill in all fields.")

def add_borrower():
    borrower_name = entry_borrower_name.get()
    book_id = entry_book_id.get()
    borrow_date = entry_borrow_date.get()
    return_date = entry_return_date.get()
    if borrower_name and book_id and borrow_date and return_date:
        c.execute('INSERT INTO borrowers (name, book_id, borrow_date, return_date) VALUES (?, ?, ?, ?)', 
                  (borrower_name, book_id, borrow_date, return_date))
        conn.commit()
        messagebox.showinfo("Success", "Borrower added successfully!")
    else:
        messagebox.showwarning("Input Error", "Please fill in all fields.")

def generate_pdf():
    borrowers_data = c.execute('SELECT * FROM borrowers').fetchall()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Library Lending History", ln=True, align="C")
    for row in borrowers_data:
        pdf.cell(200, 10, txt=f"Borrower: {row[1]}, Book ID: {row[2]}, Borrowed On: {row[3]}, Due On: {row[4]}", ln=True)
    pdf.output("lending_history.pdf")
    messagebox.showinfo("Success", "PDF generated successfully!")

def send_email_reminder():
    borrowers_data = c.execute('SELECT * FROM borrowers').fetchall()
    for row in borrowers_data:
        return_date = datetime.strptime(row[4], "%Y-%m-%d")
        today = datetime.today()
        if return_date < today:
            send_email(row[1], row[4])

def send_email(borrower_name, return_date):
    sender_email = "sg4463217@gmail.com"
    receiver_email = "2k22.aiml.2211663@gmail.com"
    password = "psru vast bzna psbr"
    subject = "Book Return Reminder"
    body = f"Dear {borrower_name},\n\nThis is a reminder to return the book by {return_date}.\n\nBest Regards,\nLibrary"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        messagebox.showinfo("Success", "Reminder email sent successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {e}")

def update_books_list():
    books_list.delete(0, tk.END)
    books = c.execute('SELECT * FROM books').fetchall()
    for book in books:
        books_list.insert(tk.END, f"{book[0]} - {book[1]} by {book[2]} (Due: {book[3]})")

def visualize_borrowing_trends():
    data = c.execute('SELECT borrow_date, COUNT(*) FROM borrowers GROUP BY borrow_date').fetchall()
    df = pd.DataFrame(data, columns=["Date", "Borrowed Books"])
    df["Date"] = pd.to_datetime(df["Date"])
    
    plt.figure(figsize=(10, 6))
    plt.plot(df["Date"], df["Borrowed Books"])
    plt.title("Books Borrowed Over Time")
    plt.xlabel("Date")
    plt.ylabel("Books Borrowed")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

tk.Label(root, text="Book Title:").pack()
entry_title = tk.Entry(root)
entry_title.pack()

tk.Label(root, text="Author:").pack()
entry_author = tk.Entry(root)
entry_author.pack()

tk.Label(root, text="Due Date (YYYY-MM-DD):").pack()
entry_due_date = tk.Entry(root)
entry_due_date.pack()

tk.Button(root, text="Add Book", command=add_book).pack()

tk.Label(root, text="Borrower Name:").pack()
entry_borrower_name = tk.Entry(root)
entry_borrower_name.pack()

tk.Label(root, text="Book ID:").pack()
entry_book_id = tk.Entry(root)
entry_book_id.pack()

tk.Label(root, text="Borrow Date (YYYY-MM-DD):").pack()
entry_borrow_date = tk.Entry(root)
entry_borrow_date.pack()

tk.Label(root, text="Return Date (YYYY-MM-DD):").pack()
entry_return_date = tk.Entry(root)
entry_return_date.pack()

tk.Button(root, text="Add Borrower", command=add_borrower).pack()

books_list = tk.Listbox(root)
books_list.pack()

tk.Button(root, text="Generate PDF Report", command=generate_pdf).pack()
tk.Button(root, text="Send Email Reminders", command=send_email_reminder).pack()
tk.Button(root, text="Visualize Borrowing Trends", command=visualize_borrowing_trends).pack()

update_books_list()
root.mainloop()
conn.close()






