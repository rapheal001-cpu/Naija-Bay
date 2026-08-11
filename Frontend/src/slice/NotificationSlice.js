import {createSlice} from "@reduxjs/toolkit";


const NotificationSlice = createSlice({
    name: "notifications",
    initialState: {
        notifications: [],
    },
    reducers: {
        setNotificatons: (state, action) => {
            state.notifications = action.payload;
        }
    }
})

export const { setNotificatons } = NotificationSlice.actions;
export default NotificationSlice.reducer;