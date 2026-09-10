
    /* Movie data is provided by home.html */


    /* ============================================================
       CINEMA SEARCH DATA
       ============================================================ */

    const availableCinemas = [

        {
            name: "Cinevo Pallas Grand",
            url: "#showtimings",
            type: "Cinema"
        },

        {
            name: "Cinevo IMAX Signature",
            url: "#showtimings",
            type: "Cinema"
        },

        {
            name: "Cinevo Royal Suite",
            url: "#showtimings",
            type: "Cinema"
        },

        {
            name: "Chennai Cinemas Hub",
            url: "#showtimings",
            type: "Location"
        }

    ];


    /* ============================================================
       MOBILE MENU
       ============================================================ */

    function toggleMobileMenu() {

        const drawer =
            document.getElementById('mobileDrawer');

        drawer.style.display =
            drawer.style.display === 'flex'
                ? 'none'
                : 'flex';

    }


    /* ============================================================
       CAROUSEL
       ============================================================ */

    function scrollCarousel(carouselId, direction) {

        const container =
            document.getElementById(carouselId);

        if (container) {

            const firstCard =
                container.querySelector('.movie-card');

            if (firstCard) {

                const cardWidth =
                    firstCard.offsetWidth + 18;

                container.scrollBy({
                    left: direction * cardWidth,
                    behavior: 'smooth'
                });

            }

        }

        if (typeof isNowShowingPaused !== 'undefined') {
            isNowShowingPaused = true;
            setTimeout(() => { isNowShowingPaused = false; }, 3500);
        }

    }


    /* ============================================================
       SEARCH
       ============================================================ */

    function handleSearchInput() {

        const query =
            document
                .getElementById('movieSearch')
                .value
                .toLowerCase()
                .trim();

        const dropdown =
            document.getElementById('searchDropdown');

        const cards =
            document.querySelectorAll('.movie-card');

        cards.forEach(card => {

            const title =
                card.getAttribute('data-title') || '';

            card.style.display =
                title.includes(query)
                    ? 'flex'
                    : 'none';

        });

        if (query.length === 0) {

            dropdown.style.display = 'none';

            return;

        }

        const moviesList = (window.availableMovies && window.availableMovies.length > 0)
            ? window.availableMovies
            : (typeof availableMovies !== 'undefined' && Array.isArray(availableMovies) ? availableMovies : []);

        const cinemasList = (window.availableCinemas && window.availableCinemas.length > 0)
            ? window.availableCinemas
            : (typeof availableCinemas !== 'undefined' && Array.isArray(availableCinemas) ? availableCinemas : []);

        const matches = [

            ...moviesList.filter(
                m => (m.name || '').toLowerCase().includes(query)
            ),

            ...cinemasList.filter(
                c => (c.name || '').toLowerCase().includes(query)
            )

        ];

        if (matches.length > 0) {

            dropdown.innerHTML = `

                <div class="search-dropdown-header">
                    Quick Suggestions
                </div>

                ${matches.map(item => `

                    <a
                        href="${item.url}"
                        class="search-dropdown-item">

                        <span>
                            ${item.name}
                        </span>

                        <span class="item-type">
                            ${item.type}
                        </span>

                    </a>

                `).join('')}

            `;

            dropdown.style.display = 'block';

        } else {

            dropdown.innerHTML = `

                <div
                    class="search-dropdown-item"
                    style="
                        color: var(--text-sub);
                        cursor: default;
                        justify-content: center;
                        padding: 16px;
                    ">

                    <span>
                        No matches found
                    </span>

                </div>

            `;

            dropdown.style.display = 'block';

        }

    }


    /* ============================================================
       CLOSE SEARCH WHEN CLICKING OUTSIDE
       ============================================================ */

    document.addEventListener('click', function(e) {

        const container =
            document.querySelector('.search-container');

        if (
            container &&
            !container.contains(e.target)
        ) {

            document
                .getElementById('searchDropdown')
                .style.display = 'none';

        }

    });

    document.getElementById('movieSearch')?.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const query = this.value.trim();
            if (query) {
                window.location.href = window.cinevoMoviesSearchUrl + encodeURIComponent(query);
            }
        }
    });


    /* ============================================================
       GENERIC MODALS
       ============================================================ */

    function openModal(id) {

        const modal =
            document.getElementById(id);

        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }

    }


    function closeModal(id) {

        const modal =
            document.getElementById(id);

        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }

    }


    /* ============================================================
       CLICK OUTSIDE MODAL
       ============================================================ */

    window.addEventListener('click', function(event) {

        if (
            event.target.classList.contains('modal-overlay')
        ) {

            if (event.target.id === 'trailerModal') {

                closeTrailer();

            } else {

                closeModal(event.target.id);

            }

        }

    });


    /* ============================================================
       ESCAPE KEY
       ============================================================ */

    document.addEventListener('keydown', function(event) {

        if (event.key === 'Escape') {

            document.querySelectorAll('.modal-overlay').forEach(modal => {
                if (modal.style.display === 'flex') {
                    if (modal.id === 'trailerModal') {
                        closeTrailer();
                    } else {
                        closeModal(modal.id);
                    }
                }
            });

        }

    });


    /* ============================================================
       CITY
       ============================================================ */

    function selectCity(cityName) {

        const citySpan = document.getElementById(
            'current-city'
        );
        if (citySpan) citySpan.innerText = cityName;
        try { localStorage.setItem('cinevo_selected_city', cityName); } catch(e) {}

        closeModal('cityModal');

    }

    document.addEventListener('DOMContentLoaded', function() {
        try {
            const savedCity = localStorage.getItem('cinevo_selected_city');
            if (savedCity && document.getElementById('current-city')) {
                document.getElementById('current-city').innerText = savedCity;
            }
        } catch(e) {}
    });


    function filterCities() {

        let query =
            document
                .getElementById('citySearchInput')
                .value
                .toLowerCase();

        let cards =
            document.querySelectorAll(
                '#cityGrid .city-card'
            );

        cards.forEach(card => {

            let name =
                card
                    .querySelector('span')
                    .innerText
                    .toLowerCase();

            card.style.display =
                name.includes(query)
                    ? 'block'
                    : 'none';

        });

    }


    /* ============================================================
       QUICK BOOKING
       ============================================================ */

        function submitQuickBook(){

    const movieSelect = document.getElementById('qbMovieSelect');
    const dateSelect = document.getElementById('qbDateSelect');
    const cinemaSelect = document.getElementById('qbCinemaSelect');
    const timingSelect = document.getElementById('qbTimingSelect');

    const movieId = movieSelect ? movieSelect.value : '';
    const date = dateSelect ? dateSelect.value : '';
    const cinema = cinemaSelect ? cinemaSelect.value : '';
    const timing = timingSelect ? timingSelect.value : '';

    if (!movieId && movieId !== '0') {

        alert('Please select a movie from the dropdown.');
        return;

    }

    const url = new URL(
        `/movie/${encodeURIComponent(movieId)}`,
        window.location.origin
    );

    if (date) {
        url.searchParams.set('date', date);
    }

    if (cinema) {
        url.searchParams.set('cinema', cinema);
    }

    if (timing) {
        url.searchParams.set('timing', timing);
    }

    window.location.assign(url.toString());

}

/* ============================================================
       SCROLL TO SHOWTIMINGS
       ============================================================ */

    function scrollToShowtimings() {

        const section =
            document.getElementById(
                'showtimings'
            );

        if (section) {

            section.scrollIntoView({
                behavior: 'smooth'
            });

        }

    }


    /* ============================================================
       PROFESSIONAL TRAILER

       This is the important corrected section.
       ============================================================ */

    function pinTrailerToViewport() {

        const modal =
            document.getElementById(
                'trailerModal'
            );

        if (!modal) {
            return;
        }

        modal.style.position = 'absolute';
        modal.style.top = window.scrollY + 'px';
        modal.style.left = window.scrollX + 'px';
        modal.style.right = 'auto';
        modal.style.bottom = 'auto';
        modal.style.width = '100vw';
        modal.style.height = window.innerHeight + 'px';
        modal.style.zIndex = '9999';

    }


    function unpinTrailerFromViewport() {

        const modal =
            document.getElementById(
                'trailerModal'
            );

        if (!modal) {
            return;
        }

        modal.style.position = '';
        modal.style.top = '';
        modal.style.left = '';
        modal.style.right = '';
        modal.style.bottom = '';
        modal.style.width = '';
        modal.style.height = '';
        modal.style.zIndex = '';

    }


    function openTrailer(url) {
        const modal = document.getElementById('trailerModal');
        const frame = document.getElementById('trailerFrame');
        if (!modal || !frame) return;
        if (!url || url.trim() === '') {
            alert('Trailer is currently unavailable.');
            return;
        }

        let embedUrl = convertToEmbedUrl(url);
        if (!/[?&]autoplay=/.test(embedUrl)) {
            embedUrl += embedUrl.includes('?') ? '&autoplay=1' : '?autoplay=1';
        }

        frame.src = embedUrl;
        pinTrailerToViewport();
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }


    /* ============================================================
       YOUTUBE URL CONVERTER
       ============================================================ */

    function convertToEmbedUrl(url) {

        try {

            const parsed =
                new URL(url);

            const host =
                parsed.hostname.replace(
                    /^www\./,
                    ''
                );

            const isYouTube =
                host === 'youtube.com' ||
                host === 'm.youtube.com' ||
                host === 'youtu.be';


            /*
             * youtube.com/watch?v=VIDEO_ID
             */

            if (
                isYouTube &&
                parsed.pathname === '/watch'
            ) {

                const videoId =
                    parsed.searchParams.get('v');

                if (videoId) {

                    return (
                        'https://www.youtube.com/embed/' +
                        videoId
                    );

                }

            }


            /*
             * youtu.be/VIDEO_ID
             */

            if (host === 'youtu.be') {

                const videoId =
                    parsed.pathname
                        .split('/')
                        .filter(Boolean)[0];

                if (videoId) {

                    return (
                        'https://www.youtube.com/embed/' +
                        videoId
                    );

                }

            }


            /*
             * youtube.com/shorts/VIDEO_ID
             */

            if (
                isYouTube &&
                parsed.pathname.indexOf(
                    '/shorts/'
                ) === 0
            ) {

                const videoId =
                    parsed.pathname
                        .split('/')
                        .filter(Boolean)[1];

                if (videoId) {

                    return (
                        'https://www.youtube.com/embed/' +
                        videoId
                    );

                }

            }


            /*
             * Already an embed URL or
             * another supported video URL.
             */

            return url;

        } catch (error) {

            return url;

        }

    }


    /* ============================================================
       CLOSE TRAILER
       ============================================================ */

    function closeTrailer() {

        const modal =
            document.getElementById(
                'trailerModal'
            );

        const frame =
            document.getElementById(
                'trailerFrame'
            );


        /*
         * IMPORTANT:
         * Clearing the iframe source stops
         * the video and audio immediately.
         */

        if (frame) {

            frame.src = 'about:blank';

        }


        /*
         * Hide the modal.
         */

        if (modal) {

            modal.style.display = 'none';
            unpinTrailerFromViewport();

        }


        /*
         * Restore page scrolling.
         */

        document.body.style.overflow = '';

    }



    // Hero Carousel Logic
    let posterCarouselIndex = 0;
    let posterCarouselInterval;
    let isPosterCarouselPaused = false;
    const posterSlides = document.querySelectorAll('.hero-poster-slide');

    // Carousel data is provided by home.html

    const heroLeftContent = document.getElementById('heroLeftContent');
    const heroBgCurrent = document.getElementById('heroBgCurrent');
    const heroBgNext = document.getElementById('heroBgNext');

    function formatHeroTitle(title) {
        if (!title) return '';
        const idx = title.indexOf(': ');
        if (idx !== -1) {
            const prefix = title.substring(0, idx + 1);
            const suffix = title.substring(idx + 2);
            return `${prefix} <span class="gold-title-part">${suffix}</span>`;
        }
        return title;
    }

    function updateHeroDots(activeIndex) {
        const dots = document.querySelectorAll('.hero-dot');
        if (!dots || dots.length === 0) return;
        dots.forEach((dot, idx) => {
            if (idx === activeIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    function goToPosterSlide(newIndex) {
        if (!posterSlides || posterSlides.length <= 1) return;

        const total = posterSlides.length;
        const normalizedIndex = ((newIndex % total) + total) % total;
        if (normalizedIndex === posterCarouselIndex) return;

        const currentSlide = posterSlides[posterCarouselIndex];
        posterCarouselIndex = normalizedIndex;
        const nextSlide = posterSlides[posterCarouselIndex];
        const nextData = carouselData[posterCarouselIndex];
        if (!nextSlide || !nextData) return;

        // 1. Fade out current left content and set next background
        if (heroLeftContent) heroLeftContent.style.opacity = '0';

        if (heroBgNext) {
            heroBgNext.style.backgroundImage = `url('${nextData.backdrop}')`;
            heroBgNext.style.opacity = '1';
        }

        // 2. Poster slide transition
        currentSlide.style.opacity = '0';
        currentSlide.style.zIndex = '1';
        nextSlide.style.opacity = '1';
        nextSlide.style.zIndex = '2';

        // 3. Update pagination dots if present
        updateHeroDots(posterCarouselIndex);

        // 4. Update left content after fade out completes
        setTimeout(() => {
            const titleEl = document.getElementById('heroTitle');
            if (titleEl) titleEl.innerHTML = formatHeroTitle(nextData.title);
            const ratingEl = document.getElementById('heroRating');
            if (ratingEl) ratingEl.innerHTML = `★ ${nextData.rating || '8.1'} RATING`;
            const ageEl = document.getElementById('heroAge');
            if (ageEl) ageEl.innerText = nextData.age_rating || 'UA 13+';
            const durEl = document.getElementById('heroDuration');
            if (durEl) durEl.innerText = nextData.duration || '3h 12m';
            const fmtEl = document.getElementById('heroFormat');
            if (fmtEl) fmtEl.innerText = nextData.format || '3D HFR • DOLBY CINEMA';
            const descEl = document.getElementById('heroDesc');
            if (descEl) descEl.innerText = nextData.description;
            const genreEl = document.getElementById('heroGenre');
            if (genreEl) genreEl.innerText = nextData.genre || 'Sci-Fi/Fantasy';
            const langEl = document.getElementById('heroLanguage');
            if (langEl) langEl.innerText = nextData.language || 'English/Tamil';
            const dirEl = document.getElementById('heroDirector');
            if (dirEl) dirEl.innerText = nextData.director || 'Cinevo Director';
            const bookEl = document.getElementById('heroBookBtn');
            if (bookEl) {
                bookEl.href = nextData.details_url;
                bookEl.innerHTML = '<span>Reserve Tickets ›</span>';
            }

            // Fade left content back in
            if (heroLeftContent) heroLeftContent.style.opacity = '1';

            // Commit background transition quietly
            if (heroBgCurrent) heroBgCurrent.style.backgroundImage = `url('${nextData.backdrop}')`;
            if (heroBgNext) heroBgNext.style.opacity = '0';

        }, 400); // 400ms transition

        // Restart timer smoothly after manual interaction
        restartPosterCarouselTimer();
    }

    function stepPosterCarousel(direction) {
        if (!posterSlides || posterSlides.length <= 1) return;
        goToPosterSlide(posterCarouselIndex + direction);
    }

    function startPosterCarousel() {
        if (!posterSlides || posterSlides.length <= 1) return;
        if (posterCarouselInterval) clearInterval(posterCarouselInterval);

        posterCarouselInterval = setInterval(() => {
            if (isPosterCarouselPaused) return;
            stepPosterCarousel(1);
        }, 5000); // 5 seconds comfortable luxury interval
    }

    function restartPosterCarouselTimer() {
        if (posterCarouselInterval) {
            clearInterval(posterCarouselInterval);
            posterCarouselInterval = null;
        }
        startPosterCarousel();
    }

    function pausePosterCarousel() {
        isPosterCarouselPaused = true;
    }

    function resumePosterCarousel() {
        isPosterCarouselPaused = false;
    }

    // Horizontal Movie Carousel Auto-Scroll (Now Showing)
    let nowShowingAutoScrollInterval = null;
    let isNowShowingPaused = false;

    function startNowShowingAutoScroll() {
        const container = document.getElementById('nowShowingCarousel');
        if (!container) return;

        if (nowShowingAutoScrollInterval) clearInterval(nowShowingAutoScrollInterval);

        nowShowingAutoScrollInterval = setInterval(() => {
            if (isNowShowingPaused) return;

            const firstCard = container.querySelector('.movie-card');
            if (!firstCard) return;

            const cardWidth = firstCard.offsetWidth + 18;
            const maxScroll = container.scrollWidth - container.clientWidth;

            // Smooth loop when reaching the end
            if (container.scrollLeft >= maxScroll - 15) {
                container.scrollTo({ left: 0, behavior: 'smooth' });
            } else {
                container.scrollBy({ left: cardWidth, behavior: 'smooth' });
            }
        }, 5000); // 5 seconds comfortable luxury interval
    }

    function initCarouselListeners() {
        const container = document.getElementById('nowShowingCarousel');
        if (!container) return;

        container.addEventListener('mouseenter', () => { isNowShowingPaused = true; });
        container.addEventListener('mouseleave', () => { isNowShowingPaused = false; });
        container.addEventListener('touchstart', () => { isNowShowingPaused = true; }, { passive: true });
        container.addEventListener('touchend', () => {
            setTimeout(() => { isNowShowingPaused = false; }, 2500);
        }, { passive: true });

        // Touch support for Hero Poster Card
        const heroPoster = document.getElementById('posterCarouselContainer');
        if (heroPoster) {
            let touchStartX = 0;
            heroPoster.addEventListener('touchstart', (e) => {
                touchStartX = e.touches[0].clientX;
                pausePosterCarousel();
            }, { passive: true });

            heroPoster.addEventListener('touchend', (e) => {
                const touchEndX = e.changedTouches[0].clientX;
                const diff = touchEndX - touchStartX;
                if (diff > 40) {
                    stepPosterCarousel(-1); // swipe right -> previous
                } else if (diff < -40) {
                    stepPosterCarousel(1);  // swipe left -> next
                }
                setTimeout(() => { resumePosterCarousel(); }, 2500);
            }, { passive: true });
        }
    }

    // Quick Reserve Date Logic
    function initQuickReserveDates() {
        const dateSelect = document.getElementById("qbDateSelect");
        if (!dateSelect) return;

        // If options are already rendered by server, don't duplicate
        if (dateSelect.options.length > 1) return;

        const today = new Date();
        const tomorrow = new Date();
        tomorrow.setDate(today.getDate() + 1);
        const dayAfter = new Date();
        dayAfter.setDate(today.getDate() + 2);
        const followingDay = new Date();
        followingDay.setDate(today.getDate() + 3);

        const formatDateVal = (d) => {
            const yyyy = d.getFullYear();
            const mm = String(d.getMonth() + 1).padStart(2, '0');
            const dd = String(d.getDate()).padStart(2, '0');
            return `${yyyy}-${mm}-${dd}`;
        };

        const formatLabel = (d, prefix) => {
            const options = { month: 'long', day: 'numeric' };
            const dateStr = d.toLocaleDateString('en-US', options);
            return `${prefix} — ${dateStr}`;
        };

        dateSelect.add(new Option(formatLabel(today, "Today"), formatDateVal(today)));
        dateSelect.add(new Option(formatLabel(tomorrow, "Tomorrow"), formatDateVal(tomorrow)));
        dateSelect.add(new Option(formatLabel(dayAfter, "Day After Tomorrow"), formatDateVal(dayAfter)));
        dateSelect.add(new Option(formatLabel(followingDay, "The Following Day"), formatDateVal(followingDay)));
    }

    // Start on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            startPosterCarousel();
            startNowShowingAutoScroll();
            initCarouselListeners();
            initQuickReserveDates();
        });
    } else {
        startPosterCarousel();
        startNowShowingAutoScroll();
        initCarouselListeners();
        initQuickReserveDates();
    }




