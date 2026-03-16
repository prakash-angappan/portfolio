let isHomeLoaded = false;
let isProjectsLoaded = false;
let isContactLoaded = false;

// Navigation Logic
function showPage(pageId) {
    const sections = document.querySelectorAll('.page-section');
    sections.forEach(section => section.style.display = 'none');

    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    document.getElementById(pageId).style.display = 'block';
    document.getElementById('btn-' + pageId).classList.add('active');
    
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // --- NEW LINE: Update the URL without reloading the page ---
    window.history.pushState(null, null, '#' + pageId);

    // Lazy load data based on the page
    if (pageId === 'home' && !isHomeLoaded) loadHomeData();
    if (pageId === 'projects' && !isProjectsLoaded) loadProjectsData();
    if (pageId === 'contact' && !isContactLoaded) loadContactData();
}
function loadHomeData() {
    Promise.all([
        fetch('home.json').then(res => res.json()),
        fetch('contact.json').then(res => res.json())
    ])
    .then(([homeData, contactData]) => {
        // Hero
        document.getElementById('hero-img').src = homeData.hero.profile_img;
        document.getElementById('hero-name').innerText = homeData.hero.name;
        document.getElementById('hero-title').innerText = homeData.hero.title;
        document.getElementById('hero-summary').innerText = homeData.hero.summary;

        // Stats
        const statsContainer = document.getElementById('hero-stats');
        statsContainer.innerHTML = '';
        homeData.hero.stats.forEach(stat => {
            statsContainer.innerHTML += `
                <div class="glass-card stat">
                    <div class="dialog-title-box">${stat.label}</div>
                    <div class="stat-number" style="font-size: 1.5rem; font-weight: bold;">${stat.value}</div>
                </div>`;
        });

        // Action Row
        const actionRow = document.getElementById('action-row');
        actionRow.innerHTML = ''; 
        contactData.actions.forEach(action => {
            const iconHtml = `<img src="${action.icon}" class="action-icon" alt="" aria-hidden="true">`;
            if (action.type === 'contact') {
                actionRow.innerHTML += `<div class="contact-item">${iconHtml}${action.label}</div>`;
            } else {
                const downloadAttr = action.type === 'download' ? 'download' : '';
                const targetAttr = action.type === 'link' ? 'target="_blank"' : '';
                actionRow.innerHTML += `<a href="${action.link}" class="btn-action" ${downloadAttr} ${targetAttr}>${iconHtml}${action.label}</a>`;
            }
        });

        // Tech Stack
        const techContainer = document.getElementById('tech-grid');
        techContainer.innerHTML = '';
        ['engines', 'platforms'].forEach(key => {
            const category = homeData.tech_stack[key];
            let itemsHtml = category.items.map(item => `
                <div class="tech-badge">
                    <img src="${item.icon}" alt="${item.name}" onerror="this.style.display='none'">
                    <span>${item.name}</span>
                </div>
            `).join('');
            techContainer.innerHTML += `
                <div class="glass-card tech-card">
                    <div class="dialog-title-box">${category.title}</div>
                    <div class="tech-items">${itemsHtml}</div>
                </div>`;
        });

        // Management
        const mgmtContainer = document.getElementById('management-grid');
        mgmtContainer.innerHTML = ''; 
        homeData.management.forEach(block => {
            let stripsHtml = block.items.map(item => `<div class="skill-strip">${item}</div>`).join('');
            mgmtContainer.innerHTML += `
                <div class="glass-card tech-card">
                    <div class="dialog-title-box">${block.category}</div>
                    <div class="skill-strip-grid">${stripsHtml}</div>
                </div>`;
        });

        isHomeLoaded = true;
        hideLoader();
    }).catch(err => console.error("Error loading home:", err));
}

function loadProjectsData() {
    fetch('projects.json').then(res => res.json()).then(data => {
        const timelineContainer = document.getElementById('timeline-container');
        timelineContainer.innerHTML = '';

        data.work_experience.forEach(job => {
            const projectsHtml = job.projects.map(proj => {
                const tasksHtml = proj.tasks.map(task => `<li>${task}</li>`).join('');
                const storeUrl = proj.link ? proj.link.url : '#';
                const buttonLabel = proj.link ? `View on ${proj.link.label}` : 'View Project';
                const buttonIcon = proj.link ? proj.link.icon : '🎮';

                // --- Media Logic (YouTube or Image) ---
                let mediaContentHtml = '';
                if (proj.video) {
                    mediaContentHtml = `
                        <div class="video-media-container" style="width: 100%; height: 100%; position: relative; overflow: hidden; border-radius: 8px;">
                            <iframe src="${proj.video}" style="width: 100%; height: 100%; border: none;" allowfullscreen></iframe>
                        </div>`;
                } else if (proj.image) {
                    mediaContentHtml = `
                        <div class="image-media-container" style="width: 100%; height: 100%; position: relative; overflow: hidden; background: #0F172A; border-radius: 8px;">
                            <img class="media-banner" src="${proj.image}" alt="${proj.title}" style="width: 100%; height: auto; display: block; transition: transform 0.4s ease;">
                            <div class="media-overlay" style="position: absolute; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(3px); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.3s ease;">
                                <a href="${storeUrl}" target="_blank" class="hover-action-btn" style="text-decoration: none; color: #fff; font-weight: bold; font-size: 1.1rem; border: 2px solid var(--accent); padding: 12px 24px; border-radius: 8px; background: rgba(46, 204, 113, 0.15); display: flex; align-items: center; gap: 8px; transform: scale(0.8); transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);">
                                    <span>${buttonIcon}</span> ${buttonLabel}
                                </a>
                            </div>
                        </div>`;
                }

                // --- Badges Logic (Engine & Platform) ---
                // Note: Ensure your projects.json has platform_icon paths!
                const engineBadge = `
                    <div class="tech-badge" style="min-width: 80px; padding: 5px;">
                        <img src="${proj.icon}" alt="${proj.engine}" style="width: 40px; height: 40px; padding: 2px;">
                        <span style="font-size: 0.7rem;">${proj.engine}</span>
                    </div>`;

                const platformBadge = `
                    <div class="tech-badge" style="min-width: 80px; padding: 5px;">
                        <img src="images/icons/platform.png" alt="Platform" style="width: 40px; height: 40px; padding: 2px; background: #fff; border-radius: 4px; object-fit: contain;">
                        <span style="font-size: 0.7rem;">${proj.platform}</span>
                    </div>`;

                return `
                    <div class="project-card" style="margin-bottom: 30px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 25px; display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                        
                        <div class="project-media-wrapper" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); overflow: hidden; aspect-ratio: 16/9;">
                            ${mediaContentHtml}
                        </div>
                        
                        <div class="project-info" style="display: flex; flex-direction: column; gap: 15px;">
                            <h3 style="margin: 0; color: #fff; font-size: 1.6rem;">${proj.title}</h3>
                            <p style="color: var(--muted); margin: 0; font-size: 0.95rem;">${proj.desc}</p>

                            <div style="display: flex; gap: 15px;">
                                ${engineBadge}
                                ${platformBadge}
                            </div>

                            <div style="margin-top: 5px;">
                                <strong style="color: var(--accent); font-size: 0.8rem; text-transform: uppercase;">Key Contributions:</strong>
                                <ul style="margin: 8px 0 0 0; padding-left: 18px; color: var(--muted); font-size: 0.9rem;">
                                    ${tasksHtml}
                                </ul>
                            </div>
                        </div>
                    </div>`;
            }).join('');

            timelineContainer.innerHTML += `
                <div class="company-block" style="margin-bottom: 60px; padding-left: 20px; border-left: 2px solid rgba(255, 255, 255, 0.1);">
                    <h2 style="color: #fff; font-size: 1.8rem; margin: 0;">${job.company}</h2>
                    <div style="color: var(--accent); font-weight: 600; margin-bottom: 20px;">${job.role} | ${job.duration}</div>
                    ${projectsHtml}
                </div>`;
        });
        isProjectsLoaded = true;
    }).catch(err => console.error("Error loading projects:", err));
}

function loadContactData() {
    fetch('contact.json').then(res => res.json()).then(data => {
        document.getElementById('contact-intro').innerText = data.contact.intro;
        document.getElementById('contact-location').innerText = data.contact.location;
        document.getElementById('contact-phone').innerText = data.contact.phone;
        document.getElementById('btn-email').href = `mailto:${data.contact.email}`;
        document.getElementById('btn-linkedin').href = data.contact.linkedin;
        document.getElementById('btn-resume').href = data.contact.resume;
        isContactLoaded = true;
    }).catch(err => console.error("Error loading contact:", err));
}

function hideLoader() {
    const loader = document.getElementById('loading-overlay');
    if(loader) {
        loader.style.opacity = '0';
        setTimeout(() => loader.style.display = 'none', 500);
    }
}

// Initialize based on URL hash
document.addEventListener('DOMContentLoaded', () => {
    // Look at the URL (e.g., website.com/#projects) and grab the word after the '#'
    const currentHash = window.location.hash.substring(1); 
    
    // Check if it's a valid page, otherwise default to 'home'
    const validPages = ['home', 'projects', 'contact'];
    
    if (validPages.includes(currentHash)) {
        showPage(currentHash);
    } else {
        showPage('home');
    }
});