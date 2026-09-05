# 🎬 CINEVO LUXE

## Premium Cinema Ticket Booking & Reservation Management Platform

**CINEVO LUXE** is a full-stack cinema ticket booking and reservation management platform designed to provide a realistic movie-booking experience while demonstrating practical software engineering principles.

The application allows customers to discover movies, explore showtimes, select seats, review their order, complete a booking, and receive a digital booking confirmation. Alongside the customer experience, I developed a protected staff administration portal for managing cinema content.

The project was built using **Python, Flask, SQLAlchemy, SQLite, HTML, CSS, and JavaScript**, with particular attention given to **security, server-side validation, booking integrity, authentication, database consistency, and production deployment**.

🌐 **Live Application:**
[https://cinevo-luxe.onrender.com](https://cinevo-luxe.onrender.com)

---

# 📖 About the Project

I developed CINEVO LUXE as a practical full-stack application rather than a simple frontend demonstration.

A cinema booking system may appear straightforward at first: choose a movie, select seats, and book tickets. However, a real booking system has several important engineering challenges.

For example:

* What happens if two customers try to reserve the same seat?
* Can a user manipulate the ticket price through browser tools?
* Can someone submit invalid seat names directly to the server?
* How should staff accounts be protected?
* How should sensitive application secrets be stored?
* How can customers retrieve their bookings without exposing everyone else's reservations?
* How should state-changing requests be protected?
* How should the database remain consistent when a booking is being created?

I designed CINEVO LUXE around these types of problems.

The goal was not simply to make the application **look like a cinema website**, but to make the underlying application logic behave more like a real-world web system.

---

# 🎯 What I Built

I developed the application across both the **customer-facing frontend** and the **backend system**.

The customer side provides a complete booking journey:

**Movie Discovery → Movie Details → Showtime → Seat Selection → Checkout → Booking Processing → Digital Confirmation**

Behind this interface, the Flask backend handles the application's business logic, validation, authentication, database operations, and booking integrity.

I also implemented a separate staff environment that allows authorized staff users to access administrative functionality.

Therefore, the project combines:

**Frontend + Backend + Database + Authentication + Authorization + Security + Business Logic + Deployment**

into one complete application.

---

# 🎬 Customer Experience

The customer experience begins with the movie catalogue.

Users can browse available movies and open individual movie pages to understand the movie and available viewing options.

From there, customers can select a cinema and showtime and continue into the reservation process.

The system then takes the customer through interactive seat selection and checkout before creating the reservation.

---

# 💺 Interactive Seat Selection

One of the main components I developed is the interactive seat-selection system.

Customers can see which seats are available and select the seats they want to reserve.

However, the important engineering decision is that **the browser is not trusted as the final authority**.

When a booking is submitted, the backend validates the selected seats again.

The server checks:

* Whether the submitted seat names are valid
* Whether duplicate seats were submitted
* Whether the seats belong to the expected seat format
* Whether the seats are already occupied
* Whether the selected seats are associated with the requested showtime

This prevents a user from bypassing the normal frontend interface and sending arbitrary booking data directly to the backend.

---

# 💳 Server-Authoritative Checkout

I specifically designed the checkout process so that important financial values are determined by the server.

The browser may display a ticket total, but the backend does not simply trust that value.

Instead, the server uses validated booking information and the configured showtime price to calculate the authoritative amount.

Conceptually:

```text
Validated Seats
       ↓
Server-Controlled Ticket Price
       ↓
Authoritative Booking Amount
```

This is important because client-side values can be modified by users.

A user should never be able to open browser developer tools, change a ticket price, and expect the server to accept the manipulated amount.

---

# 🛡️ Booking Integrity & Double-Booking Prevention

A major engineering concern in a reservation system is preventing two customers from successfully reserving the same seat.

CINEVO LUXE checks seat availability during booking processing rather than relying only on what the frontend displays.

The booking process uses transaction-aware database operations to help maintain consistency while reservations are being created.

This means the application treats **seat availability and booking integrity as backend responsibilities**, not merely UI responsibilities.

---

# 🎟️ Digital Booking Confirmation

After a successful reservation, the customer receives a dedicated booking confirmation page.

The confirmation provides important reservation information such as:

* Booking reference
* Movie
* Cinema
* Date
* Showtime
* Selected seats
* Customer information
* Total amount
* QR representation

The confirmation interface is also designed to be suitable for printing.

This gives the application a complete journey rather than stopping after a database record is created.

---

# 🔎 Protected Reservation Lookup

I also considered the privacy implications of allowing customers to retrieve their bookings.

Instead of providing an unrestricted page containing booking records, the reservation lookup requires identifying information such as the booking reference together with customer contact information.

This approach reduces unnecessary exposure of other customers' reservation information.

---

# 👨‍💼 Staff Administration Portal

CINEVO LUXE also includes a separate staff administration environment.

Authorized staff members can log in and access administrative functionality through protected routes.

The staff environment includes functionality for managing movie-related content and viewing the administrative dashboard.

The separation between the customer-facing application and staff functionality demonstrates how different user roles can interact with the same backend system while receiving different levels of access.

---

# 🔐 Security Engineering

Security was one of the areas I intentionally focused on while developing the project.

Rather than treating security as something added at the end, I incorporated security considerations into the application's architecture.

## Authentication

Staff accounts are protected using password hashing through Werkzeug.

Passwords are not intended to be stored as plaintext credentials.

---

## Authorization

Staff-only functionality is protected so that administrative routes are not treated as publicly accessible customer routes.

---

## CSRF Protection

I implemented CSRF protection for protected state-changing requests.

The application generates and validates CSRF tokens before processing relevant POST requests.

This helps protect forms from Cross-Site Request Forgery attacks.

---

## Server-Side Input Validation

The backend validates important data submitted by the client.

This includes:

* Seat information
* Duplicate seats
* Seat availability
* Customer information
* Booking parameters
* Promotional conditions
* Other booking-related values

The application therefore does not rely exclusively on frontend validation.

---

## Secure Session Configuration

Authentication-related sessions are configured with security-focused settings intended to reduce common session risks.

---

## Security Headers

The application includes security-related HTTP response headers to establish a stronger browser security baseline.

---

## Environment-Based Secret Management

Sensitive production configuration is not hardcoded into the application.

The Flask secret key is supplied through an environment variable.

This follows the principle that production secrets should be managed by the deployment environment rather than committed to source control.

---

# 🧠 A Real Security Lesson I Applied

During the development process, I also identified that a previously used development secret had existed in Git history.

Rather than simply removing it from the latest source file, I treated the historical exposure as a security issue.

I:

1. Generated a new production secret.
2. Rotated the production secret in the deployment environment.
3. Removed the exposed secret from Git history.
4. Rewrote the repository history.
5. Verified that the old secret could no longer be found in the rewritten history.
6. Force-updated the repository with the cleaned history.

This experience reinforced an important engineering principle:

> **Removing a secret from the current source code is not enough if the secret already exists in version-control history.**

---

# 🗄️ Database & Data Model

The application uses **SQLite** with **SQLAlchemy** as the ORM layer.

The main entities are:

### Movie

Represents the movies available on the platform.

### Cinema

Represents cinema venues.

### Showtime

Connects movies with scheduled viewing times and configured ticket pricing.

### Booking

Stores reservation information including:

* Booking reference
* Movie
* Cinema
* Date
* Time
* Selected seats
* Total amount
* Customer name
* Customer email
* Customer phone
* Creation timestamp

### StaffUser

Represents staff authentication accounts and their securely stored password information.

The database layer allows the application to move beyond static frontend data and perform real persistence and reservation operations.

---

# 🏗️ Application Architecture

The overall application can be understood as:

```text
                         CINEVO LUXE
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
          Frontend          Flask           Database
              │            Backend           │
              │               │               │
        HTML / CSS / JS      Routes       SQLAlchemy
                              │               │
                    ┌─────────┼─────────┐     │
                    │         │         │     │
                    ▼         ▼         ▼     ▼
               Validation  Auth      Booking  SQLite
                    │         │         │
                    └─────────┼─────────┘
                              │
                              ▼
                       Booking Integrity
                              │
                              ▼
                           Security
                              │
                              ▼
                         Deployment
```

The architecture allows the frontend to provide the user experience while the backend remains responsible for enforcing important application rules.

---

# 🔄 Complete Booking Flow

The application follows this general process:

```text
Browse Movies
     ↓
Select Movie
     ↓
View Movie Details
     ↓
Choose Cinema & Showtime
     ↓
Select Seats
     ↓
Checkout
     ↓
Server-Side Validation
     ↓
Verify Seat Availability
     ↓
Calculate Authoritative Total
     ↓
Create Booking
     ↓
Generate Booking Reference
     ↓
Display Digital Confirmation
```

This workflow connects the user interface, backend business logic, and database into one complete system.

---

# 🛠️ Technology Stack

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* SQLAlchemy
* Werkzeug

### Frontend

* HTML5
* CSS3
* JavaScript
* Responsive UI
* Modern cinema-focused interface

### Database

* SQLite

### Security

* Password hashing
* Authentication
* Authorization
* CSRF protection
* Server-side validation
* Security headers
* Secure session configuration
* Environment-based secrets
* Transaction-aware booking operations

### Development & Deployment

* Git
* GitHub
* Render

---

# 📁 Project Structure

```text
CINEVO LUXE/
│
├── app.py
├── models.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── data/
│   ├── movies.json
│   └── bookings.json
│
├── templates/
│   ├── home.html
│   ├── movies.html
│   ├── movie_details.html
│   ├── showtimings.html
│   ├── cinemas.html
│   ├── offers.html
│   ├── bookings.html
│   ├── seat_selection.html
│   ├── checkout.html
│   ├── confirmation.html
│   │
│   └── staff/
│       ├── login.html
│       ├── dashboard.html
│       └── ...
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│
└── screenshots/
    ├── home.jpg
    ├── catalog.jpg
    ├── moviedetail.jpg
    ├── seatselection.jpg
    ├── checkout.jpg
    ├── checkoutdetails.jpg
    └── staffdashboard.jpg
```

---

# 📸 Application Screenshots

The following screenshots demonstrate the main customer journey and the staff administration experience.

## 🏠 Homepage

![CINEVO LUXE Homepage](screenshots/home.jpg)

The homepage establishes the CINEVO LUXE visual identity and provides the entry point into the cinema experience.

---

## 🎬 Movie Catalogue

![Movie Catalog](screenshots/catalog.jpg)

The movie catalogue allows customers to explore the available movies.

---

## 🎞️ Movie Details

![Movie Details](screenshots/moviedetail.jpg)

The movie details interface provides information about the selected movie and connects the customer to available booking options.

---

## 💺 Seat Selection

![Interactive Seat Selection](screenshots/seatselection.jpg)

The interactive seat-selection interface allows customers to choose available seats before continuing to checkout.

---

## 💳 Checkout

![Checkout](screenshots/checkout.jpg)

The checkout interface brings together the customer's reservation details before the booking is processed.

---

## 🎟️ Booking Confirmation

![Digital Booking Confirmation](screenshots/checkoutdetails.jpg)

The confirmation page provides the completed reservation details and booking reference.

---

## 👨‍💼 Staff Dashboard

![Staff Dashboard](screenshots/staffdashboard.jpg)

The staff dashboard provides the administrative interface for authorized staff users.

---

# 🧪 Testing & Validation

I tested the application across both functional and security-sensitive areas.

Testing included:

* Application startup
* Core route availability
* Movie browsing
* Movie details
* Showtime handling
* Seat selection
* Invalid seat input
* Duplicate seat submissions
* Already-booked seats
* Server-side price calculation
* Booking processing
* Booking confirmation
* Reservation lookup
* Staff authentication
* Staff authorization
* CSRF validation
* Security headers
* Environment-based secret configuration
* Database integrity
* Dependency security checking

I also used dependency auditing to identify known vulnerabilities in installed Python dependencies.

The purpose of these tests was not only to verify that the normal user interface worked, but also to verify that important backend rules remained enforced when requests were manipulated or bypassed.

---

# 🚀 Running the Project Locally

## 1. Clone the repository

```bash
git clone https://github.com/Yathusan-tech/cinevo-luxe.git
```

## 2. Enter the project directory

```bash
cd cinevo-luxe
```

## 3. Create a virtual environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure the environment

Create a local `.env` file based on `.env.example`.

For example:

```text
SECRET_KEY=your-development-secret
```

Never commit the `.env` file.

## 6. Start the application

```bash
python app.py
```

Open the local Flask address displayed in the terminal.

---

# ☁️ Production Deployment

CINEVO LUXE is deployed using **Render**.

🌐 **Live Application:**

[https://cinevo-luxe.onrender.com](https://cinevo-luxe.onrender.com)

The deployment uses environment-based configuration for sensitive values.

The development and deployment workflow is:

```text
Local Development
       ↓
      Git
       ↓
    GitHub
       ↓
    Render
       ↓
Production Application
```

This demonstrates the complete transition from local development to a publicly accessible web application.

---

# 💡 Engineering Decisions That Matter

Several implementation decisions were made specifically to make the project more reliable and closer to real-world application development.

### The browser is not trusted

The frontend provides the user experience, but important rules are enforced by the backend.

### Prices are calculated server-side

The server determines the authoritative booking amount instead of trusting browser-submitted totals.

### Seats are validated twice

The frontend provides interactive selection, while the backend independently validates submitted seats.

### Authentication is separated from authorization

Logging in is not enough to access administrative functionality; staff routes are protected separately.

### Secrets are externalized

Production secrets belong in the deployment environment, not in source code.

### Reservation lookup respects privacy

Customers must provide identifying booking information rather than receiving unrestricted access to reservation records.

### Database operations protect booking consistency

Reservation creation is handled with transaction-aware logic to reduce inconsistent booking states.

---
# 📸 Screenshots

# 📈 What I Learned From Building CINEVO LUXE
The following screenshots showcase the main customer booking journey and the staff administration experience.

## Customer Experience

### 🏠 Homepage
![CINEVO LUXE Homepage](screenshots/home.jpg)

### 🎬 Movie Catalog
![Movie Catalog](screenshots/catalog.jpg)

### 🎞️ Movie Details
![Movie Details](screenshots/moviedetail.jpg)

### 💺 Interactive Seat Selection
![Interactive Seat Selection](screenshots/seatselection.jpg)

### 💳 Checkout
![Checkout](screenshots/checkout.jpg)

### 🎟️ Booking Confirmation
![Digital Booking Confirmation](screenshots/checkoutdetails.jpg)

## Staff Experience

### 👨‍💼 Staff Dashboard
![Staff Dashboard](screenshots/staffdashboard.jpg)

These screenshots demonstrate the complete flow from movie discovery and seat selection through checkout and booking confirmation, along with the administrative management interface.

---

Building this project helped me understand that developing a web application is not only about creating pages and connecting buttons.

The more important challenge is designing what happens **behind those pages**.

I gained practical experience with:

* Designing Flask applications
* Building backend routes
* Working with relational data
* Using SQLAlchemy
* Implementing authentication
* Hashing passwords
* Protecting forms with CSRF
* Validating untrusted input
* Designing booking workflows
* Handling reservation consistency
* Managing application secrets
* Working with Git history
* Deploying a web application
* Thinking about security from an engineering perspective

Most importantly, the project taught me to think about the difference between:

**“The application works when I use it normally.”**

and

**“The application still behaves correctly when someone sends unexpected or manipulated input.”**

That distinction strongly influenced the way I designed the backend.

---

## What This Project Demonstrates

CINEVO LUXE demonstrates practical experience in:

**Frontend Development · Backend Development · Database Integration · Authentication · Authorization · Security Engineering · Booking Systems · Server-Side Validation · Git · GitHub · Cloud Deployment**

---

## 🟢 Project Status

**Live and actively developed.**

CINEVO LUXE currently provides:

* Customer movie discovery
* Movie details
* Dynamic showtimes
* Interactive seat selection
* Server-side booking validation
* Server-authoritative pricing
* Booking creation
* Digital confirmation
* Protected reservation lookup
* Staff authentication
* Staff administration
* Security controls
* Production deployment

The project continues to be improved with a focus on:

**Functionality · Security · User Experience · Maintainability · Production Readiness**

---

## 🔮 Future Improvements

Possible future improvements include:

* Online payment gateway integration
* Automated email ticket delivery
* Expanded staff management
* Advanced analytics and reporting
* More comprehensive automated testing
* Production monitoring
* Additional notification systems
* Expanded reservation management

These improvements would extend the existing architecture rather than replace the current booking system.

---

## 📄 License

This project is intended for educational, portfolio, and demonstration purposes.

---

## 🔐 Security Notice

Sensitive information must never be committed to the repository.

This includes:

* Passwords
* API keys
* Secret keys
* Database credentials
* Authentication tokens
* `.env` files
* Private deployment configuration

Sensitive configuration should be provided through secure environment variables or deployment configuration.

> **Security is treated as an application requirement, not an afterthought.**

No web application can honestly be guaranteed to be completely vulnerability-free. CINEVO LUXE therefore treats security as an ongoing engineering responsibility involving secure development practices, validation, testing, dependency maintenance, and continuous improvement.

---

## 👨‍💻 Project

### CINEVO LUXE

**Premium Cinema Ticket Booking & Reservation Management Platform**

Built with:

**Python · Flask · SQLAlchemy · SQLite · HTML · CSS · JavaScript**

🌐 **Live Demo:**
https://cinevo-luxe.onrender.com

💻 **Source Code:**
https://github.com/Yathusan-tech/cinevo-luxe
