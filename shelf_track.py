# Import necessary modules
import sqlite3
import sys

# Create or open a file called ebookstore with an SQLite3 DB
db = sqlite3.connect('ebookstore.db')

# Get the cursor object
cursor = db.cursor()

# Create the book table if it does not already exist
cursor.execute('''
            CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY,
            title TEXT,
            authorID INTEGER,
            qty INTEGER
            )
''')

# Commit the changes to the database
db.commit()

# Insert the data provided into the book table
books = [
    (3001, 'A Tale of Two Cities', 1290, 30),
    (3002, "Harry Potter and the Philosopher's Stone", 8937, 40),
    (3003, 'The Lion, the Witch and the Wardrobe', 2356, 25),
    (3004, 'The Lord of the Rings', 6380, 37),
    (3005, "Alice's Adventures in Wonderland", 5620, 12)
]

# Use the executemany() method to instert the books data
cursor.executemany(
    '''INSERT OR IGNORE INTO book (id, title, authorID, qty)
        VALUES (?, ?, ?, ?)''',
    books
)

# Print the database in rows after insertion
for row in cursor.execute('SELECT * FROM book'):
    print(row)

# Commit the changes to the database
db.commit()

# Close the database connection
db.close()


# Create functions that can be used by the bookstore
# clerk to manage the inventory
def add_new_book():
    '''This function will allow the user to add a new book into the database'''

    print("\nAdding a new book to the inventory.\n")
    try:
        while True:

            book_id = int(input("Enter the book ID: "))
            if book_id <= 0:
                print("Book ID cannot be a negative number or zero. "
                      "Please try again.")
                continue
            # Check if the book ID already exists in the database
            if book_id in [
                row[0] for row in cursor.execute('SELECT id FROM book')
            ]:
                print("Book ID already exists. Please try again.")
                continue
            title = input("Enter the title of the book: ")
            author_id = int(input("Enter the author's ID: "))
            if author_id <= 0:
                print(
                    "The author's ID cannot be a negative number or zero. "
                    "Please try again."
                )
                continue
            qty = int(input("Enter the quantity of the book: "))
            if qty < 0:
                print("The quantity cannot be a negative number. "
                      "Please try again.")
                continue
            # Ask the user if they want to add the author's name and country
            user_input = input(
                "Would you like to add the author's details (y/n): "
            ).lower()
            if user_input == 'y':
                author_name = input("Enter the name of the author: ")
                country_name = input("Enter the country name: ").capitalize()
                new_author_id = int(input("Enter the author ID: "))
                if new_author_id <= 0:
                    print("Author ID cannot be a zero or negative number."
                          "Please try again!")
                    continue
                break
            elif user_input == 'n':
                print("Book added successfully!\n")
                break
    except Exception as e:
        # Roll back any changes if something goes wrong
        db.rollback()
        raise e
    except ValueError:
        print("Invalid input. Please check your data types and try again.")

    # Add the new book to the database
    cursor.execute(
        '''INSERT OR IGNORE INTO book (id, title, authorID, qty)
        VALUES (?, ?, ?, ?)''',
        (book_id, title, author_id, qty)
    )

    # Add the new author details in the author database
    cursor.execute(
        '''INSERT OR IGNORE INTO author (id, name, country)
        VALUES (?, ?, ?)''', (new_author_id, author_name, country_name)
    )

    # Print the database in rows after insertion
    for row in cursor.execute('SELECT * FROM book'):
        print(row)

    # Commit the changes to the database
    db.commit()

    return book_id, title, author_id, author_name, new_author_id, qty, country_name


def update_book():
    '''This function will allow the user to update a book into the database.
    When the user selects option 2 (Update book), they should enter the
    book ID they want to update, review the current author’s name and country,
    provide new values for the author’s name and/or country, and
    then save the updated information to the database.'''
    while True:
        try:
            book_id = int(
                input("Enter the book ID you wish to update: ")
            )
            if book_id <= 0:
                print("Book ID cannot be a negative number, please try again.")
                continue

            # Check if the book ID exists in the database
            cursor.execute(
                '''SELECT * FROM book WHERE id = ?''',
                (book_id,)
            )
            book = cursor.fetchone()
            if book is None:
                print("Book ID does not exist. Please try again.")
                continue

            print(f"Book details found: {book}")

            # Retrieve information from the book table and author table
            cursor.execute('''
                SELECT book.title, author.name, author.country
                FROM book
                INNER JOIN author ON book.authorID = author.id
                WHERE book.id = ?
            ''', (book_id,))

            result = cursor.fetchone()
            print(result)
            if result:
                title, author_name, author_country = result
                print(f"Current Title: {title}")
                print(f"Current Author: {author_name}")
                print(f"Author's Country: {author_country}")
            else:
                print("No matching book found.")
                continue

            new_title = input("Enter the new title of the book: ")
            new_author_id = int(input("Enter the new author's ID: "))
            if new_author_id <= 0:
                print(
                    "The author's ID cannot be a negative number or zero. "
                    "Please try again."
                )
                continue
            new_qty = int(input("Enter the new quantity of the book: "))
            if new_qty < 0:
                print("The quantity cannot be a negative number. "
                      "Please try again.")
                continue

            # Ask if the user wants to update the author's details
            ask_user = input("Would younlike to update the author's details (y/n): ").lower()
            if ask_user == 'y':
                new_author_name = input("Enter the new author name: ")
                new_auth_country = input("Enter the new author ID: ")
                continue

            elif ask_user == 'n':
                print('Update Completed!')
                break

        except ValueError:
            print("Invalid input. Please check your data types and try again.")
        except Exception as e:
            # Roll back any changes if something goes wrong
            db.rollback()
            raise e

        cursor.execute(
            '''SELECT * FROM book WHERE id = ?''',
            (book_id,)
        )
        result = cursor.fetchone()
        old_author_id = result[2]

        # Update the book and author table in the database
        cursor.execute(
            '''UPDATE book
               SET title = ?, authorID = ?, qty = ?
               WHERE id = ?''',
            (new_title, new_author_id, new_qty, book_id)
        )

        cursor.execute(
            '''UPDATE author
                SET id = ?
                WHERE id = ?''',
            (new_author_id, old_author_id)
        )

        # Print the database in rows after updating
        for row in cursor.execute(
            '''SELECT book.id, book.title, book.authorID, book.qty
               FROM book
               INNER JOIN author ON book.authorID = author.id
               WHERE book.id = ?''',
            (book_id,)
        ):
            print(row)

        # Commit the changes to the database
        db.commit()

        return book_id, new_title, new_author_id, new_qty, new_author_name, new_auth_country


def delete_book():
    '''This function will allow the user to delete a book from the database'''
    while True:
        try:
            del_book_id = int(
                input("Enter the book ID you wish to delete: ")
            )
            if del_book_id <= 0:
                print("Book ID cannot be a negative number, please try again.")
                continue

            # Check if the book ID exists in the database
            cursor.execute(
                '''SELECT * FROM book WHERE id = ?''',
                (del_book_id,)
            )
            book = cursor.fetchone()
            if book is None:
                print("Book ID does not exist. Please try again.")
                continue
        except ValueError:
            print("Invalid input. Please check your data types and try again.")
        except Exception as e:
            # Roll back any changes if something goes wrong
            db.rollback()
            raise e

        # Delete the book from the database
        cursor.execute(
            '''DELETE FROM book WHERE id = ?''',
            (del_book_id,)
        )
        print(f"Book with ID {del_book_id} has been deleted.")

        # Print the database in rows after deletion
        for row in cursor.execute('SELECT * FROM book'):
            print(row)

        # Commit the changes to the database
        db.commit()

        return del_book_id


def search_book():
    '''This function will allow the user to search for a
    book in the database'''
    while True:
        try:
            search_book_id = int(
                input("Enter the book ID you wish to search: ")
            )

            # Check if the book ID exists in the database
            if search_book_id in [
                row[0] for row in cursor.execute('SELECT id FROM book')
            ]:
                cursor.execute(
                    '''SELECT * FROM book WHERE id = ?''',
                    (search_book_id,)
                )
                book = cursor.fetchone()
                print(f"Book found: {book}")
            if search_book_id <= 0:
                print("Book ID cannot be a negative number, please try again.")
                continue

        except ValueError:
            print("Invalid input. Please check your data types and try again.")
        except Exception as e:
            # Roll back any changes if something goes wrong
            db.rollback()
            raise e

        return search_book_id

# ==================AUTHOR TABLE==================


# Create the author table if it does not already exist
db = sqlite3.connect('ebookstore.db')
cursor = db.cursor()

# Execute the SQL coomand to create the author's
# table if it does not already exist
cursor.execute('''
            CREATE TABLE IF NOT EXISTS author (
            id INTEGER PRIMARY KEY,
            name TEXT,
            country TEXT
        )
''')

# Commit the changes to the database
db.commit()

# Insert the data provided into the author table
authors = [
    (1290, 'Charles Dickens', 'England'),
    (8937, 'J.K. Rowling', 'England'),
    (2356, 'C.S. Lewis', 'Irelnd'),
    (6380, 'J.R.R Tolkien', 'South Africa'),
    (5620, 'Lewis Carroll', 'England')
]

# Use the executemany() method to insert the authors data
cursor.executemany('''
                INSERT OR IGNORE INTO author (id, name, country)
                VALUES(?, ?, ?)''', authors)

# Print the database in rows after insertion
for row in cursor.execute('SELECT * FROM author'):
    print(row)

# Commit the changes to the database
db.commit()

# Close the database connection
# db.close()


def view_details_of_all_books():
    '''This function will display the book title, author name, and country
    in a user-friendly way. Use the zip() function to combine the tables'''

    cursor.execute('''
                SELECT book.title, author.name, author.country
                FROM book
                JOIN author ON book.authorID = author.id
                ''')
    results = cursor.fetchall()
    for title, name, country in results:
        print(f"Title: {title}\nAuthor: {name}\nCountry: {country}")
        print("-" * 15)


# Main Menu options
while True:
    # Display the menu options
    print("\n--------MENU CHOICE INVENTORY--------\n")
    # try:
    menu_input = input(
        '''\nChoose from the menu options below:
        1. Enter book
        2. Update book
        3. Delete book
        4. Search book
        5. View details of all books
        0. Exit
        Enter an option (0-5): '''
    )

    if menu_input == '1':
        add_new_book()
    elif menu_input == '2':
        update_book()
    elif menu_input == '3':
        delete_book()
    elif menu_input == '4':
        search_book()
    elif menu_input == '5':
        view_details_of_all_books()
    elif menu_input == '0':
        print("Quiting the program. Goodbye!")
        sys.exit()

    # except ValueError:
    #     print("Invalid input. Please enter a number between 0 and 5.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
