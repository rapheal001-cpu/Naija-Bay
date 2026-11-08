import { useQuery, keepPreviousData } from '@tanstack/react-query';
import {
    fetchCategoriesFn,
    fetchAttributeDefinitionsFn,
    fetchOtherUserFn,
    fetchFeaturedProductDataFn,
    fetchFlashDealsFn,
    fetchUserFn,
    fetchUserNotificationsFn,
    productDetailFn,
    fetchProductsFn,
    fetchStoreDetailFn,
    fetchMyStoreFn,
    fetchMyListingsFn,
    fetchFavoriteProductsFn,
    fetchRecentlyViewedFn,
    fetchConversationsFn,
    fetchConversationFn,
    fetchMessagesFn,
    fetchUnreadCountsFn,
    fetchFollowersFn,
    fetchFollowingFn,
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

export const useFetchProducts = (params = {}) => {
    return useQuery({
        queryKey: ['products', params],
        queryFn: () => fetchProductsFn(params),
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

export const useFetchFlashDeals = () => {
    return useQuery({
        queryKey: ['flash-deals'],
        queryFn: fetchFlashDealsFn,
        staleTime: 1000 * 60 * 2,
        gcTime: 1000 * 60 * 30,
        refetchOnWindowFocus: false,
        retry: 1,
        meta: { hookName: 'useFetchFlashDeals' },
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
// ATTRIBUTE DEFINITIONS
// =============================================================================

export const useFetchAttributeDefinitions = (category, subCategory) => {
    return useQuery({
        queryKey: ['attribute-definitions', category || '', subCategory || ''],
        queryFn: () => fetchAttributeDefinitionsFn({ category, subCategory }),
        enabled: Boolean(category),
        staleTime: 1000 * 60 * 30,
        gcTime: 1000 * 60 * 60,
        refetchOnWindowFocus: false,
        retry: 1,
        meta: { hookName: 'useFetchAttributeDefinitions' },
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

export const useFetchMyStore = (isAuthenticated) => {
    return useQuery({
        queryKey: ['my-store'],
        queryFn: fetchMyStoreFn,
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 60 * 30,
        gcTime: 1000 * 60 * 60,
        refetchOnWindowFocus: false,
        retry: false,
        meta: { hookName: 'useFetchMyStore' },
    });
};

// =============================================================================
// SELLER LISTS
// =============================================================================

export const useFetchFollowers = (userId, page = 1) => {
    return useQuery({
        queryKey: ['followers', userId, page],
        queryFn: () => fetchFollowersFn(userId, { page }),
        enabled: Boolean(userId),
        staleTime: 1000 * 60 * 5,
        placeholderData: keepPreviousData,
        retry: 1,
        meta: { hookName: 'useFetchFollowers' },
    });
};

export const useFetchFollowing = (userId, page = 1) => {
    return useQuery({
        queryKey: ['following', userId, page],
        queryFn: () => fetchFollowingFn(userId, { page }),
        enabled: Boolean(userId),
        staleTime: 1000 * 60 * 5,
        placeholderData: keepPreviousData,
        retry: 1,
        meta: { hookName: 'useFetchFollowing' },
    });
};

// =============================================================================
// MY LISTINGS / FAVORITES / HISTORY
// =============================================================================

export const useFetchMyListings = (isAuthenticated, status = '', page = 1) => {
    return useQuery({
        queryKey: ['my-listings', status, page],
        queryFn: () => fetchMyListingsFn({ status, page }),
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 60,
        placeholderData: keepPreviousData,
        retry: 1,
        meta: { hookName: 'useFetchMyListings' },
    });
};

export const useFetchFavoriteProducts = (isAuthenticated, page = 1) => {
    return useQuery({
        queryKey: ['favorite-products', page],
        queryFn: () => fetchFavoriteProductsFn({ page }),
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 60,
        placeholderData: keepPreviousData,
        retry: 1,
        meta: { hookName: 'useFetchFavoriteProducts' },
    });
};

export const useFetchRecentlyViewed = (isAuthenticated, page = 1) => {
    return useQuery({
        queryKey: ['recently-viewed', page],
        queryFn: () => fetchRecentlyViewedFn({ page }),
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 60,
        placeholderData: keepPreviousData,
        retry: 1,
        meta: { hookName: 'useFetchRecentlyViewed' },
    });
};

// =============================================================================
// MESSAGING
// =============================================================================

export const useFetchConversations = (isAuthenticated, page = 1) => {
    return useQuery({
        queryKey: ['conversations', page],
        queryFn: () => fetchConversationsFn({ page }),
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 10,
        gcTime: 1000 * 60 * 10,
        refetchInterval: 15000,
        refetchOnWindowFocus: true,
        placeholderData: keepPreviousData,
        retry: 1,
        meta: { hookName: 'useFetchConversations' },
    });
};

export const useFetchConversation = (conversationId) => {
    return useQuery({
        queryKey: ['conversation', conversationId],
        queryFn: () => fetchConversationFn(conversationId),
        enabled: Boolean(conversationId),
        staleTime: 1000 * 10,
        refetchInterval: 15000,
        retry: 1,
        meta: { hookName: 'useFetchConversation' },
    });
};

export const useFetchMessages = (conversationId, page = 1) => {
    return useQuery({
        queryKey: ['messages', conversationId, page],
        queryFn: () => fetchMessagesFn({ conversationId, page }),
        enabled: Boolean(conversationId),
        staleTime: 1000 * 5,
        refetchInterval: 8000,
        retry: 1,
        meta: { hookName: 'useFetchMessages' },
    });
};

export const useFetchUnreadCounts = (isAuthenticated) => {
    return useQuery({
        queryKey: ['unread-counts'],
        queryFn: fetchUnreadCountsFn,
        enabled: Boolean(isAuthenticated),
        staleTime: 1000 * 15,
        refetchInterval: 30000,
        refetchOnWindowFocus: true,
        retry: 1,
        meta: { hookName: 'useFetchUnreadCounts' },
    });
};
