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

/**
 * @param {string|number} userId
 * @param {{ page?: number }} [params]
 */
export const fetchFollowersFn = async (userId, params = {}) => {
    const { data } = await axiosInstance.get(`/api/v1/accounts/auth/followers/${userId}/`, { params });
    return data;
};

/**
 * @param {string|number} userId
 * @param {{ page?: number }} [params]
 */
export const fetchFollowingFn = async (userId, params = {}) => {
    const { data } = await axiosInstance.get(`/api/v1/accounts/auth/following/${userId}/`, { params });
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
    const { data } = await axiosInstance.get(`/api/v1/accounts/auth/store-detail/${storeSlug}/`);
    return data;
};

/**
 * @param {{ storeSlug: string, payload: Object|FormData }} params
 */
export const updateStoreFn = async ({ storeSlug, payload }) => {
    const { data } = await axiosInstance.patch(`/api/v1/accounts/auth/store-detail/${storeSlug}/`, payload);
    return data;
};

/**
 * @param {string} storeSlug
 */
export const deleteStoreFn = async (storeSlug) => {
    const { data } = await axiosInstance.delete(`/api/v1/accounts/auth/store-detail/${storeSlug}/`);
    return data;
};

export const fetchMyStoreFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/accounts/auth/my-store/');
    return data;
};


// =============================================================================
// PRODUCTS LIST / SEARCH / FILTER / PAGINATION
// =============================================================================

/**
 * @param {{
 *   search?: string,
 *   category?: string,
 *   sub_category?: string,
 *   condition?: string,
 *   state?: string,
 *   city?: string,
 *   min_price?: number|string,
 *   max_price?: number|string,
 *   delivery_available?: boolean,
 *   verified_seller?: boolean,
 *   negotiable?: boolean,
 *   sort?: string,
 *   page?: number,
 *   page_size?: number,
 * }} [params]
 */
export const fetchProductsFn = async (params = {}) => {
    const query = {};

    Object.entries(params).forEach(([key, value]) => {
        if (value === undefined || value === null || value === '') return;
        if (value === false) return; // booleans are opt-in filters
        query[key] = value === true ? 'true' : value;
    });

    const { data } = await axiosInstance.get('/api/v1/products/', { params: query });
    return data;
};

/**
 * @param {{ status?: string, page?: number }} [params]
 */
export const fetchMyListingsFn = async (params = {}) => {
    const query = {};
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '' && value !== false) {
            query[key] = value;
        }
    });
    const { data } = await axiosInstance.get('/api/v1/products/my-listings/', { params: query });
    return data;
};

/**
 * @param {{ page?: number }} [params]
 */
export const fetchFavoriteProductsFn = async (params = {}) => {
    const { data } = await axiosInstance.get('/api/v1/products/favorites/', { params });
    return data;
};

/**
 * @param {{ page?: number }} [params]
 */
export const fetchRecentlyViewedFn = async (params = {}) => {
    const { data } = await axiosInstance.get('/api/v1/products/recently-viewed/', { params });
    return data;
};

/**
 * @param {{ productSlug: string, reason: string, details?: string }} payload
 */
export const reportProductFn = async ({ productSlug, reason, details }) => {
    const { data } = await axiosInstance.post(`/api/v1/products/report/${productSlug}/`, {
        reason,
        details: details || '',
    });
    return data;
};


// =============================================================================
// MESSAGING
// =============================================================================

/**
 * @param {{ page?: number }} [params]
 */
export const fetchConversationsFn = async (params = {}) => {
    const { data } = await axiosInstance.get('/api/v1/messaging/', { params });
    return data;
};

/**
 * @param {string|number} conversationId
 */
export const fetchConversationFn = async (conversationId) => {
    const { data } = await axiosInstance.get(`/api/v1/messaging/${conversationId}/`);
    return data;
};

/**
 * @param {{ conversationId: string|number, page?: number }} params
 */
export const fetchMessagesFn = async ({ conversationId, page }) => {
    const params = page ? { page } : {};
    const { data } = await axiosInstance.get(`/api/v1/messaging/${conversationId}/messages/`, { params });
    return data;
};

/**
 * Start (or reuse) a conversation about a product and post the first message.
 * @param {{ productId: string|number, message: string }} payload
 */
export const startConversationFn = async ({ productId, message }) => {
    const { data } = await axiosInstance.post('/api/v1/messaging/', {
        product: productId,
        message,
    });
    return data;
};

/**
 * @param {{ conversationId: string|number, body: string }} payload
 */
export const sendMessageFn = async ({ conversationId, body }) => {
    const { data } = await axiosInstance.post(`/api/v1/messaging/${conversationId}/messages/`, { body });
    return data;
};

/**
 * @param {string|number} conversationId
 */
export const markConversationReadFn = async (conversationId) => {
    const { data } = await axiosInstance.post(`/api/v1/messaging/${conversationId}/read/`);
    return data;
};

export const fetchUnreadCountsFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/messaging/unread-count/');
    return data;
};
