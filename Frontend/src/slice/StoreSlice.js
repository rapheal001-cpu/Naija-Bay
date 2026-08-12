import { createSlice } from "@reduxjs/toolkit";


const StoreSlice = createSlice({
    name: 'store',
    initialState: {
        stores: [],
        storeDetail: null,
    },
    reducers: {
        setStores: (state, action) => {
            state.stores = action.payload
        },
        setStoreDetail: (state, action) => {
            state.storeDetail = action.payload
        },
    }
})

export const { setStores, setStoreDetail } = StoreSlice.actions
export default StoreSlice.reducer;