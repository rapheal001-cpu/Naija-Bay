import {createSlice} from "@reduxjs/toolkit";


const ProductSlice = createSlice({
    name: 'products',
    initialState: {
        products: [],
        featuredProducts: [],
        productDetail: {},
    },
    reducers: {
        setProducts: (state, action) => {
            state.products = action.payload;
        },
        setFeaturedProducts: (state, action) => {
            state.featuredProducts = action.payload;
        },
        setProductDetail: (state, action) => {
            state.productDetail = action.payload;
        }
    }
})

export const { setProducts, setFeaturedProducts, setProductDetail } = ProductSlice.actions;
export default ProductSlice.reducer;