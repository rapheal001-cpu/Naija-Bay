import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { Provider } from 'react-redux'
import {persistor, store} from './store';
import {PersistGate} from "redux-persist/integration/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import '@/style.css'

// Urls
import Home from "@/pages/Home.jsx";
import NotFound from "@/pages/NotFound.jsx";
import ProductDetail from "@/pages/ProductDetail.jsx";
import Notifications from "@/pages/Notifications.jsx";
import Sell from "@/pages/Sell.jsx";
import Profile from "@/pages/Profile.jsx";
import SignIn from "@/pages/SignIn.jsx";
import Register from "@/pages/Register.jsx";
import EmailVerificationSent from "@/pages/EmailVerificationSent.jsx";
import ResendEmailVerification from '@/pages/ResendEmailVerification.jsx';
import About from '@/pages/About.jsx';
import Contact from '@/pages/Contact.jsx';
import Settings from '@/pages/Settings.jsx';
import UpdateProfile from '@/pages/UpdateProfile.jsx';
import ForgotPassword from '@/pages/ForgotPassword.jsx';
import ChangePassword from '@/pages/ChangePassword';
import Products from './pages/Products';
import NetworkError from "@/pages/NetworkError";
import EditProduct from './pages/EditProduct';


const router = createBrowserRouter([
    {
        path: "*",
        element: <NotFound />,
    },
    {
        path: '/network-error',
        element: <NetworkError />,
    },
    {
        path: '/sign-in',
        element: <SignIn />,
    },
    {
        path: '/register',
        element: <Register />,
    },
    {
        path: '/',
        element: <Home />,
    },
    {
        path: '/notifications',
        element: <Notifications />,
    },
    {
        path: '/sell',
        element: <Sell />,
    },
    {
        path: '/products',
        element: <Products />,
    },
    {
        path: '/product/detail/:product_slug',
        element: <ProductDetail />,
    },
    {
        path: '/product/:product_slug/edit',
        element: <EditProduct />,
    },
    {
        path: '/profile',
        element: <Profile />,
    },
    {
        path: '/profile/:id',
        element: <Profile />,
    },
    {
        path: '/email-verification-sent',
        element: <EmailVerificationSent />
    },
    {
        path: '/resend-email-verification',
        element: <ResendEmailVerification />
    },
    {
        path: '/about',
        element: <About />
    },
    {
        path: '/contact',
        element: <Contact />
    },
    {
        path: '/settings',
        element: <Settings />
    },
    {
        path: '/update-profile',
        element: <UpdateProfile />
    },
    {
        path: '/forgot-password',
        element: <ForgotPassword />
    },
    {
        path: '/change-password',
        element: <ChangePassword />
    },
])

const queryClient = new QueryClient();


createRoot(document.getElementById('root')).render(
    <QueryClientProvider client={queryClient}>
        <Provider store={store}>
            <PersistGate loading={null} persistor={persistor}>
                <RouterProvider router={router}/>
            </PersistGate>
        </Provider>
    </QueryClientProvider>
)
