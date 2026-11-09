import { useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
    HiOutlineHome, HiOutlineSearch, HiOutlineCollection, HiOutlineChatAlt2,
    HiOutlineBell, HiOutlineUser, HiOutlineCog, HiOutlineQuestionMarkCircle,
    HiOutlinePlusCircle,
} from 'react-icons/hi';
import { useFetchCategories, useFetchUnreadCounts } from '../../hooks/UseQuery.js';
import { setCategories } from '../../slice/CategorySlice.js';

/**
 * Desktop left sidebar — the marketplace's primary navigation.
 * (Mobile collapses to the header search + bottom nav; sidebar hidden.)
 */
const AppSidebar = () => {
    const categories = useSelector((state) => state.categories.categories) || [];
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const dispatch = useDispatch();
    const unread = useFetchUnreadCounts(isAuthenticated);
    const fetchCategories = useFetchCategories();

    useEffect(() => {
        if (fetchCategories.isSuccess && fetchCategories.data) {
            dispatch(setCategories(fetchCategories.data));
        }
    }, [fetchCategories.isSuccess, fetchCategories.data, dispatch]);

    const linkClass = ({ isActive: active }) =>
        `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-colors ${
            active ? 'bg-brand text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
        }`;

    const sectionLabel = (text) => (
        <p className="px-3.5 pb-1.5 pt-5 text-[10px] font-black uppercase tracking-[0.12em] text-gray-400 first:pt-0">
            {text}
        </p>
    );

    const badge = (count) =>
        count > 0 ? (
            <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-brand px-1.5 text-[10px] font-black text-white">
                {count > 9 ? '9+' : count}
            </span>
        ) : null;

    return (
        <nav aria-label="Sidebar" className="hidden lg:block sticky top-24 w-60 shrink-0 self-start">
            <div className="rounded-2xl border border-gray-100 bg-white p-3 shadow-sm">
                {sectionLabel('Marketplace')}
                <ul className="space-y-0.5">
                    <li><NavLink to="/" className={linkClass}><HiOutlineHome size={18} aria-hidden="true" /> Home</NavLink></li>
                    <li><NavLink to="/products" className={linkClass}><HiOutlineSearch size={18} aria-hidden="true" /> Browse Ads</NavLink></li>
                    <li><NavLink to="/sell" className={linkClass}><HiOutlinePlusCircle size={18} aria-hidden="true" /> Post a free ad</NavLink></li>
                </ul>

                {categories.length > 0 && (
                    <>
                        {sectionLabel('Categories')}
                        <ul className="space-y-0.5 max-h-52 overflow-y-auto pr-1 scrollbar-hide">
                            {categories.slice(0, 8).map((category) => (
                                <li key={category.slug}>
                                    <NavLink to={`/${category.slug}`} className={linkClass}>
                                        {category.name}
                                    </NavLink>
                                </li>
                            ))}
                        </ul>
                    </>
                )}

                {isAuthenticated && (
                    <>
                        {sectionLabel('Your account')}
                        <ul className="space-y-0.5">
                            <li><NavLink to="/my-ads" className={linkClass}><HiOutlineCollection size={18} aria-hidden="true" /> My Ads</NavLink></li>
                            <li>
                                <NavLink to="/messages" className={linkClass}>
                                    <HiOutlineChatAlt2 size={18} aria-hidden="true" /> Messages
                                    {badge(unread.data?.unread_messages ?? 0)}
                                </NavLink>
                            </li>
                            <li>
                                <NavLink to="/notifications" className={linkClass}>
                                    <HiOutlineBell size={18} aria-hidden="true" /> Notifications
                                    {badge(unread.data?.unread_notifications ?? 0)}
                                </NavLink>
                            </li>
                            <li><NavLink to="/profile" className={linkClass}><HiOutlineUser size={18} aria-hidden="true" /> Profile</NavLink></li>
                            <li><NavLink to="/settings" className={linkClass}><HiOutlineCog size={18} aria-hidden="true" /> Settings</NavLink></li>
                        </ul>
                    </>
                )}

                {sectionLabel('Support')}
                <ul className="space-y-0.5">
                    <li><NavLink to="/about" className={linkClass}><HiOutlineQuestionMarkCircle size={18} aria-hidden="true" /> About & help</NavLink></li>
                </ul>
            </div>
        </nav>
    );
};

export default AppSidebar;
