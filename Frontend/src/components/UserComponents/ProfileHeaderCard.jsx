import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { useState } from 'react';
import { HiBadgeCheck } from "react-icons/hi";
import { FaBell, FaUserPlus, FaUserCheck, FaMapMarkerAlt, FaCalendarAlt, FaClock, FaStore } from "react-icons/fa";
import { IoSettingsOutline } from "react-icons/io5";
import { useToggleFollowUserMutation } from '../../hooks/UseMutation';
import { formatJoinDate, formatLastLogin } from "../../dummyData";

const ProfileHeaderCard = ({ profile, isOwnProfile }) => {
    const currentUser = useSelector((state) => state.user.user);
    const toggleFollowUser = useToggleFollowUserMutation();
    const [hoverUnfollow, setHoverUnfollow] = useState(false);

    const isFollowing = profile?.followers?.some(
        (follower) => follower.id === currentUser?.id
    ) ?? false;

    const unreadCount = profile?.unread_notifications ?? 0;
    const unreadDisplay = unreadCount > 9 ? '9+' : unreadCount;

    const followersCount = profile?.followers_count ?? profile?.followers?.length ?? 0;
    const followingCount = profile?.following_count ?? profile?.following?.length ?? 0;
    const listingsCount = profile?.products?.length ?? 0;

    const avatarUrl = profile?.avatar || '/default-avatar.png';
    const fullName = profile?.full_name || '';
    const username = profile?.username || '';
    const isVerified = profile?.verified ?? false;
    const hasStore = profile?.has_store ?? false;

    return (
        <div className="relative bg-white border border-gray-100 rounded-3xl shadow-sm overflow-hidden">
            {/* Cover */}
            <div className="h-28 sm:h-36 bg-linear-to-r from-brand to-brand/80 relative">
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4xKSIvPjwvc3ZnPg==')] opacity-30" />
            </div>

            <div className="px-5 sm:px-8 pb-6 sm:pb-8">
                {/* Avatar + Info + Actions Row */}
                <div className="flex flex-col sm:flex-row sm:items-end gap-4 -mt-12 sm:-mt-14">
                    {/* Avatar */}
                    <div className="relative shrink-0">
                        <img
                            src={avatarUrl}
                            alt={fullName}
                            className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl object-cover border-4 border-white shadow-lg bg-gray-100"
                        />
                        {isVerified && (
                            <span className="absolute -bottom-1.5 -right-1.5 bg-emerald-500 text-white rounded-full p-1 border-2 border-white shadow-sm">
                                <HiBadgeCheck size={16} />
                            </span>
                        )}
                    </div>

                    {/* Name & Username */}
                    <div className="flex-1 min-w-0 sm:pb-1">
                        <h1 className="text-xl sm:text-2xl font-black text-gray-900 tracking-tight truncate">
                            {fullName}
                        </h1>
                        <p className="text-sm text-gray-400 font-medium mt-0.5">
                            @{username}
                        </p>
                    </div>

                    {/* Actions */}
                    {isOwnProfile ? (
                        <div className="flex items-center gap-2 sm:pb-1 flex-wrap justify-end">
                            {/* Only verified users can create a store, and only if they don't already have one */}
                            {isVerified && (
                                hasStore ? (
                                    <Link
                                        to="/my-store"
                                        className="flex items-center justify-center gap-2 font-semibold rounded-xl px-5 py-2.5 text-sm active:scale-95 transition-all shadow-sm min-w-30 bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200"
                                    >
                                        <FaStore size={14} />
                                        My Store
                                    </Link>
                                ) : (
                                    <Link
                                        to="/create-store"
                                        className="flex items-center justify-center gap-2 font-semibold rounded-xl px-5 py-2.5 text-sm active:scale-95 transition-all shadow-sm min-w-30 bg-brand text-white hover:opacity-90 shadow-brand/20"
                                    >
                                        <FaStore size={14} />
                                        Create Store
                                    </Link>
                                )
                            )}

                            <Link
                                to="/notifications"
                                aria-label="Notifications"
                                className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-all"
                            >
                                <FaBell size={16} />
                                {unreadCount >= 1 && (
                                    <span className="absolute -top-1.5 -right-1.5 flex items-center justify-center min-w-4.5 h-4.5 px-1 rounded-full bg-red-500 text-white text-[10px] font-bold border-2 border-white">
                                        {unreadDisplay}
                                    </span>
                                )}
                            </Link>

                            <Link
                                to="/settings"
                                aria-label="Settings"
                                className="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-all"
                            >
                                <IoSettingsOutline size={17} />
                            </Link>
                        </div>
                    ) : (
                        <div className="flex items-center gap-2 sm:pb-1">
                            <button
                                type="button"
                                onClick={() => toggleFollowUser.mutate(profile.id)}
                                disabled={toggleFollowUser.isPending}
                                onMouseEnter={() => isFollowing && setHoverUnfollow(true)}
                                onMouseLeave={() => setHoverUnfollow(false)}
                                className={`
                                    flex items-center justify-center gap-2 font-semibold rounded-xl px-5 py-2.5 text-sm 
                                    active:scale-95 transition-all shadow-sm min-w-30
                                    ${isFollowing
                                        ? 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-red-50 hover:text-red-600 hover:border-red-200'
                                        : 'bg-brand text-white hover:opacity-90 shadow-brand/20'
                                    }
                                    ${toggleFollowUser.isPending ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}
                                `}
                            >
                                {toggleFollowUser.isPending ? (
                                    <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                                ) : isFollowing ? (
                                    <>
                                        {hoverUnfollow ? (
                                            <>
                                                <FaUserPlus size={14} className="rotate-45" />
                                                Unfollow
                                            </>
                                        ) : (
                                            <>
                                                <FaUserCheck size={14} />
                                                Following
                                            </>
                                        )}
                                    </>
                                ) : (
                                    <>
                                        <FaUserPlus size={14} />
                                        Follow
                                    </>
                                )}
                            </button>
                        </div>
                    )}
                </div>

                {/* Meta Row */}
                <div className="flex flex-wrap items-center gap-2 mt-5">
                    {(profile?.state || profile?.address) && (
                        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-100">
                            <FaMapMarkerAlt size={11} className="text-gray-400" />
                            {profile?.address ? `${profile.address}, ` : ''}{profile?.state}
                        </span>
                    )}
                    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-100">
                        <FaCalendarAlt size={11} className="text-gray-400" />
                        Joined {formatJoinDate(profile?.date_joined)}
                    </span>
                    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-100">
                        <FaClock size={11} className="text-gray-400" />
                        Last login {formatLastLogin(profile?.last_login)}
                    </span>
                </div>

                {/* Social Stats */}
                <div className="flex items-center gap-6 mt-5 pt-5 border-t border-gray-100">
                    <div className="text-center sm:text-left">
                        <p className="text-lg font-black text-gray-900">{followersCount.toLocaleString()}</p>
                        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Followers</p>
                    </div>
                    <div className="w-px h-8 bg-gray-100" />
                    <div className="text-center sm:text-left">
                        <p className="text-lg font-black text-gray-900">{followingCount.toLocaleString()}</p>
                        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Following</p>
                    </div>
                    <div className="w-px h-8 bg-gray-100" />
                    <div className="text-center sm:text-left">
                        <p className="text-lg font-black text-gray-900">{listingsCount.toLocaleString()}</p>
                        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Listings</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfileHeaderCard;