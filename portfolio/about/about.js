async function loadAboutMe() {
    try {
        const response = await fetch('about_data.json');
        const data = await response.json();

        // Section 1: The Stories
        document.getElementById('intro').innerHTML = `<h1>${data.intro}</h1>`;
        document.getElementById('background').innerHTML = `<p>${data.background}</p>`;
        document.getElementById('hello-gamedev').innerHTML = `<p>${data.helloGamedev}</p>`;
        
        // The Mentor Highlight - Making it stand out
        document.getElementById('mentor').innerHTML = `
            <div class="mentor-card">
                <span class="quote-icon">"</span>
                <p>${data.mentorStory}</p>
                <small>- The Crazy Mentor</small>
            </div>`;

        // Section 2: Favorite Games (Grid)
        const gameContainer = document.getElementById('games-grid');
        data.favoriteGames.forEach(game => {
            gameContainer.innerHTML += `
                <div class="game-box">
                    <img src="${game.icon}" alt="${game.name}">
                    <span>${game.name}</span>
                </div>`;
        });

        // Section 4: The Pitch
        document.getElementById('pitch-section').innerHTML = `
            <div class="pitch-text">
                ${data.pitch}
            </div>
            <a href="mailto:your-email@example.com" class="cta-button">Let's Get Things Done</a>
        `;

    } catch (e) {
        console.error("Initialization error:", e);
    }
}

loadAboutMe();