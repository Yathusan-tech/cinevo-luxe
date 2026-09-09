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
            <div class="search-dropdown-item"
                 style="color: var(--text-sub); cursor: default;
                        justify-content: center; padding: 16px;">
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

        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }
});

document.getElementById('movieSearch')?.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        const query = this.value.trim();

        if (query) {
            window.location.href =
                "/movies?q=" + encodeURIComponent(query);
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

    if (citySpan) {
        citySpan.innerText = cityName;
    }

    try {
        localStorage.setItem('cinevo_selected_city', cityName);
    } catch (e) {}

    closeModal('cityModal');
}

function filterCities() {
    const input = document.getElementById('citySearchInput');

    if (!input) return;

    const query = input.value.toLowerCase();
    const cards = document.querySelectorAll('#cityGrid .city-card');

    cards.forEach(card => {
        const name =
            card.querySelector('span')?.innerText.toLowerCase() || '';

        card.style.display =
            name.includes(query) ? 'block' : 'none';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    try {
        const savedCity =
            localStorage.getItem('cinevo_selected_city');

        const cityElement =
            document.getElementById('current-city');

        if (savedCity && cityElement) {
            cityElement.innerText = savedCity;
        }
    } catch (e) {}
});

window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        closeModal(event.target.id);
    }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            if (modal.style.display === 'flex') {
                closeModal(modal.id);
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