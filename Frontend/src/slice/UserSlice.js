import { createSlice } from '@reduxjs/toolkit'


const UserSlice = createSlice({
    name: 'user',
    initialState: {
        user: null,
        otherUser: null,
    },
    reducers: {
        setUser: (state, action) => {
            state.user = action.payload
        },
        setOtherUser: (state, action) => {
            state.otherUser = action.payload
        },
        removeOtherUser: (state) => {
            state.otherUser = null
        },
        removeUserData: (state) => {
            state.user = null,
            state.otherUser = null
        }
    }
})


export const { setUser, setOtherUser, removeOtherUser, removeUserData } = UserSlice.actions;
export default UserSlice.reducer