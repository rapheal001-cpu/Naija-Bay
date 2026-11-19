import axios from 'axios';
import { store } from '../store.js';
import { removeIsAuthenticated } from '../slice/AuthSlice';
import { removeUserData } from '../slice/UserSlice';


export const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_BASE_URL,
    withCredentials: true,
});

const UNSAFE_METHODS = new Set(['post', 'put', 'patch', 'delete']);

const readCsrfCookie = () => {
    const match = document.cookie
        .split(';')
        .map((part) => part.trim())
        .find((part) => part.startsWith('csrftoken='));
    return match ? decodeURIComponent(match.slice('csrftoken='.length)) : null;
};

axiosInstance.interceptors.request.use((config) => {
    if (UNSAFE_METHODS.has((config.method || 'get').toLowerCase())) {
        const token = readCsrfCookie();
        if (token) {
            config.headers['X-CSRFToken'] = token;
        }
    }
    return config;
});

const AUTH_REFRESH_URL = '/api/v1/accounts/auth/token/refresh/';

let isRefreshing = false;
let refreshSubscribers = [];

const onRefreshed = () => {
    refreshSubscribers.forEach((callback) => callback());
    refreshSubscribers = [];
};

const onRefreshFailed = (error) => {
    refreshSubscribers.forEach((callback) => callback(error));
    refreshSubscribers = [];
};

const addRefreshSubscriber = (callback) => {
    refreshSubscribers.push(callback);
};

axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (!originalRequest) {
            return Promise.reject(error);
        }

        const isRefreshCall = originalRequest.url?.includes(AUTH_REFRESH_URL);

        if (error.response?.status === 401 && !originalRequest._retry) {

            if (isRefreshCall) {
                isRefreshing = false;
                onRefreshFailed(error);

                store.dispatch(removeIsAuthenticated());
                store.dispatch(removeUserData());

                return Promise.reject(error);
            }

            originalRequest._retry = true;

            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    addRefreshSubscriber((refreshError) => {
                        if (refreshError) {
                            reject(refreshError);
                        } else {
                            resolve(axiosInstance(originalRequest));
                        }
                    });
                });
            }

            isRefreshing = true;

            try {
                await axiosInstance.post(AUTH_REFRESH_URL);
                isRefreshing = false;
                onRefreshed();
                return axiosInstance(originalRequest);
            } catch (refreshError) {
                isRefreshing = false;
                onRefreshFailed(refreshError);

                store.dispatch(removeIsAuthenticated());
                store.dispatch(removeUserData());

                return Promise.reject(refreshError);
            }
        }

        if (error.response?.status === 502 && !originalRequest._retry) {
            originalRequest._retry = true;
            window.location.href = '/network-error';
            return Promise.reject(error);
        }

        return Promise.reject(error);
    }
);