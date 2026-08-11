import { axiosInstance } from './axiosInstance.js';


// =============================================================================
// AUTHENTICATION
// =============================================================================

/**
 * @param {{ email: string, password: string }} payload
 */
export const signInUserFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/login/', payload);
    return data;
};

/**
 * @param {{ email: string, username: string, password1: string, password2: string }} payload
 */
export const registerUserFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/registration/', payload);
    return data;
};

/**
 * @param {{ email?: string }} payload
 */
export const resendVerificationEmailFn = async (payload = {}) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/registration/resend-email/', payload);
    return data;
};

/**
 * @param {{ access?: string }}
 */
export const logoutUserFn = async () => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/logout/');
    return data;
};

/**
 * @param {{ email: string }} payload
 */
export const requestPasswordResetFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/password/reset/', payload);
    return data;
};

/**
 * @param {{ old_password: string, new_password1: string, new_password2: string }} payload
 */
export const changePasswordFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/password/change/', payload);
    return data;
};


// =============================================================================
// USER
// =============================================================================

export const fetchUserFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/accounts/auth/user/');
    return data;
};

/**
 * @param {string|number} userId
 */
export const fetchOtherUserFn = async (userId) => {
    const { data } = await axiosInstance.get(`/api/v1/accounts/auth/user/${userId}/`);
    return data;
};

/**
 * @param {Object|FormData} payload
 */
export const updateUserProfileFn = async (payload) => {
    const { data } = await axiosInstance.patch('/api/v1/accounts/auth/user/', payload);
    return data;
};


// =============================================================================
// NOTIFICATIONS
// =============================================================================

export const fetchUserNotificationsFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/accounts/auth/notifications/');
    return data;
};

/**
 * @param {string|number} notificationId
 */
export const markNotificationAsReadFn = async (notificationId) => {
    const { data } = await axiosInstance.post(`/api/v1/core/mark-notification-as-read/${notificationId}/`);
    return data;
};

export const deleteAllNotificationsFn = async () => {
    const { data } = await axiosInstance.delete('/api/v1/core/delete-all-notifications/');
    return data;
};

/**
 * @param {string|number} notificationId
 */
export const deleteNotificationFn = async (notificationId) => {
    const { data } = await axiosInstance.delete(`/api/v1/core/delete-notification/${notificationId}/`);
    return data;
};

export const markAllNotificationsAsReadFn = async () => {
    const { data } = await axiosInstance.post('/api/v1/core/mark-all-notifications-as-read/');
    return data;
};


// =============================================================================
// PRODUCTS
// =============================================================================

export const fetchFeaturedProductDataFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/products/featured/');
    return data;
};

export const fetchCategoriesFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/products/categories/');
    return data;
};

/**
 * @param {string} productSlug
 */
export const productDetailFn = async (productSlug) => {
    const { data } = await axiosInstance.get(`/api/v1/products/detail/${productSlug}/`);
    return data;
};

/**
 * @param {string} productSlug
 */
export const deleteProductFn = async (productSlug) => {
    const { data } = await axiosInstance.delete(`/api/v1/products/detail/${productSlug}/`);
    return data;
};

/**
 * @param {Object} payload
 */
export const createProductFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/products/create/', payload);
    return data;
};

/**
 * Update a single product by slug.
 * @param {{ product_slug: string, payload: Object }} params
 */
export const updateProductFn = async ({ productSlug, payload }) => {
    const { data } = await axiosInstance.patch(`/api/v1/products/detail/${productSlug}/`, payload);
    return data;
};

/**
 * @param {{ product: { id: string|number }, images: File }} payload
 */
export const createProductImagesFn = async ({ product, images }) => {
    const formData = new FormData();

    formData.append('product', product.id);

    images.forEach((image) => {
        formData.append('images', image);
    });

    const { data } = await axiosInstance.post('/api/v1/products/create/images/', formData);
    return data;
};

/**
 * @param {{ product: { id: string|number }, images: File }} payload
 */
export const updateProductImagesFn = async ({ product, images }) => {
    const formData = new FormData();

    formData.append('product', product.id);

    images.forEach((image) => {
        formData.append('images', image);
    });

    const { data } = await axiosInstance.post(`/api/v1/products/update/images/${product.id}/`, formData);
    return data;
};

/**
 * @param {string|number} imageId
 */
export const deleteProductImageFn = async (imageId) => {
    const { data } = await axiosInstance.post(`/api/v1/products/image/delete/${imageId}/`);
    return data;
}

/**
 * @param {string} productSlug
 */
export const toggleProductFavoriteFn = async (productSlug) => {
    const { data } = await axiosInstance.post(`/api/v1/core/toggle-favorite-product/${productSlug}/`);
    return data;
};

/**
 * @param {string|number} userId
 */
export const toggleFollowUserFn = async (userId) => {
    const { data } = await axiosInstance.post(`/api/v1/core/toggle-follow-user/${userId}/`);
    return data;
};


// =============================================================================
// STORE
// =============================================================================

export const createStoreFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/create-store/', payload);
    return data;
};

/**
 * @param {string} storeSlug
 */
export const fetchStoreDetailFn = async (storeSlug) => {
    const { data } = await axiosInstance.get(`/api/v1/accounts/auth/store-detail/${storeSlug}`);
    return data;
};

/**
 * @param {string} storeSlug
 */
export const updateStoreFn = async (storeSlug) => {
    const { data } = await axiosInstance.put(`/api/v1/accounts/auth/store-detail/${storeSlug}`);
    return data;
};

/**
 * @param {string} storeSlug
 */
export const deleteStoreFn = async (storeSlug) => {
    const { data } = await axiosInstance.delete(`/api/v1/accounts/auth/store-detail/${storeSlug}`);
    return data;
};


// =============================================================================
// PRODUCTS LIST / SEARCH / FILTER
// =============================================================================

/**
 * @param {string} [searchQuery]
 * @param {string} [activeCategory]
 * @param {string} [activeSubCategory]
 */
export const fetchProductsFn = async (searchQuery, activeCategory, activeSubCategory) => {
    const params = {};

    if (searchQuery) params.search = searchQuery;
    if (activeCategory && typeof activeCategory === 'string') {
        params.category = activeCategory.replace(/_/g, '-');
    }
    if (activeSubCategory && typeof activeSubCategory === 'string') {
        params.sub_category = activeSubCategory.replace(/_/g, '-');
    }

    const { data } = await axiosInstance.get('/api/v1/products/', { params });
    return data;
};