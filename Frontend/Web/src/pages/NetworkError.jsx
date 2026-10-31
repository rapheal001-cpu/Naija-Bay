import { useState } from 'react';
import { HiOutlineWifi, HiOutlineRefresh } from 'react-icons/hi';
import { useNavigate } from 'react-router-dom';

const NetworkError = () => {
    const navigate = useNavigate();
    const [isRetrying, setIsRetrying] = useState(false)

    const handleRetry = () => {
        setTimeout(() => {
            navigate(-1);
        }, 3000);
        
        setIsRetrying(true);

    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-20 bg-linear-to-b from-gray-50 to-white relative overflow-hidden">
            {/* Decorative background */}
            <div className="absolute top-1/4 left-0 w-72 h-72 bg-brand/5 rounded-full blur-3xl -translate-x-1/2 pointer-events-none" />
            <div className="absolute bottom-1/4 right-0 w-96 h-96 bg-brand/5 rounded-full blur-3xl translate-x-1/3 pointer-events-none" />

            <div className="relative flex flex-col items-center text-center max-w-md">
                {/* Icon */}
                <div className="relative mb-8">
                    <div className="w-24 h-24 rounded-3xl bg-gray-100 border border-gray-200 flex items-center justify-center shadow-inner">
                        <HiOutlineWifi className="text-gray-300" size={44} strokeWidth={1.5} />
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="w-1 h-28 bg-red-400/80 rotate-45 rounded-full shadow-sm" />
                    </div>
                    {/* Pulse ring */}
                    <div className="absolute inset-0 rounded-3xl border-2 border-gray-200 animate-pulse" />
                </div>

                {/* Content */}
                <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">
                    No internet connection
                </h1>
                <p className="text-sm sm:text-base text-gray-500 mt-3 leading-relaxed max-w-xs mx-auto">
                    Check your Wi-Fi or mobile data and try again. Your listings and messages will be here when you're back online.
                </p>

                {/* Action */}
                <button
                    type="button"
                    onClick={handleRetry}
                    className="mt-8 inline-flex items-center justify-center gap-2.5 bg-brand text-white font-bold text-sm rounded-xl px-8 py-3.5 hover:opacity-90 active:scale-[0.98] transition-all shadow-lg shadow-brand/20"
                >
                    <HiOutlineRefresh size={18} className={isRetrying ? 'animate-spin' : ''} />
                    Try again
                </button>

            </div>
        </div>
    );
};

export default NetworkError;