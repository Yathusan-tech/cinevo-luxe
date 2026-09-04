import os
import re
import ssl
import json
import uuid
import secrets
import shutil
import smtplib
import urllib.parse
import urllib.request
import urllib.error
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from datetime import datetime, date, timedelta

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    send_from_directory
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from models import (
    db,
    Customer,
    Movie,
    Cinema,
    Showtime,
    Booking,
    SeatBookingRecord,
    Staff
)


# ============================================================
# APP CREATION
# ============================================================

def create_app():

    app = Flask(__name__)

    # --------------------------------------------------------
    # CONFIGURATION
    # --------------------------------------------------------

    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() in ["true", "1", "t"]
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    instance_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "instance"
    )

    os.makedirs(instance_path, exist_ok=True)

    db_path = os.path.join(
        instance_path,
        "database.db"
    )

    # Preserve existing uploaded database.db into instance/database.db if needed
    root_db = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "database.db"
    )
    if not os.path.exists(db_path) and os.path.exists(root_db):
        try:
            shutil.copy2(root_db, db_path)
        except Exception:
            pass

    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    else:
        clean_db_path = db_path.replace("\\", "/")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{clean_db_path}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # CSRF Helper Function
    def get_csrf_token():
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_hex(32)
        return session["_csrf_token"]

    # Safe Jinja globals
    app.jinja_env.globals.update(
        int=int,
        float=float,
        round=round,
        str=str,
        len=len,
        csrf_token=get_csrf_token
    )

    @app.context_processor
    def inject_nav_data():
        try:
            active_movies = Movie.query.filter_by(status="Now Showing").all()
            if not active_movies:
                active_movies = Movie.query.all()
            active_cinemas = Cinema.query.filter_by(status="Active").all()
            if not active_cinemas:
                active_cinemas = Cinema.query.all()
        except Exception:
            active_movies = []
            active_cinemas = []
        return dict(nav_movies=active_movies, nav_cinemas=active_cinemas)

    # CSRF Protection Middleware for LIVE POST Forms
    @app.before_request
    def csrf_protect():
        if request.method == "POST":
            # Token from session
            session_token = session.get("_csrf_token")
            # Token from form or headers
            form_token = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")

            if not session_token or not form_token or not secrets.compare_digest(session_token, form_token):
                abort(400, description="CSRF validation failed: missing or invalid CSRF token.")

    db.init_app(app)

    # --------------------------------------------------------
    # DATABASE INITIALIZATION
    # --------------------------------------------------------

    with app.app_context():

        try:
            db.create_all()

            # Ensure all Booking table columns exist in SQLite database without data loss
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            if "bookings" in tables:
                columns = [col["name"] for col in inspector.get_columns("bookings")]
                with db.engine.connect() as conn:
                    if "customer_id" not in columns:
                        conn.execute(db.text("ALTER TABLE bookings ADD COLUMN customer_id INTEGER REFERENCES customers(id)"))
                    if "ticket_amount" not in columns:
                        conn.execute(db.text("ALTER TABLE bookings ADD COLUMN ticket_amount FLOAT DEFAULT 0.0"))
                    if "convenience_fee" not in columns:
                        conn.execute(db.text("ALTER TABLE bookings ADD COLUMN convenience_fee FLOAT DEFAULT 30.0"))
                    if "taxes" not in columns:
                        conn.execute(db.text("ALTER TABLE bookings ADD COLUMN taxes FLOAT DEFAULT 18.0"))
                    if "discount" not in columns:
                        conn.execute(db.text("ALTER TABLE bookings ADD COLUMN discount FLOAT DEFAULT 0.0"))
                    conn.commit()

            # Check database connectivity
            Staff.query.first()
            Movie.query.first()

        except Exception:
            db.session.rollback()

            # IMPORTANT:
            # We intentionally DO NOT drop the database.
            # Existing movies/bookings/staff must be preserved.
            try:
                db.create_all()
            except Exception:
                pass

        seed_initial_data()
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"

        # Prevent caching of sensitive transactional/staff pages
        sensitive_paths = (
            "/manage-booking",
            "/confirmation/",
            "/checkout",
            "/seat-selection/",
            "/staff/",
        )

        if request.path.startswith(sensitive_paths):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response

    return app
# ============================================================
# INITIAL DATA
# ============================================================

def seed_initial_data():
    """
    Create initial data only when the relevant tables are empty.

    IMPORTANT:
    Existing data is never deleted or overwritten.
    """

    # --------------------------------------------------------
    # STAFF
    # --------------------------------------------------------

    if not Staff.query.first():

        admin_user = os.environ.get("STAFF_ADMIN_USER", "yathusan").strip() or "yathusan"
        admin_pass = os.environ.get("STAFF_ADMIN_PASS")

        admin = Staff(username=admin_user)
        admin.set_password(admin_pass)

        db.session.add(admin)
        db.session.commit()

    # --------------------------------------------------------
    # CINEMAS
    # --------------------------------------------------------

    if not Cinema.query.first():

        cinemas = [

            Cinema(
                name="Cinevo Pallas Grand",
                location="Pallas Grand Tower, Nungambakkam",
                address="104 Nungambakkam High Road, Chennai, TN",
                city="Chennai",
                screen_name="LUXE Screen 1",
                screen_type="Dolby Atmos & Laser Projection",
                formats="Dolby Atmos, 4K Laser, Recliner",
                facilities="VIP Lounge, Artisanal F&B, Valet Parking",
                seat_capacity=40,
                status="Active"
            ),

            Cinema(
                name="Cinevo IMAX Signature",
                location="Express Avenue Signature Wing",
                address="49/50 Whites Road, Royapettah, Chennai, TN",
                city="Chennai",
                screen_name="IMAX Laser Auditorium",
                screen_type="IMAX with Laser 12-Ch Audio",
                formats="IMAX 4K Laser, 12-Channel Immersive Audio",
                facilities="Executive Concession, Reserved Lounge, Private Bar",
                seat_capacity=40,
                status="Active"
            ),

            Cinema(
                name="Cinevo Royal Suite",
                location="Phoenix Marketcity Luxury Pavilion",
                address="142 Velachery Main Road, Chennai, TN",
                city="Chennai",
                screen_name="Royal Gold Suite",
                screen_type="Full Recliner Executive Suite",
                formats="4K HDR, Dolby Atmos, Butler Service",
                facilities="Chef's Dining, Butler at Seat, Private Entrance",
                seat_capacity=32,
                status="Active"
            )

        ]

        db.session.add_all(cinemas)
        db.session.commit()

    # --------------------------------------------------------
    # MOVIES
    # --------------------------------------------------------

    if not Movie.query.first():

        movies = [

            Movie(
                title="Avengers: Endgame",
                genre="Action / Sci-Fi",
                rating=9.0,
                age_rating="UA 16+",
                duration="3h 1m",
                poster="https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_FMjpg_UX1000_.jpg",
                backdrop="https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_FMjpg_UX1000_.jpg",
                description="After the devastating events of Infinity War, the universe is in ruins. With the help of remaining allies, the Avengers assemble once more to reverse Thanos' actions and restore balance to the universe.",
                format="2D • 3D • ATMOS",
                category="now_showing",
                trailer_url="https://www.youtube.com/embed/TcMBFSGVi1c?autoplay=1&rel=0",
                language="English / Tamil",
                cast="Robert Downey Jr., Chris Evans, Mark Ruffalo, Chris Hemsworth, Scarlett Johansson",
                director="Anthony Russo, Joe Russo",
                status="Now Showing"
            ),

            Movie(
                title="Attack on Titan: The Last Attack",
                genre="Dark Fantasy / Action / Mystery",
                rating=9.8,
                age_rating="UA 16+",
                duration="2h 25m",
                poster="https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcSvAzMxVb7pQUlHGjtC8do83vd-UClldQQivBaI3Dq1ny95Ewf4",
                backdrop="https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcSvAzMxVb7pQUlHGjtC8do83vd-UClldQQivBaI3Dq1ny95Ewf4",
                description="Humanity faces its final confrontation as the truth behind the Titans reaches its catastrophic climax. The ultimate clash for survival unfolds on the giant screen with remastered sound.",
                format="IMAX 3D • DOLBY ATMOS",
                category="now_showing",
                trailer_url="https://www.youtube.com/embed/M_OauHnAFc8?autoplay=1",
                language="Japanese (Eng Sub)",
                cast="Yuki Kaji, Yui Ishikawa, Marina Inoue, Hiroshi Kamiya",
                director="Yuichiro Hayashi",
                status="Now Showing"
            ),

            Movie(
                title="Dhurandhar: The Revenge",
                genre="Action / Thriller",
                rating=9.4,
                age_rating="A 18+",
                duration="3h 49m",
                poster="https://cdn.district.in/movies-assets/images/cinema/DD-1be608f0-1d22-11f1-96c9-4539b6d27dc7.jpg?im=Resize,width=400",
                backdrop="https://cdn.district.in/movies-assets/images/cinema/DD-1be608f0-1d22-11f1-96c9-4539b6d27dc7.jpg?im=Resize,width=400",
                description="An intense action thriller following a dangerous clandestine mission filled with espionage, revenge, and high-stakes tactical warfare across borders.",
                format="DOLBY ATMOS • LASER 4K",
                category="now_showing",
                trailer_url="https://www.youtube.com/embed/NHk7scrb_9I?autoplay=1",
                language="Hindi / Tamil",
                cast="Ranveer Singh, Sanjay Dutt, R. Madhavan, Akshaye Khanna",
                director="Aditya Dhar",
                status="Now Showing"
            ),

            Movie(
                title="Inception",
                genre="Sci-Fi / Action",
                rating=9.2,
                age_rating="UA 13+",
                duration="2h 28m",
                poster="https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=600&auto=format&fit=crop&q=80",
                backdrop="https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1200&auto=format&fit=crop&q=80",
                description="A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                format="IMAX 70mm • LASER 4K",
                category="premiere",
                trailer_url="https://www.youtube.com/embed/YoHD9XEInc0?autoplay=1",
                language="English",
                cast="Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page, Tom Hardy",
                director="Christopher Nolan",
                status="Now Showing"
            ),

            Movie(
                title="Interstellar",
                genre="Sci-Fi / Adventure",
                rating=9.5,
                age_rating="UA 13+",
                duration="2h 49m",
                poster="https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=600&auto=format&fit=crop&q=80",
                backdrop="https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1200&auto=format&fit=crop&q=80",
                description="When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot is tasked with piloting a spacecraft to find a new planet for humanity.",
                format="IMAX LASER • 12-CH SOUND",
                category="imax",
                trailer_url="https://www.youtube.com/embed/zSWdZVtXT7E?autoplay=1",
                language="English",
                cast="Matthew McConaughey, Anne Hathaway, Jessica Chastain, Michael Caine",
                director="Christopher Nolan",
                status="Now Showing"
            ),

            Movie(
                title="Avatar: The Way of Water",
                genre="Sci-Fi / Fantasy",
                rating=8.8,
                age_rating="UA 13+",
                duration="3h 12m",
                poster="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
                backdrop="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1200&auto=format&fit=crop&q=80",
                description="Jake Sully lives with his newfound family on Pandora. When a familiar threat returns, Jake and Neytiri must protect their home.",
                format="3D HFR • DOLBY CINEMA",
                category="premiere",
                trailer_url="https://www.youtube.com/embed/d9MyW72ELq0?autoplay=1",
                language="English / Tamil",
                cast="Sam Worthington, Zoe Saldana, Sigourney Weaver, Stephen Lang",
                director="James Cameron",
                status="Now Showing"
            ),

            Movie(
                title="Oppenheimer",
                genre="Biography / Drama / History",
                rating=9.3,
                age_rating="A 18+",
                duration="3h 0m",
                poster="https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=80",
                backdrop="https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1200&auto=format&fit=crop&q=80",
                description="The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II.",
                format="IMAX 70MM • LASER 4K",
                category="imax",
                trailer_url="https://www.youtube.com/embed/uYPbbksJxIg?autoplay=1",
                language="English",
                cast="Cillian Murphy, Emily Blunt, Matt Damon, Robert Downey Jr.",
                director="Christopher Nolan",
                status="Now Showing"
            )

        ]

        db.session.add_all(movies)
        db.session.commit()

    # --------------------------------------------------------
    # SHOWTIMES
    # --------------------------------------------------------

    if not Showtime.query.first():

        all_movies = Movie.query.all()
        all_cinemas = Cinema.query.all()

        times_list = [
            "10:30 AM",
            "02:15 PM",
            "06:45 PM",
            "09:30 PM"
        ]

        today = date.today()

        showtimes_to_add = []

        for day_offset in range(7):

            current_date = today + timedelta(days=day_offset)

            for movie in all_movies:

                for cinema in all_cinemas:

                    selected_times = (
                        times_list
                        if (movie.id + cinema.id + day_offset) % 2 == 0
                        else times_list[:2]
                    )

                    if "IMAX" in cinema.name:
                        price = 350.0
                    elif "Royal" in cinema.name:
                        price = 450.0
                    else:
                        price = 250.0

                    for show_time in selected_times:

                        showtimes_to_add.append(
                            Showtime(
                                movie_id=movie.id,
                                cinema_id=cinema.id,
                                date=current_date,
                                time=show_time,
                                base_price=price
                            )
                        )

        db.session.add_all(showtimes_to_add)
        db.session.commit()

        # ----------------------------------------------------
        # SAMPLE BOOKING
        # ----------------------------------------------------

        first_show = Showtime.query.first()

        if first_show:

            sample_booking = Booking(
                booking_reference="CNV-778201",
                customer_name="Alexander Wright",
                email="alex.wright@executive.com",
                phone="+91 98840 12345",
                showtime_id=first_show.id,
                seat_count=2,
                seats_string="A3, A4",
                ticket_amount=first_show.base_price * 2,
                convenience_fee=30.0,
                taxes=36.0,
                final_amount=(first_show.base_price * 2) + 30.0 + 36.0,
                payment_status="Paid",
                booking_status="Confirmed"
            )

            db.session.add(sample_booking)
            db.session.flush()

            db.session.add(
                SeatBookingRecord(
                    showtime_id=first_show.id,
                    seat_number="A3",
                    booking_id=sample_booking.id
                )
            )

            db.session.add(
                SeatBookingRecord(
                    showtime_id=first_show.id,
                    seat_number="A4",
                    booking_id=sample_booking.id
                )
            )

            db.session.commit()


# ============================================================
# CREATE APP
# ============================================================

app = create_app()


# ============================================================
# STAFF AUTHENTICATION
# ============================================================

def staff_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if not session.get("staff_logged_in"):

            flash(
                "Staff authentication required to access management portal.",
                "error"
            )

            return redirect(url_for("staff_login"))

        return view(*args, **kwargs)

    return wrapped_view


# ============================================================
# ============================================================
# CUSTOMER AUTHENTICATION REDIRECTS (GUEST-FIRST PLATFORM)
# ============================================================

@app.route("/login", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
@app.route("/signup", methods=["GET", "POST"])
def customer_login():
    """
    Customer accounts have been replaced with direct guest booking.
    Redirect any direct legacy auth visits to Manage Booking.
    """
    flash("Customer accounts are no longer required. You can book tickets directly as a guest or manage your booking anytime.", "info")
    return redirect(url_for("manage_booking"))


@app.route("/logout")
def customer_logout():
    session.pop("customer_logged_in", None)
    session.pop("customer_id", None)
    session.pop("customer_email", None)
    session.pop("customer_name", None)
    session.pop("customer_phone", None)
    session.pop("authorized_booking_refs", None)
    session.pop("my_booking_refs", None)
    session.pop("guest_authorized_booking_ref", None)
    session.pop("claimed_offers", None)
    session.pop("promo_code", None)
    session.modified = True

    flash("You have been signed out.", "info")
    return redirect(url_for("home"))


# ============================================================
# CUSTOMER HOME
# ============================================================

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        app.static_folder,
        "favicon.svg",
        mimetype="image/svg+xml"
    )

@app.route("/")
def home():

    movies = Movie.query.filter_by(
        status="Now Showing"
    ).all()

    cinemas = Cinema.query.filter_by(
        status="Active"
    ).all()

    return render_template(
        "home.html",
        movies=movies,
        cinemas=cinemas
    )


# ============================================================
# CUSTOMER MOVIES
# ============================================================

@app.route("/movies")
def movies():

    category = request.args.get(
        "category",
        ""
    ).strip().lower()

    genre = request.args.get(
        "genre",
        ""
    ).strip().lower()

    search = request.args.get(
        "q",
        ""
    ).strip().lower()

    query = Movie.query.filter_by(
        status="Now Showing"
    )

    if category:
        query = query.filter(
            Movie.category.ilike(
                f"%{category}%"
            )
        )

    if genre:
        query = query.filter(
            Movie.genre.ilike(
                f"%{genre}%"
            )
        )

    all_movies = query.all()

    if search:

        all_movies = [
            movie
            for movie in all_movies
            if search in movie.title.lower()
            or search in movie.genre.lower()
        ]

    return render_template(
        "movies.html",
        movies=all_movies,
        selected_category=category,
        selected_genre=genre
    )


# ============================================================
# MOVIE DETAILS
# ============================================================

@app.route("/movie/<int:movie_id>")
def movie_details(movie_id):

    movie = Movie.query.get(movie_id)

    if not movie:
        abort(404)

    date_param = request.args.get(
        "date",
        ""
    ).strip()

    cinema_param = request.args.get(
        "cinema",
        ""
    ).strip()

    timing_param = request.args.get(
        "timing",
        ""
    ).strip()

    today = date.today()
    target_date = None

    if date_param.lower() == "today":
        target_date = today
    elif date_param.lower() == "tomorrow":
        target_date = today + timedelta(days=1)
    elif date_param:
        try:
            target_date = datetime.strptime(
                date_param,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            target_date = None

    target_cinema_id = None

    if cinema_param:
        if cinema_param.isdigit():
            target_cinema_id = int(cinema_param)
        else:
            cinema_match = Cinema.query.filter(
                Cinema.name.ilike(
                    f"%{cinema_param}%"
                )
            ).first()

            if not cinema_match:
                if "luxe" in cinema_param.lower():
                    cinema_match = Cinema.query.filter(
                        Cinema.name.ilike("%Pallas%")
                    ).first()
                elif "imax" in cinema_param.lower():
                    cinema_match = Cinema.query.filter(
                        Cinema.name.ilike("%IMAX%")
                    ).first()
                elif "royal" in cinema_param.lower():
                    cinema_match = Cinema.query.filter(
                        Cinema.name.ilike("%Royal%")
                    ).first()

            if cinema_match:
                target_cinema_id = cinema_match.id

    # Quick Reserve direct redirect
    if (
        target_date
        and target_cinema_id
        and timing_param
    ):
        matching_showtime = Showtime.query.filter(
            Showtime.movie_id == movie.id,
            Showtime.cinema_id == target_cinema_id,
            Showtime.date == target_date,
            Showtime.time.ilike(
                f"%{timing_param}%"
            )
        ).first()

        if not matching_showtime:
            # Fallback to cinema + timing or cinema match
            matching_showtime = Showtime.query.filter(
                Showtime.movie_id == movie.id,
                Showtime.cinema_id == target_cinema_id,
                Showtime.time.ilike(f"%{timing_param}%")
            ).first()

        if not matching_showtime:
            matching_showtime = Showtime.query.filter(
                Showtime.movie_id == movie.id,
                Showtime.cinema_id == target_cinema_id
            ).first()

        if not matching_showtime:
            matching_showtime = Showtime.query.filter(
                Showtime.movie_id == movie.id
            ).first()

        if matching_showtime:
            return redirect(
                url_for(
                    "seat_selection",
                    showtime_id=matching_showtime.id
                )
            )

    # 1. If target_date is explicitly requested in URL
    if target_date:
        showtimes = Showtime.query.filter(
            Showtime.movie_id == movie.id,
            Showtime.date == target_date
        ).order_by(
            Showtime.time.asc()
        ).all()
        if not showtimes:
            showtimes = Showtime.query.filter(
                Showtime.movie_id == movie.id,
                Showtime.date >= target_date
            ).order_by(
                Showtime.date.asc(),
                Showtime.time.asc()
            ).all()
    else:
        showtimes = []

    # 2. Query future/upcoming showtimes
    if not showtimes:
        showtimes = Showtime.query.filter(
            Showtime.movie_id == movie.id,
            Showtime.date >= today
        ).order_by(
            Showtime.date.asc(),
            Showtime.time.asc()
        ).all()

    # 3. If no future showtimes found in database, retrieve all existing showtimes for this movie
    if not showtimes:
        showtimes = Showtime.query.filter(
            Showtime.movie_id == movie.id
        ).order_by(
            Showtime.date.desc(),
            Showtime.time.asc()
        ).all()

    grouped_showtimes = {}

    for showtime in showtimes:
        cinema_name = showtime.cinema.name if (showtime.cinema and showtime.cinema.name) else "CINEVO LUXE Screen"

        if cinema_name not in grouped_showtimes:
            grouped_showtimes[cinema_name] = {}

        if hasattr(showtime.date, 'strftime'):
            date_string = showtime.date.strftime("%Y-%m-%d")
        else:
            date_string = str(showtime.date)

        if date_string not in grouped_showtimes[cinema_name]:
            grouped_showtimes[cinema_name][date_string] = []

        grouped_showtimes[cinema_name][date_string].append(
            showtime
        )

    return render_template(
        "movie_details.html",
        movie=movie,
        grouped_showtimes=grouped_showtimes,
        all_showtimes=showtimes,
        preselected_date=date_param,
        preselected_cinema=cinema_param,
        preselected_timing=timing_param
    )


# ============================================================
# SHOWTIMES
# ============================================================

@app.route("/showtimings")
def showtimings():

    today = date.today()

    selected_date_string = request.args.get(
        "date",
        today.strftime("%Y-%m-%d")
    )

    try:
        selected_date = datetime.strptime(
            selected_date_string,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        selected_date = today

    cinemas = Cinema.query.filter_by(
        status="Active"
    ).all()
    if not cinemas:
        cinemas = Cinema.query.all()

    # Query showtimes for the selected date
    showtimes = Showtime.query.filter(
        Showtime.date == selected_date
    ).order_by(
        Showtime.time.asc()
    ).all()

    # If no showtimes for today and no date explicitly requested in URL:
    if not showtimes and not request.args.get("date"):
        upcoming = Showtime.query.filter(
            Showtime.date >= today
        ).order_by(
            Showtime.date.asc(),
            Showtime.time.asc()
        ).all()
        if upcoming:
            showtimes = upcoming
            selected_date = upcoming[0].date
        else:
            all_st = Showtime.query.order_by(
                Showtime.date.desc(),
                Showtime.time.asc()
            ).all()
            if all_st:
                showtimes = all_st
                selected_date = all_st[0].date
    elif not showtimes and request.args.get("date"):
        closest = Showtime.query.filter(
            Showtime.date >= selected_date
        ).order_by(
            Showtime.date.asc(),
            Showtime.time.asc()
        ).all()
        if closest:
            showtimes = closest
            selected_date = closest[0].date

    date_tabs = [
        today + timedelta(days=i)
        for i in range(7)
    ]
    if selected_date and selected_date not in date_tabs:
        date_tabs = [selected_date] + [d for d in date_tabs if d != selected_date][:6]

    return render_template(
        "showtimings.html",
        cinemas=cinemas,
        showtimes=showtimes,
        selected_date=selected_date,
        date_tabs=date_tabs
    )


# ============================================================
# CINEMAS
# ============================================================

@app.route("/cinemas")
def cinemas():

    all_cinemas = Cinema.query.filter_by(
        status="Active"
    ).all()
    if not all_cinemas:
        all_cinemas = Cinema.query.all()

    today = date.today()

    showtimes = Showtime.query.filter(
        Showtime.date >= today
    ).all()

    if not showtimes:
        showtimes = Showtime.query.all()

    return render_template(
        "cinemas.html",
        cinemas=all_cinemas,
        showtimes=showtimes
    )


# ============================================================
# OFFERS
# ============================================================

@app.route("/offers")
def offers():

    return render_template(
        "offers.html"
    )

@app.route("/apply-offer/<promo_code>", methods=["GET", "POST"])
def apply_offer(promo_code):

    if promo_code == "FIRST100":
        is_first_booking = check_first_booking_eligibility()
        if not is_first_booking:
            flash("Coupon Already Used: This ₹100 welcome offer is available only for your first booking and has already been redeemed.", "error")
            return redirect(url_for("offers"))

    if "claimed_offers" not in session:
        session["claimed_offers"] = []

    if promo_code not in session["claimed_offers"]:
        session["claimed_offers"].append(promo_code)

    session["promo_code"] = promo_code
    session.modified = True

    return redirect(url_for("movies"))



# ============================================================
# SEAT SELECTION
# ============================================================

@app.route("/seat-selection/<int:showtime_id>")
def seat_selection(showtime_id):

    showtime = Showtime.query.get(
        showtime_id
    )

    if not showtime:

        flash(
            "Showtime not found.",
            "error"
        )

        return redirect(
            url_for("movies")
        )

    booked_seats = showtime.booked_seat_numbers

    return render_template(
        "seat_selection.html",
        showtime=showtime,
        booked_seats=booked_seats
    )


# ============================================================
# CHECKOUT HELPERS & VALIDATION
# ============================================================

def check_first_booking_eligibility(email=None, phone=None):
    """
    Check if a customer is genuinely eligible for FIRST100:
    - Must have no previous bookings in session['my_booking_refs']
    - Must have no saved email/phone in session that has previous bookings
    - If email provided, must have no existing confirmed bookings in the database with that email
    - If phone provided, must have no existing confirmed bookings in the database with that phone
    """
    # 1. Session booking refs check
    if session.get("authorized_booking_refs") or session.get("my_booking_refs"):
        return False

    session_email = email or session.get("customer_email")
    session_phone = phone or session.get("customer_phone")

    # 2. Database Email check
    if session_email:
        cleaned_email = session_email.strip().lower()
        if cleaned_email:
            existing = Booking.query.filter(db.func.lower(Booking.email) == cleaned_email).first()
            if existing:
                return False

    # 3. Database Phone check
    if session_phone:
        digits = "".join(filter(str.isdigit, session_phone))
        if len(digits) >= 10:
            last_10 = digits[-10:]
            existing = Booking.query.filter(Booking.phone.like(f"%{last_10}%")).first()
            if existing:
                return False

    return True


def is_weekday_evening(showtime):
    """
    Check if a showtime is on a weekday (Monday to Friday) and in the evening (>= 5:00 PM).
    """
    if not showtime or not showtime.date:
        return False
    # Weekday check: Monday (0) to Friday (4)
    if showtime.date.weekday() >= 5:
        return False
    # Evening check from showtime.time
    t_str = (showtime.time or "").strip().upper()
    if "PM" in t_str:
        try:
            hour = int(t_str.split(":")[0])
            if hour == 12:
                return False  # 12 PM is noon/afternoon
            if hour >= 5 and hour <= 11:
                return True
        except Exception:
            return True
    return False


# Authoritative Server-Side Food Menu Pricing (Prevents Client Price Manipulation)
AUTHORITATIVE_FOOD_MENU = {
    "Small Popcorn": 120.0,
    "Large Popcorn": 180.0,
    "Jumbo Popcorn": 240.0,
    "Classic Cheese Pizza": 299.0,
    "Premium Veggie Pizza": 349.0,
    "Coca-Cola": 100.0,
    "Pepsi": 100.0,
    "Red Bull": 160.0,
    "Gourmet Sandwich": 220.0,
    "French Fries": 160.0,
}


def calculate_checkout_pricing(showtime, selected_seats, food_dict, applied_promo, is_first_booking):
    """
    Unified checkout price calculation.
    Consistent across GET, POST, confirmation, and booking records.
    Calculation: TICKET TOTAL + FOOD TOTAL - VALID DISCOUNT = FINAL TOTAL
    All pricing is strictly calculated from server-side authoritative rates.
    """
    if showtime and selected_seats:
        pricing = showtime.pricing_breakdown
        num_seats = len(selected_seats)
        ticket_amount = round(num_seats * pricing["base"], 2)
        convenience_fee = round(num_seats * pricing["conv"], 2)
        taxes = round(num_seats * pricing["tax"], 2)
        ticket_total = round(num_seats * pricing["final"], 2)
    else:
        ticket_amount = 0.0
        convenience_fee = 0.0
        taxes = 0.0
        ticket_total = 0.0

    food_total = 0.0
    food_summary = []
    sanitized_food_dict = {}
    if isinstance(food_dict, dict):
        for name, details in food_dict.items():
            if name in AUTHORITATIVE_FOOD_MENU:
                authoritative_price = AUTHORITATIVE_FOOD_MENU[name]
                qty = 0
                if isinstance(details, dict):
                    try:
                        qty = int(details.get("quantity", 0))
                    except (ValueError, TypeError):
                        qty = 0
                elif isinstance(details, (int, float)):
                    qty = int(details)

                if 0 < qty <= 20:
                    food_total += float(qty) * authoritative_price
                    food_summary.append(f"{name} x{qty}")
                    sanitized_food_dict[name] = {
                        "price": authoritative_price,
                        "quantity": qty
                    }

    food_total = round(food_total, 2)
    food_summary_str = " | Food: " + ", ".join(food_summary) if food_summary else ""

    discount = 0.0
    valid_applied_promo = applied_promo

    # Offers and coupons are valid ONLY for movie ticket bookings (when showtime is present)
    if not showtime:
        discount = 0.0
        valid_applied_promo = None
    elif applied_promo == "FIRST100":
        if is_first_booking:
            discount = 100.0
        else:
            discount = 0.0
            valid_applied_promo = None
    elif applied_promo == "WEEKDAY20":
        # WEEKDAY20 is 20% off eligible food on weekday evening showtimes, not ticket discount
        if is_weekday_evening(showtime) and food_total > 0:
            discount = round(food_total * 0.20, 2)
        else:
            discount = 0.0
            valid_applied_promo = None
    elif applied_promo in ["LUXE-BLACK", "CHEF-PAIR"]:
        # Exclusive VIP cardholder/dining perks (perk badge claimed, 0 monetary ticket discount)
        discount = 0.0
    else:
        discount = 0.0
        valid_applied_promo = None

    subtotal = ticket_total + food_total
    final_amount = max(0.0, round(subtotal - discount, 2))

    return {
        "ticket_amount": ticket_amount,
        "convenience_fee": convenience_fee,
        "taxes": taxes,
        "ticket_total": ticket_total,
        "food_total": food_total,
        "food_summary_str": food_summary_str,
        "sanitized_food_dict": sanitized_food_dict,
        "discount": discount,
        "applied_promo": valid_applied_promo,
        "final_amount": final_amount
    }


# ============================================================
# CHECKOUT
# ============================================================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    import json

    if request.method == "POST":

        showtime_id = request.form.get(
            "showtime_id",
            type=int
        )

        seats_raw = request.form.get(
            "seats",
            ""
        ).strip()

        if not seats_raw:
            seats_list = request.form.getlist("seats")
            seats_raw = ", ".join(seats_list)

        customer_name = request.form.get("customer_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        confirm_booking = request.form.get("confirm_booking", "").strip()
        apply_promo_code = request.form.get("apply_promo_code", "").strip()
        customer_id_val = None

        food_items_raw = request.form.get("food_items", "").strip() or request.form.get("food_items_backup", "").strip()
        try:
            food_dict = json.loads(food_items_raw) if food_items_raw else {}
        except Exception:
            food_dict = {}

        if not showtime_id:
            flash("The Gourmet Lounge is available exclusively with a movie reservation. Please select your movie and seats first.", "info")
            return redirect(url_for("movies"))

        showtime = Showtime.query.get(showtime_id)
        if not showtime:
            flash("Showtime not found. Please select your movie and seats first.", "error")
            return redirect(url_for("movies"))

        selected_seats = list(dict.fromkeys([
            seat.strip().upper()
            for seat in seats_raw.split(",")
            if seat.strip()
        ]))

        if not selected_seats:
            flash("Please select at least one seat to proceed.", "error")
            return redirect(url_for("seat_selection", showtime_id=showtime_id))

        # Validate seat formats (must match auditorium layout A-E, 1-8)
        valid_seats = []
        for seat in selected_seats:
            if re.match(r"^[A-E][1-8]$", seat):
                valid_seats.append(seat)
            else:
                flash(f"Invalid seat selection '{seat}'. Please select valid seats from the auditorium layout.", "error")
                return redirect(url_for("seat_selection", showtime_id=showtime_id))
        selected_seats = valid_seats

        # Handle Promo Code application from Checkout form
        if apply_promo_code:
            session["promo_code"] = apply_promo_code
            session.modified = True

        # If this is NOT the final booking payment submit (e.g. user just arrived from seat selection or applied promo):
        if not confirm_booking:
            is_first_booking = check_first_booking_eligibility(email=email or None, phone=phone or None)
            claimed_offers = session.get("claimed_offers", [])
            applied_promo = session.get("promo_code")

            totals = calculate_checkout_pricing(
                showtime=showtime,
                selected_seats=selected_seats,
                food_dict=food_dict,
                applied_promo=applied_promo,
                is_first_booking=is_first_booking
            )

            seats_string = ", ".join(selected_seats)
            pricing_type = showtime.pricing_breakdown["type"] if showtime else "ATMOS"

            return render_template(
                "checkout.html",
                showtime=showtime,
                seats_string=seats_string,
                seats=selected_seats,
                food_items_raw=food_items_raw,
                food_dict=totals["sanitized_food_dict"],
                ticket_amount=totals["ticket_amount"],
                convenience_fee=totals["convenience_fee"],
                taxes=totals["taxes"],
                food_total=totals["food_total"],
                food_summary_str=totals["food_summary_str"],
                discount=totals["discount"],
                applied_promo=totals["applied_promo"],
                final_amount=totals["final_amount"],
                claimed_offers=claimed_offers,
                is_first_booking=is_first_booking,
                pricing_type=pricing_type
            )

        # ----------------------------------------------------
        # FINAL PAYMENT CONFIRMATION (from checkout.html form)
        # ----------------------------------------------------
        if not customer_name or not email or not phone:
            flash("Please provide your full name, email address, and contact number to complete your reservation.", "error")
            is_first_booking = check_first_booking_eligibility(email=email or None, phone=phone or None)
            claimed_offers = session.get("claimed_offers", [])
            applied_promo = session.get("promo_code")
            totals = calculate_checkout_pricing(
                showtime=showtime,
                selected_seats=selected_seats,
                food_dict=food_dict,
                applied_promo=applied_promo,
                is_first_booking=is_first_booking
            )
            seats_string = ", ".join(selected_seats)
            pricing_type = showtime.pricing_breakdown["type"] if showtime else "ATMOS"
            return render_template(
                "checkout.html",
                showtime=showtime,
                seats_string=seats_string,
                seats=selected_seats,
                food_items_raw=food_items_raw,
                food_dict=totals["sanitized_food_dict"],
                ticket_amount=totals["ticket_amount"],
                convenience_fee=totals["convenience_fee"],
                taxes=totals["taxes"],
                food_total=totals["food_total"],
                food_summary_str=totals["food_summary_str"],
                discount=totals["discount"],
                applied_promo=totals["applied_promo"],
                final_amount=totals["final_amount"],
                claimed_offers=claimed_offers,
                is_first_booking=is_first_booking,
                pricing_type=pricing_type
            )

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            is_first_booking = check_first_booking_eligibility(email=email, phone=phone)
            claimed_offers = session.get("claimed_offers", [])
            applied_promo = session.get("promo_code")
            totals = calculate_checkout_pricing(
                showtime=showtime,
                selected_seats=selected_seats,
                food_dict=food_dict,
                applied_promo=applied_promo,
                is_first_booking=is_first_booking
            )
            seats_string = ", ".join(selected_seats)
            pricing_type = showtime.pricing_breakdown["type"] if showtime else "ATMOS"
            return render_template(
                "checkout.html",
                showtime=showtime,
                seats_string=seats_string,
                seats=selected_seats,
                food_items_raw=food_items_raw,
                food_dict=totals["sanitized_food_dict"],
                ticket_amount=totals["ticket_amount"],
                convenience_fee=totals["convenience_fee"],
                taxes=totals["taxes"],
                food_total=totals["food_total"],
                food_summary_str=totals["food_summary_str"],
                discount=totals["discount"],
                applied_promo=totals["applied_promo"],
                final_amount=totals["final_amount"],
                claimed_offers=claimed_offers,
                is_first_booking=is_first_booking,
                pricing_type=pricing_type
            )

        clean_phone_digits, e164_phone = normalize_phone_e164(phone)
        if not clean_phone_digits:
            flash("Please enter a valid 10-digit mobile number.", "error")
            is_first_booking = check_first_booking_eligibility(email=email, phone=phone)
            claimed_offers = session.get("claimed_offers", [])
            applied_promo = session.get("promo_code")
            totals = calculate_checkout_pricing(
                showtime=showtime,
                selected_seats=selected_seats,
                food_dict=food_dict,
                applied_promo=applied_promo,
                is_first_booking=is_first_booking
            )
            seats_string = ", ".join(selected_seats)
            pricing_type = showtime.pricing_breakdown["type"] if showtime else "ATMOS"
            return render_template(
                "checkout.html",
                showtime=showtime,
                seats_string=seats_string,
                seats=selected_seats,
                food_items_raw=food_items_raw,
                food_dict=totals["sanitized_food_dict"],
                ticket_amount=totals["ticket_amount"],
                convenience_fee=totals["convenience_fee"],
                taxes=totals["taxes"],
                food_total=totals["food_total"],
                food_summary_str=totals["food_summary_str"],
                discount=totals["discount"],
                applied_promo=totals["applied_promo"],
                final_amount=totals["final_amount"],
                claimed_offers=claimed_offers,
                is_first_booking=is_first_booking,
                pricing_type=pricing_type
            )

        # Store normalized clean phone
        phone = clean_phone_digits

        # Determine First Booking Eligibility with Email & Phone & Session
        is_first_booking = check_first_booking_eligibility(email=email, phone=phone)
        applied_promo = session.get("promo_code")

        if applied_promo == "FIRST100" and not is_first_booking:
            session.pop("promo_code", None)
            flash("Coupon Already Used: This ₹100 welcome offer is available only for your first booking and has already been redeemed.", "error")
            applied_promo = None

        totals = calculate_checkout_pricing(
            showtime=showtime,
            selected_seats=selected_seats,
            food_dict=food_dict,
            applied_promo=applied_promo,
            is_first_booking=is_first_booking
        )

        # Re-verify seat conflict
        taken_seats = set()
        for seat in selected_seats:
            conflict = SeatBookingRecord.query.filter_by(
                showtime_id=showtime.id,
                seat_number=seat
            ).first()
            if conflict:
                taken_seats.add(seat)

        if not taken_seats:
            active_bookings = Booking.query.filter(
                Booking.showtime_id == showtime.id,
                Booking.booking_status == "Confirmed"
            ).all()

            for b in active_bookings:
                if b.seats_string:
                    seats_only = b.seats_string.split('|')[0]
                    for s in seats_only.split(','):
                        clean = s.strip().upper()
                        if clean in selected_seats:
                            taken_seats.add(clean)

        if not taken_seats:
            showtime_booked = showtime.booked_seat_numbers
            for s in selected_seats:
                if s in showtime_booked:
                    taken_seats.add(s)

        if taken_seats:
            flash(
                f"Seat(s) {', '.join(sorted(taken_seats))} have already been reserved by another customer. Please choose different seats.",
                "error"
            )
            return redirect(url_for("seat_selection", showtime_id=showtime_id))

        try:
            booking_ref = f"CNV-{uuid.uuid4().hex[:6].upper()}"
            while Booking.query.filter_by(booking_reference=booking_ref).first():
                booking_ref = f"CNV-{uuid.uuid4().hex[:6].upper()}"

            seats_display = (", ".join(selected_seats) if selected_seats else "") + totals["food_summary_str"]
            seat_count_val = len(selected_seats)

            new_booking = Booking(
                booking_reference=booking_ref,
                customer_id=customer_id_val,
                customer_name=customer_name,
                email=email,
                phone=phone,
                showtime_id=showtime.id,
                seat_count=seat_count_val,
                seats_string=seats_display,
                ticket_amount=totals["ticket_amount"],
                convenience_fee=totals["convenience_fee"],
                taxes=totals["taxes"],
                discount=totals["discount"],
                final_amount=totals["final_amount"],
                payment_status="Paid",
                booking_status="Confirmed"
            )

            db.session.add(new_booking)
            db.session.flush()

            for seat_number in selected_seats:
                seat_record = SeatBookingRecord(
                    showtime_id=showtime.id,
                    seat_number=seat_number,
                    booking_id=new_booking.id
                )
                db.session.add(seat_record)

            db.session.commit()

            # Authorize this newly created booking for guest access
            session["guest_authorized_booking_ref"] = booking_ref
            if "authorized_booking_refs" not in session or not isinstance(session["authorized_booking_refs"], list):
                session["authorized_booking_refs"] = []

            if booking_ref not in session["authorized_booking_refs"]:
                session["authorized_booking_refs"].append(booking_ref)

            session["my_booking_refs"] = session["authorized_booking_refs"]

            # Clear promo code and pending carts after booking completion
            session.pop("promo_code", None)
            session.pop("pending_food_items", None)
            session.pop("pending_food_cart", None)

            # ----------------------------------------------------
            # DIGITAL TICKET DISPATCH (EMAIL & WHATSAPP)
            # ----------------------------------------------------
            delivery_status = {}
            try:
                delivery_status["email"] = send_booking_email(new_booking, base_url=request.host_url)
            except Exception as e:
                logging.getLogger("cinevo").error("Email delivery exception for %s: %s", booking_ref, type(e).__name__)
                delivery_status["email"] = {"success": False, "status": "failed", "message": "Email delivery unavailable."}

            try:
                delivery_status["whatsapp"] = send_booking_whatsapp(new_booking, base_url=request.host_url)
            except Exception as e:
                logging.getLogger("cinevo").error("WhatsApp delivery exception for %s: %s", booking_ref, type(e).__name__)
                delivery_status["whatsapp"] = {"success": False, "status": "failed", "message": "WhatsApp delivery unavailable."}

            # Save delivery results in session for anti-duplication display
            if "booking_delivery_status" not in session or not isinstance(session["booking_delivery_status"], dict):
                session["booking_delivery_status"] = {}

            session["booking_delivery_status"][booking_ref] = delivery_status
            session.modified = True

            return redirect(url_for("confirmation", booking_ref=booking_ref))

        except Exception as e:
            db.session.rollback()
            flash(
                "A reservation conflict occurred. Please re-select your booking details.",
                "error"
            )
            if showtime_id:
                return redirect(url_for("seat_selection", showtime_id=showtime_id))
            return redirect(url_for("home"))

    # --------------------------------------------------------
    # CHECKOUT GET
    # --------------------------------------------------------
    showtime_id = request.args.get("showtime_id", type=int)
    seats_string = request.args.get("seats", "").strip()
    food_items_raw = request.args.get("food_items", "").strip()

    try:
        food_dict = json.loads(food_items_raw) if food_items_raw else {}
    except Exception:
        food_dict = {}

    if not showtime_id:
        flash("The Gourmet Lounge is available exclusively with a movie reservation. Please select your movie and seats first.", "info")
        return redirect(url_for("movies"))

    showtime = Showtime.query.get(showtime_id)
    if not showtime:
        flash("Showtime not found. Please select your movie and seats first.", "error")
        return redirect(url_for("movies"))

    selected_seats = list(dict.fromkeys([
        seat.strip().upper()
        for seat in seats_string.split(",")
        if seat.strip()
    ]))

    if not selected_seats:
        flash("Please select your seats before proceeding to checkout.", "error")
        return redirect(url_for("seat_selection", showtime_id=showtime_id))

    # Validate seat formats (must match auditorium layout A-E, 1-8)
    valid_seats = []
    for seat in selected_seats:
        if re.match(r"^[A-E][1-8]$", seat):
            valid_seats.append(seat)
        else:
            flash(f"Invalid seat selection '{seat}'. Please select valid seats from the auditorium layout.", "error")
            return redirect(url_for("seat_selection", showtime_id=showtime_id))
    selected_seats = valid_seats

    is_first_booking = check_first_booking_eligibility()
    applied_promo = session.get("promo_code")

    if applied_promo == "FIRST100" and not is_first_booking:
        session.pop("promo_code", None)
        flash("Coupon Already Used: This ₹100 welcome offer is available only for your first booking and has already been redeemed.", "error")
        applied_promo = None

    totals = calculate_checkout_pricing(
        showtime=showtime,
        selected_seats=selected_seats,
        food_dict=food_dict,
        applied_promo=applied_promo,
        is_first_booking=is_first_booking
    )

    claimed_offers = session.get("claimed_offers", [])

    return render_template(
        "checkout.html",
        showtime=showtime,
        seats=selected_seats,
        seats_string=", ".join(selected_seats),
        ticket_amount=totals["ticket_amount"],
        convenience_fee=totals["convenience_fee"],
        taxes=totals["taxes"],
        food_total=totals["food_total"],
        food_dict=totals["sanitized_food_dict"],
        food_summary_str=totals["food_summary_str"],
        food_items_raw=food_items_raw,
        discount=totals["discount"],
        applied_promo=totals["applied_promo"],
        final_amount=totals["final_amount"],
        claimed_offers=claimed_offers,
        is_first_booking=is_first_booking
    )


# ============================================================
# CONFIRMATION
# ============================================================

def normalize_digits(text):
    return "".join(filter(str.isdigit, text or ""))


def parse_booking_verification_credentials(query_str):
    """
    Extracts potential verification factors from a lookup query:
    - booking_reference (e.g. CNV-XXXXXX or alphanumeric token)
    - email (e.g. user@domain.com)
    - phone_digits (e.g. 10 digit phone number)
    """
    if not query_str or not isinstance(query_str, str):
        return None, None, None

    text = query_str.strip()

    # 1. Extract email if present
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    email = email_match.group(0).strip().lower() if email_match else None

    # 2. Extract booking reference (e.g. CNV-XXXXXX or CNVXXXXXX)
    ref_match = re.search(r'\b(CNV-?[A-Za-z0-9]{4,10})\b', text, re.IGNORECASE)
    booking_ref = ref_match.group(0).strip().upper() if ref_match else None

    if not booking_ref:
        tokens = [t.strip(",;/| ") for t in text.split()]
        for t in tokens:
            if email and t.lower() == email:
                continue
            if 4 <= len(t) <= 15 and any(c.isalpha() for c in t) and any(c.isdigit() for c in t):
                booking_ref = t.upper()
                break

    # 3. Extract phone digits (at least 10 consecutive or formatted digits)
    cleaned_for_phone = text
    if email_match:
        cleaned_for_phone = cleaned_for_phone.replace(email_match.group(0), " ")
    if ref_match:
        cleaned_for_phone = cleaned_for_phone.replace(ref_match.group(0), " ")
    elif booking_ref:
        cleaned_for_phone = cleaned_for_phone.replace(booking_ref, " ")

    phone_digits_all = normalize_digits(cleaned_for_phone)
    phone = phone_digits_all[-10:] if len(phone_digits_all) >= 10 else None

    return booking_ref, email, phone


def verify_two_factor_booking(query_str):
    """
    Validates that the search query contains at least two verified factors
    (Booking Ref + Email, Booking Ref + Phone, or Email + Phone)
    that match the EXACT SAME booking record in the database.

    Returns matching Booking instance if authorized, else None.
    """
    ref, email, phone = parse_booking_verification_credentials(query_str)

    # Need at least two distinct factors
    provided_factors = sum(1 for f in [ref, email, phone] if f is not None)
    if provided_factors < 2:
        return None

    ref_filters = []
    if ref:
        clean_ref = ref.upper().strip()
        formatted_ref = f"CNV-{clean_ref[3:]}" if clean_ref.startswith("CNV") and not clean_ref.startswith("CNV-") else clean_ref
        ref_filters = [
            Booking.booking_reference == formatted_ref,
            Booking.booking_reference == clean_ref,
            Booking.booking_reference == clean_ref.replace("-", "")
        ]

    # Check Ref + Email on SAME record
    if ref and email:
        match = Booking.query.filter(
            db.or_(*ref_filters),
            db.func.lower(Booking.email) == email.lower()
        ).first()
        if match:
            return match

    # Check Ref + Phone on SAME record
    if ref and phone:
        match = Booking.query.filter(
            db.or_(*ref_filters),
            Booking.phone.like(f"%{phone}%")
        ).first()
        if match:
            return match

    # Check Email + Phone on SAME record
    if email and phone:
        match = Booking.query.filter(
            db.func.lower(Booking.email) == email.lower(),
            Booking.phone.like(f"%{phone}%")
        ).first()
        if match:
            return match

    return None


# ============================================================
# DIGITAL TICKET NOTIFICATIONS (EMAIL & WHATSAPP)
# ============================================================

def normalize_phone_e164(raw_phone):
    """
    Normalizes an Indian mobile phone number:
    - Accepts 10 digits starting with 6, 7, 8, or 9
    - Accepts standard prefixes: '0' (11 digits) or '91' / '+91' (12 digits)
    - Returns (clean_10_digits, e164_destination) -> ('9876543210', '+919876543210')
    - Returns (None, None) if invalid
    """
    if not raw_phone or not isinstance(raw_phone, str):
        return None, None

    digits = "".join(filter(str.isdigit, raw_phone.strip()))

    # Handle leading 0 (e.g. 09876543210 -> 9876543210)
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    # Handle country code 91 (e.g. 919876543210 or +919876543210 -> 9876543210)
    elif len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    # MUST be exactly 10 digits AND begin with 6, 7, 8, or 9
    if len(digits) == 10 and digits[0] in "6789":
        return digits, f"+91{digits}"

    return None, None


def is_valid_email(raw_email):
    """Validates an email address using bounded, regex-free checks."""
    if not raw_email or not isinstance(raw_email, str):
        return False

    clean = raw_email.strip().lower()

    if len(clean) > 254 or clean.count("@") != 1:
        return False

    local, domain = clean.rsplit("@", 1)

    if not local or len(local) > 64 or not domain or len(domain) > 253:
        return False

    if local.startswith(".") or local.endswith(".") or ".." in local:
        return False

    allowed_local = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.+-")
    if any(char not in allowed_local for char in local):
        return False

    if ".." in domain or domain.startswith(".") or domain.endswith("."):
        return False

    labels = domain.split(".")
    if len(labels) < 2:
        return False

    for label in labels:
        if not label or len(label) > 63:
            return False
        if label.startswith("-") or label.endswith("-"):
            return False
        if not all(char.isalnum() or char == "-" for char in label):
            return False

    return all(char.isalpha() for char in labels[-1])

def build_email_html(booking, base_url="https://cinevo-luxe.onrender.com"):
    """Generates a luxury black + gold HTML email for booking confirmation."""
    ticket_url = f"{base_url.rstrip('/')}/confirmation/{booking.booking_reference}"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={booking.booking_reference}&color=07090e"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CINEVO LUXE — Executive Boarding Pass</title>
</head>
<body style="margin:0; padding:0; background-color:#07090e; font-family:'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color:#f8fafc;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#07090e; padding:30px 15px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" style="max-width:600px; background-color:#0f131c; border:1px solid rgba(229,193,88,0.35); border-radius:16px; overflow:hidden; box-shadow:0 20px 40px rgba(0,0,0,0.8);">

                    <!-- Header -->
                    <tr>
                        <td style="padding:28px 30px; background:linear-gradient(135deg, rgba(229,193,88,0.18) 0%, rgba(15,19,28,0.98) 100%); border-bottom:1px solid rgba(229,193,88,0.25);">
                            <table width="100%" role="presentation">
                                <tr>
                                    <td>
                                        <div style="font-size:22px; font-weight:800; letter-spacing:2px; color:#ffffff;">
                                            CINEVO <span style="color:#e5c158;">LUXE</span>
                                        </div>
                                        <div style="font-size:11px; color:#e5c158; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-top:4px;">
                                            Executive Cinema Reservation
                                        </div>
                                    </td>
                                    <td align="right">
                                        <div style="background:rgba(229,193,88,0.12); border:1px solid #e5c158; color:#f4df9b; padding:6px 14px; border-radius:6px; font-size:13px; font-weight:800; font-family:monospace; letter-spacing:1px;">
                                            {booking.booking_reference}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Body Content -->
                    <tr>
                        <td style="padding:30px;">
                            <div style="font-size:16px; color:#f8fafc; font-weight:700; margin-bottom:8px;">
                                Dear {booking.customer_name},
                            </div>
                            <div style="font-size:13px; color:#94a3b8; line-height:1.5; margin-bottom:24px;">
                                Your executive reservation has been authorized and guaranteed. Present this digital boarding pass at the usher pedestal for priority check-in.
                            </div>

                            <!-- Reservation Details Card -->
                            <table width="100%" role="presentation" style="background-color:#151a26; border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:18px; margin-bottom:24px;">
                                <tr>
                                    <td colspan="2" style="padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.06);">
                                        <div style="font-size:11px; color:#e5c158; text-transform:uppercase; font-weight:800; letter-spacing:0.8px;">Movie Presentation</div>
                                        <div style="font-size:18px; font-weight:800; color:#ffffff; margin-top:2px;">{booking.movie_name}</div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.06); width:50%;">
                                        <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;">Cinema Venue</div>
                                        <div style="font-size:13px; font-weight:600; color:#ffffff; margin-top:2px;">{booking.cinema_name}</div>
                                    </td>
                                    <td style="padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.06); width:50%;">
                                        <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;">Date & Showtime</div>
                                        <div style="font-size:13px; font-weight:600; color:#ffffff; margin-top:2px;">{booking.date_str} at {booking.time}</div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:10px 0; width:50%;">
                                        <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;">Confirmed Seats</div>
                                        <div style="font-size:15px; font-weight:800; color:#e5c158; margin-top:2px;">{booking.seats}</div>
                                    </td>
                                    <td style="padding:10px 0; width:50%;">
                                        <div style="font-size:11px; color:#94a3b8; text-transform:uppercase;">Total Paid</div>
                                        <div style="font-size:15px; font-weight:800; color:#e5c158; margin-top:2px;">{booking.price}</div>
                                    </td>
                                </tr>
                            </table>

                            <!-- QR Code Block -->
                            <table width="100%" role="presentation" style="background:rgba(229,193,88,0.04); border:1px solid rgba(229,193,88,0.2); border-radius:12px; padding:18px; margin-bottom:24px;">
                                <tr>
                                    <td style="vertical-align:middle;">
                                        <div style="font-size:13px; font-weight:800; color:#ffffff; text-transform:uppercase;">Digital Admission QR</div>
                                        <div style="font-size:12px; color:#94a3b8; margin-top:4px;">Scan at the lounge entry pedestal for expedited admission.</div>
                                    </td>
                                    <td align="right" style="vertical-align:middle; width:110px;">
                                        <div style="background:#ffffff; padding:6px; border-radius:8px; display:inline-block;">
                                            <img src="{qr_url}" alt="Booking QR" width="90" height="90" style="display:block;">
                                        </div>
                                    </td>
                                </tr>
                            </table>

                            <!-- Call to action button -->
                            <div style="text-align:center; margin-top:28px;">
                                <a href="{ticket_url}" style="display:inline-block; background:linear-gradient(135deg, #eed285 0%, #b88e28 100%); color:#07090e; text-decoration:none; padding:14px 32px; border-radius:8px; font-size:13px; font-weight:800; letter-spacing:1px; text-transform:uppercase;">
                                    View Digital Boarding Pass &rarr;
                                </a>
                            </div>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding:20px 30px; background-color:#090c12; border-top:1px solid rgba(255,255,255,0.06); text-align:center; font-size:11px; color:#64748b;">
                            &copy; 2026 CINEVO LUXE Cinema Inc. &bull; Save your booking reference ({booking.booking_reference}) to manage your reservation online.
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def build_email_text(booking, base_url="https://cinevo-luxe.onrender.com"):
    """Generates plain text fallback for email confirmation."""
    ticket_url = f"{base_url.rstrip('/')}/confirmation/{booking.booking_reference}"
    return f"""CINEVO LUXE — BOOKING CONFIRMED

Dear {booking.customer_name},

Your executive cinema reservation has been confirmed.

RESERVATION DETAILS:
• Booking Reference: {booking.booking_reference}
• Movie: {booking.movie_name}
• Cinema: {booking.cinema_name}
• Date & Showtime: {booking.date_str} at {booking.time}
• Confirmed Seats: {booking.seats}
• Total Amount Paid: {booking.price}

View your full digital boarding pass and QR code:
{ticket_url}

Thank you for choosing CINEVO LUXE.
"""


def send_booking_email(booking, base_url=None):
    """
    Sends a booking confirmation email using an HTTPS email API (Resend / Brevo / SendGrid)
    or SMTP (SSL port 465 / STARTTLS port 587).
    Returns: {"success": bool, "status": str, "message": str}
    """
    if not booking or not getattr(booking, "email", None):
        return {
            "success": False,
            "status": "failed",
            "message": "Invalid booking recipient email."
        }

    recipient_email = booking.email.strip().lower()

    if not is_valid_email(recipient_email):
        return {
            "success": False,
            "status": "failed",
            "message": "Invalid recipient email address format."
        }

    from_name = os.environ.get("MAIL_FROM_NAME", "CINEVO LUXE Concierge")
    from_addr = (
        os.environ.get("MAIL_FROM_ADDRESS")
        or os.environ.get("SMTP_FROM_EMAIL")
        or os.environ.get("SMTP_USER")
        or "concierge@cinevoluxe.com"
    )

    app_base = (
        base_url
        or os.environ.get(
            "APP_BASE_URL",
            "https://cinevo-luxe.onrender.com"
        )
    )

    email_subject = f"CINEVO LUXE — Booking Confirmed | {booking.booking_reference}"
    html_content = build_email_html(booking, app_base)
    text_content = build_email_text(booking, app_base)

    # ------------------------------------------------------------
    # 1. HTTPS Email Providers (Recommended for Render, uses port 443)
    # ------------------------------------------------------------
    resend_api_key = os.environ.get("RESEND_API_KEY")
    brevo_api_key = os.environ.get("BREVO_API_KEY") or os.environ.get("SENDINBLUE_API_KEY")
    sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")

    # A. Resend Provider (https://resend.com)
    if resend_api_key:
        try:
            url = "https://api.resend.com/emails"
            payload = {
                "from": f"{from_name} <{from_addr}>",
                "to": [recipient_email],
                "subject": email_subject,
                "html": html_content,
                "text": text_content
            }
            headers = {
                "Authorization": f"Bearer {resend_api_key.strip()}",
                "Content-Type": "application/json",
                "User-Agent": "CinevoLuxe/1.0"
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                if res_body.get("id"):
                    app.logger.info("BOOKING EMAIL DELIVERED via Resend: id=%s ref=%s", res_body.get("id"), booking.booking_reference)
                    return {
                        "success": True,
                        "status": "delivered",
                        "message": f"Ticket sent to your email ({recipient_email})"
                    }
                else:
                    app.logger.error("BOOKING EMAIL ERROR: Resend response missing message ID: %s", res_body)
                    return {
                        "success": False,
                        "status": "failed",
                        "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
                    }
        except urllib.error.HTTPError as e:
            err_msg = ""
            try:
                err_msg = e.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            app.logger.error("BOOKING EMAIL RESEND HTTP ERROR: code=%s reason=%s details=%s", e.code, e.reason, err_msg)
            return {
                "success": False,
                "status": "failed",
                "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
            }
        except Exception as e:
            app.logger.error("BOOKING EMAIL RESEND ERROR: %s: %s", type(e).__name__, str(e))
            return {
                "success": False,
                "status": "failed",
                "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
            }

    # B. Brevo / Sendinblue Provider (https://brevo.com)
    if brevo_api_key:
        try:
            url = "https://api.brevo.com/v3/smtp/email"
            customer_display_name = getattr(booking, "customer_name", "Guest")
            payload = {
                "sender": {"name": from_name, "email": from_addr},
                "to": [{"email": recipient_email, "name": customer_display_name}],
                "subject": email_subject,
                "htmlContent": html_content,
                "textContent": text_content
            }
            headers = {
                "api-key": brevo_api_key.strip(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                if res_body.get("messageId"):
                    app.logger.info("BOOKING EMAIL DELIVERED via Brevo: id=%s ref=%s", res_body.get("messageId"), booking.booking_reference)
                    return {
                        "success": True,
                        "status": "delivered",
                        "message": f"Ticket sent to your email ({recipient_email})"
                    }
                else:
                    app.logger.error("BOOKING EMAIL ERROR: Brevo response missing messageId: %s", res_body)
                    return {
                        "success": False,
                        "status": "failed",
                        "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
                    }
        except urllib.error.HTTPError as e:
            err_msg = ""
            try:
                err_msg = e.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            app.logger.error("BOOKING EMAIL BREVO HTTP ERROR: code=%s reason=%s details=%s", e.code, e.reason, err_msg)
            return {
                "success": False,
                "status": "failed",
                "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
            }
        except Exception as e:
            app.logger.error("BOOKING EMAIL BREVO ERROR: %s: %s", type(e).__name__, str(e))
            return {
                "success": False,
                "status": "failed",
                "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
            }

    # C. SendGrid Provider (https://sendgrid.com)
    if sendgrid_api_key:
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            payload = {
                "personalizations": [{"to": [{"email": recipient_email}]}],
                "from": {"email": from_addr, "name": from_name},
                "subject": email_subject,
                "content": [
                    {"type": "text/plain", "value": text_content},
                    {"type": "text/html", "value": html_content}
                ]
            }
            headers = {
                "Authorization": f"Bearer {sendgrid_api_key.strip()}",
                "Content-Type": "application/json"
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status in (200, 201, 202):
                    app.logger.info("BOOKING EMAIL DELIVERED via SendGrid: ref=%s", booking.booking_reference)
                    return {
                        "success": True,
                        "status": "delivered",
                        "message": f"Ticket sent to your email ({recipient_email})"
                    }
                else:
                    app.logger.error("BOOKING EMAIL ERROR: SendGrid returned status %s", response.status)
                    return {
                        "success": False,
                        "status": "failed",
                        "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
                    }
        except urllib.error.HTTPError as e:
            err_msg = ""
            try:
                err_msg = e.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            app.logger.error("BOOKING EMAIL SENDGRID HTTP ERROR: code=%s reason=%s details=%s", e.code, e.reason, err_msg)
            return {
                "success": False,
                "status": "failed",
                "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
            }
        except Exception as e:
            app.logger.error("BOOKING EMAIL SENDGRID ERROR: %s: %s", type(e).__name__, str(e))
            return {
                "success": False,
                "status": "failed",
                "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
            }

    # ------------------------------------------------------------
    # 2. SMTP Provider (Fallback for environments with open SMTP)
    # ------------------------------------------------------------
    smtp_host = os.environ.get("SMTP_HOST") or os.environ.get("SMTP_SERVER")
    smtp_user = os.environ.get("SMTP_USER") or os.environ.get("SMTP_USERNAME")
    smtp_pass = os.environ.get("SMTP_PASSWORD") or os.environ.get("SMTP_PASS")
    smtp_port_raw = os.environ.get("SMTP_PORT", "587")
    try:
        smtp_port = int(smtp_port_raw)
    except (ValueError, TypeError):
        smtp_port = 587

    if not smtp_host or not smtp_user or not smtp_pass:
        return {
            "success": False,
            "status": "not_configured",
            "message": "Email delivery service not configured in environment."
        }

    msg = MIMEMultipart("alternative")
    msg["Subject"] = email_subject
    msg["From"] = f"{from_name} <{from_addr}>"
    msg["To"] = recipient_email

    text_part = MIMEText(text_content, "plain")
    html_part = MIMEText(html_content, "html")
    msg.attach(text_part)
    msg.attach(html_part)

    try:
        if smtp_port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                smtp_host,
                smtp_port,
                context=context,
                timeout=10
            ) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(
                smtp_host,
                smtp_port,
                timeout=10
            ) as server:
                server.ehlo()
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

        app.logger.info("BOOKING EMAIL DELIVERED via SMTP (host=%s, port=%s) for ref=%s", smtp_host, smtp_port, booking.booking_reference)
        return {
            "success": True,
            "status": "delivered",
            "message": f"Ticket sent to your email ({recipient_email})"
        }

    except smtplib.SMTPAuthenticationError as e:
        app.logger.error(
            "BOOKING EMAIL AUTH ERROR: SMTP code=%s (check your SMTP_USER and SMTP_PASSWORD / App Password)",
            getattr(e, "smtp_code", "unknown")
        )
        return {
            "success": False,
            "status": "failed",
            "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
        }

    except OSError as e:
        app.logger.error(
            "BOOKING EMAIL NETWORK ERROR: %s (%s). NOTE: Render blocks outbound SMTP ports 25/465/587 by default. Set RESEND_API_KEY or BREVO_API_KEY to send via HTTPS REST API (port 443).",
            type(e).__name__,
            str(e)
        )
        return {
            "success": False,
            "status": "failed",
            "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
        }

    except Exception as e:
        app.logger.error(
            "BOOKING EMAIL ERROR: %s: %s",
            type(e).__name__,
            str(e)
        )
        return {
            "success": False,
            "status": "failed",
            "message": "We couldn't deliver the ticket to your email. Please use the confirmation below."
        }
    
def build_whatsapp_message(booking, base_url="https://cinevo-luxe.onrender.com"):
    """Formats the official WhatsApp notification text message."""
    ticket_url = f"{base_url.rstrip('/')}/confirmation/{booking.booking_reference}"
    return (
        f"🎬 *CINEVO LUXE — BOOKING CONFIRMED*\n\n"
        f"Dear *{booking.customer_name}*,\n\n"
        f"Your executive cinema reservation has been confirmed.\n\n"
        f"🎟️ *Booking Reference:* `{booking.booking_reference}`\n"
        f"🍿 *Movie:* {booking.movie_name}\n"
        f"📍 *Cinema:* {booking.cinema_name}\n"
        f"📅 *Date & Showtime:* {booking.date_str} at {booking.time}\n"
        f"🪑 *Confirmed Seats:* {booking.seats}\n"
        f"💳 *Total Paid:* {booking.price}\n\n"
        f"📲 *Digital Boarding Pass & QR:* \n{ticket_url}\n\n"
        f"Thank you for choosing CINEVO LUXE."
    )


def send_booking_whatsapp(booking, base_url=None):
    """
    Sends a WhatsApp booking confirmation using Meta Cloud API or Twilio WhatsApp API.
    Returns: {"success": bool, "status": str, "message": str}
    """
    if not booking or not getattr(booking, "phone", None):
        return {"success": False, "status": "failed", "message": "Invalid booking recipient phone."}

    raw_phone = booking.phone
    clean_digits, e164_phone = normalize_phone_e164(raw_phone)

    if not clean_digits or not e164_phone:
        return {"success": False, "status": "failed", "message": "Invalid recipient phone number format."}

    meta_token = os.environ.get("WHATSAPP_API_TOKEN") or os.environ.get("META_WHATSAPP_TOKEN")
    meta_phone_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID") or os.environ.get("META_PHONE_ID")

    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_from = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

    app_base = base_url or os.environ.get("APP_BASE_URL", "https://cinevo-luxe.onrender.com")
    message_text = build_whatsapp_message(booking, app_base)

    # 1. Meta WhatsApp Cloud API Provider
    if meta_token and meta_phone_id:
        url = f"https://graph.facebook.com/v19.0/{meta_phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {meta_token}",
            "Content-Type": "application/json"
        }
        dest_number = e164_phone.replace("+", "")
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": dest_number,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": message_text
            }
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                if "messages" in res_body:
                    return {
                        "success": True,
                        "status": "accepted",
                        "message": "WhatsApp notification accepted for delivery."
                    }
                else:
                    return {
                        "success": False,
                        "status": "failed",
                        "message": "We couldn't deliver the ticket to WhatsApp. Please use the confirmation below."
                    }
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "status": "failed",
                "message": "We couldn't deliver the ticket to WhatsApp. Please use the confirmation below."
            }
        except Exception as e:
            return {
                "success": False,
                "status": "failed",
                "message": "We couldn't deliver the ticket to WhatsApp. Please use the confirmation below."
            }

    # 2. Twilio WhatsApp Provider
    elif twilio_sid and twilio_token:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
        data = urllib.parse.urlencode({
            "From": twilio_from if twilio_from.startswith("whatsapp:") else f"whatsapp:{twilio_from}",
            "To": f"whatsapp:{e164_phone}",
            "Body": message_text
        }).encode("utf-8")

        import base64
        auth_header = "Basic " + base64.b64encode(f"{twilio_sid}:{twilio_token}".encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                twilio_status = res_body.get("status")
                if twilio_status == "delivered":
                    return {
                        "success": True,
                        "status": "delivered",
                        "message": f"Ticket sent to your WhatsApp ({e164_phone})"
                    }
                elif twilio_status in ["queued", "sent", "accepted"]:
                    return {
                        "success": True,
                        "status": "accepted",
                        "message": "WhatsApp notification accepted for delivery."
                    }
                else:
                    return {
                        "success": False,
                        "status": "failed",
                        "message": "We couldn't deliver the ticket to WhatsApp. Please use the confirmation below."
                    }
        except Exception as e:
            return {
                "success": False,
                "status": "failed",
                "message": "We couldn't deliver the ticket to WhatsApp. Please use the confirmation below."
            }

    # 3. Not configured
    else:
        return {
            "success": False,
            "status": "not_configured",
            "message": "WhatsApp delivery service not configured in environment."
        }


# ============================================================
# CONFIRMATION & GUEST MANAGE BOOKING
# ============================================================

GENERIC_BOOKING_VERIFY_ERROR = "We couldn't verify those booking details. Please check your booking reference and email and try again."


@app.route("/confirmation/<string:booking_ref>")
def confirmation(booking_ref):
    clean_ref = (booking_ref or "").strip().upper()
    booking = Booking.query.filter(
        db.or_(
            Booking.booking_reference == clean_ref,
            db.func.upper(Booking.booking_reference) == clean_ref
        )
    ).first()

    if not booking:
        flash("Booking reference not found.", "error")
        return redirect(url_for("manage_booking"))

    delivery_status = session.get("booking_delivery_status", {}).get(booking.booking_reference)

    # Staff access
    if session.get("staff_logged_in"):
        return render_template(
            "confirmation.html",
            booking=booking,
            delivery_status=delivery_status
        )

    # Guest session authorization check for this specific booking
    guest_auth_ref = session.get("guest_authorized_booking_ref")
    if guest_auth_ref and guest_auth_ref.upper() == booking.booking_reference.upper():
        return render_template(
            "confirmation.html",
            booking=booking,
            delivery_status=delivery_status
        )

    # Block unauthorized access and redirect to secure Manage Booking
    flash("Please enter your booking reference and email to view your booking details.", "error")
    return redirect(url_for("manage_booking"))


GENERIC_RECOVERY_ERROR = "We couldn't find a booking matching those details. Please check your email and contact number and try again."


@app.route("/manage-booking", methods=["GET", "POST"])
def manage_booking():
    if request.method == "POST":
        raw_ref = request.form.get("booking_ref", "").strip()
        raw_email = request.form.get("email", "").strip()

        if not raw_ref or not raw_email:
            flash(GENERIC_BOOKING_VERIFY_ERROR, "error")
            return render_template("manage_booking.html", view_mode="form", booking_ref=raw_ref, email=raw_email)

        # Validate email format
        if not is_valid_email(raw_email):
            flash(GENERIC_BOOKING_VERIFY_ERROR, "error")
            return render_template("manage_booking.html", view_mode="form", booking_ref=raw_ref, email=raw_email)

        # Normalize reference and email
        clean_ref = raw_ref.upper().replace(" ", "")
        formatted_ref = f"CNV-{clean_ref[3:]}" if clean_ref.startswith("CNV") and not clean_ref.startswith("CNV-") else clean_ref
        normalized_email = raw_email.lower().strip()

        # Query database strictly for the matching booking reference
        booking = Booking.query.filter(
            db.or_(
                Booking.booking_reference == clean_ref,
                Booking.booking_reference == formatted_ref,
                db.func.upper(Booking.booking_reference) == clean_ref
            )
        ).first()

        # Authoritative server-side verification: MUST match both booking reference and stored email
        if not booking or not booking.email or booking.email.strip().lower() != normalized_email:
            flash(GENERIC_BOOKING_VERIFY_ERROR, "error")
            return render_template("manage_booking.html", view_mode="form", booking_ref=raw_ref, email=raw_email)

        # Successfully verified: authorize ONLY this specific booking reference in session
        session["guest_authorized_booking_ref"] = booking.booking_reference
        session.modified = True

        return redirect(url_for("manage_booking"))

    # GET Request Handling
    if request.args.get("action") == "exit":
        session.pop("guest_authorized_booking_ref", None)
        session.modified = True
        flash("You have exited your booking view.", "info")
        return redirect(url_for("manage_booking"))

    # Mode: Forgot Booking Reference Recovery Form
    if request.args.get("mode") == "recover":
        return render_template("manage_booking.html", view_mode="recover")

    guest_auth_ref = session.get("guest_authorized_booking_ref")
    if guest_auth_ref:
        booking = Booking.query.filter(
            db.func.upper(Booking.booking_reference) == guest_auth_ref.upper()
        ).first()
        if booking:
            return render_template("manage_booking.html", view_mode="booking", booking=booking)
        else:
            session.pop("guest_authorized_booking_ref", None)
            session.modified = True

    return render_template("manage_booking.html", view_mode="form")


@app.route("/manage-booking/recover", methods=["GET", "POST"])
def recover_booking_reference():
    if request.method == "POST":
        raw_email = request.form.get("recover_email", "").strip().lower()
        raw_phone = request.form.get("recover_phone", "").strip()
        clean_phone_digits, _ = normalize_phone_e164(raw_phone)

        # Strict dual-factor validation: MUST provide BOTH valid email AND 10-digit phone (starting with 6-9)
        if not raw_email or not is_valid_email(raw_email) or not clean_phone_digits:
            flash(GENERIC_RECOVERY_ERROR, "error")
            return render_template("manage_booking.html", view_mode="recover", recover_email=raw_email, recover_phone=raw_phone)

        # Database Query: Matches BOTH email AND phone on the SAME record
        booking = Booking.query.filter(
            db.func.lower(Booking.email) == raw_email,
            Booking.phone.like(f"%{clean_phone_digits}%")
        ).order_by(
            Booking.created_at.desc(),
            Booking.id.desc()
        ).first()

        if not booking:
            flash(GENERIC_RECOVERY_ERROR, "error")
            return render_template("manage_booking.html", view_mode="recover", recover_email=raw_email, recover_phone=raw_phone)

        # Return single verified recovered booking card
        return render_template("manage_booking.html", view_mode="recovered", recovered_booking=booking)

    # GET returns recover form
    return render_template("manage_booking.html", view_mode="recover")


@app.route("/manage-booking/exit", methods=["POST", "GET"])
def exit_manage_booking():
    session.pop("guest_authorized_booking_ref", None)
    session.modified = True
    flash("You have exited your booking view.", "info")
    return redirect(url_for("manage_booking"))


# ============================================================
# LEGACY MY BOOKINGS ROUTE REDIRECT
# ============================================================

@app.route("/my-bookings")
@app.route("/bookings")
def my_bookings():
    return redirect(url_for("manage_booking"))


# ============================================================
# STAFF LOGIN
# ============================================================

@app.route("/staff/login", methods=["GET", "POST"])
def staff_login():

    if session.get("staff_logged_in"):

        return redirect(
            url_for("staff_dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        staff_member = Staff.query.filter_by(
            username=username
        ).first()

        if (
            staff_member
            and staff_member.check_password(password)
        ):

            session["staff_logged_in"] = True

            session["staff_username"] = (
                staff_member.username
            )

            flash(
                f"Welcome back, {staff_member.username}.",
                "success"
            )

            return redirect(
                url_for("staff_dashboard")
            )

        flash(
            "Invalid credentials. Please verify your staff username and password.",
            "error"
        )

    return render_template(
        "staff/login.html"
    )


# ============================================================
# STAFF LOGOUT
# ============================================================

@app.route("/staff/logout")
def staff_logout():

    session.pop(
        "staff_logged_in",
        None
    )

    session.pop(
        "staff_username",
        None
    )

    session.pop(
        "guest_authorized_booking_ref",
        None
    )

    session.modified = True

    flash(
        "You have been securely logged out.",
        "success"
    )

    return redirect(
        url_for("staff_login")
    )


# ============================================================
# STAFF DASHBOARD
# ============================================================

@app.route("/staff/dashboard")
@staff_required
def staff_dashboard():

    movies = Movie.query.all()
    cinemas = Cinema.query.all()
    showtimes = Showtime.query.all()
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()

    total_bookings = len(bookings)
    confirmed_bookings = len([
        b for b in bookings
        if (b.booking_status or "").strip().lower() == "confirmed"
    ])
    paid_revenue = sum(
        float(b.final_amount or 0.0)
        for b in bookings
        if (b.payment_status or "").strip().lower() == "paid"
        and (b.booking_status or "").strip().lower() == "confirmed"
    )

    return render_template(
        "staff/dashboard.html",
        movies=movies,
        cinemas=cinemas,
        showtimes=showtimes,
        bookings=bookings,
        total_bookings=total_bookings,
        confirmed_bookings=confirmed_bookings,
        paid_revenue=paid_revenue
    )


# ============================================================
# STAFF MOVIE MANAGEMENT
# ============================================================

@app.route("/staff/movies")
@staff_required
def staff_movies():

    movies = Movie.query.order_by(
        Movie.id.desc()
    ).all()

    return render_template(
        "staff/movies.html",
        movies=movies
    )


# ============================================================
# MOVIE VALIDATION HELPERS
# ============================================================

def is_search_engine_redirect(url):
    """
    Detects if the URL is a search engine result or redirect page
    rather than a direct media URL.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urllib.parse.urlparse(url.strip())
        hostname = (parsed.hostname or "").lower()
        path = (parsed.path or "").lower()
        query = (parsed.query or "").lower()

        # Google Search / Image redirect detection
        if hostname == "google.com" or hostname.endswith(".google.com") or (hostname.startswith("google.") and hostname.count(".") == 1):
            if any(path.startswith(p) for p in ["/imgres", "/url", "/search", "/images"]):
                return True
            if any(param in query for param in ["tbnid=", "imgurl=", "sa=i", "source=images", "q="]):
                return True

        # Shortened google links / app links
        if hostname == "goo.gl":
            return True

        # Bing Images search
                # Bing Images search
        if hostname == "bing.com" or hostname.endswith(".bing.com"):
            if "/images" in path or "view=detail" in query:
                return True
        # Yandex / Yahoo search results
        if ((hostname == "yandex.com" or hostname.endswith(".yandex.com") or
             hostname == "yahoo.com" or hostname.endswith(".yahoo.com"))
                and ("/images" in path or "/search" in path)):
            return True
        # DuckDuckGo images
        if (hostname == "duckduckgo.com" or hostname.endswith(".duckduckgo.com")) and "iax=images" in query:
            return True

    except Exception:
        pass

    return False


def validate_image_url(url, field_label="Poster URL", max_length=500, required=True):
    """
    Validates an image URL (poster / backdrop).
    Returns (is_valid: bool, error_message: str).
    """
    if not url or not url.strip():
        if required:
            return False, "Title and Poster URL are required." if field_label == "Poster URL" else f"{field_label} is required."
        return True, ""

    url = url.strip()

    if len(url) > max_length:
        return False, f"This URL is not allowed. The {field_label} exceeds the maximum allowed length of {max_length} characters. Please enter a valid direct image URL."

    if any(c in url for c in ['\n', '\r', '\t', ' ']):
        return False, "Invalid URL. Please enter a valid image URL."

    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False, "Invalid URL. Please enter a valid image URL."

    if parsed.scheme.lower() not in ('http', 'https'):
        return False, "Invalid URL. Please enter a valid image URL starting with http:// or https://."

    if not parsed.netloc or not parsed.hostname:
        return False, "Invalid URL. Please enter a valid image URL."

    hostname = parsed.hostname.lower()
    if hostname != "localhost" and "." not in hostname:
        return False, "Invalid URL. Please enter a valid image URL."

    if is_search_engine_redirect(url):
        return False, "This URL is not allowed. Please enter a valid direct image URL."

    return True, ""


def validate_trailer_url(url, field_label="Trailer URL", max_length=500, required=False):
    """
    Validates a trailer video/embed URL (e.g. YouTube, Vimeo, direct mp4, etc.).
    Returns (is_valid: bool, error_message: str).
    """
    if not url or not url.strip():
        if required:
            return False, f"{field_label} is required."
        return True, ""

    url = url.strip()

    if len(url) > max_length:
        return False, f"This URL is not allowed. The {field_label} exceeds the maximum allowed length of {max_length} characters."

    if any(c in url for c in ['\n', '\r', '\t', ' ']):
        return False, "Invalid URL. Please enter a valid trailer URL."

    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False, "Invalid URL. Please enter a valid trailer URL."

    if parsed.scheme.lower() not in ('http', 'https'):
        return False, "Invalid URL. Please enter a valid trailer URL starting with http:// or https://."

    if not parsed.netloc or not parsed.hostname:
        return False, "Invalid URL. Please enter a valid trailer URL."

    hostname = parsed.hostname.lower()
    if hostname != "localhost" and "." not in hostname:
        return False, "Invalid URL. Please enter a valid trailer URL."

    return True, ""


def validate_movie_form(data, is_update=False):
    """
    Validates movie fields against database model column limits and constraints.
    Returns (is_valid: bool, error_message: str).
    """
    title = (data.get("title") or "").strip()
    poster = (data.get("poster") or "").strip()

    if not title or not poster:
        return False, "Title and Poster URL are required."

    if len(title) > 150:
        return False, "Movie title cannot exceed 150 characters."

    valid_poster, poster_err = validate_image_url(poster, field_label="Poster URL", max_length=500, required=True)
    if not valid_poster:
        return False, poster_err

    backdrop = (data.get("backdrop") or "").strip()
    if backdrop:
        valid_backdrop, backdrop_err = validate_image_url(backdrop, field_label="Backdrop URL", max_length=500, required=False)
        if not valid_backdrop:
            return False, backdrop_err

    trailer_url = (data.get("trailer_url") or "").strip()
    if trailer_url:
        valid_trailer, trailer_err = validate_trailer_url(trailer_url, field_label="Trailer URL", max_length=500, required=False)
        if not valid_trailer:
            return False, trailer_err

    genre = (data.get("genre") or "").strip()
    if len(genre) > 100:
        return False, "Genre cannot exceed 100 characters."

    format_type = (data.get("format") or "").strip()
    if len(format_type) > 100:
        return False, "Format description cannot exceed 100 characters."

    age_rating = (data.get("age_rating") or "").strip()
    if len(age_rating) > 20:
        return False, "Age rating cannot exceed 20 characters."

    duration = (data.get("duration") or "").strip()
    if len(duration) > 50:
        return False, "Duration cannot exceed 50 characters."

    category = (data.get("category") or "").strip()
    if len(category) > 50:
        return False, "Category cannot exceed 50 characters."

    language = (data.get("language") or "").strip()
    if len(language) > 50:
        return False, "Language cannot exceed 50 characters."

    director = (data.get("director") or "").strip()
    if len(director) > 100:
        return False, "Director cannot exceed 100 characters."

    status = (data.get("status") or "").strip()
    if len(status) > 30:
        return False, "Status cannot exceed 30 characters."

    rating_val = str(data.get("rating") or "").strip()
    if rating_val:
        try:
            r = float(rating_val)
            if r < 0.0 or r > 10.0:
                return False, "Rating must be between 0.0 and 10.0."
        except ValueError:
            return False, "Rating must be a valid number."

    description = (data.get("description") or "").strip()
    if not description:
        return False, "Synopsis / Description is required."

    return True, ""


# ============================================================
# ADD MOVIE
# ============================================================

@app.route(
    "/staff/add-movie",
    methods=["GET", "POST"]
)
@staff_required
def staff_add_movie():
    if request.method == "GET":
        return redirect(url_for("staff_movies"))

    title = request.form.get(
        "title",
        ""
    ).strip()

    genre = request.form.get(
        "genre",
        "Action / Sci-Fi"
    ).strip()

    format_type = request.form.get(
        "format",
        "2D • 3D • ATMOS"
    ).strip()

    rating = request.form.get(
        "rating",
        "9.0"
    ).strip()

    age_rating = request.form.get(
        "age_rating",
        "UA 16+"
    ).strip()

    duration = request.form.get(
        "duration",
        "2h 30m"
    ).strip()

    poster = request.form.get(
        "poster",
        ""
    ).strip()

    backdrop = request.form.get(
        "backdrop",
        ""
    ).strip()

    category = request.form.get(
        "category",
        "now_showing"
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    trailer_url = request.form.get(
        "trailer_url",
        ""
    ).strip()

    language = request.form.get(
        "language",
        "English"
    ).strip() or "English"

    cast = request.form.get(
        "cast",
        "Ensemble Cast"
    ).strip() or "Ensemble Cast"

    director = request.form.get(
        "director",
        "Cinevo Director"
    ).strip() or "Cinevo Director"

    status = request.form.get(
        "status",
        "Now Showing"
    ).strip() or "Now Showing"

    form_data = {
        "title": title,
        "genre": genre,
        "format": format_type,
        "rating": rating,
        "age_rating": age_rating,
        "duration": duration,
        "poster": poster,
        "backdrop": backdrop,
        "category": category,
        "description": description,
        "trailer_url": trailer_url,
        "language": language,
        "cast": cast,
        "director": director,
        "status": status
    }

    is_valid, err_msg = validate_movie_form(form_data)
    if not is_valid:
        flash(
            err_msg,
            "error"
        )
        return redirect(
            url_for("staff_movies")
        )

    try:
        rating_value = (
            float(rating)
            if rating
            else 9.0
        )
    except ValueError:
        rating_value = 9.0

    if not backdrop:
        backdrop = poster

    if not trailer_url:
        trailer_url = "https://www.youtube.com/embed/TcMBFSGVi1c?autoplay=1"

    try:
        new_movie = Movie(
            title=title,
            genre=genre or "Action / Sci-Fi",
            format=format_type or "2D • 3D • ATMOS",
            rating=rating_value,
            age_rating=age_rating or "UA 16+",
            duration=duration or "2h 30m",
            poster=poster,
            backdrop=backdrop,
            category=category or "now_showing",
            description=description,
            trailer_url=trailer_url,
            language=language,
            cast=cast,
            director=director,
            status=status
        )

        db.session.add(
            new_movie
        )

        db.session.flush()

        # --------------------------------------------------------
        # AUTO CREATE SHOWTIMES
        # --------------------------------------------------------

        cinemas = Cinema.query.filter_by(
            status="Active"
        ).all()

        today = date.today()

        times_list = [
            "10:30 AM",
            "02:15 PM",
            "06:45 PM",
            "09:30 PM"
        ]

        for day_offset in range(7):
            current_date = (
                today
                + timedelta(days=day_offset)
            )

            for cinema in cinemas:
                if "IMAX" in cinema.name:
                    price = 350.0
                elif "Royal" in cinema.name:
                    price = 450.0
                else:
                    price = 250.0

                for show_time in times_list[:2]:
                    db.session.add(
                        Showtime(
                            movie_id=new_movie.id,
                            cinema_id=cinema.id,
                            date=current_date,
                            time=show_time,
                            base_price=price
                        )
                    )

        db.session.commit()

        flash(
            f"Movie '{title}' added and scheduled successfully!",
            "success"
        )

    except Exception as exc:
        db.session.rollback()
        app.logger.exception("Error while adding movie: %s", exc)
        flash(
            "Unable to add the movie. Please check the entered information and try again.",
            "error"
        )

    return redirect(
        url_for("staff_movies")
    )


# ============================================================
# EDIT MOVIE — GET
# ============================================================

@app.route(
    "/staff/edit-movie/<int:movie_id>",
    methods=["GET"]
)
@staff_required
def staff_edit_movie(movie_id):

    movie = Movie.query.get(
        movie_id
    )

    if not movie:

        flash(
            "Movie not found.",
            "error"
        )

        return redirect(
            url_for("staff_movies")
        )

    return render_template(
        "staff/edit_movie.html",
        movie=movie
    )


# ============================================================
# EDIT MOVIE — POST
# ============================================================

@app.route(
    "/staff/edit-movie/<int:movie_id>",
    methods=["POST"]
)
@staff_required
def staff_update_movie(movie_id):

    movie = Movie.query.get(
        movie_id
    )

    if not movie:

        flash(
            "Movie not found.",
            "error"
        )

        return redirect(
            url_for("staff_movies")
        )

    # --------------------------------------------------------
    # READ FORM
    # --------------------------------------------------------

    title = request.form.get(
        "title",
        movie.title
    ).strip()

    genre = request.form.get(
        "genre",
        movie.genre
    ).strip()

    format_type = request.form.get(
        "format",
        movie.format
    ).strip()

    rating = request.form.get(
        "rating",
        str(movie.rating)
    ).strip()

    age_rating = request.form.get(
        "age_rating",
        movie.age_rating
    ).strip()

    duration = request.form.get(
        "duration",
        movie.duration
    ).strip()

    poster = request.form.get(
        "poster",
        movie.poster
    ).strip()

    backdrop = request.form.get(
        "backdrop",
        movie.backdrop or ""
    ).strip()

    category = request.form.get(
        "category",
        movie.category
    ).strip()

    description = request.form.get(
        "description",
        movie.description
    ).strip()

    trailer_url = request.form.get(
        "trailer_url",
        movie.trailer_url or ""
    ).strip()

    language = request.form.get(
        "language",
        movie.language or ""
    ).strip()

    cast = request.form.get(
        "cast",
        movie.cast or ""
    ).strip()

    director = request.form.get(
        "director",
        movie.director or ""
    ).strip()

    status = request.form.get(
        "status",
        movie.status
    ).strip()

    form_data = {
        "title": title,
        "genre": genre,
        "format": format_type,
        "rating": rating,
        "age_rating": age_rating,
        "duration": duration,
        "poster": poster,
        "backdrop": backdrop,
        "category": category,
        "description": description,
        "trailer_url": trailer_url,
        "language": language,
        "cast": cast,
        "director": director,
        "status": status
    }

    is_valid, err_msg = validate_movie_form(form_data, is_update=True)
    if not is_valid:
        flash(
            err_msg,
            "error"
        )
        return redirect(
            url_for("staff_edit_movie", movie_id=movie_id)
        )

    try:
        movie.title = title
        movie.genre = genre
        movie.format = format_type

        try:
            movie.rating = float(rating) if rating else movie.rating
        except ValueError:
            pass

        movie.age_rating = age_rating
        movie.duration = duration
        movie.poster = poster
        movie.backdrop = backdrop or poster
        movie.category = category
        movie.description = description
        movie.trailer_url = trailer_url or movie.trailer_url
        movie.language = language
        movie.cast = cast
        movie.director = director

        if status:
            movie.status = status

        db.session.commit()

        flash(
            f"Movie '{movie.title}' updated successfully!",
            "success"
        )

    except Exception as exc:
        db.session.rollback()
        app.logger.exception("Error while updating movie: %s", exc)
        flash(
            "Unable to update the movie. Please check the entered information and try again.",
            "error"
        )
        return redirect(
            url_for("staff_edit_movie", movie_id=movie_id)
        )

    return redirect(
        url_for("staff_movies")
    )


# ============================================================
# DELETE MOVIE
# ============================================================

@app.route(
    "/staff/delete-movie/<int:movie_id>",
    methods=["POST"]
)
@staff_required
def staff_delete_movie(movie_id):

    movie = Movie.query.get(
        movie_id
    )

    if not movie:

        flash(
            "Movie not found.",
            "error"
        )

        return redirect(
            url_for("staff_movies")
        )

    movie_title = movie.title

    # Check if any showtime for this movie has existing bookings
    showtimes = Showtime.query.filter_by(movie_id=movie.id).all()
    showtime_ids = [st.id for st in showtimes]

    if showtime_ids:
        has_bookings = Booking.query.filter(Booking.showtime_id.in_(showtime_ids)).first()
        if has_bookings:
            flash(
                f"Cannot delete movie '{movie_title}' because it is connected to existing customer bookings. Historical records are preserved.",
                "error"
            )
            return redirect(url_for("staff_movies"))

    try:
        # Delete related unbooked seat records first
        for showtime in showtimes:
            SeatBookingRecord.query.filter_by(
                showtime_id=showtime.id
            ).delete(
                synchronize_session=False
            )

        # Delete unbooked showtimes
        Showtime.query.filter_by(
            movie_id=movie.id
        ).delete(
            synchronize_session=False
        )

        # Delete movie
        db.session.delete(
            movie
        )

        db.session.commit()

        flash(
            f"Movie '{movie_title}' removed successfully.",
            "success"
        )

    except Exception:
        db.session.rollback()
        flash(
            "Unable to delete the movie because it is connected to existing bookings.",
            "error"
        )

    return redirect(
        url_for("staff_movies")
    )


# ============================================================
# STAFF SHOWTIMES
# ============================================================

@app.route("/staff/showtimes")
@staff_required
def staff_showtimes():

    showtimes = Showtime.query.order_by(
        Showtime.date.desc(),
        Showtime.time.desc()
    ).all()

    movies = Movie.query.order_by(
        Movie.title.asc()
    ).all()

    cinemas = Cinema.query.order_by(
        Cinema.name.asc()
    ).all()

    return render_template(
        "staff/showtimes.html",
        showtimes=showtimes,
        movies=movies,
        cinemas=cinemas
    )


@app.route(
    "/staff/add-showtime",
    methods=["POST"]
)
@staff_required
def staff_add_showtime():

    movie_id = request.form.get("movie_id", type=int)
    cinema_id = request.form.get("cinema_id", type=int)
    date_value = request.form.get("date", "").strip()
    time_value = request.form.get("time", "").strip()
    price_value = request.form.get("base_price", "").strip()

    movie = Movie.query.get(movie_id)
    cinema = Cinema.query.get(cinema_id)

    try:
        show_date = datetime.strptime(date_value, "%Y-%m-%d").date()
        base_price = float(price_value)
    except ValueError:
        show_date = None
        base_price = -1

    if not movie or not cinema or not show_date or not time_value or base_price < 0:
        flash("Please provide a valid movie, cinema, date, time, and ticket price.", "error")
        return redirect(url_for("staff_showtimes"))

    db.session.add(
        Showtime(
            movie_id=movie.id,
            cinema_id=cinema.id,
            date=show_date,
            time=time_value,
            base_price=base_price
        )
    )
    db.session.commit()

    flash("Showtime added successfully.", "success")
    return redirect(url_for("staff_showtimes"))


@app.route(
    "/staff/edit-showtime/<int:showtime_id>",
    methods=["GET"]
)
@staff_required
def staff_edit_showtime(showtime_id):

    showtime = Showtime.query.get(showtime_id)
    if not showtime:
        flash("Showtime not found.", "error")
        return redirect(url_for("staff_showtimes"))

    return render_template(
        "staff/edit_showtime.html",
        showtime=showtime,
        movies=Movie.query.order_by(Movie.title.asc()).all(),
        cinemas=Cinema.query.order_by(Cinema.name.asc()).all(),
        has_reservations=bool(showtime.bookings or showtime.seat_records)
    )


@app.route(
    "/staff/edit-showtime/<int:showtime_id>",
    methods=["POST"]
)
@staff_required
def staff_update_showtime(showtime_id):

    showtime = Showtime.query.get(showtime_id)
    if not showtime:
        flash("Showtime not found.", "error")
        return redirect(url_for("staff_showtimes"))

    movie_id = request.form.get("movie_id", type=int)
    cinema_id = request.form.get("cinema_id", type=int)
    date_value = request.form.get("date", "").strip()
    time_value = request.form.get("time", "").strip()
    price_value = request.form.get("base_price", "").strip()

    movie = Movie.query.get(movie_id)
    cinema = Cinema.query.get(cinema_id)

    try:
        show_date = datetime.strptime(date_value, "%Y-%m-%d").date()
        base_price = float(price_value)
    except ValueError:
        show_date = None
        base_price = -1

    if not movie or not cinema or not show_date or not time_value or base_price < 0:
        flash("Please provide a valid movie, cinema, date, time, and ticket price.", "error")
        return redirect(url_for("staff_edit_showtime", showtime_id=showtime.id))

    has_reservations = bool(showtime.bookings or showtime.seat_records)
    structural_change = (
        showtime.movie_id != movie.id or
        showtime.cinema_id != cinema.id or
        showtime.date != show_date or
        showtime.time != time_value
    )

    if has_reservations and structural_change:
        flash("Booked showtimes cannot have their movie, cinema, date, or time changed.", "error")
        return redirect(url_for("staff_edit_showtime", showtime_id=showtime.id))

    showtime.movie_id = movie.id
    showtime.cinema_id = cinema.id
    showtime.date = show_date
    showtime.time = time_value
    showtime.base_price = base_price
    db.session.commit()

    flash("Showtime updated successfully.", "success")
    return redirect(url_for("staff_showtimes"))


@app.route(
    "/staff/delete-showtime/<int:showtime_id>",
    methods=["POST"]
)
@staff_required
def staff_delete_showtime(showtime_id):

    showtime = Showtime.query.get(showtime_id)
    if not showtime:
        flash("Showtime not found.", "error")
        return redirect(url_for("staff_showtimes"))

    if showtime.bookings or showtime.seat_records:
        flash("Booked showtimes cannot be deleted. Existing customer reservations were preserved.", "error")
        return redirect(url_for("staff_showtimes"))

    db.session.delete(showtime)
    db.session.commit()

    flash("Showtime deleted successfully.", "success")
    return redirect(url_for("staff_showtimes"))


# ============================================================
# STAFF CINEMAS
# ============================================================

@app.route("/staff/cinemas")
@staff_required
def staff_cinemas():

    cinemas = Cinema.query.all()

    return render_template(
        "staff/cinemas.html",
        cinemas=cinemas
    )


@app.route(
    "/staff/add-cinema",
    methods=["POST"]
)
@staff_required
def staff_add_cinema():

    name = request.form.get("name", "").strip()
    location = request.form.get("location", "").strip()
    address = request.form.get("address", "").strip()
    city = request.form.get("city", "Chennai").strip() or "Chennai"
    screen_name = request.form.get("screen_name", "LUXE Screen 1").strip() or "LUXE Screen 1"
    formats = request.form.get("formats", "IMAX 4K Laser, Dolby Atmos 12-Channel").strip() or "IMAX 4K Laser, Dolby Atmos 12-Channel"
    screen_type = formats
    status = request.form.get("status", "Active").strip() or "Active"
    facilities = "VIP Lounge, Gourmet Dining, Valet"
    seat_capacity = 40

    if not name or not location or not address:
        flash("Venue name, location, and full address are required.", "error")
        return redirect(url_for("staff_cinemas"))

    try:
        new_cinema = Cinema(
            name=name,
            location=location,
            address=address,
            city=city,
            screen_name=screen_name,
            screen_type=screen_type,
            formats=formats,
            facilities=facilities,
            seat_capacity=seat_capacity,
            status=status
        )
        db.session.add(new_cinema)
        db.session.commit()
        flash("Luxury venue added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding venue: {str(e)}", "error")

    return redirect(url_for("staff_cinemas"))


@app.route(
    "/staff/delete-cinema/<int:cinema_id>",
    methods=["POST"]
)
@staff_required
def staff_delete_cinema(cinema_id):

    cinema = Cinema.query.get(cinema_id)

    if not cinema:
        flash("Cinema venue not found.", "error")
        return redirect(url_for("staff_cinemas"))

    # Relationship Protection: Check if this venue is associated with existing showtimes/screenings
    showtimes = Showtime.query.filter_by(cinema_id=cinema.id).all()
    if showtimes:
        flash(
            "This venue cannot be deleted because it is associated with existing screenings or bookings.",
            "error"
        )
        return redirect(url_for("staff_cinemas"))

    try:
        cinema_name = cinema.name
        db.session.delete(cinema)
        db.session.commit()
        flash(f"Luxury venue '{cinema_name}' removed successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("This venue cannot be deleted because it is associated with existing screenings or bookings.", "error")

    return redirect(url_for("staff_cinemas"))


# ============================================================
# STAFF BOOKINGS
# ============================================================

@app.route("/staff/bookings")
@staff_required
def staff_bookings():

    booking_query = request.args.get(
        "q",
        ""
    ).strip()

    bookings_query = Booking.query

    if booking_query:

        bookings_query = bookings_query.filter(
            (Booking.booking_reference.ilike(
                f"%{booking_query}%"
            ))
            |
            (Booking.customer_name.ilike(
                f"%{booking_query}%"
            ))
            |
            (Booking.email.ilike(
                f"%{booking_query}%"
            ))
            |
            (Booking.phone.ilike(
                f"%{booking_query}%"
            ))
        )

    bookings = bookings_query.order_by(
        Booking.created_at.desc()
    ).all()

    return render_template(
        "staff/bookings.html",
        bookings=bookings,
        booking_query=booking_query
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def server_error(error):

    return render_template(
        "500.html"
    ), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    debug_mode = (
        os.environ.get(
            "DEBUG",
            "False"
        ).lower()
        in ["true", "1", "t"]
    )

    app.run(
        debug=debug_mode,
        port=5000
    )
