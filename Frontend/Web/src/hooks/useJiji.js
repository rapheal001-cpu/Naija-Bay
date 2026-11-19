import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    fetchFeedbackFn, createFeedbackFn, updateFeedbackFn, deleteFeedbackFn,
    appealFeedbackFn, respondFeedbackFn,
    fetchSavedSearchesFn, createSavedSearchFn, deleteSavedSearchFn,
    submitVerificationFn, fetchMyVerificationFn,
    fetchOffersFn, createOfferFn, respondOfferFn, createCallbackFn,
    fetchVideosFn, uploadVideoFn,
    fetchSafeDealsFn, safeDealActionFn,
    fetchCreditFn, fetchCreditTransactionsFn, fetchReferralsFn,
    fetchAutoRenewalsFn, createAutoRenewalFn, deleteAutoRenewalFn,
    fetchProSalesFn, createProSalesFn, updateProSalesFn, deleteProSalesFn,
} from '../service/JijiEndpoints.js';

const useQ = (key, fn, enabled = true) => useQuery({
    queryKey: key,
    queryFn: fn,
    enabled,
    staleTime: 1000 * 60,
    retry: 1,
});

// ---------------------------------------------------------------------------
// FEEDBACK
// ---------------------------------------------------------------------------
export const useFeedback = (sellerId, enabled = true) =>
    useQ(['feedback', sellerId], () => fetchFeedbackFn(sellerId), Boolean(sellerId && enabled));

export const useCreateFeedback = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: createFeedbackFn,
        onSuccess: (_d, vars) => c.invalidateQueries({ queryKey: ['feedback', vars.seller] }),
    });
};

export const useUpdateFeedback = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: updateFeedbackFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['feedback'] }),
    });
};

export const useDeleteFeedback = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: deleteFeedbackFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['feedback'] }),
    });
};

export const useAppealFeedback = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: appealFeedbackFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['feedback'] }),
    });
};

export const useRespondFeedback = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: respondFeedbackFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['feedback'] }),
    });
};

// ---------------------------------------------------------------------------
// SAVED SEARCHES / VERIFICATION
// ---------------------------------------------------------------------------
export const useSavedSearches = (enabled = true) => useQ(['saved-searches'], fetchSavedSearchesFn, enabled);

export const useCreateSavedSearch = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: createSavedSearchFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['saved-searches'] }),
    });
};

export const useDeleteSavedSearch = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: deleteSavedSearchFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['saved-searches'] }),
    });
};

export const useMyVerification = (enabled = true) => useQ(['verification', 'me'], fetchMyVerificationFn, enabled);

export const useSubmitVerification = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: submitVerificationFn,
        onSuccess: () => {
            c.invalidateQueries({ queryKey: ['verification'] });
            c.invalidateQueries({ queryKey: ['user'] });
        },
    });
};

// ---------------------------------------------------------------------------
// OFFERS / CALLBACKS / VIDEOS
// ---------------------------------------------------------------------------
export const useOffers = (slug, enabled = true) => useQ(['offers', slug], () => fetchOffersFn(slug), Boolean(slug && enabled));

export const useCreateOffer = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: createOfferFn,
        onSuccess: (_d, v) => c.invalidateQueries({ queryKey: ['offers', v.slug] }),
    });
};

export const useRespondOffer = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: respondOfferFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['offers'] }),
    });
};

export const useCreateCallback = () => useMutation({ mutationFn: createCallbackFn });

export const useVideos = (slug, enabled = true) => useQ(['videos', slug], () => fetchVideosFn(slug), Boolean(slug && enabled));

export const useUploadVideo = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: uploadVideoFn,
        onSuccess: (_d, v) => c.invalidateQueries({ queryKey: ['videos', v.slug] }),
    });
};

// ---------------------------------------------------------------------------
// SAFE DEAL
// ---------------------------------------------------------------------------
export const useSafeDeals = (enabled = true) => useQ(['safe-deals'], fetchSafeDealsFn, enabled);

export const useSafeDealAction = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: safeDealActionFn,
        onSuccess: () => {
            c.invalidateQueries({ queryKey: ['safe-deals'] });
            c.invalidateQueries({ queryKey: ['orders'] });
        },
    });
};

// ---------------------------------------------------------------------------
// MONETISATION
// ---------------------------------------------------------------------------
export const useCredit = (enabled = true) => useQ(['credit'], fetchCreditFn, enabled);
export const useCreditTransactions = (enabled = true) => useQ(['credit-transactions'], fetchCreditTransactionsFn, enabled);
export const useReferrals = (enabled = true) => useQ(['referrals'], fetchReferralsFn, enabled);

export const useAutoRenewals = (enabled = true) => useQ(['auto-renewals'], fetchAutoRenewalsFn, enabled);
export const useCreateAutoRenewal = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: createAutoRenewalFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['auto-renewals'] }),
    });
};
export const useDeleteAutoRenewal = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: deleteAutoRenewalFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['auto-renewals'] }),
    });
};

export const useProSales = (enabled = true) => useQ(['pro-sales'], fetchProSalesFn, enabled);
export const useCreateProSales = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: createProSalesFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['pro-sales'] }),
    });
};
export const useUpdateProSales = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: updateProSalesFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['pro-sales'] }),
    });
};
export const useDeleteProSales = () => {
    const c = useQueryClient();
    return useMutation({
        mutationFn: deleteProSalesFn,
        onSuccess: () => c.invalidateQueries({ queryKey: ['pro-sales'] }),
    });
};
