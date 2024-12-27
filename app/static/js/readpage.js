// Set the reading status
let isReading = false;

document.getElementById('readPage').addEventListener('click', function () {
    let contentToRead = '';

    // Get the page title
    const pageTitle = document.querySelector('h1');
    if (pageTitle) {
        contentToRead += pageTitle.innerText + ". ";
    }

    // Get the course list
    const courseCards = document.querySelectorAll('.search-result, .course-card');
    courseCards.forEach(card => {
        const title = card.querySelector('h2, .course-title');
        if (title) {
            contentToRead += 'Course Title: ' + title.innerText + '. ';
        }
    });

    // Use the Speech Synthesis API to read the content
    const speech = new SpeechSynthesisUtterance(contentToRead);
    speech.rate = 1; // Speed rate
    speech.pitch = 1; // Pitch
    speech.lang = "en-US"; // Set the English language

    // Ensure the icon and status reset after speaking finishes
    speech.onend = () => {
        document.getElementById('speakerIcon').classList.replace('bi-volume-up', 'bi-volume-mute');
        isReading = false;
    };

    if (!isReading) {
        // Change the icon
        document.getElementById('speakerIcon').classList.replace('bi-volume-mute', 'bi-volume-up');
        // Start reading
        window.speechSynthesis.speak(speech);
    } else {
        // Change the icon
        document.getElementById('speakerIcon').classList.replace('bi-volume-up', 'bi-volume-mute');
        // Stop reading
        window.speechSynthesis.cancel();
    }

    isReading = !isReading;
});

// Stop speech synthesis when the page is unloaded
window.addEventListener('beforeunload', function () {
    window.speechSynthesis.cancel();
});