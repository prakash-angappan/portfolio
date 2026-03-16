// Verification: Ensure this is how your stats render
let isHomeLoaded = false;
let isProjectsLoaded = false;

function showPage(pageId) {
    const sections = document.querySelectorAll('.page-section');
    sections.forEach(section => section.style.display = 'none');

    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    document.getElementById(pageId).style.display = 'block';
    document.getElementById('btn-' + pageId).classList.add('active');
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
    window.history.pushState(null, null, '#' + pageId);

    if (pageId === 'home' && !isHomeLoaded) loadHomeData();
    if (pageId === 'projects' && !isProjectsLoaded) loadProjectsData();
}

function loadHomeData() {
    const statsContainer = document.getElementById('hero-stats');
    const techContainer = document.getElementById('tech-grid');
    const mgmtContainer = document.getElementById('management-grid');
    const featuredContainer = document.getElementById('featured-grid');
    const actionRow = document.getElementById('action-row');

    Promise.all([
        fetch('home.json').then(res => res.json()),
        fetch('contact.json').then(res => res.json())
    ])
    .then(([homeData, contactData]) => {
        document.getElementById('hero-img').src = homeData.hero.profile_img;
        document.getElementById('hero-name').innerText = homeData.hero.name;
        document.getElementById('hero-title').innerText = homeData.hero.title;
        document.getElementById('hero-summary').innerText = homeData.hero.summary;

        statsContainer.innerHTML = homeData.hero.stats.map(stat => `
            <div class="glass-card stat">
                <div class="dialog-title-box">${stat.label}</div>
                <div class="stat-number">${stat.value}</div>
            </div>`).join('');

        actionRow.innerHTML = ''; 
        contactData.actions.forEach(action => {
            const iconHtml = `<img src="${action.icon}" class="action-icon">`;
            actionRow.innerHTML += `
                <a href="${action.link}" class="btn-action" 
                   ${action.type === 'download' ? 'download' : 'target="_blank"'}>
                   ${iconHtml}${action.label}
                </a>`;
        });

        techContainer.innerHTML = '';
        ['engines', 'platforms'].forEach(key => {
            const category = homeData.tech_stack[key];
            let itemsHtml = category.items.map(item => `
                <div class="tech-badge">
                    <img src="${item.icon}">
                    <span>${item.name}</span>
                </div>`).join('');
            
            techContainer.innerHTML += `
                <div class="glass-card tech-card">
                    <div class="dialog-title-box">${category.title}</div>
                    <div class="tech-items">${itemsHtml}</div>
                </div>`;
        });

        featuredContainer.innerHTML = homeData.featured_projects.map(proj => `
            <div class="featured-project-card glass-card" onclick="navigateToProject('${proj.title}')">
                <div class="featured-banner-wrapper">
                    <img src="${proj.image}" alt="${proj.title}" onerror="this.src='images/icons/unity.png'; this.style.padding='20px';">
                </div>
                <div class="featured-footer">
                    <span>${proj.title}</span>
                </div>
            </div>`).join('');

        mgmtContainer.innerHTML = homeData.management.map(block => {
            let stripsHtml = block.items.map(item => `<div class="skill-strip">${item}</div>`).join('');
            return `
                <div class="glass-card tech-card">
                    <div class="dialog-title-box">${block.category}</div>
                    <div class="skill-strip-grid">${stripsHtml}</div>
                </div>`;
        }).join('');

        isHomeLoaded = true;
        hideLoader();
    });
}

window.navigateToProject = function(projectTitle) {
    showPage('projects');
    const checkExist = setInterval(() => {
        const elements = document.querySelectorAll('h3');
        const target = Array.from(elements).find(el => el.innerText === projectTitle);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
            const card = target.closest('.project-card');
            card.style.borderColor = 'var(--accent)';
            setTimeout(() => card.style.borderColor = 'rgba(255, 255, 255, 0.1)', 2000);
            clearInterval(checkExist);
        }
    }, 100);
};

function loadProjectsData() {
    fetch('projects.json').then(res => res.json()).then(data => {
        const timelineContainer = document.getElementById('timeline-container');
        timelineContainer.innerHTML = '';
        data.work_experience.forEach(job => {

            const projectsHtml = job.projects.map(proj => {
                const tasksHtml = proj.tasks.map(task => `<li>${task}</li>`).join('');
                const storeUrl = proj.link ? proj.link.url : '#';
                const buttonLabel = proj.link ? `View on ${proj.link.label}` : 'View Project';
                
                let mediaContentHtml = '';
                if (proj.video) {
                    // Optimized video container, no fixed height
                    mediaContentHtml = `<div class="video-media-container"><iframe src="${proj.video}" style="width: 100%; height: 100%; border: none;" allowfullscreen></iframe></div>`;
                } else if (proj.image) {
                    // Optimized image container (icons removed)
                    const hoverButtonHtml = proj.link ? `<a href="${storeUrl}" target="_blank" class="hover-action-btn">${buttonLabel}</a>` : '';
                    mediaContentHtml = `<div class="image-media-container"><img class="media-banner" src="${proj.image}" alt="${proj.title}"><div class="media-overlay">${hoverButtonHtml}</div></div>`;
                }

                // Compact badges for the title row
                const engineBadge = `<div class="compact-tech-badge"><img src="${proj.icon}" title="${proj.engine}"></div>`;
                const platformBadges = proj.platforms.map(plat => `<div class="compact-tech-badge"><img src="${plat.icon}" title="${plat.name}"></div>`).join('');

                return `
                    <div class="project-card">
                        <div class="project-media-wrapper">${mediaContentHtml}</div>
                        <div class="project-info">
                            <div class="project-header-row">
                                <h3>${proj.title}</h3>
                                <div class="project-header-icons">${engineBadge}${platformBadges}</div>
                            </div>
                            <p class="project-description">${proj.desc}</p>
                            <div class="contribution-section">
                                <strong class="contribution-title">Contributions:</strong>
                                <ul class="glowing-tasks-list">${tasksHtml}</ul>
                            </div>
                        </div>
                    </div>`;
            }).join('');
            
            timelineContainer.innerHTML += `
    <div class="company-block">
        <h2>${job.company}</h2>
        <div class="project-role-text">${job.role} | ${job.duration}</div>
        ${projectsHtml}
    </div>`;
        });
        isProjectsLoaded = true;
        hideLoader();
    }).catch(err => { console.error("Error:", err); hideLoader(); });
}

function hideLoader() {
    const loader = document.getElementById('loading-overlay');
    if(loader) {
        loader.style.opacity = '0';
        setTimeout(() => loader.style.display = 'none', 500);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const currentHash = window.location.hash.substring(1); 
    if (['home', 'projects', 'contact'].includes(currentHash)) showPage(currentHash);
    else showPage('home');
});