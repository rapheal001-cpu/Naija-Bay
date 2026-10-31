import { HiOutlineTrash } from 'react-icons/hi';
import { timeAgo, typeConfig, typeLabels } from "../../dummyData";
import { useMarkNotificationAsReadMutation, useDeleteNotificationMutation } from '../../hooks/UseMutation';

const NotificationCard = ({ notifications }) => {
    const markNotificationAsRead = useMarkNotificationAsReadMutation();
    const deleteNotification = useDeleteNotificationMutation();

    const markAsRead = (e, notification_id) => {
        e.preventDefault();
        e.stopPropagation();
        markNotificationAsRead.mutate(notification_id);
    };

    const handleDelete = (e, notification_id) => {
        e.preventDefault();
        e.stopPropagation();
        deleteNotification.mutate(notification_id);
    };

    return (
        <div className="flex flex-col bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
            {notifications.map((n, index) => {
                const config = typeConfig[n.notification_type] ?? typeConfig.other;
                const Icon = config.icon;
                const isLast = index === notifications.length - 1;

                return (
                    <div
                        key={n.id}
                        role="button"
                        tabIndex={0}
                        onClick={(e) => markAsRead(e, n.id)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                markAsRead(e, n.id);
                            }
                        }}
                        className={`
                            group relative flex items-start gap-4 p-4 sm:p-5 text-left cursor-pointer transition-all duration-200
                            ${!n.read ? 'bg-brand/3 hover:bg-brand/6' : 'hover:bg-gray-50/80'}
                            ${!isLast ? 'border-b border-gray-50' : ''}
                        `}
                    >
                        {/* Icon */}
                        <span className={`
                            flex items-center justify-center w-10 h-10 rounded-xl shrink-0 transition-transform duration-200 group-hover:scale-105
                            ${config.bg} ${config.color}
                        `}>
                            <Icon size={18} strokeWidth={2} />
                        </span>

                        {/* Content */}
                        <div className="flex-1 min-w-0 pr-10">
                            <div className="flex items-center gap-2 mb-0.5">
                                <p className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
                                    {typeLabels[n.notification_type] ?? typeLabels.other}
                                </p>
                                {!n.read && (
                                    <span className="relative flex h-2 w-2">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand opacity-75" />
                                        <span className="relative inline-flex rounded-full h-2 w-2 bg-brand" />
                                    </span>
                                )}
                            </div>

                            <p className={`
                                text-sm leading-relaxed
                                ${!n.read ? 'text-gray-900 font-semibold' : 'text-gray-500 font-normal'}
                            `}>
                                {n.message}
                            </p>

                            <p className="text-[11px] text-gray-400 mt-1.5 font-medium">
                                {timeAgo(n.timestamp)}
                            </p>
                        </div>

                        {/* Delete */}
                        <button
                            type="button"
                            onClick={(e) => handleDelete(e, n.id)}
                            aria-label="Delete notification"
                            disabled={deleteNotification.isPending}
                            className="
                                absolute top-1/2 -translate-y-1/2 right-3 sm:right-4
                                flex items-center justify-center w-8 h-8 rounded-lg
                                text-gray-300 opacity-100 sm:opacity-0 sm:group-hover:opacity-100
                                hover:bg-red-50 hover:text-red-500
                                active:scale-90 transition-all duration-200
                                disabled:opacity-50
                            "
                        >
                            <HiOutlineTrash size={16} />
                        </button>
                    </div>
                );
            })}

            {notifications.length === 0 && (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                    <div className="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
                        <svg className="w-6 h-6 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                    </div>
                    <p className="text-sm font-bold text-gray-900">No notifications</p>
                    <p className="text-xs text-gray-400 mt-1">You're all caught up!</p>
                </div>
            )}
        </div>
    );
};

export default NotificationCard;