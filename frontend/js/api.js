/* ═══════════════════════════════════════════════════════════════════════════════
   API Helper — All fetch calls to FastAPI backend
   ═══════════════════════════════════════════════════════════════════════════════ */

// When running on Vercel (production), call the Render backend directly.
// When running locally (localhost), call the same origin (FastAPI serves frontend).
const IS_LOCAL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const BACKEND_URL = "https://parth-edits-api.onrender.com";
const BASE_URL = IS_LOCAL ? window.location.origin : BACKEND_URL;

/**
 * Resolve relative /uploads/ paths to the Render backend URL.
 * Fixes thumbnails and videos not loading on Vercel deployment.
 */
function resolveUploadUrl(url) {
    if (!url) return url;
    if (url.startsWith("/uploads/") && !IS_LOCAL) {
        return BACKEND_URL + url;
    }
    return url;
}

/**
 * Extract YouTube video ID from any common URL format.
 * Supports: youtube.com/watch?v=, youtu.be/, youtube.com/embed/, youtube.com/shorts/
 */
function extractYouTubeId(url) {
    if (!url) return "";
    const patterns = [
        /(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/,
        /(?:youtu\.be\/)([a-zA-Z0-9_-]{11})/,
        /(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
        /(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})/,
    ];
    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) return match[1];
    }
    return "";
}

/**
 * Generate YouTube thumbnail URL from a YouTube video URL.
 */
function getYouTubeThumbnail(url) {
    const id = extractYouTubeId(url);
    return id ? `https://img.youtube.com/vi/${id}/maxresdefault.jpg` : "";
}

/* ── In-memory + sessionStorage token store (persists across reloads) ────────── */
let _authToken = null;

function setAuthToken(token) {
    _authToken = token;
    if (token) {
        sessionStorage.setItem("authToken", token);
    } else {
        sessionStorage.removeItem("authToken");
    }
}

function getAuthToken() {
    if (!_authToken) {
        _authToken = sessionStorage.getItem("authToken");
    }
    return _authToken;
}

function clearAuthToken() {
    _authToken = null;
    sessionStorage.removeItem("authToken");
}

/**
 * Build headers for authenticated requests.
 */
function authHeaders() {
    const headers = { "Content-Type": "application/json" };
    if (_authToken) {
        headers["Authorization"] = `Bearer ${_authToken}`;
    }
    return headers;
}

/* ── Videos ─────────────────────────────────────────────────────────────────── */

async function fetchVideos(category = null) {
    let url = `${BASE_URL}/api/videos/`;
    if (category) url += `?category=${encodeURIComponent(category)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch videos");
    return res.json();
}

async function fetchFeaturedVideos() {
    const res = await fetch(`${BASE_URL}/api/videos/featured`);
    if (!res.ok) throw new Error("Failed to fetch featured videos");
    return res.json();
}

async function createVideo(data) {
    const res = await fetch(`${BASE_URL}/api/videos/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to create video");
    }
    return res.json();
}

async function updateVideo(id, data) {
    const res = await fetch(`${BASE_URL}/api/videos/${id}`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to update video");
    }
    return res.json();
}

async function deleteVideo(id) {
    const res = await fetch(`${BASE_URL}/api/videos/${id}`, {
        method: "DELETE",
        headers: authHeaders(),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to delete video");
    }
    return res.json();
}

/* ── Contact / Enquiries ───────────────────────────────────────────────────── */

async function submitEnquiry(data) {
    const res = await fetch(`${BASE_URL}/api/contact/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to submit enquiry");
    }
    return res.json();
}

async function adminLogin(username, password) {
    const res = await fetch(`${BASE_URL}/api/contact/admin/token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Login failed");
    }
    const data = await res.json();
    setAuthToken(data.access_token);
    return data;
}

async function fetchEnquiries() {
    const res = await fetch(`${BASE_URL}/api/contact/admin/enquiries`, {
        headers: authHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch enquiries");
    return res.json();
}

async function markEnquiryRead(id) {
    const res = await fetch(`${BASE_URL}/api/contact/admin/enquiries/${id}/read`, {
        method: "PATCH",
        headers: authHeaders(),
    });
    if (!res.ok) throw new Error("Failed to toggle read status");
    return res.json();
}

/* ── Blog ──────────────────────────────────────────────────────────────────── */

async function fetchBlogPosts() {
    const res = await fetch(`${BASE_URL}/api/blog/`);
    if (!res.ok) throw new Error("Failed to fetch blog posts");
    return res.json();
}

async function fetchBlogPost(slug) {
    const res = await fetch(`${BASE_URL}/api/blog/${slug}`);
    if (!res.ok) throw new Error("Post not found");
    return res.json();
}

async function createBlogPost(data) {
    const res = await fetch(`${BASE_URL}/api/blog/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to create post");
    }
    return res.json();
}

async function updateBlogPost(id, data) {
    const res = await fetch(`${BASE_URL}/api/blog/${id}`, {
        method: "PATCH",
        headers: authHeaders(),
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to update post");
    }
    return res.json();
}

async function deleteBlogPost(id) {
    const res = await fetch(`${BASE_URL}/api/blog/${id}`, {
        method: "DELETE",
        headers: authHeaders(),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to delete post");
    }
    return res.json();
}

/* ── Pricing ───────────────────────────────────────────────────────────────── */

async function fetchPricingPlans() {
    const res = await fetch(`${BASE_URL}/api/pricing/`);
    if (!res.ok) throw new Error("Failed to fetch pricing plans");
    return res.json();
}

async function createPricingPlan(data) {
    const res = await fetch(`${BASE_URL}/api/pricing/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to create plan");
    }
    return res.json();
}

async function updatePricingPlan(id, data) {
    const res = await fetch(`${BASE_URL}/api/pricing/${id}`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to update plan");
    }
    return res.json();
}

async function deletePricingPlan(id) {
    const res = await fetch(`${BASE_URL}/api/pricing/${id}`, {
        method: "DELETE",
        headers: authHeaders(),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to delete plan");
    }
    return res.json();
}

async function fetchSiteSettings() {
    const res = await fetch(`${BASE_URL}/api/settings/`);
    if (!res.ok) throw new Error("Failed to fetch site settings");
    return res.json();
}

async function updateSiteSettings(data) {
    const res = await fetch(`${BASE_URL}/api/settings/`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to update settings");
    }
    return res.json();
}

async function fetchAllBlogPosts() {
    const res = await fetch(`${BASE_URL}/api/blog/admin/all`, {
        headers: authHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch all blog posts");
    return res.json();
}

async function applySiteSettings() {
    try {
        const res = await fetchSiteSettings();
        const settings = res.settings;

        if (settings.site_name) {
            document.querySelectorAll(".setting-site_name").forEach(el => {
                // Skip logo elements that use the image logo
                if (el.tagName === "SPAN" && el.classList.contains("logo-accent")) {
                    return; // Logo is now image-based, skip text replacement
                }
                el.textContent = settings.site_name;
            });
        }
        if (settings.tagline) {
            document.querySelectorAll(".setting-tagline").forEach(el => {
                el.textContent = settings.tagline;
            });
        }
        if (settings.email) {
            document.querySelectorAll(".setting-email").forEach(el => {
                if (el.tagName === "A") {
                    el.href = `mailto:${settings.email}`;
                }
                el.textContent = settings.email;
            });
        }
        if (settings.phone) {
            document.querySelectorAll(".setting-phone").forEach(el => {
                if (el.tagName === "A") {
                    el.href = `tel:${settings.phone.replace(/\s+/g, "")}`;
                }
                el.textContent = settings.phone;
            });
        }
        if (settings.location) {
            document.querySelectorAll(".setting-location").forEach(el => {
                el.textContent = settings.location;
            });
        }
        if (settings.about_text) {
            document.querySelectorAll(".setting-about_text").forEach(el => {
                el.textContent = settings.about_text;
            });
        }
        if (settings.about_bio) {
            document.querySelectorAll(".setting-about_bio").forEach(el => {
                el.innerHTML = settings.about_bio.replace(/\n/g, "<br>");
            });
        }

        // Social Links
        if (settings.youtube) {
            document.querySelectorAll(".setting-youtube").forEach(el => {
                el.href = settings.youtube;
                if (settings.youtube === "#" || settings.youtube === "") {
                    el.style.display = "none";
                } else {
                    el.style.display = "";
                }
            });
        }
        if (settings.instagram) {
            document.querySelectorAll(".setting-instagram").forEach(el => {
                el.href = settings.instagram;
                if (settings.instagram === "#" || settings.instagram === "") {
                    el.style.display = "none";
                } else {
                    el.style.display = "";
                }
            });
        }
        if (settings.twitter) {
            document.querySelectorAll(".setting-twitter").forEach(el => {
                el.href = settings.twitter;
                if (settings.twitter === "#" || settings.twitter === "") {
                    el.style.display = "none";
                } else {
                    el.style.display = "";
                }
            });
        }
    } catch (err) {
        console.error("Error applying site settings:", err);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    if (!window.location.pathname.includes("admin.html")) {
        applySiteSettings();
    }
});

async function uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    // Upload directly to Render backend (bypasses Vercel's 4.5MB body limit)
    const res = await fetch(`${BACKEND_URL}/api/videos/upload`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${getAuthToken()}`
        },
        body: formData
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to upload file");
    }
    return res.json();
}

/* ── F12 / Right-Click Inspect Blocker ─────────────────────────────────── */
document.addEventListener("contextmenu", (e) => e.preventDefault());

document.addEventListener("keydown", (e) => {
    // Disable F12
    if (e.key === "F12") {
        e.preventDefault();
    }
    // Disable Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C
    if (e.ctrlKey && e.shiftKey && (e.key === "I" || e.key === "J" || e.key === "C" || e.key === "i" || e.key === "j" || e.key === "c")) {
        e.preventDefault();
    }
    // Disable Ctrl+U (View Source)
    if (e.ctrlKey && (e.key === "U" || e.key === "u")) {
        e.preventDefault();
    }
});

// Periodically run debugger statement to halt execution if devtools is open
setInterval(() => {
    (function() {
        try {
            (function() {}).constructor("debugger")();
        } catch (e) {}
    })();
}, 1000);

/* ── Global Fetch Interceptor to catch 401 Unauthorized errors ─────────────── */
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const res = await originalFetch(...args);
    if (res.status === 401) {
        clearAuthToken();
        if (typeof handleLogout === "function") {
            handleLogout();
        }
    }
    return res;
};


