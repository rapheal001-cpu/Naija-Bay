// WebSocket URLs come from the configured API base only — never from
// window.location (a Render static site's host is not the ASGI host).
// Mirrors SkillStream: derive the ws/wss URL from the API origin, then set
// the Channels route path.

const API_BASE = import.meta.env.VITE_BASE_URL || 'http://localhost:8000';

export const buildSocketUrl = (path) => {
    const url = new URL(API_BASE);
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    url.pathname = path;
    url.search = '';
    url.hash = '';
    return url.toString();
};
