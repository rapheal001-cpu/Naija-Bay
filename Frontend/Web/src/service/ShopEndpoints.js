import { axiosInstance } from './axiosInstance.js';

// All amounts, totals and statuses come from the backend. Nothing here sends a
// price or a payment status: the server reads prices from its own database and
// only marks things paid after verifying with Paystack.

const clean = (params = {}) => {
    const query = {};
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '' && value !== false) {
            query[key] = value;
        }
    });
    return query;
};


// =============================================================================
// CART
// =============================================================================

export const fetchCartFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/orders/cart/');
    return data;
};

/** @param {{ productId: number|string, quantity?: number }} payload */
export const addToCartFn = async ({ productId, quantity = 1 }) => {
    const { data } = await axiosInstance.post('/api/v1/orders/cart/items/', {
        product_id: productId,
        quantity,
    });
    return data;
};

/** @param {{ productId: number|string, quantity: number }} payload */
export const updateCartItemFn = async ({ productId, quantity }) => {
    const { data } = await axiosInstance.patch(`/api/v1/orders/cart/items/${productId}/`, { quantity });
    return data;
};

export const removeCartItemFn = async (productId) => {
    const { data } = await axiosInstance.delete(`/api/v1/orders/cart/items/${productId}/`);
    return data;
};

export const clearCartFn = async () => {
    const { data } = await axiosInstance.delete('/api/v1/orders/cart/');
    return data;
};


// =============================================================================
// CHECKOUT & ORDERS
// =============================================================================

/** @param {{ recipient_name: string, phone: string, address: string, state: string, note?: string }} payload */
export const checkoutFn = async (payload) => {
    const { data } = await axiosInstance.post('/api/v1/orders/checkout/', payload);
    return data;
};

/** @param {{ payment_status?: string, page?: number }} [params] */
export const fetchOrdersFn = async (params = {}) => {
    const { data } = await axiosInstance.get('/api/v1/orders/', { params: clean(params) });
    return data;
};

export const fetchOrderFn = async (reference) => {
    const { data } = await axiosInstance.get(`/api/v1/orders/${reference}/`);
    return data;
};

export const cancelOrderFn = async (reference) => {
    const { data } = await axiosInstance.post(`/api/v1/orders/${reference}/cancel/`);
    return data;
};

/** @param {{ status?: string, page?: number }} [params] */
export const fetchSalesFn = async (params = {}) => {
    const { data } = await axiosInstance.get('/api/v1/orders/sales/', { params: clean(params) });
    return data;
};

/** @param {{ itemId: number|string, status: string }} payload */
export const updateSaleStatusFn = async ({ itemId, status }) => {
    const { data } = await axiosInstance.post(`/api/v1/orders/sales/${itemId}/status/`, { status });
    return data;
};


// =============================================================================
// PAYMENTS (PAYSTACK) & AD BOOSTING
// =============================================================================

/** Returns { reference, authorization_url, amount, currency } */
export const initializeOrderPaymentFn = async (orderReference) => {
    const { data } = await axiosInstance.post(`/api/v1/payments/orders/${orderReference}/initialize/`);
    return data;
};

export const verifyPaymentFn = async (reference) => {
    const { data } = await axiosInstance.get(`/api/v1/payments/verify/${encodeURIComponent(reference)}/`);
    return data;
};

export const fetchBoostPlansFn = async () => {
    const { data } = await axiosInstance.get('/api/v1/payments/boost/plans/');
    return data;
};

/** @param {{ productId: number|string, planId: number|string }} payload */
export const initializeBoostFn = async ({ productId, planId }) => {
    const { data } = await axiosInstance.post('/api/v1/payments/boost/initialize/', {
        product_id: productId,
        plan_id: planId,
    });
    return data;
};

/** @param {{ status?: string, page?: number }} [params] */
export const fetchMyBoostsFn = async (params = {}) => {
    const { data } = await axiosInstance.get('/api/v1/payments/boost/my/', { params: clean(params) });
    return data;
};
