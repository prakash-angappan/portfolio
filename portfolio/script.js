(() => {
  "use strict";

  let isHomeLoaded = false;
  let isProjectsLoaded = false;
  let projectScrollTimer = null;

  const VALID_PAGES = new Set(["home", "projects", "contact"]);

  /* -------------------------------------------------------------------------
     Helpers
     ------------------------------------------------------------------------- */

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/`/g, "&#96;");
  }

  async function fetchJson(url) {
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) {
      throw new Error(`Failed to load ${url} (${res.status})`);
    }
    return res.json();
  }

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? "";
  }

  function showLoadError(message) {
    const main = document.getElementById("main-content");
    if (!main) return;
    let banner = document.getElementById("load-error");
    if (!banner) {
      banner = document.createElement("div");
      banner.id = "load-error";
      banner.className = "load-error";
      banner.setAttribute("role", "alert");
      main.prepend(banner);
    }
    banner.textContent = message;
  }

  function hideLoader() {
    const loader = document.getElementById("loading-overlay");
    if (!loader) return;
    loader.classList.add("is-hidden");
    window.setTimeout(() => {
      loader.style.display = "none";
    }, 350);
  }

  function youtubeEmbedUrl(url) {
    return String(url || "").replace("www.youtube.com", "www.youtube-nocookie.com");
  }

  function projectSlug(title) {
    return String(title || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "");
  }

  /* -------------------------------------------------------------------------
     Navigation
     ------------------------------------------------------------------------- */

  function showPage(pageId) {
    const targetId = pageId === "contact" ? "home" : pageId;

    document.querySelectorAll(".page-section").forEach((section) => {
      section.classList.add("is-hidden");
      section.style.display = "none";
    });

    document.querySelectorAll(".nav-btn").forEach((btn) => {
      btn.classList.remove("active");
      btn.removeAttribute("aria-current");
    });

    const page = document.getElementById(targetId);
    if (!page) return;

    page.classList.remove("is-hidden");
    page.style.display = "block";

    const btn = document.getElementById(`btn-${pageId === "contact" ? "contact" : targetId}`);
    if (btn) {
      btn.classList.add("active");
      btn.setAttribute("aria-current", "page");
    }

    if (pageId !== "contact") {
      window.scrollTo({ top: 0, behavior: "instant" });
    }
    window.history.pushState(null, "", `#${pageId}`);

    if (targetId === "home" && !isHomeLoaded) loadHomeData();
    if (targetId === "projects" && !isProjectsLoaded) loadProjectsData();
  }

  function goToContact() {
    showPage("contact");
    window.setTimeout(() => {
      const contactSection = document.getElementById("contact");
      if (contactSection) {
        contactSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }, 50);
  }

  function navigateToProject(projectTitle) {
    showPage("projects");

    if (projectScrollTimer) {
      clearInterval(projectScrollTimer);
      projectScrollTimer = null;
    }

    const slug = projectSlug(projectTitle);
    let attempts = 0;

    projectScrollTimer = setInterval(() => {
      attempts += 1;
      const target =
        document.getElementById(`project-${slug}`) ||
        Array.from(document.querySelectorAll(".project-card h3")).find(
          (el) => el.textContent === projectTitle
        );

      if (target) {
        clearInterval(projectScrollTimer);
        projectScrollTimer = null;
        target.scrollIntoView({ behavior: "smooth", block: "center" });
        const card = target.closest(".project-card");
        if (card) {
          card.classList.add("is-highlighted");
          window.setTimeout(() => card.classList.remove("is-highlighted"), 2000);
        }
      } else if (attempts > 50) {
        clearInterval(projectScrollTimer);
        projectScrollTimer = null;
      }
    }, 100);
  }

  /* -------------------------------------------------------------------------
     Home
     ------------------------------------------------------------------------- */

  function renderStats(stats) {
    return (stats || [])
      .map(
        (stat) => `
      <div class="glass-card stat">
        <div class="stat-number">${escapeHtml(stat.value)}</div>
        <div class="stat-label">${escapeHtml(stat.label)}</div>
      </div>`
      )
      .join("");
  }

  function renderActions(actions) {
    if (!actions || !actions.length) return "";

    const downloadAction = actions.find((a) => a.type === "download");
    const otherActions = actions.filter((a) => a.type !== "download");
    const parts = [];

    if (downloadAction) {
      parts.push(`
        <a href="${escapeAttr(downloadAction.link)}" class="btn-action" download>
          <img src="${escapeAttr(downloadAction.icon)}" class="action-icon" alt="" loading="lazy" decoding="async" width="18" height="18">
          ${escapeHtml(downloadAction.label)}
        </a>`);
    }

    otherActions.forEach((action) => {
      const external = action.link.startsWith("http");
      const rel = external ? ' target="_blank" rel="noopener noreferrer"' : "";
      parts.push(`
        <a href="${escapeAttr(action.link)}" class="btn-action"${rel}>
          <img src="${escapeAttr(action.icon)}" class="action-icon" alt="" loading="lazy" decoding="async" width="18" height="18">
          ${escapeHtml(action.label)}
        </a>`);
    });

    return parts.join("");
  }

  function renderSkillIcon(item) {
    if (item.icon) {
      return `<img src="${escapeAttr(item.icon)}" alt="${escapeAttr(item.name)}" loading="lazy" decoding="async" width="48" height="48">`;
    }
    const abbr = escapeHtml(item.abbr || item.name.slice(0, 3));
    return `<span class="skill-icon-fallback" aria-hidden="true">${abbr}</span>`;
  }

  function renderTechGrid(techStack) {
    const categoryOrder = ["programming_engines", "ai_workflows", "platforms", "tools"];
    return categoryOrder
      .map((key) => {
        const category = techStack[key];
        if (!category) return "";
        const itemsHtml = (category.items || [])
          .map(
            (item) => `
          <div class="skill-item">
            ${renderSkillIcon(item)}
            <span>${escapeHtml(item.name)}</span>
          </div>`
          )
          .join("");

        return `
          <div class="glass-card tech-card">
            <div class="dialog-title-box">${escapeHtml(category.title)}</div>
            <div class="skills-container">${itemsHtml}</div>
          </div>`;
      })
      .join("");
  }

  function renderDetailCard(item) {
    const badge = item.badge
      ? `<span class="team-badge-inline">${escapeHtml(item.badge)}</span>`
      : "";

    return `
      <article class="detail-card glass-card">
        <div class="project-header-row">
          <div class="header-left-group">
            <h3>${escapeHtml(item.title)}</h3>
            ${badge}
          </div>
        </div>
        <p class="project-description">${escapeHtml(item.desc)}</p>
      </article>`;
  }

  function renderDetailCards(items) {
    return (items || []).map(renderDetailCard).join("");
  }

  function renderBadgeGrid(items) {
    return (items || [])
      .map(
        (item) => `
      <div class="glass-card mgmt-badge">
        <img src="${escapeAttr(item.icon)}" alt="" class="mgmt-badge-icon" loading="lazy" decoding="async" width="36" height="36">
        <span class="mgmt-text-label">${escapeHtml(item.name)}</span>
      </div>`
      )
      .join("");
  }

  function renderFeatured(projects) {
    return (projects || [])
      .map((proj) => {
        const title = escapeHtml(proj.title);
        const titleAttr = escapeAttr(proj.title);
        return `
        <button type="button" class="featured-project-card glass-card" data-project-title="${titleAttr}" aria-label="View ${titleAttr} details">
          <div class="featured-banner-wrapper">
            <img src="${escapeAttr(proj.image)}" alt="${titleAttr}" loading="lazy" decoding="async" width="480" height="480">
          </div>
          <div class="featured-footer">
            <span>${title}</span>
          </div>
        </button>`;
      })
      .join("");
  }

  async function loadHomeData() {
    try {
      const [homeData, contactData] = await Promise.all([
        fetchJson("home.json"),
        fetchJson("contact.json"),
      ]);

      const heroImg = document.getElementById("hero-img");
      if (heroImg && homeData.hero?.profile_img) {
        heroImg.src = homeData.hero.profile_img;
        heroImg.decoding = "async";
      }

      setText("hero-name", homeData.hero?.name);
      setText("hero-title", homeData.hero?.title);
      setText("hero-summary", homeData.hero?.summary);

      const statsContainer = document.getElementById("hero-stats");
      if (statsContainer) statsContainer.innerHTML = renderStats(homeData.hero?.stats);

      const introEl = document.getElementById("contact-intro");
      if (introEl && contactData.contact?.intro) {
        introEl.textContent = contactData.contact.intro;
      }

      const actionRow = document.getElementById("action-row");
      if (actionRow) actionRow.innerHTML = renderActions(contactData.actions);

      const techContainer = document.getElementById("tech-grid");
      if (techContainer) techContainer.innerHTML = renderTechGrid(homeData.tech_stack || {});

      const featuredContainer = document.getElementById("featured-grid");
      if (featuredContainer) {
        featuredContainer.innerHTML = renderFeatured(homeData.featured_projects);
        featuredContainer.querySelectorAll("[data-project-title]").forEach((btn) => {
          btn.addEventListener("click", () => {
            navigateToProject(btn.getAttribute("data-project-title"));
          });
        });
      }

      const competenciesGrid = document.getElementById("core-competencies-grid");
      if (competenciesGrid) {
        competenciesGrid.innerHTML = renderBadgeGrid(homeData.core_competencies);
      }

      const achievementsList = document.getElementById("key-achievements-list");
      if (achievementsList) {
        achievementsList.innerHTML = renderDetailCards(homeData.key_achievements);
      }

      isHomeLoaded = true;
    } catch (err) {
      console.error("Error loading home data:", err);
      showLoadError("Unable to load portfolio content. Please refresh the page.");
    } finally {
      hideLoader();
    }
  }

  /* -------------------------------------------------------------------------
     Projects
     ------------------------------------------------------------------------- */

  function renderProjectCard(proj) {
    const title = escapeHtml(proj.title);
    const slug = projectSlug(proj.title);
    const hasRealLink = proj.link && proj.link.url && proj.link.url !== "#";
    const overlayHtml = hasRealLink
      ? `<div class="media-overlay">
           <a href="${escapeAttr(proj.link.url)}" target="_blank" rel="noopener noreferrer" class="hover-action-btn">
             View on ${escapeHtml(proj.link.label)}
           </a>
         </div>`
      : "";

    const teamTag = proj.team_size
      ? `<span class="team-badge-inline">${escapeHtml(proj.team_size)}</span>`
      : "";

    const engineIcon = proj.icon
      ? `<div class="compact-tech-badge"><img src="${escapeAttr(proj.icon)}" title="${escapeAttr(proj.engine)}" alt="${escapeAttr(proj.engine)}" loading="lazy" decoding="async" width="36" height="36"></div>`
      : "";

    const platformIcons = (proj.platforms || [])
      .map(
        (plat) =>
          `<div class="compact-tech-badge"><img src="${escapeAttr(plat.icon)}" title="${escapeAttr(plat.name)}" alt="${escapeAttr(plat.name)}" loading="lazy" decoding="async" width="36" height="36"></div>`
      )
      .join("");

    let mediaContentHtml = "";
    if (proj.video) {
      mediaContentHtml = `
        <div class="video-media-container">
          <iframe
            src="${escapeAttr(youtubeEmbedUrl(proj.video))}"
            title="${escapeAttr(proj.title)} gameplay video"
            loading="lazy"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
          ${overlayHtml}
        </div>`;
    } else if (proj.image) {
      mediaContentHtml = `
        <div class="image-media-container">
          <img class="media-banner" src="${escapeAttr(proj.image)}" alt="${escapeAttr(proj.title)}" loading="lazy" decoding="async" width="960" height="540">
          ${overlayHtml}
        </div>`;
    }

    const tasksHtml = (proj.tasks || [])
      .map((task) => `<li>${escapeHtml(task)}</li>`)
      .join("");

    return `
      <article class="project-card" id="project-${slug}">
        <div class="project-media-wrapper">${mediaContentHtml}</div>
        <div class="project-info">
          <div class="project-header-row">
            <div class="header-left-group">
              <h3>${title}</h3>
              ${teamTag}
              <span class="header-pipe" aria-hidden="true">|</span>
              ${engineIcon}
              ${platformIcons}
            </div>
          </div>
          <p class="project-description">${escapeHtml(proj.desc)}</p>
          <div class="contribution-section">
            <ul class="glowing-tasks-list">${tasksHtml}</ul>
          </div>
        </div>
      </article>`;
  }

  async function loadProjectsData() {
    try {
      const data = await fetchJson("projects.json");
      const timelineContainer = document.getElementById("timeline-container");
      if (!timelineContainer) return;

      const html = (data.work_experience || [])
        .map((job) => {
          const projectsHtml = (job.projects || []).map(renderProjectCard).join("");
          return `
            <section class="company-block">
              <h2>${escapeHtml(job.company)}</h2>
              <div class="project-role-text">${escapeHtml(job.role)} | ${escapeHtml(job.duration)}</div>
              <div class="company-project-grid">
                ${projectsHtml}
              </div>
            </section>`;
        })
        .join("");

      timelineContainer.innerHTML = html;
      isProjectsLoaded = true;
    } catch (err) {
      console.error("Error loading projects:", err);
      showLoadError("Unable to load project history. Please refresh the page.");
    } finally {
      hideLoader();
    }
  }

  /* -------------------------------------------------------------------------
     Boot
     ------------------------------------------------------------------------- */

  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("btn-home")?.addEventListener("click", () => showPage("home"));
    document.getElementById("btn-projects")?.addEventListener("click", () => showPage("projects"));
    document.getElementById("btn-contact")?.addEventListener("click", () => goToContact());

    const hash = window.location.hash.substring(1);
    if (VALID_PAGES.has(hash)) {
      if (hash === "contact") goToContact();
      else showPage(hash);
    } else {
      showPage("home");
    }
  });

  // Expose for any remaining inline callers / debugging
  window.showPage = showPage;
  window.goToContact = goToContact;
  window.navigateToProject = navigateToProject;
})();
