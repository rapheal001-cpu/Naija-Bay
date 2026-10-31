import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
    HiOutlineUserCircle,
    HiOutlineLockClosed,
    HiChevronRight,
} from 'react-icons/hi';
import { HiOutlineArrowLeft } from 'react-icons/hi2';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';

const SETTINGS_ITEMS = [
    {
        to: '/update-profile',
        icon: HiOutlineUserCircle,
        title: 'Update profile',
        description: 'Change your name, contact information, address, and avatar.',
        highlight: false,
        color: 'text-blue-600',
        bg: 'bg-blue-50',
        border: 'border-blue-100',
    },
    {
        to: '/change-password',
        icon: HiOutlineLockClosed,
        title: 'Change password',
        description: 'Update your password to keep your account secure.',
        highlight: false,
        color: 'text-gray-600',
        bg: 'bg-gray-100',
        border: 'border-gray-200',
    },
];

const Settings = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const navigate = useNavigate();

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/sign-in', { replace: true });
        }
    }, [isAuthenticated, navigate]);

    // Prevent flash of settings UI while redirecting or if auth is unknown
    if (!isAuthenticated) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
            </div>
        );
    }

    return (
        <>
            <Header />
            <Spacer space="mb-20" />

            <div className="min-h-[85vh] bg-linear-to-b from-gray-50 to-white py-10">
                <div className="max-w-2xl mx-auto px-4 sm:px-6">

                    {/* Back link */}
                    <Link
                        to="/profile"
                        className="group inline-flex items-center gap-2 text-sm font-semibold text-gray-500 hover:text-gray-900 transition-colors mb-6"
                    >
                        <span className="flex items-center justify-center w-8 h-8 rounded-full bg-white border border-gray-200 group-hover:border-gray-300 group-hover:shadow-sm transition-all">
                            <HiOutlineArrowLeft size={16} />
                        </span>
                        Back to profile
                    </Link>

                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-3xl font-black text-gray-900 tracking-tight">
                            Settings
                        </h1>
                        <p className="text-sm text-gray-500 mt-2 leading-relaxed">
                            Manage your account, security, and seller details.
                        </p>
                    </div>

                    {/* Settings List */}
                    <div className="bg-white rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100 overflow-hidden divide-y divide-gray-50">
                        {SETTINGS_ITEMS.map((item) => {
                            const { to, icon: Icon, title, description, highlight, color, bg, border } = item;

                            return (
                                <Link
                                    key={to}
                                    to={to}
                                    className="group flex items-center gap-4 sm:gap-5 p-5 sm:p-6 hover:bg-gray-50/80 transition-all duration-200"
                                >
                                    <span
                                        className={`
                                            w-12 h-12 shrink-0 rounded-2xl flex items-center justify-center border transition-transform duration-200 group-hover:scale-105
                                            ${bg} ${color} ${border}
                                        `}
                                    >
                                        <Icon size={22} strokeWidth={1.5} />
                                    </span>

                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 flex-wrap">
                                            <p className="font-bold text-gray-900 text-[15px]">{title}</p>
                                            {highlight && (
                                                <span className="text-[10px] font-bold text-amber-700 bg-amber-100 border border-amber-200 px-2 py-0.5 rounded-full uppercase tracking-wider">
                                                    Recommended
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-sm text-gray-500 mt-1 leading-relaxed">{description}</p>
                                    </div>

                                    <span className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-50 text-gray-300 group-hover:bg-white group-hover:text-brand group-hover:shadow-sm transition-all">
                                        <HiChevronRight size={18} />
                                    </span>
                                </Link>
                            );
                        })}
                    </div>

                    {/* Footer hint */}
                    <p className="text-center text-xs text-gray-400 mt-8">
                        Need help? Contact our support team for assistance.
                    </p>

                </div>
            </div>
        </>
    );
};

export default Settings;