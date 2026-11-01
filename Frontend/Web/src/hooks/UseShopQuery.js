import { useQuery, keepPreviousData } from '@tanstack/react-query';
import {
    fetchCartFn,
    fetchOrdersFn,
    fetchOrderFn,
    fetchSalesFn,
    fetchBoostPlansFn,
    fetchMyBoostsFn,
    verifyPaymentFn,
} from '../service/ShopEndpoints.js';

const MAX_VERIFY_POLLS = 10;

export const useFetchCart = (isAuthenticated) => {
    return useQuery({
        queryKey: ['cart'],
        queryFn: fetchCartFn,
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 30,
        refetchOnWindowFocus: true,
        retry: 1,
    });
};

export const useFetchOrders = (isAuthenticated, paymentStatus = '', page = 1) => {
    return useQuery({
        queryKey: ['orders', paymentStatus, page],
        queryFn: () => fetchOrdersFn({ payment_status: paymentStatus, page }),
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 30,
        placeholderData: keepPreviousData,
        retry: 1,
    });
};

export const useFetchOrder = (isAuthenticated, reference) => {
    return useQuery({
        queryKey: ['order', reference],
        queryFn: () => fetchOrderFn(reference),
        enabled: Boolean(isAuthenticated && reference),
        staleTime: 1000 * 15,
        retry: false,
    });
};

export const useFetchSales = (isAuthenticated, status = '', page = 1) => {
    return useQuery({
        queryKey: ['sales', status, page],
        queryFn: () => fetchSalesFn({ status, page }),
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 30,
        placeholderData: keepPreviousData,
        retry: 1,
    });
};

export const useFetchBoostPlans = () => {
    return useQuery({
        queryKey: ['boost-plans'],
        queryFn: fetchBoostPlansFn,
        staleTime: 1000 * 60 * 5,
        retry: 1,
    });
};

export const useFetchMyBoosts = (isAuthenticated, status = '', page = 1) => {
    return useQuery({
        queryKey: ['my-boosts', status, page],
        queryFn: () => fetchMyBoostsFn({ status, page }),
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 30,
        placeholderData: keepPreviousData,
        retry: 1,
    });
};

/**
 * Asks OUR backend to verify the payment with Paystack. While the backend still
 * reports "pending" we poll a few times; the result is only ever shown from the
 * backend's recorded status, never from the redirect URL.
 */
export const useVerifyPayment = (isAuthenticated, reference) => {
    return useQuery({
        queryKey: ['payment-verify', reference],
        queryFn: () => verifyPaymentFn(reference),
        enabled: Boolean(isAuthenticated && reference),
        staleTime: 0,
        gcTime: 0,
        retry: false,
        refetchOnWindowFocus: false,
        refetchInterval: (query) =>
            query.state.data?.status === 'pending' && query.state.dataUpdateCount < MAX_VERIFY_POLLS
                ? 3000
                : false,
    });
};
