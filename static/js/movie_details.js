function handleSearchInput() {
    const input = document.getElementById('movieSearch');
    if (!input) return;

    const query = input.value.toLowerCase().trim();
    const dropdown = document.getElementById('searchDropdown');
    if (!dropdown) return;

    if (query.length === 0) {
        dropdown.style.display = 'none';
        return;
    }

    const matches = [
        ...availableMovies.filter(m => m.name.toLowerCase().includes(query)),
        ...availableCinemas.filter(c => c.name.toLowerCase().includes(query))
    ];

    if (matches.length > 0) {
        dropdown.innerHTML = `
            <div class="search-dropdown-header">Quick Suggestions</div>
            ${matches.map(item => `
                <a href="${item.url}" class="search-dropdown-item">
                    <span>${item.name}</span>
                    <span class="item-type">${item.type}</span>
                </a>
            `).join('')}
        `;
        dropdown.style.display = 'block';
    } else {
        dropdown.innerHTML = `
            <div class="search-dropdown-item" style="color: var(--text-sub); cursor: default; justify-content: center; padding: 16px;">
                <span>No matches found</span>
            </div>
        `;
        dropdown.style.display = 'block';
    }
}

document.addEventListener('click', function(e) {
    const container = document.querySelector('.search-container');
    if (container && !container.contains(e.target)) {
        const dropdown = document.getElementById('searchDropdown');
        if (dropdown) dropdown.style.display = 'none';
    }
});

document.getElementById('movieSearch')?.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        const query = this.value.trim();
        if (query) {
            window.location.href = "/movies?q=" + encodeURIComponent(query);
        }
    }
});

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

function selectCity(cityName) {
    const citySpan = document.getElementById('current-city');
    if (citySpan) citySpan.innerText = cityName;

    try {
        localStorage.setItem('cinevo_selected_city', cityName);
    } catch(e) {}

    closeModal('cityModal');
}

function filterCities() {
    const input = document.getElementById('citySearchInput');
    if (!input) return;

    const query = input.value.toLowerCase();
    const cards = document.querySelectorAll('#cityGrid .city-card');

    cards.forEach(card => {
        const name = card.querySelector('span')?.innerText.toLowerCase() || '';
        card.style.display = name.includes(query) ? 'block' : 'none';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    try {
        const savedCity = localStorage.getItem('cinevo_selected_city');

        if (savedCity && document.getElementById('current-city')) {
            document.getElementById('current-city').innerText = savedCity;
        }
    } catch(e) {}
});


/* ============================================================
   TRAILER MODAL
   ============================================================ */

function convertToEmbedUrl(url) {
    try {
        const parsed = new URL(url);
        const host = parsed.hostname.replace(/^www\./, '');

        const isYouTube =
            host === 'youtube.com' ||
            host === 'm.youtube.com' ||
            host === 'youtu.be';

        if (isYouTube && parsed.pathname === '/watch') {
            const videoId = parsed.searchParams.get('v');

            if (videoId) {
                return 'https://www.youtube.com/embed/' + videoId;
            }
        }

        if (host === 'youtu.be') {
            return 'https://www.youtube.com/embed' + parsed.pathname;
        }

        return url;

    } catch (e) {
        return url;
    }
}

function pinTrailerToViewport() {
    const modal = document.getElementById('trailerModal');

    if (!modal) return;

    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.zIndex = '9999';
}

function unpinTrailerFromViewport() {
    const modal = document.getElementById('trailerModal');

    if (!modal) return;

    modal.style.position = '';
    modal.style.top = '';
    modal.style.left = '';
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
        embedUrl += embedUrl.includes('?')
            ? '&autoplay=1'
            : '?autoplay=1';
    }

    frame.src = embedUrl;

    pinTrailerToViewport();

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeTrailer() {
    const modal = document.getElementById('trailerModal');
    const frame = document.getElementById('trailerFrame');

    if (frame) {
        frame.src = 'about:blank';
    }

    if (modal) {
        modal.style.display = 'none';
        unpinTrailerFromViewport();
    }

    document.body.style.overflow = '';
}


window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal-overlay')) {

        if (event.target.id === 'trailerModal') {
            closeTrailer();
        } else {
            closeModal(event.target.id);
        }
    }
});


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


function toggleCinevoNav() {

    var drawer = document.getElementById('cinevoNavDrawer');
    var overlay = document.getElementById('cinevoDrawerOverlay');

    if (drawer && overlay) {

        var isOpen = drawer.classList.contains('open');

        if (isOpen) {

            drawer.classList.remove('open');
            overlay.classList.remove('active');

        } else {

            drawer.classList.add('open');
            overlay.classList.add('active');

        }

    }

}