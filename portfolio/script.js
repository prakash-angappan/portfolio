let isHomeLoaded = false;
let isProjectsLoaded = false;

function showPage(pageId) {
    const sections = document.querySelectorAll('.page-section');
    sections.forEach(section => section.style.display = 'none');

    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    const page = document.getElementById(pageId);
    if (!page) return; 

    page.style.display = 'block'; 
    
    const btn = document.getElementById('btn-' + pageId);
    if (btn) btn.classList.add('active');
    
    window.scrollTo({ top: 0, behavior: 'instant' });
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
        
        // Hero Data
        document.getElementById('hero-img').src = homeData.hero.profile_img;
        document.getElementById('hero-name').innerText = homeData.hero.name;
        document.getElementById('hero-title').innerText = homeData.hero.title;
        document.getElementById('hero-summary').innerText = homeData.hero.summary;

        if (statsContainer && homeData.hero.stats) {
            statsContainer.innerHTML = homeData.hero.stats.map(stat => `
                <div class="glass-card stat">
                    <div class="stat-number">${stat.value}</div>
                    <div class="stat-label">${stat.label}</div>
                </div>`).join('');
        }

        // Contact Actions (Compact)
        if (actionRow && contactData.actions) {
            const introEl = document.getElementById('contact-intro');
            if(introEl && contactData.contact.intro) introEl.innerText = contactData.contact.intro;

            const downloadAction = contactData.actions.find(a => a.type === 'download');
            const otherActions = contactData.actions.filter(a => a.type !== 'download');
            
            let actionsHtml = '';
            if (downloadAction) {
                actionsHtml += `<a href="${downloadAction.link}" class="btn-action" download><img src="${downloadAction.icon}" class="action-icon">${downloadAction.label}</a>`;
            }
            actionsHtml += otherActions.map(action => `<a href="${action.link}" class="btn-action" target="_blank"><img src="${action.icon}" class="action-icon">${action.label}</a>`).join('');
            actionRow.innerHTML = actionsHtml;
        }

        // Tech Grid
        if (techContainer && homeData.tech_stack) {
            techContainer.innerHTML = '';
            ['engines', 'platforms'].forEach(key => {
                const category = homeData.tech_stack[key];
                let itemsHtml = category.items.map(item => `
                    <div class="skill-item">
                        <img src="${item.icon}">
                        <span>${item.name}</span>
                    </div>`).join('');
                
                techContainer.innerHTML += `
                    <div class="glass-card tech-card">
                        <div class="dialog-title-box">${category.title}</div>
                        <div class="skills-container">${itemsHtml}</div>
                    </div>`;
            });
        }

        // Featured projects
        if (featuredContainer && homeData.featured_projects) {
            featuredContainer.innerHTML = homeData.featured_projects.map(proj => `
                <div class="featured-project-card glass-card" onclick="navigateToProject('${proj.title}')">
                    <div class="featured-banner-wrapper">
                        <img src="${proj.image}" alt="${proj.title}" onerror="this.src='images/icons/gameengines/unity.png'; this.style.padding='20px';">
                    </div>
                    <div class="featured-footer">
                        <span>${proj.title}</span>
                    </div>
                </div>`).join('');
        }

        // Management Grid
        if (mgmtContainer && homeData.management) {
            mgmtContainer.innerHTML = homeData.management.map(item => `
                <div class="glass-card mgmt-badge">
                    <img src="${item.icon}" alt="${item.name}" class="mgmt-badge-icon">
                    <span class="mgmt-text-label">${item.name}</span>
                </div>`).join('');
        }

        isHomeLoaded = true;
        hideLoader();
    }).catch(err => {
        console.error("error loading data:", err);
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
            setTimeout(() => card.style.borderColor = 'var(--glass-border)', 2000);
            clearInterval(checkExist);
        }
    }, 100);
};

// --- PROJECTS DATA ---
function loadProjectsData() {
    fetch('projects.json').then(res => res.json()).then(data => {
        const timelineContainer = document.getElementById('timeline-container');
        timelineContainer.innerHTML = '';

        data.work_experience.forEach(job => {
            const projectsHtml = job.projects.map(proj => {
                const tasksHtml = proj.tasks.map(task => `<li>${task}</li>`).join('');
                
                // Only create buttons if a REAL url exists (not "#")
                const hasRealLink = proj.link && proj.link.url !== "#";
                const storeUrl = hasRealLink ? proj.link.url : null;
                const buttonLabel = hasRealLink ? `View on ${proj.link.label}` : '';
                const hoverButtonHtml = hasRealLink ? `<a href="${storeUrl}" target="_blank" class="hover-action-btn">${buttonLabel}</a>` : '';
                const overlayHtml = hasRealLink ? `<div class="media-overlay">${hoverButtonHtml}</div>` : '';

                // Header Sequence Elements
                const bgColor = proj.team_bg ? proj.team_bg : 'rgba(46, 204, 113, 0.15)';
                const teamTag = proj.team_size ? `<span class="team-badge-inline" style="background: ${bgColor}">${proj.team_size}</span>` : '';
                const engineIcon = `<div class="compact-tech-badge"><img src="${proj.icon}" title="${proj.engine}"></div>`;
                const platformIcons = proj.platforms ? proj.platforms.map(plat => `<div class="compact-tech-badge"><img src="${plat.icon}" title="${plat.name}"></div>`).join('') : '';

                // Media Elements
                let mediaContentHtml = '';
                if (proj.video) {
                    mediaContentHtml = `
                        <div class="video-media-container">
                            <iframe src="${proj.video}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="width: 100%; height: 100%; position: relative; z-index: 10;"></iframe>
                            ${overlayHtml}
                        </div>`;
                } else if (proj.image) {
                    mediaContentHtml = `
                        <div class="image-media-container">
                            <img class="media-banner" src="${proj.image}" alt="${proj.title}">
                            ${overlayHtml}
                        </div>`;
                }

                return `
                    <div class="project-card">
                        <div class="project-media-wrapper">${mediaContentHtml}</div>
                        <div class="project-info">
                            <div class="project-header-row">
                                <div class="header-left-group">
                                    <h3>${proj.title}</h3>
                                    ${teamTag}
                                    <span class="header-pipe">|</span>
                                    ${engineIcon}
                                    ${platformIcons}
                                </div>
                            </div>
                            <p class="project-description">${proj.desc}</p>
                            <div class="contribution-section">
                                <ul class="glowing-tasks-list">${tasksHtml}</ul>
                            </div>
                        </div>
                    </div>`;
            }).join('');
            
            timelineContainer.innerHTML += `
            <div class="company-block">
                <h2>${job.company}</h2>
                <div class="project-role-text">${job.role} | ${job.duration}</div>
                <div class="company-project-grid">
                    ${projectsHtml}
                </div>
            </div>`;
        });
        isProjectsLoaded = true;
        hideLoader();
    }).catch(err => { console.error("Error:", err); hideLoader(); });
}

function hideLoader() {
    const loader = document.getElementById('loading-overlay');
    if(loader) {
        requestAnimationFrame(() => {
            loader.style.display = 'none';
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const currentHash = window.location.hash.substring(1); 
    if (['home', 'projects', 'contact'].includes(currentHash)) showPage(currentHash);
    else showPage('home');
});

window.goToContact = function() {
    showPage('home'); 
    setTimeout(() => {
        const contactSection = document.getElementById('contact');
        if (contactSection) {
            contactSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 50);
};