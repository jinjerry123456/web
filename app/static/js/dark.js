// theme switcher dark and light mode script

const bodyElement = document.querySelector('body');
const themeToggle = document.querySelector('#themeToggle');
const darkModeMql = window.matchMedia('(prefers-color-scheme: dark)');

const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : userPreference(darkModeMql);

if (currentTheme) {
    bodyElement.classList.add(currentTheme);

    if (currentTheme === 'dark') {
        themeToggle.checked = true;
    }
}

function userPreference(e) {
    if (e.matches) {
        bodyElement.classList.add("dark");
        return "dark"
    } else {
        bodyElement.classList.remove("dark");
        return ""
    }
}

darkModeMql.addListener(userPreference);

function themeSwitcher(e) {
    if (e.target.checked) {
        bodyElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    } else {
        bodyElement.classList.remove('dark');
        localStorage.setItem('theme', '');
    }
}

themeToggle.addEventListener('change', themeSwitcher);


