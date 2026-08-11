import { Link } from 'react-router-dom';
import { HiOutlineBadgeCheck, HiOutlineTrendingUp, HiOutlineEye, HiOutlineShieldCheck } from 'react-icons/hi';
import { FaArrowLeft } from 'react-icons/fa';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';

const VERIFICATION_PLANS = [
    { days: 1, label: '1 Day', price: 700, tag: null },
    { days: 3, label: '3 Days', price: 1800, tag: null },
    { days: 7, label: '7 Days', price: 3500, tag: 'Popular' },
    { days: 30, label: '1 Month', price: 9000, tag: 'Best value' },
    { days: 180, label: '6 Months', price: 39000, tag: null },
    { days: 365, label: '1 Year', price: 65000, tag: null },
    { days: null, label: 'Forever', price: 120000, tag: 'Lifetime' },
];

const BENEFITS = [
    {
        icon: HiOutlineTrendingUp,
        title: 'Top placement',
        description: 'Your listings appear above unverified sellers in search and category pages.',
    },
    {
        icon: HiOutlineBadgeCheck,
        title: 'Verified badge',
        description: 'A blue checkmark appears next to your name everywhere buyers see you.',
    },
    {
        icon: HiOutlineEye,
        title: 'More views',
        description: 'Verified sellers get priority in featured and recommended sections.',
    },
    {
        icon: HiOutlineShieldCheck,
        title: 'Buyer trust',
        description: 'Buyers are more likely to complete a purchase from a verified account.',
    },
];

const formatNaira = (amount) => `₦${amount.toLocaleString()}`;

const GetVerified = () => {
    const handleSelectPlan = (days) => {
        const url = days
            ? `${import.meta.env.STRIPE_BASE_URL}?days=${days}`
            : `${import.meta.env.STRIPE_BASE_URL}?days=forever`;
        window.location.href = url;
    };

    return (
        <>
            <Header />
            <Spacer space="mb-20" />

            <div className="min-h-[85vh] bg-[#FAF9F6] py-8">
                <div className="max-w-4xl mx-auto px-4">

                    <Link to="/settings" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-brand transition-colors mb-4">
                        <FaArrowLeft size={14} />
                        Back to settings
                    </Link>

                    {/* Hero */}
                    <div className="text-center mb-10">
                        <span className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-amber-100 mb-4">
                            <HiOutlineBadgeCheck className="text-amber-600" size={28} />
                        </span>
                        <h1 className="text-[26px] sm:text-[30px] font-bold text-gray-900 tracking-tight">
                            Get verified, get seen
                        </h1>
                        <p className="text-sm sm:text-[15px] text-gray-500 mt-2 max-w-md mx-auto leading-relaxed">
                            Verified sellers rank higher, earn more trust, and sell faster. Pick how long you want to stay verified.
                        </p>
                    </div>

                    {/* Benefits row */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-10">
                        {BENEFITS.map(({ icon: Icon, title, description }) => (
                            <div key={title} className="bg-white rounded-xl border border-gray-100 p-4 text-center">
                                <span className="inline-flex items-center justify-center w-9 h-9 rounded-lg bg-brand/10 mb-2">
                                    <Icon className="text-brand" size={18} />
                                </span>
                                <p className="text-[13px] font-semibold text-gray-900">{title}</p>
                                <p className="text-[11px] text-gray-500 mt-1 leading-snug hidden sm:block">{description}</p>
                            </div>
                        ))}
                    </div>

                    {/* Plan cards */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                        {VERIFICATION_PLANS.map(({ days, label, price, tag }) => {
                            const isForever = days === null;
                            return (
                                <button
                                    key={label}
                                    type="button"
                                    onClick={() => handleSelectPlan(days)}
                                    className={`relative text-left rounded-2xl p-5 border transition-all hover:-translate-y-0.5 ${
                                        isForever
                                            ? 'bg-gray-900 border-gray-900 hover:shadow-lg hover:shadow-gray-900/20'
                                            : 'bg-white border-gray-100 hover:border-brand hover:shadow-[0_12px_32px_-12px_rgba(0,0,0,0.15)]'
                                    }`}
                                >
                                    {tag && (
                                        <span className={`absolute -top-2.5 left-4 text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                            isForever
                                                ? 'bg-amber-400 text-gray-900'
                                                : 'bg-brand text-white'
                                        }`}>
                                            {tag}
                                        </span>
                                    )}

                                    <p className={`text-[13px] font-semibold ${isForever ? 'text-gray-300' : 'text-gray-500'}`}>
                                        {label}
                                    </p>

                                    <p className={`text-2xl font-bold tracking-tight mt-1 ${isForever ? 'text-white' : 'text-gray-900'}`}>
                                        {formatNaira(price)}
                                    </p>

                                    {!isForever && (
                                        <p className="text-[11px] text-gray-400 mt-1">
                                            {formatNaira(Math.round(price / days))}/day
                                        </p>
                                    )}
                                    {isForever && (
                                        <p className="text-[11px] text-gray-400 mt-1">
                                            One-time payment
                                        </p>
                                    )}

                                    <span className={`inline-flex items-center gap-1 text-[12px] font-semibold mt-4 ${
                                        isForever ? 'text-amber-400' : 'text-brand'
                                    }`}>
                                        Choose plan →
                                    </span>
                                </button>
                            );
                        })}
                    </div>

                    <p className="text-center text-xs text-gray-400 mt-8">
                        Payments are processed securely by Stripe. Verification activates automatically after payment.
                    </p>

                </div>
            </div>
        </>
    );
};

export default GetVerified;