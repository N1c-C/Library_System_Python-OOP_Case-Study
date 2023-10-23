# <p style="text-align: center;">Introduction</p>

This project looks at how some library system functions can be implemented using ***object-oriented programming (OOP)*** and ***Singleton*** and ***Observer*** design patterns. 

The case study provides three comma-separated value files (CSV): books.csv, members.csv and bookloans.csv.

 - Books.csv contains the details of 120 library books.

 - Members.csv includes the details of 200 library members.

- bookloans.csv contains historical loan data.

Book/member data is initially retrieved from the CSV files, but from then on, files are saved and restored in JSON (JavaScript Object Notation) format.

## Functionality
The following typical library functions are developed.

### Book Loans.

Allows a member to borrow a book. Both member and book classes have a `scan()` method to represent a library environment; which returns their unique id numbers. The loan is recorded.

### Book Returns.

Allows a member to return a book. The completed loan is recorded.

### Membership Applications

The request details are recorded while membership cards are manufactured. The card number is the member’s id, followed by an issue number, starting at one. It is set to zero whilst a member is waiting for a card to be issued.

### Book Reservations

Reservations are made using the book’s id and stored. When a reserved book is returned a trigger is fired for a notification.

### Notification System

Implements an Observer design pattern to automatically send notifications when:

 - A reserved book has become available.

 - An ordered book arrives at the library.

 - A returned book was overdue, and a fine is payable.

The system is easily expanded for other notifications. All notifications are sent by email using a `sendEmail()` method. (Currently, these are just displayed on the console).


## The system design is documented in the project [WIKI](https://github.com/N1c-C/Python-OOP-Case-Study/wiki)

