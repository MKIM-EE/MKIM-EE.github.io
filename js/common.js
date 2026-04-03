/**
 * common.js
 * Shared nav injection, theme toggle, hamburger, back-to-top.
 * Call initPage(basePath) once per page, e.g. initPage('./') or initPage('../')
 */

function initPage(basePath) {
    _injectNav(basePath);
    _initTheme();
    _initHamburger();
    _initBackToTop();
}

function _injectNav(base) {
    const navHTML = `
<nav class="top-nav">
    <div class="nav-container">
        <div class="hamburger" id="hamburger">
            <span></span><span></span><span></span>
        </div>
        <ul class="nav-list" id="nav-list">
            <li class="nav-item"><a href="${base}">About</a></li>
            <li class="nav-item"><a href="${base}research/">Research</a></li>
            <li class="nav-item"><a href="${base}journals/">Journals</a></li>
            <li class="nav-item"><a href="${base}conferences/">Conferences</a></li>
            <li class="nav-item"><a href="${base}patents/">Patents</a></li>
            <li class="nav-item"><a href="${base}cv/">CV</a></li>
        </ul>
        <button class="theme-toggle" id="theme-toggle" aria-label="Toggle dark mode">
            <svg id="sun-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            <svg id="moon-icon" style="display:none" xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                stroke-linejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
        </button>
    </div>
</nav>`;
    document.body.insertAdjacentHTML('afterbegin', navHTML);
}

function _initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');

    function updateTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        if (theme === 'dark') {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        } else {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        }
    }

    themeToggle.addEventListener('click', () => {
        const current = document.body.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        updateTheme(next);
        localStorage.setItem('theme', next);
    });

    const saved = localStorage.getItem('theme');
    if (saved) updateTheme(saved);
}

function _initHamburger() {
    const hamburger = document.getElementById('hamburger');
    const navList = document.getElementById('nav-list');

    hamburger.addEventListener('click', () => {
        navList.classList.toggle('active');
    });

    document.querySelectorAll('.nav-item a').forEach(link => {
        link.addEventListener('click', () => navList.classList.remove('active'));
    });
}

function _initBackToTop() {
    const btn = document.getElementById('back-to-top');
    if (!btn) return;

    window.addEventListener('scroll', () => {
        btn.classList.toggle('visible', window.scrollY > 300);
    });

    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

/** Utility: bold the highlighted author name in an authors string */
function highlightAuthor(authors, highlight) {
    if (!highlight) return authors;
    return authors.replace(highlight, `<strong>${highlight}</strong>`);
}

/** Utility: render badge HTML from array of badge class names */
function renderBadges(badges) {
    if (!badges || badges.length === 0) return '';
    return badges.map(b => {
        const label = b.charAt(0).toUpperCase() + b.slice(1);
        return `<span class="badge ${b}">${label}</span>`;
    }).join('');
}
