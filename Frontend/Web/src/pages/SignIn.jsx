import { useEffect } from "react";
import { useSelector } from "react-redux";
import { useNavigate, Link } from "react-router-dom";
import { HiOutlineArrowLeft } from "react-icons/hi";
import SignInForm from "../components/AuthComponents/SignInForm.jsx";

const SignIn = () => {
    const isAuthenticated = useSelector(state => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);

    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated || user) navigate("/");
    }, [isAuthenticated, user, navigate]);

    return (
        <div className="min-h-screen bg-linear-to-b from-gray-50 to-white relative overflow-hidden">
            {/* Decorative background blobs */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-brand/5 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
            <div className="absolute bottom-0 right-0 w-120 h-120 bg-brand/5 rounded-full blur-3xl translate-x-1/3 translate-y-1/3 pointer-events-none" />

            {/* Top bar */}
            <div className="absolute top-0 left-0 right-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16 sm:h-20">
                        <Link 
                            to="/" 
                            className="group flex items-center gap-2 text-gray-500 hover:text-gray-900 transition-colors"
                        >
                            <span className="flex items-center justify-center w-9 h-9 rounded-full bg-white border border-gray-200 group-hover:border-gray-300 group-hover:shadow-md transition-all shadow-sm">
                                <HiOutlineArrowLeft size={16} />
                            </span>
                            <span className="text-sm font-semibold hidden sm:inline">Back to home</span>
                        </Link>

                        <p className="text-sm text-gray-400">
                            New here?{' '}
                            <Link to="/register" className="text-brand font-bold hover:underline underline-offset-4">
                                Create account
                            </Link>
                        </p>
                    </div>
                </div>
            </div>

            {/* Form */}
            <div className="relative z-10 min-h-screen flex flex-col justify-center">
                <SignInForm />
            </div>
        </div>
    );
};

export default SignIn;