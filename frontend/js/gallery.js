/* ═══════════════════════════════════════════════════════════════════════════════
   Gallery — Filter buttons + Lightbox logic for portfolio.html
   ═══════════════════════════════════════════════════════════════════════════════ */

let allVideos = [];
let currentCategory = "all";

/**
 * Initialize the portfolio gallery page.
 */
async function initGallery() {
    const grid = document.getElementById("video-grid");
    const filterBar = document.getElementById("filter-bar");

    if (!grid) return;

    // Show loading
    grid.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

    try {
        allVideos = await fetchVideos();
        renderVideoGrid(allVideos);
    } catch (err) {
        grid.innerHTML = `<div class="empty-state"><div class="icon">⚠️</div><p>Could not load videos. Is the backend running?</p></div>`;
        console.error(err);
    }

    // Bind filter buttons
    if (filterBar) {
        filterBar.addEventListener("click", (e) => {
            const btn = e.target.closest(".filter-btn");
            if (!btn) return;

            const category = btn.dataset.category;
            currentCategory = category;

            // Update active state
            filterBar.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");

            // Filter & render
            if (category === "all") {
                renderVideoGrid(allVideos);
            } else {
                renderVideoGrid(allVideos.filter((v) => v.category === category));
            }
        });
    }
}

/**
 * Render video cards into the grid.
 */
function renderVideoGrid(videos) {
    const grid = document.getElementById("video-grid");
    if (!grid) return;

    if (videos.length === 0) {
        grid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1"><div class="icon">🎬</div><p>No videos found in this category.</p></div>`;
        return;
    }

    grid.innerHTML = videos
        .map((v) => {
            const thumbnail = v.thumbnail_url || (v.youtube_url ? getYouTubeThumbnail(v.youtube_url) : "") || "https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=800";
            return `
            <div class="video-card glass-card fade-in" onclick="openLightbox('${v.youtube_url || ''}', '${v.video_file_url || ''}')">
                <div class="video-card-thumb">
                    <img src="${thumbnail}" alt="${v.title}" loading="lazy">
                    <div class="video-card-play"></div>
                </div>
                <div class="video-card-body">
                    <span class="category-badge">${v.category}</span>
                    <h3>${v.title}</h3>
                </div>
            </div>`;
        })
        .join("");

    // Trigger fade-in animations
    requestAnimationFrame(() => {
        grid.querySelectorAll(".fade-in").forEach((el, i) => {
            setTimeout(() => el.classList.add("visible"), i * 80);
        });
    });
}

/* ── Lightbox ──────────────────────────────────────────────────────────────── */

function openLightbox(youtubeUrl, videoFileUrl) {
    const lightbox = document.getElementById("lightbox");
    const iframe = document.getElementById("lightbox-iframe");
    if (!lightbox) return;

    let videoEl = document.getElementById("lightbox-video");
    if (videoEl) videoEl.remove();

    if (videoFileUrl || (youtubeUrl && (youtubeUrl.startsWith("/uploads/") || youtubeUrl.endsWith(".mp4") || youtubeUrl.endsWith(".mov")))) {
        const url = videoFileUrl || youtubeUrl;
        if (iframe) iframe.style.display = "none";

        videoEl = document.createElement("video");
        videoEl.id = "lightbox-video";
        videoEl.src = url;
        videoEl.controls = true;
        videoEl.autoplay = true;
        videoEl.setAttribute("controlsList", "nodownload");
        videoEl.setAttribute("disablePictureInPicture", "true");
        videoEl.oncontextmenu = (e) => e.preventDefault();
        videoEl.style.width = "100%";
        videoEl.style.height = "100%";
        videoEl.style.borderRadius = "var(--radius-lg)";
        videoEl.style.outline = "none";

        const contentWrap = lightbox.querySelector(".lightbox-content");
        if (contentWrap) contentWrap.appendChild(videoEl);
    } else {
        const videoId = extractYouTubeId(youtubeUrl);
        if (!videoId) return;
        if (iframe) {
            iframe.style.display = "block";
            iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
        }
    }

    lightbox.classList.add("active");
    document.body.style.overflow = "hidden";
}

function closeLightbox() {
    const lightbox = document.getElementById("lightbox");
    const iframe = document.getElementById("lightbox-iframe");
    if (!lightbox) return;

    if (iframe) iframe.src = "";

    const videoEl = document.getElementById("lightbox-video");
    if (videoEl) {
        videoEl.pause();
        videoEl.remove();
    }

    lightbox.classList.remove("active");
    document.body.style.overflow = "";
}

// Close on backdrop click
document.addEventListener("click", (e) => {
    const lightbox = document.getElementById("lightbox");
    if (lightbox && e.target === lightbox) {
        closeLightbox();
    }
});

// Close on Escape key
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeLightbox();
});
