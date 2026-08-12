import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
    createProductFn,
    createProductImagesFn,
    logoutUserFn,
    markAllNotificationsAsReadFn,
    markNotificationAsReadFn,
    deleteNotificationFn,
    deleteAllNotificationsFn,
    registerUserFn,
    requestPasswordResetFn,
    signInUserFn,
    toggleProductFavoriteFn,
    updateUserProfileFn,
    toggleFollowUserFn,
    changePasswordFn,
    deleteProductFn,
    resendVerificationEmailFn,
    updateProductFn,
    updateProductImagesFn,
    deleteProductImageFn,
    createStoreFn,
} from '../service/Endpoints';
import { removeIsAuthenticated, setIsAuthenticated } from '../slice/AuthSlice';
import { setUser, removeUserData } from '../slice/UserSlice.js';


// =============================================================================
// ERROR UTILITIES
// =============================================================================

/**
 * Maps server validation errors to react-hook-form's setError and a general
 */
const handleFieldErrors = (error, setError, setServerError) => {
    const data = error.response?.data;

    // Guard first — before touching Object.entries
    if (!data || typeof data !== 'object') {
        setServerError?.(error.message || 'An unexpected error occurred. Please try again.');
        return;
    }

    Object.entries(data).forEach(([field, value]) => {
        let msg;

        if (typeof value === 'string') {
            msg = value;
        } else if (Array.isArray(value)) {
            msg = value[0];
        } else if (value && typeof value === 'object') {
    
            const nested = Object.values(value)[0];
            msg = Array.isArray(nested) ? nested[0] : nested;
        } else {
            msg = String(value);
        }

        if (field === 'detail' || field === 'non_field_errors') {
            setServerError(msg);
        } else {
            setError(field, { type: 'server', message: msg });
        }
    });
};


// =============================================================================
// AUTHENTICATION
// =============================================================================

export const useSignInMutation = (setError, setServerError) => {
    const navigate = useNavigate();
    const dispatch = useDispatch();

    return useMutation({
        mutationKey: ['sign-in'],
        mutationFn: (payload) => signInUserFn(payload),
        onSuccess: () => {
            dispatch(setIsAuthenticated());
            navigate('/');
        },
        onError: (error) => {
            handleFieldErrors(error, setError, setServerError);
        },
    });
};

export const useRegisterMutation = (setError, setServerError) => {
    const navigate = useNavigate();

    return useMutation({
        mutationKey: ['register'],
        mutationFn: (payload) => registerUserFn(payload),
        onSuccess: () => {
            navigate('/email-verification-sent');
        },
        onError: (error) => {
            console.log(error.response.data);
            handleFieldErrors(error, setError, setServerError);
        },
    });
};

export const useLogoutMutation = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['logout'],
        mutationFn: logoutUserFn,
        onSuccess: () => {
            dispatch(removeIsAuthenticated());
            dispatch(removeUserData());
            queryClient.clear();
            navigate('/');
        },
        onError: () => {
            dispatch(removeIsAuthenticated());
            dispatch(removeUserData());
            queryClient.clear();
            navigate('/');
        },
    });
};

export const useRequestPasswordResetMutation = (setError, setServerError, setServerMessage) => {
    return useMutation({
        mutationKey: ['password-reset'],
        mutationFn: (payload) => requestPasswordResetFn(payload),
        onSuccess: (data) => {
            setServerMessage(data.detail);
        },
        onError: (error) => {
            handleFieldErrors(error, setError, setServerError)
        },
    });
};

export const useChangePasswordMutation = (setError, setServerError, setServerMessage) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['change-password'],
        mutationFn: (payload) => changePasswordFn(payload),
        onMutate: async () => {
            await queryClient.cancelQueries(['user']);

            const previousUserData = queryClient.getQueryData({ queryKey: ['user'] });

            return { previousUserData }
        },
        onSuccess: () => {
            setServerMessage('Password changed successfully.');
            setServerError('');
            queryClient.invalidateQueries({ queryKey: ['user'] });
        },
        onError: (error, variables, context) => {
            if (context?.previousUserData) queryClient.getQueryData(['user'], context.previousUserData);

            handleFieldErrors(error, setError, setServerError);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['user'] });
        }
    });
};


// =============================================================================
// USER
// =============================================================================

export const useUpdateProfileMutation = (setError, setServerError, setServerMessage) => {
    const dispatch = useDispatch();
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['update-user'],
        mutationFn: (payload) => updateUserProfileFn(payload),
        onMutate: async () => {
            await queryClient.cancelQueries({ queryKey: ['user'] });

            const previousUserData = queryClient.getQueryData(['user']);

            return { previousUserData }
        },
        onSuccess: (data) => {
            dispatch(setUser(data));
            setServerMessage('Profile updated successfully.');
            setServerError('');

            queryClient.invalidateQueries({ queryKey: ['user'] });
        },
        onError: (error, variables, context) => {
            if (context?.previousUserData) queryClient.getQueryData(['user'], context.previousUserData);

            handleFieldErrors(error, setError, setServerError);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['user'] });
        }
    });
};

// =============================================================================
// PRODUCTS
// =============================================================================

export const useCreateProductMutation = (setError, setServerError) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['create-product'],
        mutationFn: (payload) => createProductFn(payload),
        onMutate: async () => {
            await queryClient.cancelQueries(['products']);
            await queryClient.cancelQueries(['featured-products']);
            await queryClient.cancelQueries(['notifications']);
            await queryClient.cancelQueries(['user']);
            await queryClient.cancelQueries(['stores']);

            const previousProducts = queryClient.getQueryData(['products']);
            const previousFeaturedProducts = queryClient.getQueryData(['featured-products']);
            const previousNotifications = queryClient.getQueryData(['notifications']);
            const previousUserData = queryClient.getQueryData(['user']);
            const previousStores = queryClient.getQueryData(['stores']);

            return { previousProducts, previousFeaturedProducts, previousNotifications, previousUserData, previousStores }

        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
            queryClient.invalidateQueries({ queryKey: ['stores'] });

            setServerError('');
        },
        onError: (error, variables, context) => {
            if (context?.previousProducts) queryClient.getQueryData(['products'], context.previousProducts);
            if (context?.previousFeaturedProducts) queryClient.getQueryData(['featured-products'], context.previousFeaturedProducts);
            if (context?.previousNotifications) queryClient.getQueryData(['notifications'], context.previousNotifications);
            if (context?.previousUserData) queryClient.getQueryData(['user'], context.previousUserData);
            if (context?.previousStores) queryClient.getQueryData(['stores'], context.previousStores);

            handleFieldErrors(error, setError, setServerError);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
            queryClient.invalidateQueries({ queryKey: ['stores'] });
        }
    });
};

export const useUpdateProductMutation = (setError, setServerError) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['update-product'],
        mutationFn: ({ productSlug, payload }) => updateProductFn({ productSlug, payload }),
        onMutate: async (productSlug) => {
            await queryClient.cancelQueries(['products']);
            await queryClient.cancelQueries(['featured-products']);
            await queryClient.cancelQueries(['notifications']);
            await queryClient.cancelQueries(['user']);
            await queryClient.cancelQueries(['stores']);
            await queryClient.cancelQueries(['product-detail', productSlug]);

            const previousProducts = queryClient.getQueryData(['products']);
            const previousFeaturedProducts = queryClient.getQueryData(['featured-products']);
            const previousNotifications = queryClient.getQueryData(['notifications']);
            const previousUserData = queryClient.getQueryData(['user']);
            const previousStores = queryClient.getQueryData(['stores']);
            const previousProductDetail = queryClient.getQueryData(['product-detail', productSlug]);

            return { previousProducts, previousFeaturedProducts, previousNotifications, previousUserData, previousStores, previousProductDetail }

        },
        onSuccess: (data, variables) => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['stores'] });
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['product-detail', variables.productSlug] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
            setServerError?.('');
        },
        onError: (error, variables, context) => {
            if (context?.previousProducts) queryClient.getQueryData(['products'], context.previousProducts);
            if (context?.previousFeaturedProducts) queryClient.getQueryData(['featured-products'], context.previousFeaturedProducts);
            if (context?.previousNotifications) queryClient.getQueryData(['notifications'], context.previousNotifications);
            if (context?.previousUserData) queryClient.getQueryData(['user'], context.previousUserData);
            if (context?.previousStores) queryClient.getQueryData(['stores'], context.previousStores);
            if (context?.previousProductDetail) queryClient.getQueryData(['product-detail', variables.productSlug]);

            handleFieldErrors(error, setError, setServerError);
        },
        onSettled: (variables) => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
            queryClient.invalidateQueries({ queryKey: ['stores'] });
            queryClient.invalidateQueries({ queryKey: ['product-detail', variables.productSlug] });
        }
    });
};

export const useCreateProductImagesMutation = (setServerError) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['create-product-images'],
        mutationFn: (payload) => createProductImagesFn(payload),
        onMutate: async () => {
            await queryClient.cancelQueries(['products']);
            await queryClient.cancelQueries(['featured-products']);
            await queryClient.cancelQueries(['notifications']);
            await queryClient.cancelQueries(['user']);
            await queryClient.cancelQueries(['stores']);

            const previousProducts = queryClient.getQueryData(['products']);
            const previousFeaturedProducts = queryClient.getQueryData(['featured-products']);
            const previousNotifications = queryClient.getQueryData(['notifications']);
            const previousUserData = queryClient.getQueryData(['user']);
            const previousStores = queryClient.getQueryData(['stores']);

            return { previousProducts, previousFeaturedProducts, previousNotifications, previousUserData, previousStores }

        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
            queryClient.invalidateQueries({ queryKey: ['stores'] });

            setServerError('');
        },
        onError: (error, variables, context) => {
            if (context?.previousProducts) queryClient.getQueryData(['products'], context.previousProducts);
            if (context?.previousFeaturedProducts) queryClient.getQueryData(['featured-products'], context.previousFeaturedProducts);
            if (context?.previousNotifications) queryClient.getQueryData(['notifications'], context.previousNotifications);
            if (context?.previousUserData) queryClient.getQueryData(['user'], context.previousUserData);
            if (context?.previousStores) queryClient.getQueryData(['stores'], context.previousStores);

            handleFieldErrors(error, setServerError);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
            queryClient.invalidateQueries({ queryKey: ['stores'] });
        }
    });
};


export const useUpdateProductImagesMutation = (setServerError) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['update-product-images'],
        mutationFn: (payload) => updateProductImagesFn(payload),
        onMutate: async () => {
            await queryClient.cancelQueries(['products']);
            await queryClient.cancelQueries(['featured-products']);
            await queryClient.cancelQueries(['notifications']);
            await queryClient.cancelQueries(['user']);
            await queryClient.cancelQueries(['stores']);

            const previousProducts = queryClient.getQueryData(['products']);
            const previousFeaturedProducts = queryClient.getQueryData(['featured-products']);
            const previousNotifications = queryClient.getQueryData(['notifications']);
            const previousUserData = queryClient.getQueryData(['user']);
            const previousStores = queryClient.getQueryData(['stores']);

            return { previousProducts, previousFeaturedProducts, previousNotifications, previousUserData, previousStores }

        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
            queryClient.invalidateQueries({ queryKey: ['stores'] });

            setServerError('');
        },
        onError: (error, variables, context) => {
            if (context?.previousProducts) queryClient.getQueryData(['products'], context.previousProducts);
            if (context?.previousFeaturedProducts) queryClient.getQueryData(['featured-products'], context.previousFeaturedProducts);
            if (context?.previousNotifications) queryClient.getQueryData(['notifications'], context.previousNotifications);
            if (context?.previousUserData) queryClient.getQueryData(['user'], context.previousUserData);
            if (context?.previousStores) queryClient.getQueryData(['stores'], context.previousStores);

            handleFieldErrors(error, setServerError);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
            queryClient.invalidateQueries({ queryKey: ['stores'] });
        }
    });
};

export const useResendVerificationEmailMutation = (setError, setServerError, setServerMessage) => {
    return useMutation({
        mutationKey: ['resend-verification-email'],
        mutationFn: (payload) => resendVerificationEmailFn(payload),
        onSuccess: () => {
            setServerError('');
            setServerMessage('A new verification link has been sent to your email address.');
        },
        onError: (error) => {
            handleFieldErrors(error, setError, setServerError)
        },
    });
};

export const useDeleteProductImageMutation = (setServerError) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['delete-product-image'],
        mutationFn: (imageId) => deleteProductImageFn(imageId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
            setServerError?.('');
        },
        onError: (error) => {
            handleFieldErrors(error, setServerError);
        },
    });
};

export const useDeleteProductMutation = () => {
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    return useMutation({
        mutationKey: ['delete-product'],
        mutationFn: (productSlug) => deleteProductFn(productSlug),
        onMutate: async (productSlug) => {
            await queryClient.cancelQueries({ queryKey: ['products'] });
            await queryClient.cancelQueries({ queryKey: ['user'] });
            await queryClient.cancelQueries({ queryKey: ['featured-products'] });
            await queryClient.cancelQueries({ queryKey: ['product-detail', productSlug] });

            const previousProducts = queryClient.getQueryData(['products']);
            const previousUserData = queryClient.getQueryData(['user']);
            const previousFeatured = queryClient.getQueryData(['featured-products']);
            const previousDetail = queryClient.getQueryData(['product-detail', productSlug]);

            return { previousProducts, previousFeatured, previousDetail, previousUserData };
        },
        onSuccess: (productSlug) => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['product-detail', productSlug] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
            navigate(-1);
        },
        onError: (error, productSlug, context) => {
            if (context?.previousProducts) queryClient.setQueryData(['products'], context.previousProducts);
            if (context?.previousFeatured) queryClient.setQueryData(['featured-products'], context.previousFeatured);
            if (context?.previousDetail) queryClient.setQueryData(['product-detail', productSlug], context.previousDetail);
            if (context?.previousUserData) queryClient.setQueryData(['user'], context.previousUserData);
        },
        onSettled: (data, error, productSlug) => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['product-detail', productSlug] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
        },
    });
};

export const useToggleFavoriteMutation = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['toggle-favorite-products'],
        mutationFn: (productSlug) => toggleProductFavoriteFn(productSlug),
        onMutate: async (productSlug) => {
            await queryClient.cancelQueries({ queryKey: ['products'] });
            await queryClient.cancelQueries({ queryKey: ['featured-products'] });
            await queryClient.cancelQueries({ queryKey: ['product-detail', productSlug] });
            await queryClient.cancelQueries({ queryKey: ['user']});

            const previousProducts = queryClient.getQueryData(['products']);
            const previousFeatured = queryClient.getQueryData(['featured-products']);
            const previousDetail = queryClient.getQueryData(['product-detail', productSlug]);
            const previousUser = queryClient.getQueryData(['user']);

            return { previousProducts, previousFeatured, previousDetail, previousUser };
        },
        onError: (error, productSlug, context) => {
            if (context?.previousProducts) queryClient.setQueryData(['products'], context.previousProducts);
            if (context?.previousFeatured) queryClient.setQueryData(['featured-products'], context.previousFeatured);
            if (context?.previousDetail) queryClient.setQueryData(['product-detail', productSlug], context.previousDetail);
            if (context?.previousUser) queryClient.setQueryData(['user'], context.previousUser);
        },
        onSettled: (data, error, productSlug) => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            queryClient.invalidateQueries({ queryKey: ['featured-products'] });
            queryClient.invalidateQueries({ queryKey: ['product-detail', productSlug] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
        },
    });
};

// =============================================================================
// NOTIFICATIONS
// =============================================================================

export const useMarkAllNotificationsAsReadMutation = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['mark-all-notifications-as-read'],
        mutationFn: markAllNotificationsAsReadFn,
        onMutate: async () => {
            await queryClient.cancelQueries({ queryKey: ['notifications'] });
            await queryClient.cancelQueries({ queryKey: ['user']});

            const previousNotifications = queryClient.getQueryData(['notifications']);
            const previousUserData = queryClient.getQueryData(['user']);
            
            return { previousNotifications, previousUserData };
        },
        onError: (error, variables, context) => {
            if (context?.previousNotifications) queryClient.setQueryData(['notifications'], context.previousNotifications);
            if (context?.previousUserData) queryClient.setQueryData(['user'], context.previousUserData);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
        },
    });
};

export const useDeleteAllNotificationsMutation = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['delete-all-notifications'],
        mutationFn: deleteAllNotificationsFn,
        onMutate: async () => {
            await queryClient.cancelQueries({ queryKey: ['notifications'] });
            await queryClient.cancelQueries({ queryKey: ['user']});

            const previousNotifications = queryClient.getQueryData(['notifications']);
            const previousUserData = queryClient.getQueryData(['user']);
            
            return { previousNotifications, previousUserData };
        },
        onError: (error, variables, context) => {
            if (context?.previousNotifications) queryClient.setQueryData(['notifications'], context.previousNotifications);
            if (context?.previousUserData) queryClient.setQueryData(['user'], context.previousUserData);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
        },
    });
};

export const useMarkNotificationAsReadMutation = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['mark-notification-as-read'],
        mutationFn: (notificationId) => markNotificationAsReadFn(notificationId),
        onMutate: async () => {
            await queryClient.cancelQueries({ queryKey: ['notifications'] });
            await queryClient.cancelQueries({ queryKey: ['user']});

            const previousNotifications = queryClient.getQueryData(['notifications']);
            const previousUserData = queryClient.getQueryData(['user']);
            
            return { previousNotifications, previousUserData };
        },
        onError: (error, variables, context) => {
            if (context?.previousNotifications) queryClient.setQueryData(['notifications'], context.previousNotifications);
            if (context?.previousUserData) queryClient.setQueryData(['user'], context.previousUserData);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
        },
    });
};

export const useDeleteNotificationMutation = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['delete-notification'],
        mutationFn: (notificationId) => deleteNotificationFn(notificationId),
        onMutate: async () => {
            await queryClient.cancelQueries({ queryKey: ['notifications'] });
            await queryClient.cancelQueries({ queryKey: ['user']});

            const previousNotifications = queryClient.getQueryData(['notifications']);
            const previousUserData = queryClient.getQueryData(['user']);
            
            return { previousNotifications, previousUserData };
        },
        onError: (error, variables, context) => {
            if (context?.previousNotifications) queryClient.setQueryData(['notifications'], context.previousNotifications);
            if (context?.previousUserData) queryClient.setQueryData(['user'], context.previousUserData);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['user'] });
        },
    });
};

// =============================================================================
// SOCIAL / FOLLOW
// =============================================================================

export const useToggleFollowUserMutation = () => {
    const queryClient = useQueryClient();
    
    return useMutation({
        mutationKey: ['toggle-follow-user'],
        mutationFn: (userId) => toggleFollowUserFn(userId),
        onMutate: async (userId) => {
            await queryClient.cancelQueries({ queryKey: ['user'] });
            await queryClient.cancelQueries({ queryKey: ['other-user', userId] });

            const previousUser = queryClient.getQueryData(['user']);
            const previousOtherUser = queryClient.getQueryData(['other-user', userId]);

            return { previousUser, previousOtherUser };
        },
        onError: (error, userId, context) => {
            if (context?.previousUser) queryClient.setQueryData(['user'], context.previousUser);
            if (context?.previousOtherUser) queryClient.setQueryData(['other-user', userId], context.previousOtherUser);
        },
        onSettled: (data, error, userId) => {
            queryClient.invalidateQueries({ queryKey: ['user'] });
            queryClient.invalidateQueries({ queryKey: ['other-user', userId] });
        },
    });
};

// =============================================================================
// STORE
// =============================================================================

export const useCreateStoreMutation = (setError, setServerErrors, setServerMessage) => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    return useMutation({
        mutationKey: ['create-store'],
        mutationFn: (formData) => createStoreFn(formData),
        onMutate: async () => {
            await queryClient.cancelQueries({ queryKey: ['user'] });

            const previousUserData = queryClient.getQueryData(['user']);

            return { previousUserData }

        },
        onSuccess: () => {
            setServerMessage?.('Store created successfully!');
            setServerErrors?.([]);
            
            queryClient.invalidateQueries({ queryKey: ['user'] });
            
            setTimeout(() => navigate('/profile'), 1500);
        },
        onError: (error, variables, context) => {
            if (context.previousUserData) queryClient.getQueryData(['user'], context.previousUserData);

            handleFieldErrors(error, setError, setServerErrors)
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['user'] });
        },
    });
};
