import {createSlice} from "@reduxjs/toolkit";


const  AuthSlice = createSlice({
    name: "auth",
    initialState: {
        isAuthenticated: false,
    },
    reducers: {
        setIsAuthenticated: (state) => {
            state.isAuthenticated = true;
        },
        removeIsAuthenticated: (state) => {
            state.isAuthenticated = false;
        }
    }
})


export const { setIsAuthenticated, removeIsAuthenticated } = AuthSlice.actions;
export default AuthSlice.reducer;