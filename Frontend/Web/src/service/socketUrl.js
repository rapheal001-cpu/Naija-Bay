// WebSocket URLs must point at the API/ASGI host, not the static frontend
// host. Derive them from VITE_BASE_URL (the same origin Axios uses).

export const buildSocketUrl = (path) => {
    const configured = import.meta.env.VITE_BASE_URL || '/api/v1';
    const base = new URL(configured, window.location.origin);
    base.protocol = base.protocol === 'https:' ? 'wss:' : 'ws:';
    base.pathname = path;
    base.search = '';
    base.hash = '';
    return base.toString();
};
