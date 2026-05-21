import mysql.connector
from datetime import date, timedelta

# ---------------- DATABASE CONNECTION ---------------- #

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",
        database="student"
    )

    cur = conn.cursor()
    print("Database Connected Successfully")

except mysql.connector.Error as err:
    print("Database Connection Error:", err)
    exit()

# ---------------- ADD BOOK ---------------- #

def add_book():
    try:
        title = input("Enter Title: ").strip()
        author = input("Enter Author: ").strip()

        if not title or not author:
            print("Title and Author cannot be empty")
            return

        query = """
        INSERT INTO books(title, author, available)
        VALUES(%s, %s, 1)
        """

        cur.execute(query, (title, author))
        conn.commit()

        print("Book added successfully")

    except mysql.connector.Error as err:
        print("Error:", err)

# ---------------- ADD MEMBER ---------------- #

def add_member():
    try:
        name = input("Enter Name: ").strip()
        student_class = input("Enter Class: ").strip()

        if not name or not student_class:
            print("Fields cannot be empty")
            return

        query = """
        INSERT INTO members(name, class)
        VALUES(%s, %s)
        """

        cur.execute(query, (name, student_class))
        conn.commit()

        print("Member added successfully")

    except mysql.connector.Error as err:
        print("Error:", err)

# ---------------- VIEW BOOKS ---------------- #

def view_books():
    try:
        cur.execute("SELECT * FROM books")

        books = cur.fetchall()

        if not books:
            print("No books found")
            return

        print("\n--- BOOK LIST ---")

        for book in books:
            status = "Available" if book[3] == 1 else "Borrowed"

            print(
                f"ID: {book[0]} | "
                f"Title: {book[1]} | "
                f"Author: {book[2]} | "
                f"Status: {status}"
            )

    except mysql.connector.Error as err:
        print("Error:", err)

# ---------------- SEARCH BOOK ---------------- #

def search_book():
    try:
        keyword = input("Enter title keyword: ").strip()

        query = """
        SELECT * FROM books
        WHERE title LIKE %s
        """

        cur.execute(query, ('%' + keyword + '%',))

        books = cur.fetchall()

        if not books:
            print("No matching books found")
            return

        print("\n--- SEARCH RESULTS ---")

        for book in books:
            status = "Available" if book[3] == 1 else "Borrowed"

            print(
                f"ID: {book[0]} | "
                f"Title: {book[1]} | "
                f"Author: {book[2]} | "
                f"Status: {status}"
            )

    except mysql.connector.Error as err:
        print("Error:", err)

# ---------------- BORROW BOOK ---------------- #

def borrow_book():
    try:
        book_id = int(input("Enter Book ID: "))
        member_id = int(input("Enter Member ID: "))

        # Check book availability
        cur.execute(
            "SELECT available FROM books WHERE book_id = %s",
            (book_id,)
        )

        book = cur.fetchone()

        if not book:
            print("Book ID not found")
            return

        if book[0] == 0:
            print("Book is currently unavailable")
            return

        # Check member existence
        cur.execute(
            "SELECT * FROM members WHERE member_id = %s",
            (member_id,)
        )

        member = cur.fetchone()

        if not member:
            print("Member ID not found")
            return

        loan_date = date.today()
        due_date = loan_date + timedelta(days=7)

        query = """
        INSERT INTO loans(book_id, member_id, loan_date, due_date)
        VALUES(%s, %s, %s, %s)
        """

        cur.execute(
            query,
            (book_id, member_id, loan_date, due_date)
        )

        cur.execute(
            "UPDATE books SET available = 0 WHERE book_id = %s",
            (book_id,)
        )

        conn.commit()

        print("Book borrowed successfully")
        print("Due Date:", due_date)

    except ValueError:
        print("Please enter valid numeric IDs")

    except mysql.connector.Error as err:
        print("Error:", err)

# ---------------- RETURN BOOK ---------------- #

def return_book():
    try:
        loan_id = int(input("Enter Loan ID: "))

        cur.execute(
            """
            SELECT due_date, book_id
            FROM loans
            WHERE loan_id = %s
            """,
            (loan_id,)
        )

        loan = cur.fetchone()

        if not loan:
            print("Loan ID not found")
            return

        due_date, book_id = loan

        return_date = date.today()

        late_days = (return_date - due_date).days

        fine = max(0, late_days * 10)

        query = """
        INSERT INTO returns(loan_id, return_date, fine)
        VALUES(%s, %s, %s)
        """

        cur.execute(
            query,
            (loan_id, return_date, fine)
        )

        cur.execute(
            "UPDATE books SET available = 1 WHERE book_id = %s",
            (book_id,)
        )

        conn.commit()

        print("Book returned successfully")
        print("Fine:", fine)

    except ValueError:
        print("Please enter a valid Loan ID")

    except mysql.connector.Error as err:
        print("Error:", err)

# ---------------- OVERDUE REPORT ---------------- #

def overdue_books():
    try:
        today = date.today()

        query = """
        SELECT loan_id, book_id, member_id, due_date
        FROM loans
        WHERE due_date < %s
        """

        cur.execute(query, (today,))

        data = cur.fetchall()

        if not data:
            print("No overdue books")
            return

        print("\n--- OVERDUE BOOKS ---")

        for row in data:
            print(
                f"Loan ID: {row[0]} | "
                f"Book ID: {row[1]} | "
                f"Member ID: {row[2]} | "
                f"Due Date: {row[3]}"
            )

    except mysql.connector.Error as err:
        print("Error:", err)

# ---------------- MAIN MENU ---------------- #

while True:

    print("\n========= LIBRARY MANAGEMENT SYSTEM =========")
    print("1. Add Book")
    print("2. Add Member")
    print("3. View Books")
    print("4. Search Book")
    print("5. Borrow Book")
    print("6. Return Book")
    print("7. Overdue Books")
    print("8. Exit")

    choice = input("Enter Choice: ").strip()

    if choice == "1":
        add_book()

    elif choice == "2":
        add_member()

    elif choice == "3":
        view_books()

    elif choice == "4":
        search_book()

    elif choice == "5":
        borrow_book()

    elif choice == "6":
        return_book()

    elif choice == "7":
        overdue_books()

    elif choice == "8":
        print("Thank You")
        break

    else:
        print("Invalid Choice")

# ---------------- CLOSE CONNECTION ---------------- #

cur.close()
conn.close()
