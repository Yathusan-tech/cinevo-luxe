# 🎬 CINEVO LUXE

### Premium Cinema Ticket Booking & Reservation Management Platform

**CINEVO LUXE** is a full-stack movie ticket booking platform that I designed and developed using **Python, Flask, SQLAlchemy, SQLite, HTML5, CSS3, and Vanilla JavaScript**.

The project was built to simulate a real-world cinema reservation platform rather than a basic CRUD application. It combines a premium cinema-style user interface with a backend designed around **booking integrity, server-side validation, authentication, database transactions, and secure application configuration**.

🌐 **Live Demo:** https://cinevo-luxe.onrender.com

---

## 📌 What is CINEVO LUXE?

CINEVO LUXE allows customers to discover movies, explore cinemas and showtimes, select seats, complete checkout, receive a digital booking confirmation, and retrieve their reservations.

The platform also provides a separate **staff administration portal** for managing cinema content and monitoring reservations.

### Complete booking workflow

```text
Movie Discovery
      ↓
Movie Details
      ↓
Showtime Selection
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
      ↓
Reservation Lookup
```

The central engineering principle behind the booking system is:

> **The browser improves the user experience, but the server makes the final decision.**

Critical values such as seat availability and booking prices are therefore validated by the backend instead of being blindly trusted from the browser.

---

# 🎯 Why I Built This Project

I wanted to build more than a movie-ticket UI.

The goal was to create a complete application that demonstrates how a real-world web product connects:

* Frontend user experience
* Backend application logic
* Relational database design
* Authentication and authorization
* Booking workflows
* Server-side validation
* Transaction handling
* Application security
* Responsive UI
* Cloud deployment
* Version-controlled development

This project gave me practical experience in designing and connecting these components into one working application.

---

# 🚀 What I Implemented

## 🎬 1. Movie Discovery

I implemented a movie discovery experience where users can:

* Browse movies
* Search movies
* Filter by genre
* Filter by category
* View movie details
* View featured movies
* Access trailer information
* Explore cinema and showtime information

The interface was designed around a **premium/luxury cinema aesthetic** rather than a simple database listing.

---

## ⚡ 2. Quick Reservation

Users can quickly start a reservation by selecting:

```text
Movie → Date → Cinema → Showtime
```

This reduces unnecessary navigation and creates a direct path from movie discovery to ticket booking.

---

## 📅 3. Dynamic Showtime System

The application uses database-driven showtime information.

Users can view:

* Screening dates
* Screening times
* Cinemas
* Cinema formats
* Ticket prices
* Available booking options

The application also supports premium cinema experiences such as:

* IMAX
* Dolby Atmos
* Premium/Recliner seating

The booking-date interface is dynamically generated instead of depending entirely on permanently hardcoded dates.

---

# 🪑 4. Interactive Seat Selection

I implemented an interactive seat-selection workflow for individual showtimes.

Customers can:

* View available seats
* Identify occupied seats
* Select multiple seats
* Review their selection
* See the booking amount update during selection

However, the browser is **not treated as the authority for seat availability**.

The backend validates the submitted seats again before creating a reservation.

---

# 🛡️ 5. Server-Authoritative Booking

One of the most important engineering decisions in CINEVO LUXE is that the **server remains authoritative over critical booking information**.

The backend validates:

* Seat identifiers
* Seat format
* Duplicate seat selections
* Showtime validity
* Seat availability
* Ticket pricing
* Customer booking information
* Final booking amount

For example, a user cannot simply modify a browser-side price and expect the server to accept that manipulated value.

The backend calculates the authoritative booking total from trusted showtime and seat information.

### Design principle

```text
Client
  ↓
Request
  ↓
Server Validation
  ↓
Database Checks
  ↓
Authoritative Calculation
  ↓
Booking
```

This was intentionally designed to avoid relying on client-side values for security-critical decisions.

---

# 🔒 6. Double-Booking Protection

I designed the booking workflow to reduce conflicting seat reservations.

During booking processing, the application:

1. Validates the requested showtime.
2. Validates seat identifiers.
3. Removes duplicate selections.
4. Checks existing seat occupancy.
5. Calculates the authoritative booking price.
6. Performs reservation operations with database transaction handling.
7. Rejects conflicting reservations.

This approach improves reservation consistency and helps reduce double-booking scenarios.

---

# 💳 7. Checkout System

The checkout process collects customer information and presents a complete reservation summary.

The browser submits the required information, but the backend recalculates and validates the final booking amount.

This prevents client-side price manipulation from becoming the authoritative booking price.

---

# 🎫 8. Digital Booking Confirmation

After a successful reservation, the customer receives a dedicated digital confirmation page.

The confirmation can contain:

* Unique booking reference
* Movie
* Cinema
* Date
* Showtime
* Selected seats
* Customer information
* Total amount
* QR admission representation

The confirmation page uses a digital-ticket/boarding-pass inspired presentation and includes a print-friendly experience.

---

# 🔎 9. Reservation Lookup

I implemented a reservation lookup workflow rather than exposing an unrestricted list of customer bookings.

Customers can retrieve reservation information using booking information together with customer verification details.

This provides a more privacy-conscious approach to reservation retrieval.

---

# 👨‍💼 10. Staff Administration Portal

CINEVO LUXE contains a separate authenticated staff environment.

Staff functionality includes:

* Staff login
* Protected dashboard
* Movie management
* Movie creation
* Showtime generation
* Cinema management
* Reservation monitoring
* Customer reservation information
* Operational statistics
* Secure logout

The staff portal is separated from the customer-facing booking experience and protected through authenticated sessions.

---

# 🔐 Security Engineering

Security was considered throughout the application rather than being treated only as a deployment concern.

## Authentication

Staff authentication uses password hashing and verification through **Werkzeug Security**.

Passwords are not intended to be stored as plaintext in the source repository.

## Session Security

The application uses security-focused session configuration including:

* HTTP-only cookies
* SameSite cookie configuration
* Secure cookies in the deployed environment
* Protected staff routes
* Session invalidation during logout

## CSRF Protection

State-changing POST requests are protected using CSRF validation.

Requests with missing or invalid CSRF tokens are rejected.

This protects operations such as:

* Authentication
* Booking processing
* Staff management operations
* Other state-changing requests

## Security Headers

The application uses security-related response headers including:

* `X-Content-Type-Options`
* `X-Frame-Options`
* `Referrer-Policy`
* `Permissions-Policy`
* `Strict-Transport-Security`

Sensitive booking and staff pages also use restrictive cache-control behaviour.

## Environment-Based Secrets

Sensitive configuration is supplied through environment variables rather than being embedded in application source code.

Example:

```env
CINEVO_SECRET_KEY=<your-secret-value>
STAFF_ADMIN_PASS=<your-secure-password>
```

Real credentials, API keys, authentication tokens, and `.env` files are excluded from source control.

---

# 🏗️ Application Architecture

CINEVO LUXE follows a Flask-based server-rendered architecture.

```text
                         CINEVO LUXE
                              │
              ┌───────────────┴───────────────┐
              │                               │
       Customer Portal                  Staff Portal
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
                       Flask Application
                              │
              ┌───────────────┼───────────────┐
              │               │               │
            Routes       Authentication   Booking Logic
              │               │               │
              └───────────────┼───────────────┘
                              │
                              ▼
                       SQLAlchemy ORM
                              │
                              ▼
                            SQLite
                              │
             ┌────────────────┼────────────────┐
             │                │                │
          Movies          Showtimes         Bookings
             │                │                │
             └────────────────┼────────────────┘
                              │
                              ▼
                           Staff
```

The architecture keeps customer-facing and staff-facing workflows separated while allowing both to use the same backend and database layer.

---

# 🗄️ Database Design

The application uses **SQLAlchemy ORM with SQLite**.

### Core models

| Model       | Responsibility                                |
| ----------- | --------------------------------------------- |
| `Movie`     | Movie catalogue information                   |
| `Cinema`    | Cinema and screening-location information     |
| `Showtime`  | Screening schedules and ticket pricing        |
| `Booking`   | Customer reservations and booking information |
| `StaffUser` | Authenticated staff accounts                  |

The database provides persistent storage for the core cinema reservation workflow.

---

# 🛠️ Technology Stack

| Layer             | Technology         |
| ----------------- | ------------------ |
| Language          | Python             |
| Backend           | Flask              |
| ORM               | Flask-SQLAlchemy   |
| Database          | SQLite             |
| Authentication    | Werkzeug Security  |
| Frontend          | HTML5              |
| Styling           | CSS3               |
| Client-side Logic | Vanilla JavaScript |
| Configuration     | python-dotenv      |
| Version Control   | Git                |
| Repository        | GitHub             |
| Deployment        | Render             |

I intentionally used **Vanilla JavaScript** instead of a large frontend framework to keep the application lightweight and maintain a straightforward architecture.

---

# 📂 Project Structure

```text
movie-ticket-web/
│
├── app.py
├── models.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── instance/
│   └── database.db
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   └── favicon.svg
│
└── templates/
    ├── home.html
    ├── index.html
    ├── movies.html
    ├── movie_details.html
    ├── showtimings.html
    ├── cinemas.html
    ├── offers.html
    ├── seat_selection.html
    ├── seats.html
    ├── checkout.html
    ├── confirmation.html
    ├── bookings.html
    ├── my_bookings.html
    ├── 404.html
    ├── 500.html
    │
    └── staff/
        ├── base_staff.html
        └── login.html
```

> The structure may evolve as the project continues to be developed.

---

# 📧 Digital Ticket Delivery

CINEVO LUXE supports optional automated digital ticket delivery through email and WhatsApp integrations.

Configuration is handled through environment variables rather than hardcoded credentials.

Possible integrations include:

### Email

* Resend
* Brevo
* SendGrid
* SMTP

### WhatsApp

* Meta WhatsApp Cloud API
* Twilio WhatsApp

Example configuration:

```env
RESEND_API_KEY=re_your_resend_api_key

WHATSAPP_API_TOKEN=your_meta_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

These values are **placeholders only**.

If notification credentials are not configured, the application can still provide the on-screen digital booking confirmation and QR representation.

---

# 🧪 Testing & Validation

The application has been tested across customer and staff workflows.

## Customer Workflow

```text
Homepage
   ↓
Movie Discovery
   ↓
Movie Details
   ↓
Showtime Selection
   ↓
Seat Selection
   ↓
Checkout
   ↓
Server Validation
   ↓
Booking Processing
   ↓
Confirmation
   ↓
Reservation Lookup
```

## Booking Integrity Scenarios

Testing includes:

* Valid seat selection
* Multiple-seat selection
* Duplicate seat submissions
* Already occupied seats
* Invalid seat identifiers
* Manipulated client-side prices
* Missing CSRF tokens
* Invalid booking information
* Conflicting reservation attempts
* Unique booking-reference generation

## Staff Security Scenarios

The staff portal is tested to verify that:

* Unauthenticated users cannot access protected pages
* Valid authentication permits authorized access
* Invalid credentials are rejected
* Missing CSRF tokens are rejected for protected POST requests
* Logout invalidates the authenticated session
* Protected pages remain inaccessible after logout
* Staff functionality remains separated from the customer interface

---

# 🚀 Running Locally

## Prerequisites

* Python 3.10+
* pip
* Git

## 1. Clone the repository

```bash
git clone https://github.com/Yathusan-tech/cinevo-luxe.git
cd cinevo-luxe
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a local `.env` file based on `.env.example`.

```env
CINEVO_SECRET_KEY=<your-secret-value>
STAFF_ADMIN_PASS=<your-secure-password>
```

**Never commit the real `.env` file or production credentials.**

## 5. Start the application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# 🌐 Deployment

The application is deployed using **Render**.

### Production application

https://cinevo-luxe.onrender.com

The project uses Git and GitHub for source control, while production configuration and sensitive values are maintained through environment variables.

---

# 💡 Key Engineering Highlights

### Full-Stack Development

Designed and connected a complete frontend, backend, database, authentication, booking workflow, and deployment environment.

### Backend Engineering

Implemented Flask routes and application logic covering:

```text
Movies
Cinemas
Showtimes
Seat Selection
Checkout
Bookings
Confirmation
Reservation Lookup
Staff Administration
```

### Booking Integrity

Designed the booking workflow so that critical information is validated on the server instead of relying on browser-controlled values.

### Database Engineering

Used SQLAlchemy ORM and SQLite to implement persistent database-backed cinema and reservation functionality.

### Authentication & Authorization

Implemented protected staff routes, password hashing, authenticated sessions, CSRF protection, and secure logout behaviour.

### Transaction-Aware Reservations

Used database transaction handling and seat availability checks to improve reservation consistency.

### Security Engineering

Applied practical security controls including:

* Environment-based secrets
* CSRF validation
* Secure cookies
* Security headers
* Server-side validation
* Controlled error handling
* Sensitive-page cache protection
* Authentication and authorization controls

### Responsive UI Engineering

Created a premium cinema interface using HTML, CSS, and Vanilla JavaScript with responsive layouts and interactive booking components.

### Cloud Deployment

Configured the application for production deployment using Render and environment-based configuration.

### Version-Controlled Development

Maintained the application with Git and GitHub, allowing development changes to be tracked and deployed systematically.

---

# 📸 Screenshots

Recommended screenshots for the project portfolio:

### Customer Experience

* Homepage
* Movie catalogue
* Movie details
* Showtime selection
* Seat selection
* Checkout
* Booking confirmation
* Reservation lookup

### Staff Experience

* Staff login
* Staff dashboard
* Movie management
* Showtime management
* Reservation management

Screenshots demonstrate both the visual design and the functional depth of the application.

---

# 📊 Project Status

### 🟢 Live & Actively Developed

CINEVO LUXE currently provides a complete cinema reservation workflow together with a protected staff administration environment.

The project demonstrates practical experience across:

**Frontend Development · Backend Development · Database Integration · Authentication · Booking Systems · Server-Side Validation · Application Security · Responsive UI · Git · GitHub · Cloud Deployment**

---

# 🎓 What This Project Demonstrates

CINEVO LUXE demonstrates my ability to work across the complete lifecycle of a web application:

```text
                    CINEVO LUXE
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
   Frontend           Backend           Database
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                  Security & Auth
                         │
                  Booking Integrity
                         │
                    Deployment
                         │
                    Git / GitHub
```

Rather than focusing only on the visual interface, I designed the application around the engineering concerns that appear in real-world systems: **validation, data integrity, authentication, authorization, secure configuration, reservation consistency, and maintainable application structure**.

---

# 📄 License

This project is intended for **educational, portfolio, and demonstration purposes**.

---

# 🔐 Security Notice

Never commit sensitive information to this repository.

This includes:

* Passwords
* API keys
* Secret keys
* Database credentials
* Authentication tokens
* `.env` files
* Private deployment configuration

Sensitive configuration should always be supplied through secure environment variables or deployment configuration.

> **Security is treated as an application requirement, not an afterthought.**

---

## 👨‍💻 Project

**CINEVO LUXE**
Premium Cinema Ticket Booking & Reservation Management Platform

Built with **Python · Flask · SQLAlchemy · SQLite · HTML · CSS · JavaScript**

🌐 **Live Demo:** https://cinevo-luxe.onrender.com
