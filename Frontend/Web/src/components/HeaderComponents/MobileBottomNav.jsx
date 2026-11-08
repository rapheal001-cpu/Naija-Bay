import { NavLink, useNavigate } from 'react-router-dom';
import { HiOutlineHome, HiOutlineSearch, HiOutlinePlusCircle, HiOutlineChatAlt2, HiOutlineCollection } from 'react-icons/hi';
import { useSelector } from 'react-redux';
import { useFetchUnreadCounts } from '../../hooks/UseQuery.js';

/**
 * Mobile-first bottom navigation (shown below the lg breakpoint).
 * Unread message/notification badges come from the existing messaging API.
 */
const MobileBottomNav = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const unread = useFetchUnreadCounts(isAuthenticated);
    const navigate = useNavigate();

    const itemClass = ({ isActive }) =>
        `relative flex min-h-14 flex-col items-center justify-center gap-0.5 text-[10px] font-bold transition-colors ${
            isActive ? 'text-brand' : 'text-gray-500'
        }`;

    const badge = (count) =>
        count > 0 && (
            <span className="absolute right-1/2 translate-x-6 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-brand px-1 text-[9px] font-black text-white">
                {count > 9 ? '9+' : count}
            </span>
        );

    const unreadMessages = unread.data?.unread_messages ?? 0;
    const unreadNotifications = unread.data?.unread_notifications ?? 0;

    return (
        <nav
            aria-label="Mobile"
            className="fixed inset-x-0 bottom-0 z-40 border-t border-gray-100 bg-white/95 backdrop-blur lg:hidden"
            style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
        >
            <div className="grid grid-cols-5">
                <NavLink to="/" className={itemClass}>
                    <HiOutlineHome size={22} aria-hidden="true" />
                    Home
                </NavLink>
                <NavLink to="/products" className={itemClass}>
                    <HiOutlineSearch size={22} aria-hidden="true" />
                    Search
                </NavLink>
                <button
                    type="button"
                    onClick={() => navigate(isAuthenticated ? '/sell' : '/sign-in')}
                    className="flex min-h-14 flex-col items-center justify-center gap-0.5 text-[10px] font-bold text-brand"
                >
                    <HiOutlinePlusCircle size={26} aria-hidden="true" />
                    Post Ad
                </button>
                <NavLink to="/messages" className={itemClass}>
                    <span className="relative">
                        <HiOutlineChatAlt2 size={22} aria-hidden="true" />
                        {badge(unreadMessages)}
                    </span>
                    Messages
                </NavLink>
                <NavLink to="/my-ads" className={itemClass}>
                    <span className="relative">
                        <HiOutlineCollection size={22} aria-hidden="true" />
                        {badge(unreadNotifications)}
                    </span>
                    My Ads
                </NavLink>
            </div>
        </nav>
    );
};

export default MobileBottomNav;
