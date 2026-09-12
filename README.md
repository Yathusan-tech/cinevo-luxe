# 🎬 CINEVO LUXE

### Full-Stack Cinema Ticket Booking & Reservation Platform

**CINEVO LUXE** is a full-stack cinema booking platform designed to demonstrate real-world web application development, including **backend business logic, database integration, secure booking workflows, authentication, authorization, and cloud deployment**.

The application provides a complete cinema reservation experience—from browsing movies and selecting showtimes to choosing seats, processing bookings, and generating digital confirmations.

It also includes a **protected staff administration portal** for managing movies, cinemas, showtimes, and booking-related operations.

### 🌐 Live Application

**[cinevo-luxe.onrender.com](https://cinevo-luxe.onrender.com)**

### 💻 Source Code

**[GitHub Repository](https://github.com/Yathusan-tech/cinevo-luxe)**

---

# 📌 Project Overview

CINEVO LUXE was built as more than a movie catalogue.

The main goal was to create a functional reservation system where important operations are enforced by the backend rather than relying only on browser-side controls.

The application separates responsibilities between:

* **Frontend presentation and interaction**
* **Flask backend business logic**
* **Database persistence**
* **Authentication and authorization**
* **Server-side validation**
* **Booking integrity controls**

> **The browser provides the interface. The server enforces the rules.**

---

# ✨ Key Features

## 🎟️ Customer Experience

* Browse available movies
* View detailed movie information
* Browse cinemas and showtimes
* Select seats interactively
* Validate seat availability
* Review booking details at checkout
* Calculate pricing on the server
* Create reservations
* Generate unique booking references
* View digital booking confirmations
* QR-based booking representation
* Protected reservation lookup
* Promotional and offer logic
* Food and refreshment selection

---

## 👨‍💼 Staff Administration

The application includes a separate staff environment protected by authentication and authorization.

Staff functionality includes:

* Secure staff login
* Protected dashboard
* Movie management
* Cinema management
* Showtime management
* Booking administration

Administrative routes are protected at the backend and cannot be accessed simply by hiding or modifying frontend links.

---

# 🏗️ System Architecture

```text
                         CINEVO LUXE
                                │
                                ▼
┌─────────────────────────────────────────────────────┐
│                     FRONTEND                        │
│                                                     │
│            HTML5 • CSS3 • JavaScript                │
│                                                     │
│ Movies → Showtimes → Seats → Checkout               │
└──────────────────────────┬──────────────────────────┘
                           │
                           │ HTTP Requests
                           ▼
┌─────────────────────────────────────────────────────┐
│                  FLASK APPLICATION                  │
│                                                     │
│ Routes • Business Logic • Validation                │
│ Authentication • Authorization • Booking Logic      │
│                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌────────────────┐  │
│ │ Customer    │ │ Booking     │ │ Staff/Admin    │  │
│ │ Routes      │ │ Processing  │ │ Routes         │  │
│ └─────────────┘ └─────────────┘ └────────────────┘  │
│                                                     │
│ Security Controls                                   │
│ • CSRF Protection                                   │
│ • Input Validation                                  │
│ • Session Security                                  │
│ • Security Headers                                  │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│                    DATA LAYER                       │
│                                                     │
│             Flask-SQLAlchemy / SQLAlchemy           │
│                                                     │
│ Movie • Cinema • Showtime • Booking • Staff         │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
                    SQLite Database
```

---

# 🔄 Complete Booking Workflow

The booking system was designed so that important user input is independently validated by the backend.

```text
Browse Movie
      │
      ▼
Select Showtime
      │
      ▼
Select Seats
      │
      ▼
Checkout
      │
      ▼
Server-Side Validation
      │
      ├── Validate customer information
      ├── Validate seat format
      ├── Detect duplicate seats
      ├── Verify showtime
      ├── Check seat availability
      └── Calculate authoritative price
      │
      ▼
Database Transaction
      │
      ▼
Create Booking
      │
      ▼
Generate Booking Reference
      │
      ▼
Digital Confirmation
```

This design ensures that the backend remains responsible for important business decisions.

---

# 💺 Seat Reservation & Booking Integrity

Seat selection is one of the core features of the application.

The frontend provides an interactive interface for selecting seats, but the backend independently validates submitted data.

### Backend validation includes:

* Valid seat format
* Duplicate seat detection
* Valid showtime verification
* Seat availability checks
* Booking consistency checks

```text
User selects:

A1, A2, A3

        │
        ▼

Backend receives request

        │
        ▼

✓ Validate seat format
✓ Reject duplicate seats
✓ Verify showtime
✓ Check availability

        │
        ▼

Create Reservation
```

The application does not rely solely on the visual state of the seat-selection interface.

---

# 💳 Server-Authoritative Pricing

The application does not blindly trust booking totals submitted by the browser.

Instead, the server calculates the booking amount using trusted application and database data.

```text
Selected Seats
       │
       ▼
Backend Validation
       │
       ▼
Configured Showtime Price
       │
       ▼
Server-Side Calculation
       │
       ▼
Authoritative Booking Total
```

This prevents client-side values from becoming the source of truth for booking prices.

---

# 🛡️ Double-Booking Protection

A reservation system must handle the possibility of multiple users attempting to reserve the same seat.

CINEVO LUXE performs seat availability checks on the backend before completing a reservation.

The booking process includes:

1. Validating submitted seats
2. Rejecting duplicate seat values
3. Checking existing reservations
4. Verifying seat availability
5. Creating booking records using database operations
6. Completing the reservation only after validation succeeds

This helps maintain consistent reservation data and reduces the risk of duplicate bookings.

---

# 🎟️ Digital Booking Confirmation

After a successful booking, the application generates a dedicated confirmation page.

The confirmation includes:

* Unique booking reference
* Movie information
* Cinema information
* Showtime details
* Selected seats
* Customer information
* Booking total
* QR representation

The confirmation page also supports a print-friendly experience.

---

# 🔎 Protected Reservation Lookup

Customer booking information is not exposed through an unrestricted public booking list.

Instead, reservation lookup requires identifying information.

```text
Booking Reference
        +
Customer Information
        │
        ▼
Backend Verification
        │
        ▼
Matching Reservation
        │
        ▼
Booking Details
```

This provides a more controlled approach to accessing reservation information.

---

# 🔐 Security Implementation

Security considerations were incorporated into backend development and booking workflows.

## Authentication

Staff authentication is implemented using **Werkzeug password hashing**.

Passwords are handled using hashed credentials rather than plaintext password storage.

---

## Authorization

Staff functionality is protected through backend authorization checks.

Authentication and authorization are treated as separate responsibilities.

Protected routes verify that the current session has appropriate access.

---

## CSRF Protection

Relevant state-changing requests use CSRF protection.

```text
POST Request
      │
      ▼
CSRF Token
      │
      ▼
Token Validation
      │
      ├── Valid → Continue
      │
      └── Invalid → Reject
```

---

## Server-Side Validation

Client input is treated as untrusted.

The backend independently validates important information, including:

* Seat selections
* Duplicate seats
* Booking parameters
* Customer information
* Promotional conditions
* Showtime information

---

## Security Headers

The application includes security-focused HTTP response headers to establish a stronger browser security baseline.

---

## Secure Session Configuration

Session configuration includes security-focused settings designed to reduce common session risks.

---

## Environment-Based Configuration

Sensitive production configuration is supplied through environment variables rather than being stored directly in source code.

```text
Application
     │
     ▼
Environment Configuration
     │
     ▼
Sensitive Production Values
```

Local environment files are excluded from version control.

---

# 🗄️ Database Design

CINEVO LUXE uses:

**SQLite + Flask-SQLAlchemy + SQLAlchemy**

Core entities include:

```text
                     DATABASE

      Movie ────────┐
                    │
      Cinema ─── Showtime
                    │
                    ▼
                 Booking

      StaffUser
          │
          ▼
   Staff Authentication
```

### Core Entities

| Entity                  | Responsibility                                   |
| ----------------------- | ------------------------------------------------ |
| **Movie**               | Stores movie information                         |
| **Cinema**              | Represents cinema venues                         |
| **Showtime**            | Connects movies, cinemas, schedules, and pricing |
| **Booking**             | Stores reservation and customer information      |
| **Seat Booking Record** | Helps track reserved seats and booking integrity |
| **Staff User**          | Supports protected staff authentication          |

---

# 🧠 Key Engineering Decisions

## 1. Do Not Trust the Browser

The frontend improves the user experience, but important values are validated on the backend.

---

## 2. Server-Side Pricing

Booking prices are calculated using trusted showtime data rather than relying on browser-submitted totals.

---

## 3. Independent Seat Validation

Seat selections are validated independently of the frontend interface.

---

## 4. Protected Administrative Routes

Staff functionality requires authentication and authorization.

---

## 5. CSRF Protection

Relevant state-changing requests are protected against cross-site request forgery.

---

## 6. Booking Integrity

Seat availability and booking consistency are checked before reservations are completed.

---

## 7. Environment-Based Configuration

Sensitive deployment configuration is kept outside source code and managed through environment variables.

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
* Responsive Design

### Database

* SQLite

### Security

* Password hashing
* Authentication
* Authorization
* CSRF protection
* Server-side validation
* Server-authoritative pricing
* Secure sessions
* Security headers
* Environment-based configuration

### Development & Deployment

* Git
* GitHub
* Render
* Gunicorn

---

# 📸 Application Screenshots

## 🏠 Homepage

![CINEVO LUXE Homepage](screenshots/home.png)

---

## 🎬 Movie Catalogue

![Movie Catalogue](screenshots/movies.png)

---

## 🎞️ Movie Details

![Movie Details](screenshots/movie-details.png)

---

## 💺 Interactive Seat Selection

![Seat Selection](screenshots/seat-selection.png)

---

## 🍿 Food Selection

![Food Selection](screenshots/food-selection.png)

---

## 💳 Checkout

![Checkout](screenshots/checkout.png)

---

## 🎟️ Booking Confirmation

![Booking Confirmation](screenshots/booking-confirmation.png)

---

## 👨‍💼 Staff Dashboard

![Staff Dashboard](screenshots/staff-dashboard.png)

---

# 🧪 Testing & Verification

The project was tested against both normal application workflows and security-sensitive scenarios.

### Functional Testing

* Application startup
* Core route behavior
* Movie browsing
* Movie details
* Cinema handling
* Showtime handling
* Seat selection
* Checkout workflow
* Booking processing
* Booking confirmation
* Reservation lookup
* Staff authentication
* Staff administration

### Backend & Security Testing

* Invalid seat submissions
* Duplicate seat submissions
* Already-reserved seats
* Manipulated booking parameters
* CSRF validation
* Unauthorized staff access
* Invalid routes
* Security headers
* Database integrity
* Environment-based configuration

The goal of testing was not only to verify normal functionality, but also to confirm that backend rules remain enforced when requests are modified or routes are accessed directly.

---

# 📁 Project Structure

```text
cinevo-luxe/
│
├── app.py
├── models.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── screenshots/
│
├── static/
│   ├── css/
│   ├── images/
│   ├── js/
│   └── favicon.svg
│
└── templates/
    ├── base.html
    ├── home.html
    ├── movies.html
    ├── movie_details.html
    ├── cinemas.html
    ├── showtimings.html
    ├── seat_selection.html
    ├── checkout.html
    ├── confirmation.html
    ├── manage_booking.html
    └── staff/
```

> Local environment files, database files, virtual environments, backups, and other machine-specific artifacts are excluded from version control.

---

# 🚀 Running Locally

## 1. Clone the Repository

```bash
git clone https://github.com/Yathusan-tech/cinevo-luxe.git
cd cinevo-luxe
```

## 2. Create a Virtual Environment

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

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a local `.env` file using `.env.example` as a reference.

Example:

```text
SECRET_KEY=replace_with_a_secure_random_secret
```

Use your own secure value.

**Never commit `.env` files to Git.**

## 5. Run the Application

```bash
python app.py
```

Open the local URL displayed in the terminal.

---

# ☁️ Deployment

The application is deployed as a live web application.

```text
Local Development
       │
       ▼
      Git
       │
       ▼
    GitHub
       │
       ▼
    Render
       │
       ▼
 Live Production Application
```

### 🌐 Live Application

**https://cinevo-luxe.onrender.com**

---

# 📚 What This Project Demonstrates

This project demonstrates practical experience in:

### Full-Stack Development

Building a complete web application connecting frontend interfaces, backend services, and persistent data.

### Backend Engineering

Implementing routes, business logic, validation, authentication, authorization, and booking workflows.

### Database Development

Designing and working with relational data using SQLAlchemy and SQLite.

### Application Security

Implementing:

* Password hashing
* Authentication
* Authorization
* CSRF protection
* Server-side validation
* Secure session configuration
* Security headers
* Environment-based configuration

### Booking System Design

Handling:

* Seat selection
* Seat availability
* Reservation processing
* Server-side pricing
* Booking references
* Booking confirmation

### Cloud Deployment

Deploying a Flask application from local development through GitHub to a publicly accessible production environment.

---

# 🎯 Key Lessons Learned

One of the most important lessons from building CINEVO LUXE was understanding that users do not always interact with an application exactly as the frontend intends.

Requests can be modified, values can be manipulated, and routes can be accessed directly.

This led to an important design principle used throughout the project:

> **Frontend controls improve the user experience. Backend controls protect the application.**

Building this project also provided practical experience with the complete development lifecycle:

```text
Design
  ↓
Frontend Development
  ↓
Backend Development
  ↓
Database Integration
  ↓
Validation & Security
  ↓
Testing
  ↓
Git & GitHub
  ↓
Cloud Deployment
  ↓
Live Application
```

---

# 🔮 Future Improvements

The current architecture can be extended with:

* Online payment gateway integration
* Automated email ticket delivery
* Expanded staff management
* Advanced analytics and reporting
* Additional automated testing
* Production monitoring
* Notification systems
* Expanded reservation management

These features can be added without replacing the core booking architecture.

---

# 👨‍💻 Skills Demonstrated

**Python • Flask • SQLAlchemy • SQLite • HTML5 • CSS3 • JavaScript**

**Full-Stack Development • Backend Engineering • Database Design • Authentication • Authorization • Application Security • CSRF Protection • Server-Side Validation • Booking Systems • Git • GitHub • Cloud Deployment**

---

# ⭐ Final Summary

**CINEVO LUXE is a full-stack cinema reservation platform built to demonstrate practical software engineering beyond static frontend development.**

The project combines:

* 🎨 **Frontend user experience**
* ⚙️ **Backend business logic**
* 🗄️ **Database persistence**
* 💺 **Interactive seat reservation**
* 💳 **Server-side pricing**
* 🔐 **Authentication and security controls**
* 👨‍💼 **Protected staff administration**
* 🧪 **Functional and security-focused testing**
* ☁️ **Cloud deployment**

> **CINEVO LUXE demonstrates how a real-world web application can combine user experience, backend logic, data integrity, security controls, and cloud deployment into one complete system.**

---

## 🌐 Live Application

**https://cinevo-luxe.onrender.com**

## 💻 Source Code

**https://github.com/Yathusan-tech/cinevo-luxe**
