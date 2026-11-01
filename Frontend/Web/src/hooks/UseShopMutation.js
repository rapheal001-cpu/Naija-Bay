import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
    addToCartFn,
    updateCartItemFn,
    removeCartItemFn,
    clearCartFn,
    checkoutFn,
    cancelOrderFn,
    updateSaleStatusFn,
    initializeOrderPaymentFn,
    initializeBoostFn,
} from '../service/ShopEndpoints.js';

export const useAddToCartMutation = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationKey: ['add-to-cart'],
        mutationFn: (payload) => addToCartFn(payload),
        onSuccess: (cart) => queryClient.setQueryData(['cart'], cart),
        onSettled: () => queryClient.invalidateQueries({ queryKey: ['cart'] }),
    });
};

export const useUpdateCartItemMutation = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationKey: ['update-cart-item'],
        mutationFn: (payload) => updateCartItemFn(payload),
        onSuccess: (cart) => queryClient.setQueryData(['cart'], cart),
        onSettled: () => queryClient.invalidateQueries({ queryKey: ['cart'] }),
    });
};

export const useRemoveCartItemMutation = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationKey: ['remove-cart-item'],
        mutationFn: (productId) => removeCartItemFn(productId),
        onSuccess: (cart) => queryClient.setQueryData(['cart'], cart),
        onSettled: () => queryClient.invalidateQueries({ queryKey: ['cart'] }),
    });
};

export const useClearCartMutation = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationKey: ['clear-cart'],
        mutationFn: clearCartFn,
        onSuccess: (cart) => queryClient.setQueryData(['cart'], cart),
        onSettled: () => queryClient.invalidateQueries({ queryKey: ['cart'] }),
    });
};

export const useCheckoutMutation = () => {
    return useMutation({
        mutationKey: ['checkout'],
        mutationFn: (payload) => checkoutFn(payload),
    });
};

export const useInitializeOrderPaymentMutation = () => {
    return useMutation({
        mutationKey: ['initialize-order-payment'],
        mutationFn: (orderReference) => initializeOrderPaymentFn(orderReference),
    });
};

export const useCancelOrderMutation = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationKey: ['cancel-order'],
        mutationFn: (reference) => cancelOrderFn(reference),
        onSettled: (data, error, reference) => {
            queryClient.invalidateQueries({ queryKey: ['orders'] });
            queryClient.invalidateQueries({ queryKey: ['order', reference] });
        },
    });
};

export const useUpdateSaleStatusMutation = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationKey: ['update-sale-status'],
        mutationFn: (payload) => updateSaleStatusFn(payload),
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['sales'] });
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
        },
    });
};

export const useInitializeBoostMutation = () => {
    return useMutation({
        mutationKey: ['initialize-boost'],
        mutationFn: (payload) => initializeBoostFn(payload),
    });
};
