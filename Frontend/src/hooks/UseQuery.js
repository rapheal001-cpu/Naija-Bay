import { useQuery, keepPreviousData } from '@tanstack/react-query';
import {
    fetchCategoriesFn,
    fetchOtherUserFn,
    fetchFeaturedProductDataFn,
    fetchUserFn,
    fetchUserNotificationsFn,
    productDetailFn,
    fetchProductsFn,
    fetchStoreDetailFn,
} from '../service/Endpoints.js';

// =============================================================================
// USER
// =============================================================================

export const useFetchUserData = (isAuthenticated) => {
    return useQuery({ 
        queryKey: ['user'],
        queryFn: fetchUserFn,
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 60 * 30,      // 30 min — profile rarely changes
        gcTime: 1000 * 60 * 60,         // keep in cache 1 hour after unmount
        refetchOnWindowFocus: true,
        retry: 1,
        meta: { hookName: 'useFetchUserData' },
    });
};

/**
 * @param {string|number} userId
 * @param {boolean} [isAuthenticated=true] — set to false if you want to block unauthenticated users
 */
export const useFetchOtherUserData = (userId, isAuthenticated) => {
    return useQuery({
        queryKey: ['other-user', userId],
        queryFn: () => fetchOtherUserFn(userId),
        enabled: Boolean(userId && isAuthenticated),
        staleTime: 1000 * 60 * 30,
        gcTime: 1000 * 60 * 30,
        refetchOnWindowFocus: false,
        retry: 1,
        meta: { hookName: 'useFetchOtherUserData' },
    });
};

// =============================================================================
// NOTIFICATIONS
// =============================================================================

export const useFetchUserNotifications = (isAuthenticated) => {
    return useQuery({
        queryKey: ['notifications'],
        queryFn: fetchUserNotificationsFn,
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 60,           // 1 min — reasonably fresh without spam
        gcTime: 1000 * 60 * 5,
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
        retry: 1,
        meta: { hookName: 'useFetchUserNotifications' },
    });
};

// =============================================================================
// PRODUCTS
// =============================================================================

export const useFetchProducts = (searchQuery, activeCategory, activeSubCategory) => {
    return useQuery({
        queryKey: ['products', { searchQuery, activeCategory, activeSubCategory }],
        queryFn: () => fetchProductsFn(searchQuery, activeCategory, activeSubCategory),
        staleTime: 1000 * 60 * 5,       // 5 min
        gcTime: 1000 * 60 * 10,
        refetchOnWindowFocus: false,    // heavy endpoint — don't refetch on tab switch
        refetchOnReconnect: false,
        retry: 1,
        placeholderData: keepPreviousData, // smooth UX when filters change
        meta: { hookName: 'useFetchProducts' },
    });
};

export const useFetchFeaturedProductData = () => {
    return useQuery({
        queryKey: ['featured-products'],
        queryFn: fetchFeaturedProductDataFn,
        staleTime: 1000 * 60 * 2,      // 1 hour — homepage hero data is static
        gcTime: 1000 * 60 * 60 * 2,     // 2 hours
        refetchOnWindowFocus: false,
        retry: 1,
        meta: { hookName: 'useFetchFeaturedProductData' },
    });
};

export const useFetchProductDetailData = (productSlug) => {
    return useQuery({
        queryKey: ['product-detail', productSlug],
        queryFn: () => productDetailFn(productSlug),
        enabled: Boolean(productSlug),
        staleTime: 1000 * 60 * 10,      // 10 min — single product doesn't change often
        gcTime: 1000 * 60 * 30,
        refetchOnWindowFocus: false,
        retry: 1,
        meta: { hookName: 'useFetchProductDetailData' },
    });
};

// =============================================================================
// CATEGORIES
// =============================================================================

export const useFetchCategories = () => {
    return useQuery({
        queryKey: ['categories'],
        queryFn: fetchCategoriesFn,
        staleTime: 1000 * 60 * 60 * 24, // 24 hours — categories are almost static
        gcTime: 1000 * 60 * 60 * 24 * 7, // 7 days
        refetchOnWindowFocus: false,
        retry: 1,
        meta: { hookName: 'useFetchCategories' },
    });
};

// =============================================================================
// STORE
// =============================================================================

export const useFetchStoreDetail = (store_slug) => {
    return useQuery({
        queryKey: ['store-detail', store_slug],
        queryFn: () => fetchStoreDetailFn(store_slug),
        enabled: Boolean(store_slug),
        staleTime: 1000 * 60 * 30,
        gcTime: 1000 * 60 * 60,
        refetchOnWindowFocus: false,
        retry: 1,
        meta: { hookName: 'useFetchStoreDetail' },
    });
};