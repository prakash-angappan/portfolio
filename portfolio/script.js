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
                const linkBtn = proj.link ? `<a href="${proj.link.url}" target="_blank" class="btn-action"><span style="margin-right: 6px;">${proj.link.icon}</span> ${proj.link.label}</a>` : '';

                return `
                    <div class="project-card" style="margin-bottom: 20px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 25px; display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                        <div class="project-media" style="width: 100%; aspect-ratio: 16/9; border-radius: 8px; overflow: hidden; background: #000;">
                            <iframe src="${proj.video}" style="width: 100%; height: 100%; border: none;" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
                        </div>
                        <div class="project-info">
                            <div class="project-header" style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                                <img src="${proj.icon}" alt="Engine" style="width: 32px; height: 32px; background: #fff; padding: 4px; border-radius: 6px; object-fit: contain;">
                                <h3 style="margin: 0; color: #fff; font-size: 1.5rem;">${proj.title}</h3>
                            </div>
                            <p class="project-desc" style="color: var(--muted); font-size: 0.95rem;">${proj.desc}</p>
                            <ul class="project-tasks" style="list-style: none; padding: 0; margin: 0 0 20px 0;">
                                ${tasksHtml}
                            </ul>
                            <div class="project-links">${linkBtn}</div>
                        </div>
                    </div>`;
            }).join('');

            timelineContainer.innerHTML += `
                <div class="company-block" style="margin-bottom: 50px; position: relative; padding-left: 20px; border-left: 2px solid rgba(255, 255, 255, 0.1);">
                    <div class="company-header" style="margin-bottom: 20px;">
                        <h2 style="color: #fff; font-size: 1.8rem; margin: 0;">${job.company}</h2>
                        <div class="company-meta" style="color: var(--accent); font-weight: 600; margin-top: 5px;">${job.role} | ${job.duration}</div>
                    </div>
                    <div class="company-projects-grid">${projectsHtml}</div>
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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    showPage('home');
});