
const API_BASE = import.meta.env.VITE_BASE_URL || 'http://localhost:8000';

export const buildSocketUrl = (path) => {
    const url = new URL(API_BASE);
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    url.pathname = path;
    url.search = '';
    url.hash = '';
    return url.toString();
};
