import { useEffect } from 'react';
import { LuCheckCheck, LuTrash2, LuBell, LuInbox } from 'react-icons/lu';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';
import NotificationCard from '../components/UserComponents/NotificationCard.jsx';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import SkeletonNotificationCard from '../skeletons/SkeletonNotificationCard.jsx';
import { useFetchUserNotifications } from '../hooks/UseQuery.js';
import { 
    useMarkAllNotificationsAsReadMutation,
    useDeleteAllNotificationsMutation 
} from '../hooks/UseMutation.js';
import { setNotificatons } from '../slice/NotificationSlice.js';


const Notifications = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const notifications = useSelector((state) => state.notifications.notifications);
    const user = useSelector((state) => state.user.user);

    const unreadCount = notifications.filter((notification) => !notification.read).length;
    const hasNotifications = notifications.length > 0;

    const navigate = useNavigate();
    const dispatch = useDispatch();

    const notificationData = useFetchUserNotifications(isAuthenticated);
    const markAllAsReadMutation = useMarkAllNotificationsAsReadMutation();
    const deleteAllNotificationsMutation = useDeleteAllNotificationsMutation();

    useEffect(() => {
        if (!isAuthenticated && !user) {
            navigate('/sign-in');
            return;
        }

        if (notificationData.isSuccess && notificationData.data) {
            dispatch(setNotificatons(notificationData.data));
        }
    }, [isAuthenticated, user, navigate, dispatch, notificationData.isSuccess, notificationData.data]);

    return (
        <>
            <Header />
            <Spacer />

            <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-brand/10 text-brand">
                            <LuBell size={20} strokeWidth={2} />
                        </div>
                        <div>
                            <h1 className="text-2xl font-black text-gray-900 tracking-tight">
                                Notifications
                            </h1>
                            <p className="text-sm text-gray-500 mt-0.5">
                                {unreadCount > 0 
                                    ? `You have ${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}` 
                                    : 'All caught up!'}
                            </p>
                        </div>
                    </div>

                    {hasNotifications && (
                        <div className="flex items-center gap-2">
                            {unreadCount > 0 && (
                                <button
                                    type="button"
                                    onClick={() => markAllAsReadMutation.mutate()}
                                    disabled={markAllAsReadMutation.isPending}
                                    className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold text-brand bg-brand/10 hover:bg-brand/15 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    <LuCheckCheck size={16} strokeWidth={2.5} />
                                    {markAllAsReadMutation.isPending ? 'Marking...' : 'Mark all read'}
                                </button>
                            )}

                            <button
                                type="button"
                                onClick={() => deleteAllNotificationsMutation.mutate()}
                                disabled={deleteAllNotificationsMutation.isPending}
                                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold text-red-600 bg-red-50 hover:bg-red-100 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <LuTrash2 size={16} strokeWidth={2} />
                                {deleteAllNotificationsMutation.isPending ? 'Deleting...' : 'Clear all'}
                            </button>
                        </div>
                    )}
                </div>

                {/* Content */}
                <div className="min-h-[40vh]">
                    {notificationData.isLoading ? (
                        <div className="space-y-3">
                            <SkeletonNotificationCard />
                        </div>
                    ) : notifications.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20 text-center">
                            <div className="w-20 h-20 rounded-2xl bg-gray-50 flex items-center justify-center mb-5">
                                <LuInbox size={32} className="text-gray-300" strokeWidth={1.5} />
                            </div>
                            <h3 className="text-lg font-bold text-gray-900">No notifications yet</h3>
                            <p className="text-sm text-gray-400 mt-1.5 max-w-xs">
                                When you get notifications about your listings, messages, or account activity, they'll show up here.
                            </p>
                        </div>
                    ) : (
                        <NotificationCard notifications={notifications} />
                    )}
                </div>
            </div>
        </>
    );
};

export default Notifications;