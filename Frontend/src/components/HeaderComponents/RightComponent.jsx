import { useState, useRef, useEffect } from 'react';
import { NavLink } from "react-router-dom";
import { FaSignalMessenger, FaCircleInfo } from "react-icons/fa6";
import { GoBellFill } from "react-icons/go";
import { FaUserAlt, FaShoppingCart, FaPhoneAlt, FaChevronDown, FaChevronUp } from "react-icons/fa";
import { RiLogoutCircleRLine } from "react-icons/ri";
import { FiMenu, FiX } from "react-icons/fi";
import { useLogoutMutation } from '@/hooks/UseMutation.js';
import { useSelector } from 'react-redux';

const RightComponent = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);

    const [toggleProfile, setToggleProfile] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const menuRef = useRef(null);
    const mobileMenuRef = useRef(null);

    const logoutUser = useLogoutMutation();

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (menuRef.current && !menuRef.current.contains(e.target)) {
                setToggleProfile(false);
            }
            if (mobileMenuRef.current && !mobileMenuRef.current.contains(e.target)) {
                setMobileMenuOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const navLinkClass = "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-white/90 hover:text-white hover:bg-white/10 transition-all duration-200";

    const dropdownItem = "flex items-center gap-3 px-4 py-2.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors";

    return (
        <>
            {/* Desktop */}
            <div className="hidden lg:flex items-center gap-1">
                {/* About — visible to everyone */}
                <NavLink to="/about" className={navLinkClass}>
                    <FaCircleInfo size={16} />
                    <span>About</span>
                </NavLink>

                {isAuthenticated ? (
                    <div className="relative flex items-center gap-0.5" ref={menuRef}>
                        <NavLink to="/message-list" className={navLinkClass}>
                            <FaSignalMessenger size={17} />
                            <span>Messages</span>
                        </NavLink>

                        <NavLink to="/notifications" className={navLinkClass}>
                            <GoBellFill size={17} />
                            <span>Notifications</span>
                        </NavLink>

                        <button
                            type="button"
                            onClick={() => setToggleProfile(prev => !prev)}
                            className={`flex items-center gap-2.5 pl-2 pr-3 py-1 rounded-full transition-all duration-200 ${toggleProfile ? 'bg-white/15' : 'hover:bg-white/10'}`}
                        >
                            <img
                                src={user?.avatar}
                                alt={user?.username || 'User'}
                                className="w-9 h-9 rounded-full border-2 border-white/70 object-cover bg-gray-200"
                            />
                            <span className='font-semibold text-sm text-white max-w-25 truncate'>
                                {user?.username || user?.email || 'User'}
                            </span>
                            {toggleProfile 
                                ? <FaChevronUp size={13} className="text-white/70" /> 
                                : <FaChevronDown size={13} className="text-white/70" />
                            }
                        </button>

                        {toggleProfile && (
                            <div className="absolute right-0 top-full mt-3 w-64 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden z-50">
                                <div className="px-4 py-3.5 bg-gray-50/50 border-b border-gray-100">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-brand/10 flex items-center justify-center text-brand font-bold text-lg shrink-0">
                                            {user?.username ? user.username.charAt(0).toUpperCase() : 'U'}
                                        </div>
                                        <div className="min-w-0">
                                            <p className="text-sm font-bold text-gray-900 truncate">
                                                {user?.username || 'User'}
                                            </p>
                                            <p className="text-xs text-gray-500 truncate">
                                                {user?.email || ''}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="py-1">
                                    <NavLink to="/profile" onClick={() => setToggleProfile(false)} className={dropdownItem}>
                                        <FaUserAlt size={15} className="text-gray-400" /> Profile
                                    </NavLink>
                                    <NavLink to="/sell" onClick={() => setToggleProfile(false)} className={dropdownItem}>
                                        <FaShoppingCart size={15} className="text-gray-400" /> Sell
                                    </NavLink>
                                </div>

                                <div className="border-t border-gray-100 py-1">
                                    <NavLink to="/contact" onClick={() => setToggleProfile(false)} className={dropdownItem}>
                                        <FaPhoneAlt size={15} className="text-gray-400" /> Contact us
                                    </NavLink>
                                </div>

                                <div className="border-t border-gray-100 py-1">
                                    <button 
                                        onClick={() => logoutUser.mutate(null)} 
                                        className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                                    >
                                        <RiLogoutCircleRLine size={15} /> Logout
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="flex items-center gap-2.5 ml-1">
                        <NavLink
                            to="/sign-in"
                            className={({ isActive }) =>
                                isActive
                                    ? "px-5 py-2 rounded-full bg-white text-brand text-sm font-bold shadow-md transition-all"
                                    : "px-5 py-2 rounded-full text-white text-sm font-semibold hover:bg-white/15 transition-colors"
                            }
                        >
                            Sign in
                        </NavLink>
                        <NavLink
                            to="/register"
                            className={({ isActive }) =>
                                isActive
                                    ? "px-5 py-2 rounded-full bg-white text-brand text-sm font-bold shadow-md transition-all"
                                    : "px-5 py-2 rounded-full border border-white/40 text-white text-sm font-semibold hover:bg-white/15 transition-colors"
                            }
                        >
                            Register
                        </NavLink>
                    </div>
                )}
            </div>

            {/* Mobile */}
            <div className="lg:hidden relative" ref={mobileMenuRef}>
                <button
                    type="button"
                    aria-label="Toggle menu"
                    onClick={() => setMobileMenuOpen(prev => !prev)}
                    className={`text-white p-2 rounded-lg transition-colors ${mobileMenuOpen ? 'bg-white/20' : 'hover:bg-white/10'}`}
                >
                    {mobileMenuOpen ? <FiX size={22} /> : <FiMenu size={22} />}
                </button>

                {mobileMenuOpen && (
                    <div className="absolute right-0 top-full mt-3 w-72 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden z-50">
                        {/* About — visible to everyone */}
                        <div className="py-1">
                            <NavLink to="/about" onClick={() => setMobileMenuOpen(false)} className={dropdownItem}>
                                <FaCircleInfo size={15} className="text-gray-400" /> About
                            </NavLink>
                        </div>

                        {isAuthenticated ? (
                            <>
                                <div className="px-5 py-4 bg-gray-50/50 border-b border-gray-100">
                                    <div className="flex items-center gap-3">
                                        <img
                                            src={user?.avatar}
                                            alt={user?.username || 'User'}
                                            className="w-11 h-11 rounded-full border-2 border-white object-cover bg-gray-200 shadow-sm"
                                        />
                                        <div className="min-w-0">
                                            <p className="text-sm font-bold text-gray-900 truncate">
                                                {user?.username || 'User'}
                                            </p>
                                            <p className="text-xs text-gray-500 truncate">
                                                {user?.email || ''}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="py-1">
                                    <NavLink to="/profile" onClick={() => setMobileMenuOpen(false)} className={dropdownItem}>
                                        <FaUserAlt size={15} className="text-gray-400" /> Profile
                                    </NavLink>
                                    <NavLink to="/sell" onClick={() => setMobileMenuOpen(false)} className={dropdownItem}>
                                        <FaShoppingCart size={15} className="text-gray-400" /> Sell
                                    </NavLink>
                                </div>

                                <div className="border-t border-gray-100 py-1">
                                    <NavLink to="/message-list" onClick={() => setMobileMenuOpen(false)} className={dropdownItem}>
                                        <FaSignalMessenger size={15} className="text-gray-400" /> Messages
                                    </NavLink>
                                    <NavLink to="/notifications" onClick={() => setMobileMenuOpen(false)} className={dropdownItem}>
                                        <GoBellFill size={15} className="text-gray-400" /> Notifications
                                    </NavLink>
                                </div>

                                <div className="border-t border-gray-100 py-1">
                                    <NavLink to="/contact" onClick={() => setMobileMenuOpen(false)} className={dropdownItem}>
                                        <FaPhoneAlt size={15} className="text-gray-400" /> Contact us
                                    </NavLink>
                                </div>

                                <div className="border-t border-gray-100 py-1">
                                    <button 
                                        onClick={() => logoutUser.mutate(null)} 
                                        className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                                    >
                                        <RiLogoutCircleRLine size={15} /> Logout
                                    </button>
                                </div>
                            </>
                        ) : (
                            <div className="p-4 space-y-2 border-t border-gray-100">
                                <NavLink
                                    to="/sign-in"
                                    onClick={() => setMobileMenuOpen(false)}
                                    className="block w-full text-center px-4 py-2.5 rounded-xl bg-brand text-white font-semibold hover:opacity-90 transition-opacity"
                                >
                                    Sign in
                                </NavLink>
                                <NavLink
                                    to="/register"
                                    onClick={() => setMobileMenuOpen(false)}
                                    className="block w-full text-center px-4 py-2.5 rounded-xl border-2 border-gray-200 text-gray-700 font-semibold hover:border-brand hover:text-brand transition-colors"
                                >
                                    Create account
                                </NavLink>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </>
    );
};

export default RightComponent;