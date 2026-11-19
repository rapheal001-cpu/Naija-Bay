import { axiosInstance } from './axiosInstance.js';



export const signInUserFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/login/', payload);
    return data;
};

export const registerUserFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/registration/', payload);
    return data;
};

export const resendVerificationEmailFn = async (payload = {}) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/registration/resend-email/', payload);
    return data;
};

export const logoutUserFn = async () => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/logout/');
    return data;
};

export const requestPasswordResetFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/password/reset/', payload);
    return data;
};

export const changePasswordFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/password/change/', payload);
    return data;
};



export const fetchUserFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/accounts/auth/user/');
    return data;
};

export const fetchOtherUserFn = async (userId) => {
    const { data } = await axiosInstance.get(`/api/v1/accounts/auth/user/${userId}/`);
    return data;
};

export const updateUserProfileFn = async (payload) => {
    const { data } = await axiosInstance.patch('/api/v1/accounts/auth/user/', payload);
    return data;
};



export const fetchUserNotificationsFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/accounts/auth/notifications/');
    return data;
};

export const markNotificationAsReadFn = async (notificationId) => {
    const { data } = await axiosInstance.post(`/api/v1/core/mark-notification-as-read/${notificationId}/`);
    return data;
};

export const deleteAllNotificationsFn = async () => {
    const { data } = await axiosInstance.delete('/api/v1/core/delete-all-notifications/');
    return data;
};

export const deleteNotificationFn = async (notificationId) => {
    const { data } = await axiosInstance.delete(`/api/v1/core/delete-notification/${notificationId}/`);
    return data;
};

export const markAllNotificationsAsReadFn = async () => {
    const { data } = await axiosInstance.post('/api/v1/core/mark-all-notifications-as-read/');
    return data;
};



export const fetchFeaturedProductDataFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/products/featured/');
    return data;
};

export const fetchFlashDealsFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/products/deals/flash/');
    return data;
};

export const rateProductFn = async ({ productSlug, value }) => {
    const { data } = await axiosInstance.post(`/api/v1/products/rate/${productSlug}/`, { value });
    return data;
};

export const fetchCategoriesFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/products/categories/');
    return data;
};

export const fetchAttributeDefinitionsFn = async (params = {}) => {
    const query = {};
    if (params.category) query.category = params.category;
    if (params.subCategory) query.sub_category = params.subCategory;
    const { data } = await axiosInstance.get('/api/v1/core/attributes/', { params: query });
    return data;
};

export const productDetailFn = async (productSlug) => {
    const { data } = await axiosInstance.get(`/api/v1/products/detail/${productSlug}/`);
    return data;
};

export const deleteProductFn = async (productSlug) => {
    const { data } = await axiosInstance.delete(`/api/v1/products/detail/${productSlug}/`);
    return data;
};

export const createProductFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/products/create/', payload);
    return data;
};

export const updateProductFn = async ({ productSlug, payload }) => {
    const { data } = await axiosInstance.patch(`/api/v1/products/detail/${productSlug}/`, payload);
    return data;
};

export const createProductImagesFn = async ({ product, images }) => {
    const formData = new FormData();

    formData.append('product', product.id);

    images.forEach((image) => {
        formData.append('images', image);
    });

    const { data } = await axiosInstance.post('/api/v1/products/create/images/', formData);
    return data;
};

export const createProductImagesByKeyFn = async ({ product, keys }) => {
    const formData = new FormData();
    formData.append('product', product.id);
    keys.forEach((key) => formData.append('keys', key));
    const { data } = await axiosInstance.post('/api/v1/products/create/images/', formData);
    return data;
};

export const updateProductImagesFn = async ({ product, images }) => {
    const formData = new FormData();

    formData.append('product', product.id);

    images.forEach((image) => {
        formData.append('images', image);
    });

    const { data } = await axiosInstance.post(`/api/v1/products/update/images/${product.id}/`, formData);
    return data;
};

export const deleteProductImageFn = async (imageId) => {
    const { data } = await axiosInstance.post(`/api/v1/products/image/delete/${imageId}/`);
    return data;
}

export const toggleProductFavoriteFn = async (productSlug) => {
    const { data } = await axiosInstance.post(`/api/v1/core/toggle-favorite-product/${productSlug}/`);
    return data;
};

export const toggleFollowUserFn = async (userId) => {
    const { data } = await axiosInstance.post(`/api/v1/core/toggle-follow-user/${userId}/`);
    return data;
};

export const fetchFollowersFn = async (userId, params = {}) => {
    const { data } = await axiosInstance.get(`/api/v1/accounts/auth/followers/${userId}/`, { params });
    return data;
};

export const fetchFollowingFn = async (userId, params = {}) => {
    const { data } = await axiosInstance.get(`/api/v1/accounts/auth/following/${userId}/`, { params });
    return data;
};



export const createStoreFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/accounts/auth/create-store/', payload);
    return data;
};

export const fetchStoreDetailFn = async (storeSlug) => {
    const { data } = await axiosInstance.get(`/api/v1/accounts/auth/store-detail/${storeSlug}/`);
    return data;
};

export const updateStoreFn = async ({ storeSlug, payload }) => {
    const { data } = await axiosInstance.patch(`/api/v1/accounts/auth/store-detail/${storeSlug}/`, payload);
    return data;
};

export const deleteStoreFn = async (storeSlug) => {
    const { data } = await axiosInstance.delete(`/api/v1/accounts/auth/store-detail/${storeSlug}/`);
    return data;
};

export const fetchMyStoreFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/accounts/auth/my-store/');
    return data;
};



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

export const fetchFavoriteProductsFn = async (params = {}) => {
    const { data } = await axiosInstance.get('/api/v1/products/favorites/', { params });
    return data;
};

export const fetchRecentlyViewedFn = async (params = {}) => {
    const { data } = await axiosInstance.get('/api/v1/products/recently-viewed/', { params });
    return data;
};

export const reportProductFn = async ({ productSlug, reason, details }) => {
    const { data } = await axiosInstance.post(`/api/v1/products/report/${productSlug}/`, {
        reason,
        details: details || '',
    });
    return data;
};



export const fetchConversationsFn = async (params = {}) => {
    const { data } = await axiosInstance.get('/api/v1/messaging/', { params });
    return data;
};

export const fetchConversationFn = async (conversationId) => {
    const { data } = await axiosInstance.get(`/api/v1/messaging/${conversationId}/`);
    return data;
};

export const fetchMessagesFn = async ({ conversationId, page, pageSize }) => {
    const params = {};
    if (page) params.page = page;
    if (pageSize) params.page_size = pageSize;
    const { data } = await axiosInstance.get(`/api/v1/messaging/${conversationId}/messages/`, { params });
    return data;
};

export const startConversationFn = async ({ productId, message }) => {
    const { data } = await axiosInstance.post('/api/v1/messaging/', {
        product: productId,
        message,
    });
    return data;
};

export const sendMessageFn = async ({ conversationId, body, attachment_type, attachment_url, duration_ms }) => {
    const payload = { body };
    if (attachment_type) payload.attachment_type = attachment_type;
    if (attachment_url) payload.attachment_url = attachment_url;
    if (duration_ms) payload.duration_ms = duration_ms;
    const { data } = await axiosInstance.post(`/api/v1/messaging/${conversationId}/messages/`, payload);
    return data;
};

export const markConversationReadFn = async (conversationId) => {
    const { data } = await axiosInstance.post(`/api/v1/messaging/${conversationId}/read/`);
    return data;
};

export const fetchUnreadCountsFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/messaging/unread-count/');
    return data;
};
