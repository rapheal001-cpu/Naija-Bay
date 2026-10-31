import axios from 'axios';
import { store } from '../store.js';
import { removeIsAuthenticated } from '../slice/AuthSlice';
import { removeUserData } from '../slice/UserSlice';


export const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_BASE_URL,
    withCredentials: true,
    // timeout: 10000,
});


axiosInstance.interceptors.request.use((config) => {
    return config;
});

// Endpoint(s) that should never trigger the refresh flow themselves
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

        // No config (e.g. request was cancelled) — nothing we can do
        if (!originalRequest) {
            return Promise.reject(error);
        }

        const isRefreshCall = originalRequest.url?.includes(AUTH_REFRESH_URL);

        // --- 401 handling ---
        if (error.response?.status === 401 && !originalRequest._retry) {

            // The refresh request itself failed with 401 → refresh token is
            // invalid/expired. Do NOT try to refresh again, just log out.
            if (isRefreshCall) {
                isRefreshing = false;
                onRefreshFailed(error);

                store.dispatch(removeIsAuthenticated());
                store.dispatch(removeUserData());

                return Promise.reject(error);
            }

            originalRequest._retry = true;

            // If a refresh is already in progress, wait for it instead of firing another
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

                // Refresh failed — refresh token itself expired, force logout
                store.dispatch(removeIsAuthenticated());
                store.dispatch(removeUserData());

                return Promise.reject(refreshError);
            }
        }

        // --- 502 handling ---
        if (error.response?.status === 502 && !originalRequest._retry) {
            originalRequest._retry = true;
            window.location.href = '/network-error';
            return Promise.reject(error);
        }

        return Promise.reject(error);
    }
);