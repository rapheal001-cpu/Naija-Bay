import { configureStore, combineReducers } from '@reduxjs/toolkit'
import {persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER} from "redux-persist";
import storage from "redux-persist/es/storage";
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
    whiswhitelist: ['auth', 'user', 'notifications', 'categories', 'products', 'store'],
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