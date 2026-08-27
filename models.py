from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    poster = db.Column(db.String(500), nullable=False)
    backdrop = db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Float, default=9.0)
    age_rating = db.Column(db.String(20), nullable=False, default='UA 16+')
    duration = db.Column(db.String(50), nullable=False, default='2h 30m')
    format = db.Column(db.String(100), nullable=False, default='2D • 3D • ATMOS')
    genre = db.Column(db.String(100), nullable=False, default='Action / Sci-Fi')
    category = db.Column(db.String(50), nullable=False, default='now_showing') # now_showing, premiere, imax
    trailer_url = db.Column(db.String(500), default='https://www.youtube.com/embed/TcMBFSGVi1c?autoplay=1')
    release_date = db.Column(db.Date, default=date.today)
    language = db.Column(db.String(50), default='English')
    cast = db.Column(db.Text, default='Ensemble Cast')
    director = db.Column(db.String(100), default='Cinevo Director')
    status = db.Column(db.String(30), nullable=False, default='Now Showing')

    showtimes = db.relationship('Showtime', backref='movie', lazy=True, cascade='all, delete-orphan')

    @property
    def name(self):
        return self.title

    @name.setter
    def name(self, val):
        self.title = val

    @property
    def formatted_rating(self):
        if self.rating is not None:
            return f"{self.rating:.1f}" if not float(self.rating).is_integer() else f"{int(self.rating)}"
        return "9.0"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.title,
            'title': self.title,
            'genre': self.genre,
            'duration': self.duration,
            'rating': self.formatted_rating,
            'poster': self.poster,
            'backdrop': self.backdrop or self.poster,
            'description': self.description,
            'format': self.format,
            'category': self.category,
            'trailer_url': self.trailer_url,
            'age_rating': self.age_rating,
            'language': self.language,
            'status': self.status
        }


class Cinema(db.Model):
    __tablename__ = 'cinemas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False, default='Chennai')
    screen_name = db.Column(db.String(50), nullable=False, default='LUXE Screen 1')
    screen_type = db.Column(db.String(50), nullable=False, default='IMAX Laser & Dolby Atmos')
    formats = db.Column(db.String(100), nullable=False, default='IMAX 4K Laser, Dolby Atmos 12-Channel')
    facilities = db.Column(db.String(250), nullable=False, default='VIP Lounge, Gourmet Dining, Valet')
    seat_capacity = db.Column(db.Integer, nullable=False, default=40)
    status = db.Column(db.String(30), nullable=False, default='Active')

    showtimes = db.relationship('Showtime', backref='cinema', lazy=True, cascade='all, delete-orphan')


class Showtime(db.Model):
    __tablename__ = 'showtimes'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    cinema_id = db.Column(db.Integer, db.ForeignKey('cinemas.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    time = db.Column(db.String(20), nullable=False, default='07:00 PM') # e.g. '10:30 AM', '02:15 PM', '06:45 PM', '09:30 PM'
    base_price = db.Column(db.Float, nullable=False, default=250.0)

    bookings = db.relationship('Booking', backref='showtime', lazy=True, cascade='all, delete-orphan')
    seat_records = db.relationship('SeatBookingRecord', backref='showtime', lazy=True, cascade='all, delete-orphan')

    @property
    def pricing_breakdown(self):
        base = float(self.base_price) if self.base_price is not None else 250.0
        tax = round(base * 0.18, 2)
        conv = 30.0
        final = round(base + conv + tax, 2)

        c_name = self.cinema.name if self.cinema else ""
        c_type = self.cinema.screen_type if self.cinema else ""
        m_cat = self.movie.category if self.movie else ""

        if "IMAX" in c_name or "IMAX" in c_type or m_cat == "imax":
            stype = "IMAX"
        elif "Royal" in c_name or "VIP" in c_name or "VIP" in c_type:
            stype = "VIP LOUNGE"
        elif m_cat == "premiere":
            stype = "PREMIERE"
        else:
            stype = "ATMOS"

        return {
            "type": stype,
            "base": base,
            "tax": tax,
            "conv": conv,
            "final": final
        }

    @property
    def price(self):
        return self.pricing_breakdown["final"]

    @property
    def base_ticket_price(self):
        return float(self.base_price) if self.base_price is not None else 250.0

    @property
    def booked_seat_numbers(self):
        seats = set()
        for record in self.seat_records:
            if record.seat_number:
                seats.add(record.seat_number.strip().upper())
        for b in self.bookings:
            if b.seats_string:
                seats_part = b.seats_string.split('|')[0]
                for s in seats_part.split(','):
                    clean = s.strip().upper()
                    if clean and len(clean) <= 4 and clean[0].isalpha() and clean[1:].isdigit():
                        seats.add(clean)
        return list(seats)


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(30), unique=True, nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    showtime_id = db.Column(db.Integer, db.ForeignKey('showtimes.id'), nullable=True)

    seat_count = db.Column(db.Integer, nullable=False, default=1)
    seats_string = db.Column(db.Text, nullable=False) # e.g. "A1, A2, A3" or "Food Order: Popcorn x2"
    ticket_amount = db.Column(db.Float, nullable=False)
    convenience_fee = db.Column(db.Float, nullable=False, default=30.0)
    taxes = db.Column(db.Float, nullable=False, default=18.0)
    discount = db.Column(db.Float, nullable=False, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)

    payment_status = db.Column(db.String(30), nullable=False, default='Paid')
    booking_status = db.Column(db.String(30), nullable=False, default='Confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    seat_records = db.relationship('SeatBookingRecord', backref='booking', lazy=True, cascade='all, delete-orphan')

    @property
    def is_food_only(self):
        return self.showtime_id is None

    @property
    def booking_ref(self):
        return self.booking_reference

    @property
    def seats(self):
        return self.seats_string

    @property
    def total_amount(self):
        return self.final_amount

    @property
    def movie_name(self):
        if self.showtime and self.showtime.movie:
            return self.showtime.movie.title
        return "Food / Lounge Reservation"

    @property
    def movie_title(self):
        return self.movie_name

    @property
    def poster(self):
        return self.showtime.movie.poster if self.showtime and self.showtime.movie else ""

    @property
    def cinema_name(self):
        if self.showtime and self.showtime.cinema:
            return self.showtime.cinema.name
        return "Cinevo Gourmet Lounge"

    @property
    def time(self):
        if self.showtime and self.showtime.time:
            return self.showtime.time
        if self.created_at:
            return self.created_at.strftime('%I:%M %p')
        return "Lounge Service"

    @property
    def date_str(self):
        if self.showtime and self.showtime.date:
            return self.showtime.date.strftime('%a, %d %b %Y')
        if self.created_at:
            return self.created_at.strftime('%a, %d %b %Y')
        return datetime.utcnow().strftime('%a, %d %b %Y')

    @property
    def price(self):
        return f"₹{int(self.final_amount)}" if float(self.final_amount).is_integer() else f"₹{self.final_amount:.2f}"


class SeatBookingRecord(db.Model):
    """Tracks globally locked/booked seats per showtime to prevent race conditions & double-booking."""
    __tablename__ = 'seat_booking_records'
    id = db.Column(db.Integer, primary_key=True)
    showtime_id = db.Column(db.Integer, db.ForeignKey('showtimes.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False) # e.g. A1, B4
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('showtime_id', 'seat_number', name='unique_showtime_seat'),
    )