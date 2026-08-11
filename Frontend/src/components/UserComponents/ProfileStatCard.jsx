import { FaCheckCircle, FaHeart } from "react-icons/fa";
import { GoPackage } from "react-icons/go";

const ProfileStatCard = ({ activeListings = [], soldListings = [], favoriteListings = [] }) => {
    const stats = [
        {
            icon: GoPackage,
            label: 'Active',
            fullLabel: 'Active Products',
            value: activeListings?.length ?? 0,
            color: 'text-brand',
            bg: 'bg-brand/10',
            border: 'border-brand/10',
        },
        {
            icon: FaCheckCircle,
            label: 'Sold',
            fullLabel: 'Sold Products',
            value: soldListings?.length ?? 0,
            color: 'text-emerald-600',
            bg: 'bg-emerald-50',
            border: 'border-emerald-100',
        },
        {
            icon: FaHeart,
            label: 'Favorites',
            fullLabel: 'Favorites',
            value: favoriteListings?.length ?? 0,
            color: 'text-red-500',
            bg: 'bg-red-50',
            border: 'border-red-100',
        },
    ];

    return (
        <div className="grid grid-cols-1 gap-3">
            {stats.map((stat, index) => {
                const Icon = stat.icon;
                return (
                    <div
                        key={index}
                        className="group relative flex items-center gap-3 sm:gap-4 bg-white border border-gray-100 rounded-xl sm:rounded-2xl p-4 sm:p-5 hover:shadow-md hover:shadow-gray-100/50 hover:-translate-y-0.5 transition-all duration-200 overflow-hidden"
                    >
                        <span className={`
                            flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl shrink-0 transition-transform duration-200 group-hover:scale-105
                            ${stat.bg} ${stat.color} ${stat.border} border
                        `}>
                            <Icon size={18} className="sm:w-5 sm:h-5" />
                        </span>

                        <div className="min-w-0">
                            <p className="text-xl sm:text-2xl font-black text-gray-900 tracking-tight leading-none">
                                {stat.value.toLocaleString()}
                            </p>
                            <p className="text-[11px] sm:text-xs font-semibold text-gray-400 uppercase tracking-wider mt-1 sm:mt-1.5">
                                <span className="sm:hidden">{stat.label}</span>
                                <span className="hidden sm:inline">{stat.fullLabel}</span>
                            </p>
                        </div>

                        {/* Decorative corner - hidden on very small screens */}
                        <div className={`hidden sm:block absolute top-0 right-0 w-12 h-12 sm:w-16 sm:h-16 rounded-bl-4xl sm:rounded-bl-[40px] opacity-30 pointer-events-none ${stat.bg}`} />
                    </div>
                );
            })}
        </div>
    );
};

export default ProfileStatCard;