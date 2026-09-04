# 🎬 CINEVO LUXE

### Executive Cinema & Intelligent Ticket Reservation Platform

**CINEVO LUXE** is a full-stack cinema ticket reservation platform built with **Python, Flask, SQLAlchemy, SQLite, HTML5, CSS3, and Vanilla JavaScript**.

The project was designed to provide a premium cinema-booking experience while demonstrating practical full-stack engineering principles including **database-driven application design, authenticated staff administration, server-side validation, secure session handling, transaction-aware booking operations, responsive UI development, and cloud deployment**.

The platform covers the complete reservation lifecycle:

**Movie Discovery → Showtime Selection → Seat Selection → Checkout → Server Validation → Booking → Digital Confirmation → Reservation Lookup**

It also includes a dedicated **staff administration portal** for managing cinema content and monitoring reservations.

---

## 🌐 Live Application

**[Visit CINEVO LUXE](https://cinevo-luxe.onrender.com)**

---

# 📌 Project Overview

CINEVO LUXE was developed to go beyond a basic movie-ticket booking interface.

The application combines a **luxury executive cinema design** with a structured backend capable of handling real booking workflows.

The system separates customer-facing functionality from staff administration while maintaining a shared backend and database architecture.

A major engineering principle throughout the project is:

> **The browser improves the user experience, but the server makes the final decision.**

Critical information such as seat availability, duplicate seats, showtime validity, and booking prices is validated on the server rather than being trusted from client-side values.

This approach helps protect the integrity of the booking workflow against manipulated browser requests and conflicting reservations.

---

# 🎯 Project Objectives

The primary objectives of CINEVO LUXE were to:

* Build a complete full-stack cinema reservation workflow.
* Create a premium and responsive cinema user interface.
* Implement database-driven movie, cinema, showtime, and booking management.
* Provide secure staff authentication and protected administration routes.
* Ensure booking prices are calculated and validated server-side.
* Prevent duplicate and conflicting seat reservations.
* Protect sensitive application configuration using environment variables.
* Deploy the application as a live cloud-hosted service.
* Apply practical web application security principles throughout the system.

---

# ✨ Core Features

## 🎬 1. Movie Discovery

Customers can explore available movies through a structured movie catalog.

Features include:

* Movie browsing
* Search functionality
* Genre filtering
* Category filtering
* Movie detail pages
* Featured movie presentation
* Trailer integration
* Cinema and showtime information

The interface is designed to provide a commercial-style movie discovery experience rather than a simple database listing.

---

## ⚡ 2. Quick Reservation

The quick reservation workflow allows customers to begin booking directly by selecting:

**Movie → Date → Cinema → Showtime**

This reduces unnecessary navigation and provides a streamlined path from movie discovery to ticket reservation.

---

## 📅 3. Dynamic Showtime System

Showtimes are generated from application data rather than relying entirely on static pages.

Customers can view:

* Screening dates
* Screening times
* Cinemas
* Cinema formats
* Ticket prices
* Available booking options

The application supports premium cinema experiences such as:

* IMAX
* Dolby Atmos
* Recliner / premium seating

The date interface is dynamically generated rather than relying on permanently hardcoded booking dates.

---

## 🪑 4. Interactive Seat Selection

Customers can visually select seats for a specific showtime.

The interface provides:

* Available seat visualization
* Occupied seat identification
* Multiple-seat selection
* Selection summary
* Real-time booking amount display

However, the client interface is not treated as the source of truth.

Before a reservation is committed, the backend validates the submitted seats again.

---

# 🛡️ 5. Server-Authoritative Booking

One of the key engineering decisions in CINEVO LUXE is keeping the backend authoritative over critical booking information.

The server validates:

* Seat identifiers
* Seat format
* Duplicate seat selections
* Showtime validity
* Seat availability
* Ticket pricing
* Customer booking information
* Final booking amount

For example, a customer cannot simply modify a browser-side price field and force the server to accept the manipulated amount.

The server calculates the authoritative booking total using trusted showtime and seat information.

This follows an important application-security principle:

> **Never trust security-critical values simply because they came from the client.**

---

# 🔒 6. Anti-Double-Booking Protection

Seat reservation integrity is handled through backend availability checks and database transaction handling.

During booking processing, the application:

1. Validates the requested showtime.
2. Validates the submitted seat identifiers.
3. Removes duplicate selections.
4. Checks whether requested seats are already occupied.
5. Calculates the authoritative booking price.
6. Performs the reservation within database transaction handling.
7. Rejects conflicting reservations instead of silently overwriting existing booking information.

This design helps reduce race-condition and double-booking scenarios.

---

# 💳 7. Secure Checkout

The checkout process collects the required customer information and displays the reservation summary.

The browser may submit booking information, but the final amount is recalculated and validated by the backend.

This prevents users from relying on manipulated client-side pricing values.

---

# 🎫 8. Digital Booking Confirmation

After a successful reservation, the application generates a dedicated digital confirmation page.

The confirmation can include:

* Unique booking reference
* Movie
* Cinema
* Date
* Showtime
* Selected seats
* Customer information
* Total amount
* QR admission representation

The confirmation interface follows a digital ticket / boarding-pass inspired design.

The page also provides a print-friendly presentation for reservation records.

---

# 🔎 9. Reservation Lookup

Customers can retrieve reservation information through the application's secure booking lookup workflow.

The lookup process is designed to avoid exposing an unrestricted list of customer bookings.

Reservation retrieval uses booking information and customer verification details rather than publicly displaying all reservations.

---

# 👨‍💼 Staff Administration Portal

CINEVO LUXE includes a separate authenticated administration environment for cinema operations.

### Staff functionality includes:

* Staff authentication
* Protected staff dashboard
* Movie management
* Adding movies
* Showtime generation
* Cinema management
* Reservation monitoring
* Customer reservation information
* Operational statistics
* Secure logout

The staff portal is separated from the customer-facing booking experience and protected by authenticated sessions.

---

# 🔐 Security Architecture

Security was considered as part of the application architecture rather than being added only at the deployment stage.

## Authentication

Staff authentication uses password hashing and verification through **Werkzeug Security**.

Plaintext application passwords are not intended to be stored in the repository.

---

## Session Security

The application uses security-focused session configuration including:

* HTTP-only cookies
* SameSite cookie configuration
* Secure cookies in the deployed environment
* Protected staff routes
* Session invalidation during logout

---

## CSRF Protection

State-changing POST requests are protected using CSRF validation.

Requests containing missing or invalid CSRF tokens are rejected by the application.

This helps protect sensitive operations such as:

* Staff authentication
* Booking processing
* Staff management operations
* Other state-changing requests

---

## Security Headers

The deployed application uses security-related HTTP response headers including:

* `X-Content-Type-Options`
* `X-Frame-Options`
* `Referrer-Policy`
* `Permissions-Policy`
* `Strict-Transport-Security`

Sensitive booking and staff-related pages also use restrictive cache-control headers to reduce the possibility of sensitive information remaining in browser caches.

---

## Environment-Based Secrets

Sensitive configuration is supplied through environment variables rather than being embedded directly in application source code.

Examples include:

```text
CINEVO_SECRET_KEY=<your-secret-value>
STAFF_ADMIN_PASS=<your-secure-password>
```

Production secrets are intentionally excluded from the repository.

> **No real passwords, API keys, secret keys, authentication tokens, or `.env` files should be committed to source control.**

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
          ┌───────────────────┼───────────────────┐
          │                   │                   │
        Routes          Authentication       Booking Logic
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
                       SQLAlchemy ORM
                              │
                              ▼
                           SQLite
                              │
          ┌────────────┬────────────┬────────────┐
          │            │            │            │
        Movies      Cinemas     Showtimes     Bookings
                                                   
                              │
                              ▼
                            Staff
```

The architecture separates major responsibilities while keeping the customer and staff workflows connected through the same backend and database layer.

---

# 🧱 Data Model

The application uses database-backed entities for the primary cinema workflow.

Core models include:

* **Movie** — movie information and catalog data.
* **Cinema** — cinema and screening-location information.
* **Showtime** — movie screening schedules and pricing.
* **Booking** — customer reservations and booking information.
* **StaffUser** — authenticated staff accounts.

SQLAlchemy provides the ORM layer between the Flask application and SQLite database.

---

# 🛠️ Technology Stack

| Area                 | Technology         |
| -------------------- | ------------------ |
| Programming Language | Python             |
| Backend Framework    | Flask              |
| ORM                  | Flask-SQLAlchemy   |
| Database             | SQLite             |
| Authentication       | Werkzeug Security  |
| Frontend             | HTML5              |
| Styling              | CSS3               |
| Client-side Logic    | Vanilla JavaScript |
| Configuration        | python-dotenv      |
| Version Control      | Git                |
| Repository           | GitHub             |
| Deployment           | Render             |

The frontend intentionally uses **Vanilla JavaScript** rather than a large frontend framework, keeping the application lightweight and maintaining a straightforward architecture.

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

> The repository structure may evolve as the application continues to be developed.

---

# 📧 Digital Ticket Delivery

CINEVO LUXE supports optional automated digital ticket delivery through **Email and WhatsApp**.

Notification integrations are configured through environment variables rather than hardcoded credentials.

Supported configuration can include:

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

These are **example placeholders only**.

If notification credentials are not configured, the application can still provide the on-screen digital booking confirmation and QR representation without blocking the booking workflow.

---

# 🧪 Testing & Security Verification

The application has been tested across both customer and staff workflows.

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

## Booking Integrity Tests

Testing includes scenarios such as:

* Valid seat selection
* Multiple-seat selection
* Duplicate seat submissions
* Already occupied seats
* Invalid seat identifiers
* Manipulated client-side prices
* Missing CSRF tokens
* Invalid booking information
* Conflicting reservation attempts
* Unique booking reference generation

## Staff Security Tests

The staff portal is tested to verify that:

* Unauthenticated users cannot access protected staff pages.
* Valid authentication permits authorized access.
* Invalid credentials are rejected.
* Missing CSRF tokens are rejected for protected POST requests.
* Logout invalidates the authenticated session.
* Protected pages remain inaccessible after logout.
* Staff functionality is separated from the customer interface.

---

# 🚀 Getting Started

## Prerequisites

Install:

* Python 3.10+
* pip
* Git

## Clone the Repository

```bash
git clone https://github.com/Yathusan-tech/cinevo-luxe.git
cd cinevo-luxe
```

## Create a Virtual Environment

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

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a local `.env` file based on `.env.example`.

Example:

```env
CINEVO_SECRET_KEY=<your-secret-value>
STAFF_ADMIN_PASS=<your-secure-password>
```

Never commit the real `.env` file or real credentials.

## Run the Application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

# 🌐 Deployment

CINEVO LUXE is deployed as a live web application using **Render**.

### Production Environment

```text
https://cinevo-luxe.onrender.com
```

The project uses Git and GitHub for version control and source management, with the deployed application connected to the repository.

Production configuration and secrets are maintained through environment variables rather than source-controlled files.

---

# 💡 Engineering Highlights

CINEVO LUXE demonstrates practical experience across several areas of full-stack development.

### Full-Stack Development

Designed and implemented a complete application connecting frontend interfaces, backend routes, database operations, authentication, and deployment.

### Backend Engineering

Built Flask routes and application logic for movies, cinemas, showtimes, bookings, checkout, confirmation, reservation lookup, and staff administration.

### Database Integration

Implemented a relational database architecture using SQLAlchemy and SQLite for persistent application data.

### Secure Booking Architecture

Designed the booking process so critical values such as seat availability and final pricing are validated server-side.

### Authentication & Authorization

Implemented protected staff routes, password hashing, authenticated sessions, CSRF protection, and secure logout behavior.

### Transaction-Aware Reservations

Applied database transaction handling and seat-availability checks to improve reservation consistency and reduce conflicting bookings.

### Responsive UI Engineering

Developed a premium responsive cinema interface using HTML, CSS, and Vanilla JavaScript.

### Security Engineering

Applied practical protections including environment-based secrets, security headers, secure cookies, CSRF validation, controlled error handling, sensitive-page cache protection, and server-side validation.

### Cloud Deployment

Configured the application for production deployment using Render and environment-based configuration.

### Version-Controlled Development

Maintained the project using Git and GitHub, allowing application changes to be tracked, reviewed, and deployed systematically.

---

# 📸 Screenshots

Recommended screenshots for demonstrating the project include:

### Customer Experience

* Homepage
* Movie catalog
* Movie details
* Showtime selection
* Interactive seat selection
* Checkout
* Booking confirmation
* Reservation lookup

### Staff Experience

* Staff login
* Staff dashboard
* Movie management
* Showtime management
* Reservation management

Screenshots provide recruiters and technical reviewers with an immediate understanding of the application's interface and functionality.

---

# 📊 Project Status

### 🟢 Active Development / Live Demonstration

CINEVO LUXE currently provides a complete cinema reservation workflow together with a protected staff administration environment.

The project demonstrates practical implementation across:

**Frontend Development · Backend Development · Database Integration · Authentication · Booking Systems · Application Security · Responsive UI · Git · GitHub · Cloud Deployment**

---

# 🎬 Project

**CINEVO LUXE** demonstrates the development of a production-oriented full-stack web application combining premium user experience with reliable backend functionality.

The project focuses on practical implementation of:

**Web Application Architecture · Database-Driven Workflows · Authentication · Booking Integrity · Server-Side Validation · Application Security · Responsive UI · Version Control · Cloud Deployment**

---

# 📄 License

This project is intended for **educational, portfolio, and demonstration purposes**.

---

# 🔐 Security Notice

**Never commit sensitive information to this repository.**

This includes:

* Passwords
* API keys
* Secret keys
* Database credentials
* Authentication tokens
* `.env` files
* Private deployment configuration

Use environment variables and secure deployment configuration for sensitive values.

**Security is treated as an application requirement, not as an afterthought.**
