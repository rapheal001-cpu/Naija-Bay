import { configureStore, combineReducers } from '@reduxjs/toolkit'
import { persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from "redux-persist";
import storage from "redux-persist/lib/storage";
import expireReducer from 'redux-persist-expire';

import AuthReducer from '@/slice/AuthSlice.js'
import UserReducer from '@/slice/UserSlice.js'
import CategoryReducer from '@/slice/CategorySlice.js'
import NotificationReducer from '@/slice/NotificationSlice.js'
import ProductReducer from '@/slice/ProductSlice.js'
import StoreReducer from '@/slice/StoreSlice.js';

const rootReducer = combineReducers({
    auth: AuthReducer,
    user: UserReducer,
    categories: CategoryReducer,
    notifications: NotificationReducer,
    products: ProductReducer,
    store: StoreReducer,
})

const persistedConfig = {
    key: 'root',
    storage,
    whitelist: ['auth', 'user', 'notifications', 'categories', 'products', 'store'],
    
    transforms: [
        // This timer handles the 'categories' reducer
        expireReducer('categories', {
            expireSeconds: 24 * 60 * 60, // 24 hours
            expiredState: { categories: [], subCategories: [] },
            autoExpire: true
        }),
        // This timer handles the 'products' reducer
        expireReducer('products', {
            expireSeconds: 24 * 60 * 60, // 24 hours
            expiredState: { products: [], featuredProducts: [], productDetail: {} },
            autoExpire: true
        }),
        // This timer handles the 'store' reducer
        expireReducer('store', {
            expireSeconds: 24 * 60 * 60, // 24 hours
            expiredState: { stores: [], storeDetail: {} }, 
            autoExpire: true
        }),
        // This timer handles the 'user' reducer
        expireReducer('user', {
            expireSeconds: 24 * 60 * 60, // 24 hours
            expiredState: { user: {}, otherUser: {} }, 
            autoExpire: true
        }),
        // This timer handles the 'notifications' reducer
        expireReducer('notifications', {
            expireSeconds: 24 * 60 * 60, // 24 hours
            expiredState: { notifications: [] }, 
            autoExpire: true
        })
    ]
}

const persistedReducer = persistReducer(persistedConfig, rootReducer);

export const store = configureStore({
    reducer: persistedReducer,
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
            },
            immutableCheck: {
                warnAfter: 100,
            },
        })
})

export const persistor = persistStore(store)
