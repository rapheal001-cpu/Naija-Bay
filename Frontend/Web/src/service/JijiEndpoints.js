import { axiosInstance } from './axiosInstance.js';

const AUTH = '/api/v1/accounts/auth';
const PRODUCTS = '/api/v1/products';
const ORDERS = '/api/v1/orders';
const PAYMENTS = '/api/v1/payments';

// ---------------------------------------------------------------------------
// SELLER FEEDBACK
// ---------------------------------------------------------------------------
export const fetchFeedbackFn = async (sellerId) => {
    const { data } = await axiosInstance.get(`${AUTH}/feedback/`, { params: { seller: sellerId } });
    return data;
};
export const createFeedbackFn = async (payload) => {
    const { data } = await axiosInstance.post(`${AUTH}/feedback/create/`, payload);
    return data;
};
export const updateFeedbackFn = async ({ id, payload }) => {
    const { data } = await axiosInstance.patch(`${AUTH}/feedback/${id}/`, payload);
    return data;
};
export const deleteFeedbackFn = async (id) => {
    const { data } = await axiosInstance.delete(`${AUTH}/feedback/${id}/`);
    return data;
};
export const appealFeedbackFn = async ({ id, appeal }) => {
    const { data } = await axiosInstance.post(`${AUTH}/feedback/${id}/appeal/`, { appeal });
    return data;
};
export const respondFeedbackFn = async ({ id, response }) => {
    const { data } = await axiosInstance.post(`${AUTH}/feedback/${id}/respond/`, { response });
    return data;
};

// ---------------------------------------------------------------------------
// SAVED SEARCHES
// ---------------------------------------------------------------------------
export const fetchSavedSearchesFn = async () => {
    const { data } = await axiosInstance.get(`${AUTH}/saved-searches/`);
    return data;
};
export const createSavedSearchFn = async (payload) => {
    const { data } = await axiosInstance.post(`${AUTH}/saved-searches/`, payload);
    return data;
};
export const deleteSavedSearchFn = async (id) => {
    const { data } = await axiosInstance.delete(`${AUTH}/saved-searches/${id}/`);
    return data;
};

// ---------------------------------------------------------------------------
// VERIFIED ID
// ---------------------------------------------------------------------------
export const submitVerificationFn = async (formData) => {
    const { data } = await axiosInstance.post(`${AUTH}/verification/submit/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
};
export const fetchMyVerificationFn = async () => {
    const { data } = await axiosInstance.get(`${AUTH}/verification/me/`);
    return data;
};

// ---------------------------------------------------------------------------
// OFFERS / CALLBACKS / VIDEOS
// ---------------------------------------------------------------------------
export const fetchOffersFn = async (slug) => {
    const { data } = await axiosInstance.get(`${PRODUCTS}/${encodeURIComponent(slug)}/offers/`);
    return data;
};
export const createOfferFn = async ({ slug, payload }) => {
    const { data } = await axiosInstance.post(`${PRODUCTS}/${encodeURIComponent(slug)}/offers/`, payload);
    return data;
};
export const respondOfferFn = async ({ id, action }) => {
    const { data } = await axiosInstance.post(`${PRODUCTS}/offers/${id}/respond/`, { action });
    return data;
};
export const createCallbackFn = async ({ slug, payload }) => {
    const { data } = await axiosInstance.post(`${PRODUCTS}/${encodeURIComponent(slug)}/callbacks/`, payload);
    return data;
};
export const fetchVideosFn = async (slug) => {
    const { data } = await axiosInstance.get(`${PRODUCTS}/${encodeURIComponent(slug)}/videos/`);
    return data;
};
export const uploadVideoFn = async ({ slug, formData }) => {
    const { data } = await axiosInstance.post(`${PRODUCTS}/${encodeURIComponent(slug)}/videos/upload/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
};

// ---------------------------------------------------------------------------
// SAFE DEAL
// ---------------------------------------------------------------------------
export const fetchSafeDealsFn = async () => {
    const { data } = await axiosInstance.get(`${ORDERS}/safe-deal/`);
    return data;
};
export const safeDealActionFn = async ({ reference, action, payload = {} }) => {
    const { data } = await axiosInstance.post(`${ORDERS}/${encodeURIComponent(reference)}/safe-deal/${action}/`, payload);
    return data;
};

// ---------------------------------------------------------------------------
// CREDITS / REFERRALS / AUTO-RENEW / PRO SALES
// ---------------------------------------------------------------------------
export const fetchCreditFn = async () => {
    const { data } = await axiosInstance.get(`${PAYMENTS}/credit/`);
    return data;
};
export const fetchCreditTransactionsFn = async () => {
    const { data } = await axiosInstance.get(`${PAYMENTS}/credit/transactions/`);
    return data;
};
export const fetchReferralsFn = async () => {
    const { data } = await axiosInstance.get(`${PAYMENTS}/referrals/`);
    return data;
};
export const fetchAutoRenewalsFn = async () => {
    const { data } = await axiosInstance.get(`${PAYMENTS}/boost/auto-renew/`);
    return data;
};
export const createAutoRenewalFn = async (payload) => {
    const { data } = await axiosInstance.post(`${PAYMENTS}/boost/auto-renew/`, payload);
    return data;
};
export const deleteAutoRenewalFn = async (id) => {
    const { data } = await axiosInstance.delete(`${PAYMENTS}/boost/auto-renew/${id}/`);
    return data;
};
export const fetchProSalesFn = async () => {
    const { data } = await axiosInstance.get(`${PAYMENTS}/pro-sales/`);
    return data;
};
export const createProSalesFn = async (payload) => {
    const { data } = await axiosInstance.post(`${PAYMENTS}/pro-sales/`, payload);
    return data;
};
export const updateProSalesFn = async ({ id, payload }) => {
    const { data } = await axiosInstance.patch(`${PAYMENTS}/pro-sales/${id}/`, payload);
    return data;
};
export const deleteProSalesFn = async (id) => {
    const { data } = await axiosInstance.delete(`${PAYMENTS}/pro-sales/${id}/`);
    return data;
};
