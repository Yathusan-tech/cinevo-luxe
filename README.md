# 🎬 CINEVO LUXE

## Premium Cinema Ticket Booking & Reservation Management Platform

**CINEVO LUXE** is a full-stack cinema ticket booking and reservation management platform built with **Python, Flask, SQLAlchemy, SQLite, HTML, CSS, and JavaScript**.

The application provides a complete cinema booking experience where customers can discover movies, explore showtimes, select seats, review their booking, complete checkout, and receive a digital booking confirmation.

Alongside the customer experience, the project includes a protected **staff administration portal** for managing cinema-related content.

The project focuses on practical software engineering concepts including:

**Backend Development · Database Integration · Authentication · Authorization · Server-Side Validation · Booking Integrity · Security · Git · GitHub · Cloud Deployment**

🌐 **Live Application:**
https://cinevo-luxe.onrender.com

---

# 📖 About the Project

CINEVO LUXE was developed as a practical full-stack application rather than a simple frontend demonstration.

A cinema booking system involves more than displaying movies and creating buttons. Important backend problems must also be considered:

* What happens when two customers attempt to reserve the same seat?
* Can a customer manipulate the ticket price through browser developer tools?
* Can invalid seat names be submitted directly to the server?
* How should staff accounts be protected?
* How should sensitive application secrets be stored?
* How can customers retrieve their own bookings without exposing other customers' reservations?
* How should state-changing requests be protected?
* How should the database maintain consistent booking information?

CINEVO LUXE was designed around these types of real-world application concerns.

The goal was to create a system where important business rules are enforced by the **backend and database**, rather than relying only on the frontend.

---

# 🎯 What I Built

The application combines a customer-facing cinema experience with a protected staff administration environment.

The main customer journey is:

```text
Movie Discovery
      ↓
Movie Details
      ↓
Cinema & Showtime
      ↓
Seat Selection
      ↓
Checkout
      ↓
Server-Side Validation
      ↓
Booking Processing
      ↓
Digital Confirmation
```

Behind this interface, the Flask backend handles:

* Application routing
* Business logic
* Input validation
* Authentication
* Authorization
* Database operations
* Booking processing
* Seat availability
* Pricing calculation
* Security controls

---

# 🎬 Customer Experience

Customers can browse available movies and explore individual movie details.

The booking experience allows customers to:

* Discover movies
* View movie information
* Explore cinemas
* View available showtimes
* Select seats
* Review booking information
* Continue through checkout
* Create a reservation
* Receive a digital booking confirmation
* Retrieve reservations through protected lookup

The system is designed around a complete booking journey rather than a collection of disconnected pages.

---

# 💺 Interactive Seat Selection

One of the main components of CINEVO LUXE is the interactive seat-selection system.

Customers can view available seats and select the seats they want to reserve.

However, the frontend is **not treated as the final authority**.

When a booking is submitted, the backend validates the submitted seat information again.

The server checks:

* Whether submitted seat names are valid
* Whether duplicate seats were submitted
* Whether the seats follow the expected seat format
* Whether selected seats are already occupied
* Whether the seats belong to the expected showtime

This means a customer cannot simply bypass the normal interface and expect arbitrary seat information sent directly to the backend to be accepted.

---

# 💳 Server-Authoritative Checkout

The checkout system does not rely on a ticket total submitted by the browser.

Instead, the backend calculates the authoritative booking amount using validated booking information and the configured showtime price.

The basic flow is:

```text
Validated Seats
      ↓
Configured Showtime Price
      ↓
Server-Side Calculation
      ↓
Authoritative Booking Amount
```

This is important because values displayed or submitted by the browser can be modified by the user.

The server therefore remains responsible for determining the final booking amount.

---

# 🛡️ Booking Integrity & Double-Booking Protection

Seat availability is treated as a backend responsibility.

During booking processing, the application checks whether requested seats are already occupied before creating the reservation.

The booking process also uses transaction-aware database operations to help maintain consistency while reservations are being created.

This design helps reduce the possibility of inconsistent booking states and prevents the application from relying solely on what the frontend displays.

---

# 🎟️ Digital Booking Confirmation

After a successful booking, customers receive a dedicated confirmation page.

The confirmation contains reservation information including:

* Booking reference
* Movie
* Cinema
* Date
* Showtime
* Selected seats
* Customer information
* Total amount
* QR representation

The confirmation page also provides a print-friendly experience.

This completes the booking journey from movie discovery through reservation confirmation.

---

# 🔎 Protected Reservation Lookup

CINEVO LUXE includes a protected reservation lookup process.

Instead of exposing an unrestricted list of bookings, customers must provide identifying booking information such as:

* Booking reference
* Customer email or phone

This approach helps reduce unnecessary exposure of other customers' reservation information.

---

# 👨‍💼 Staff Administration Portal

The project includes a separate staff administration environment.

Authorized staff members can authenticate through protected staff routes and access administrative functionality.

The staff environment includes functionality related to:

* Staff authentication
* Administrative dashboard
* Movie management
* Cinema/showtime management
* Booking-related administration

The separation between customer-facing functionality and staff functionality demonstrates role-based access within the application.

---

# 🔐 Security Engineering

Security was treated as an important part of the application architecture rather than something added only after development.

## Authentication

Staff accounts use password hashing through **Werkzeug**.

Passwords are not intended to be stored as plaintext credentials.

## Authorization

Administrative functionality is protected through staff-only routes so that customer-facing users cannot simply access staff functionality.

## CSRF Protection

The application implements CSRF protection for protected state-changing requests.

CSRF tokens are generated and validated before relevant POST requests are processed.

## Server-Side Input Validation

Important client-submitted values are independently validated by the backend.

Validation includes areas such as:

* Seat information
* Duplicate seats
* Seat availability
* Customer information
* Booking parameters
* Promotional conditions
* Other booking-related values

## Secure Session Configuration

Authentication-related session configuration includes security-focused settings intended to reduce common session-related risks.

## Security Headers

The application includes security-related HTTP response headers to establish a stronger browser security baseline.

## Environment-Based Secret Management

Production-sensitive configuration is externalized from the source code.

The Flask secret key is supplied through an environment variable rather than being hardcoded into the application.

---

# 🧠 Security Lesson: Git History Matters

During development, I identified that a previously used development secret had existed in Git history.

Simply deleting the secret from the latest source code would not have been sufficient because the value could still exist in previous commits.

I therefore:

1. Generated a new production secret.
2. Rotated the production secret in the deployment environment.
3. Removed the exposed secret from Git history.
4. Rewrote the affected repository history.
5. Verified that the old secret could no longer be found in the rewritten history.
6. Force-updated the cleaned repository.

This reinforced an important software engineering principle:

> **Removing a secret from the current source code is not enough when that secret has already entered version-control history.**

---

# 🗄️ Database & Data Model

CINEVO LUXE uses **SQLite** with **SQLAlchemy** for database persistence and ORM-based data management.

The main application entities include:

### Movie

Represents movies available on the platform.

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

Represents staff authentication accounts and securely stored password information.

The database allows the application to perform real persistence and reservation operations rather than relying solely on static frontend data.

---

# 🏗️ Application Architecture

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
               Validation   Auth      Booking SQLite
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

The frontend provides the user experience while the backend remains responsible for enforcing important application rules.

---

# 🔄 Complete Booking Flow

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

This workflow connects the frontend, backend business logic, and database into one complete reservation system.

---

# 🛠️ Technology Stack

## Backend

* Python
* Flask
* Flask-SQLAlchemy
* SQLAlchemy
* Werkzeug

## Frontend

* HTML5
* CSS3
* JavaScript
* Responsive user interface
* Cinema-focused visual design

## Database

* SQLite

## Security

* Password hashing
* Authentication
* Authorization
* CSRF protection
* Server-side validation
* Security headers
* Secure session configuration
* Environment-based secrets
* Transaction-aware booking operations

## Development & Deployment

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
├── screenshots/
│   ├── addvenue.jpg
│   ├── catalog.jpg
│   ├── checkout.jpg
│   ├── checkoutdetails.jpg
│   ├── foodselection.jpg
│   ├── home.jpg
│   ├── moviedetail.jpg
│   ├── seatselection.jpg
│   ├── staffdashboard.jpg
│   └── staflogin.jpg
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── favicon.svg
│
└── templates/
    ├── home.html
    ├── movies.html
    ├── movie_details.html
    ├── showtimings.html
    ├── cinemas.html
    ├── offers.html
    ├── bookings.html
    ├── seat_selection.html
    ├── checkout.html
    ├── confirmation.html
    │
    └── staff/
        ├── login.html
        ├── dashboard.html
        ├── movies.html
        ├── bookings.html
        ├── cinemas.html
        ├── showtimes.html
        └── ...
```

> Local environment files, virtual environments, database files, and other sensitive/local artifacts are excluded from version control through `.gitignore`.

---

# 📸 Application Screenshots

The following screenshots demonstrate the main customer booking journey and staff administration experience.

## 🏠 Homepage

![CINEVO LUXE Homepage](screenshots/home.jpg)

The homepage establishes the CINEVO LUXE visual identity and provides the entry point to the cinema experience.

## 🎬 Movie Catalogue

![Movie Catalog](screenshots/catalog.jpg)

The movie catalogue allows customers to explore available movies.

## 🎞️ Movie Details

![Movie Details](screenshots/moviedetail.jpg)

The movie details page provides information about the selected movie and available booking options.

## 💺 Interactive Seat Selection

![Interactive Seat Selection](screenshots/seatselection.jpg)

The seat-selection interface allows customers to choose available seats before continuing to checkout.

## 💳 Checkout

![Checkout](screenshots/checkout.jpg)

The checkout interface brings together reservation details before the booking is processed.

## 🎟️ Booking Confirmation

![Digital Booking Confirmation](screenshots/checkoutdetails.jpg)

The confirmation page displays completed reservation information and the booking reference.

## 👨‍💼 Staff Dashboard

![Staff Dashboard](screenshots/staffdashboard.jpg)

The staff dashboard provides the administrative interface for authorized staff users.

---

# 🧪 Testing & Security Verification

Testing focused on both normal application functionality and security-sensitive backend behavior.

Testing areas included:

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

Dependency auditing was also used to identify known vulnerabilities in installed Python dependencies.

The purpose of testing was not only to verify that the application works under normal usage, but also to verify that important backend rules remain enforced when requests are manipulated or bypass the normal frontend flow.

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

## 5. Configure environment variables

Create a local `.env` file based on `.env.example`.

Example:

```text
SECRET_KEY=your-development-secret
```

Use your own secure values for local development.

**Never commit `.env` to Git.**

## 6. Start the application

```bash
python app.py
```

Open the local Flask address displayed in the terminal.

---

# ☁️ Production Deployment

CINEVO LUXE is deployed using **Render**.

🌐 **Live Application:**
https://cinevo-luxe.onrender.com

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

This demonstrates the transition from local development to a publicly accessible web application.

---

# 💡 Engineering Decisions

Several implementation decisions were made to make the application more reliable and closer to real-world web development.

### The browser is not trusted

The frontend provides the user experience, but important application rules are enforced by the backend.

### Prices are calculated server-side

The server determines the authoritative booking amount instead of trusting browser-submitted totals.

### Seats are independently validated

The frontend provides interactive selection, while the backend independently validates submitted seats.

### Authentication and authorization are separated

Successful authentication does not automatically mean that every application route is accessible.

### Secrets are externalized

Production secrets belong in the deployment environment rather than source code.

### Reservation lookup respects privacy

Customers must provide identifying booking information instead of receiving unrestricted access to reservation records.

### Database operations protect booking consistency

Reservation creation uses transaction-aware logic to help maintain consistent booking states.

---

# 📚 What I Learned

Building CINEVO LUXE helped me understand that developing a web application is not only about creating pages and connecting buttons.

The more important challenge is designing what happens **behind those pages**.

Through this project, I gained practical experience with:

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
* Working with Git and GitHub
* Deploying a web application
* Thinking about security from an engineering perspective

One of the most important lessons was understanding the difference between:

> **“The application works when I use it normally.”**

and:

> **“The application still behaves correctly when someone sends unexpected or manipulated input.”**

That distinction strongly influenced the backend design of CINEVO LUXE.

---

# 🟢 Project Status

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

# 🔮 Future Improvements

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

# 📄 License

This project is intended for educational, portfolio, and demonstration purposes.

---

# 🔐 Security Notice

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

# 👨‍💻 Project

## CINEVO LUXE

**Premium Cinema Ticket Booking & Reservation Management Platform**

Built with:

**Python · Flask · SQLAlchemy · SQLite · HTML · CSS · JavaScript**

🌐 **Live Demo:**
https://cinevo-luxe.onrender.com

💻 **Source Code:**
https://github.com/Yathusan-tech/cinevo-luxe

---

## ⭐ Project Highlights

**Full-Stack Application**
Customer-facing booking experience combined with a protected staff administration portal.

**Security-Focused Backend**
Server-side validation, CSRF protection, authentication, authorization, security headers, and environment-based secret management.

**Booking Integrity**
Backend-controlled seat validation, availability checks, authoritative pricing, and transaction-aware booking operations.

**Production Deployment**
Publicly deployed application with GitHub-based source control and Render deployment.

**Practical Engineering**
Designed to demonstrate how frontend functionality, backend business rules, database persistence, and security controls work together in a complete application.
