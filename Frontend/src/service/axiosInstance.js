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

let isRefreshing = false;
let refreshSubscribers = [];

const onRefreshed = () => {
    refreshSubscribers.forEach((callback) => callback());
    refreshSubscribers = [];
};

const addRefreshSubscriber = (callback) => {
    refreshSubscribers.push(callback);
};

axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Only handle 401s, and don't retry more than once
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            // If a refresh is already in progress, wait for it instead of firing another
            if (isRefreshing) {
                return new Promise((resolve) => {
                    addRefreshSubscriber(() => {
                        resolve(axiosInstance(originalRequest));
                    });
                });
            }

            isRefreshing = true;

            try {
                await axiosInstance.post('/api/v1/accounts/auth/token/refresh/');
                isRefreshing = false;
                onRefreshed();
                return axiosInstance(originalRequest);
            } catch (refreshError) {
                isRefreshing = false;
                refreshSubscribers = [];

                // Refresh failed — refresh token itself expired, force logout
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