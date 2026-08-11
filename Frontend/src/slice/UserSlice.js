import { createSlice } from '@reduxjs/toolkit'


const UserSlice = createSlice({
    name: 'user',
    initialState: {
        user: {},
        otherUser: {},
    },
    reducers: {
        setUser: (state, action) => {
            state.user = action.payload
        },
        setOtherUser: (state, action) => {
            state.otherUser = action.payload
        },
        removeOtherUser: (state) => {
            state.otherUser = {}
        },
        removeUserData: (state) => {
            state.user = {},
            state.otherUser = {}
        }
    }
})


export const { setUser, setOtherUser, removeOtherUser, removeUserData } = UserSlice.actions;
export default UserSlice.reducer