# Cinevo Luxe — Executive Cinema & Ticket Booking Platform

**Cinevo Luxe** is a premier, luxury movie ticket reservation platform engineered with Flask, SQLAlchemy, and a bespoke executive dark-and-gold aesthetic. The platform delivers an end-to-end luxury booking flow featuring interactive seat allocation, atomic anti-double-booking protection, dynamic showtime management, and a secure administration console.

🌐 Live Website

👉  https://cinevo-luxe.onrender.com

---

## 🏛️ Key Features

### 🌟 Executive Customer Portal
* **Approved Luxury Design:** Dark surface palette (`#07090e`, `#0f131c`, `#151a26`) accented with refined gold gradients (`#eed285` to `#b88e28`).
* **Interactive Hero & Carousels:** High-impact featured movie showcase, official trailer integration, and category carousels (*Now Showing*, *Premiere Screenings*, *IMAX Experience*).
* **Quick Reserve Bar:** Real-time dropdown selector for Movie, Date, Cinema Venue, and Show Timing.
* **Curated Movie Catalog:** Filter titles by genre, category, or search term with high-resolution poster artwork.
* **Date-Driven Showtime Schedule:** 7-day navigation matrix displaying venue formats (*Dolby Atmos*, *IMAX Laser*, *Recliner Suites*).
* **Interactive Executive Seat Map:** Real-time visual seat layout (Rows A–E) with live pricing calculation and locked seat protection.
* **Anti-Double-Booking Protection:** Server-side atomic validation ensuring no two guests can reserve the same seat simultaneously.
* **Executive Boarding Pass:** Instant booking confirmation receipt complete with unique reference code (e.g. `CNV-778201`), cinema location, and breakdown.
* **Customer Reservation History:** Search bookings by reference ID, phone number, email address, or guest name.

### 🔐 Staff & Administration Portal
* **Secure Authentication:** Password verification via Werkzeug cryptographic hashing.
* **Live Operations Metrics:** Real-time tracking of active movie titles, reservations, and partner cinemas.
* **Movie Management:** Add new movies with automated 7-day schedule generation across all active partner venues.
* **Live Reservation Audit:** Complete guest log detailing passenger information, confirmed seats, and amounts.

---

## 🛠️ Technology Stack

* **Backend:** Python 3.10+, Flask 3.x
* **Database & ORM:** SQLite / Flask-SQLAlchemy 3.x
* **Security & Auth:** Werkzeug Security (SHA256 password hashing), Session-based auth
* **Frontend:** Semantic HTML5, CSS3 Custom Properties, Vanilla JavaScript (zero heavy JS dependencies)
* **Configuration:** Python-Dotenv

---

## 📂 Project Structure

```text
movie-ticket-web/
│
├── app.py                  # Main Flask application and route controllers
├── models.py               # SQLAlchemy database models (Movie, Cinema, Showtime, Booking, Staff)
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore configuration
├── README.md               # Project documentation
│
├── instance/
│   └── database.db         # Authoritative SQLite database (auto-seeded on launch)
│
├── static/
│   └── css/
│       └── style.css       # Master gold styling and layout helpers
│
└── templates/
    ├── home.html           # Approved Cinevo Luxe Homepage
    ├── movies.html         # Curated Movie Catalog & Filters
    ├── movie_details.html  # Movie Overview & Venue Schedule
    ├── showtimings.html    # 7-Day Showtimes Matrix
    ├── cinemas.html        # Partner Luxury Venues & Amenities
    ├── offers.html         # VIP Lounge & Cardholder Privileges
    ├── seat_selection.html # Interactive Seat Layout
    ├── checkout.html       # Guest Details & Billing Breakdown
    ├── confirmation.html   # Executive Boarding Pass / Receipt
    ├── my_bookings.html    # Customer Booking Lookup & History
    ├── staff_login.html    # Secure Staff Portal Login
    ├── staff_dashboard.html# Staff Management Console
    ├── 404.html            # Luxury 404 Error Page
    └── 500.html            # Luxury 500 Error Page
```

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.10 or newer
* `pip` (Python package manager)

### 2. Installation

1. Open your terminal in the project directory:
   ```bash
   cd movie-ticket-web
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS / Linux:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create local environment configuration:
   ```bash
   cp .env.example .env
   ```

---

## 🎬 Running the Application

Start the Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

*The database (`instance/database.db`) will automatically initialize and seed with default luxury movies, cinemas, schedules, and staff credentials on first run.*

---

## 🔑 Default Staff Credentials

To access the Staff Management Portal (`/staff/login`):

* **Username:** `yathusan`
* **Password:** Configured securely through the `STAFF_ADMIN_PASS` environment variable.

*(You can update or add credentials in the database or via environment variables.)*

---

## 🧪 Verification & Testing Flow

1. **Homepage:** Navigate to `http://127.0.0.1:5000` to browse movies and view the hero section.
2. **Explore Catalog:** Click **Explore Movies** (`/movies`) and filter by *Premiere* or *IMAX*.
3. **Movie Schedule:** Select any movie (e.g. *Avengers: Endgame*) to view venue showtimes.
4. **Seat Allocation:** Select a showtime to load the interactive seat layout (`/seat-selection/<id>`).
5. **Checkout & Reservation:** Select your seats, enter guest details, and submit.
6. **Boarding Pass:** Verify your confirmation receipt and reference ID.
7. **Anti-Double-Booking Test:** Attempt to book the same seats on another browser tab — notice the server atomically blocks duplicate reservations.
8. **Staff Portal:** Visit `/staff/login`, authenticate, view the new reservation in real-time, and schedule new titles.
