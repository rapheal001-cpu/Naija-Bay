const SkeletonNotificationCard = () => {
    const notifications = Array.from({ length: 6 }, (_, i) => i + 1);

    return (
        <div className="flex flex-col divide-y divide-gray-100 bg-white rounded-2xl border border-gray-100 overflow-hidden">
            {notifications.map((n) => (
                <div key={n} className="flex items-start gap-3.5 p-4">
                    <div className="w-10 h-10 rounded-full bg-gray-100 shrink-0" />
                    <div className="flex-1 min-w-0 space-y-2 pt-1">
                        <div className="h-4 w-40 bg-gray-100 rounded-md" />
                        <div className="h-3 w-56 bg-gray-100 rounded-md" />
                    </div>
                    <div className="w-2 h-2 rounded-full bg-gray-100 shrink-0 mt-2" />
                </div>
            ))}
        </div>
    );
};

export default SkeletonNotificationCard;