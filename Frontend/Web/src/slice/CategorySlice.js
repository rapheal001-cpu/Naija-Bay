  import { createSlice } from "@reduxjs/toolkit";

  
export const CategorySlice = createSlice({
    name: "categories",
    initialState: {
        categories: [],
        subCategories: [],
    },
    reducers: {
        setCategories: (state, action) => {
            state.categories = action.payload;
        },
        setSubCategories: (state, action) => {
            state.subCategories = action.payload;
        },
    }
})

export const { setCategories, setSubCategories } = CategorySlice.actions
export default CategorySlice.reducer;