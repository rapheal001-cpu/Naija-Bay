import { LuMapPin, LuPhone, LuMail } from "react-icons/lu";

const ProfileContactDetailCard = ({ profile, isOwnProfile }) => {
    const contactItems = [
        {
            icon: LuPhone,
            label: 'Phone',
            value: profile?.phone_number,
            show: true,
            href: profile?.phone_number ? `tel:${profile.phone_number}` : null,
        },
        {
            icon: LuMail,
            label: 'Email',
            value: profile?.email,
            show: isOwnProfile,
            href: profile?.email ? `mailto:${profile.email}` : null,
        },
        {
            icon: LuMapPin,
            label: 'Address',
            value: profile?.address,
            show: true,
        },
        {
            icon: LuMapPin,
            label: 'State',
            value: profile?.state,
            show: true,
        },
    ];

    return (
        <div className="bg-white border border-gray-100 rounded-2xl sm:rounded-3xl shadow-sm p-4 sm:p-6 lg:p-7 overflow-hidden">
            <div className="flex items-center gap-2.5 mb-4 sm:mb-5">
                <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-brand/10 flex items-center justify-center shrink-0">
                    <LuPhone size={14} className="text-brand sm:w-4 sm:h-4" />
                </div>
                <h3 className="text-xs sm:text-sm font-bold text-gray-900 uppercase tracking-wider">
                    Contact Details
                </h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {contactItems.map((item, index) => {
                    if (!item.show) return null;
                    const Icon = item.icon;
                    const hasValue = !!item.value;
                    const Wrapper = item.href ? 'a' : 'div';
                    const wrapperProps = item.href
                        ? { href: item.href, className: "block" }
                        : {};

                    return (
                        <Wrapper key={index} {...wrapperProps}>
                            <div
                                className={`
                                    flex items-center gap-3 sm:gap-3.5 p-3 sm:p-3.5 
                                    rounded-xl sm:rounded-2xl bg-gray-50/50 border border-gray-50 
                                    transition-colors
                                    ${item.href ? 'hover:border-gray-200 hover:bg-gray-50 cursor-pointer' : 'hover:border-gray-100 hover:bg-gray-50'}
                                `}
                            >
                                <span className="flex items-center justify-center w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-white border border-gray-100 text-gray-400 shadow-sm shrink-0">
                                    <Icon size={16} strokeWidth={2} className="sm:w-4.25 sm:h-4.25" />
                                </span>
                                <div className="min-w-0 flex-1 overflow-hidden">
                                    <p className="text-[10px] sm:text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                                        {item.label}
                                    </p>
                                    <p 
                                        className="text-sm font-semibold text-gray-800 mt-0.5 break-all sm:wrap-break-word sm:truncate"
                                        title={hasValue ? item.value : undefined}
                                    >
                                        {hasValue ? item.value : (
                                            <span className="text-gray-300 italic font-medium">Not provided</span>
                                        )}
                                    </p>
                                </div>
                            </div>
                        </Wrapper>
                    );
                })}
            </div>
        </div>
    );
};

export default ProfileContactDetailCard;