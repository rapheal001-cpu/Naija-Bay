import { Link, useNavigate } from 'react-router-dom';
import { HiOutlineUserCircle } from 'react-icons/hi';
import { FaArrowLeft } from 'react-icons/fa';

const ProfileNotFound = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-[60vh] flex items-center justify-center px-4 py-16 bg-gray-50/30">
            <div className="max-w-sm w-full text-center">
                {/* Illustration */}
                <div className="relative mx-auto w-36 h-36 mb-8">
                    <div className="absolute inset-0 bg-brand/5 rounded-full animate-pulse" />
                    <div className="relative w-full h-full rounded-3xl bg-white border border-gray-100 shadow-sm flex items-center justify-center">
                        <svg
                            className="w-16 h-16 text-gray-300"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                            <circle cx="12" cy="7" r="4" />
                            <line x1="4" y1="4" x2="20" y2="20" />
                        </svg>
                    </div>
                    {/* Floating badge */}
                    <div className="absolute -top-1 -right-1 w-9 h-9 bg-brand text-white rounded-xl flex items-center justify-center shadow-lg shadow-brand/20">
                        <span className="text-sm font-bold">?</span>
                    </div>
                </div>

                {/* Text content */}
                <h1 className="text-xl font-bold text-gray-900 tracking-tight">
                    User not found
                </h1>
                <p className="mt-2 text-sm text-gray-500 leading-relaxed px-2">
                    This profile doesn't exist, may have been removed, or the username might be misspelled.
                </p>

                {/* Action buttons */}
                <div className="mt-7 flex flex-col sm:flex-row items-center justify-center gap-3">
                    <button
                        onClick={() => navigate(-1)}
                        className="w-full sm:w-auto flex items-center justify-center gap-2 bg-brand text-white font-semibold text-sm rounded-xl px-5 py-2.5 hover:bg-brand/90 active:scale-[0.98] transition-all shadow-sm shadow-brand/20"
                    >
                        <FaArrowLeft className="w-3.5 h-3.5" />
                        Go Back
                    </button>

                    <Link
                        to="/"
                        className="w-full sm:w-auto flex items-center justify-center gap-2 bg-white text-gray-700 font-semibold text-sm rounded-xl px-5 py-2.5 border border-gray-200 hover:bg-gray-50 hover:border-gray-300 active:scale-[0.98] transition-all"
                    >
                        <HiOutlineUserCircle className="w-4 h-4 text-gray-400" />
                        Back to home
                    </Link>
                </div>

                {/* Subtle help text */}
                <p className="mt-6 text-[11px] text-gray-400 font-medium">
                    If you believe this is an error, please contact support.
                </p>
            </div>
        </div>
    );
};

export default ProfileNotFound;