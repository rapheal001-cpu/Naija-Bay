import { Link } from 'react-router-dom';
import { FaSpinner, FaExclamationTriangle } from 'react-icons/fa';

const BADGE_STYLES = {
    // order / item status
    pending: 'bg-amber-50 text-amber-700 border-amber-100',
    processing: 'bg-blue-50 text-blue-700 border-blue-100',
    shipped: 'bg-indigo-50 text-indigo-700 border-indigo-100',
    delivered: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    cancelled: 'bg-gray-100 text-gray-500 border-gray-200',
    // payment status
    paid: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    unpaid: 'bg-amber-50 text-amber-700 border-amber-100',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    failed: 'bg-red-50 text-red-600 border-red-100',
    abandoned: 'bg-gray-100 text-gray-500 border-gray-200',
    refunded: 'bg-gray-100 text-gray-500 border-gray-200',
    // boosts
    active: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    expired: 'bg-gray-100 text-gray-500 border-gray-200',
};

export const StatusBadge = ({ status, label }) => (
    <span
        className={`inline-flex items-center px-2.5 py-1 rounded-full border text-[11px] font-bold uppercase tracking-wide ${
            BADGE_STYLES[status] || 'bg-gray-100 text-gray-600 border-gray-200'
        }`}
    >
        {label || status}
    </span>
);

export const PageContainer = ({ title, subtitle, actions, children, width = 'max-w-5xl' }) => (
    <div className={`${width} mx-auto px-4 sm:px-6 py-8 sm:py-10`}>
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 mb-6">
            <div>
                <h1 className="text-2xl font-black text-gray-900 tracking-tight">{title}</h1>
                {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
            </div>
            {actions}
        </div>
        {children}
    </div>
);

export const LoadingBlock = ({ label = 'Loading...' }) => (
    <div className="flex flex-col items-center justify-center py-20 text-gray-400" role="status">
        <FaSpinner className="animate-spin mb-3" size={24} />
        <p className="text-sm font-medium">{label}</p>
    </div>
);

export const ErrorBlock = ({ message, onRetry }) => (
    <div className="flex flex-col items-center text-center py-16 px-4" role="alert">
        <div className="w-14 h-14 rounded-2xl bg-red-50 text-red-500 flex items-center justify-center mb-4">
            <FaExclamationTriangle size={22} />
        </div>
        <p className="text-sm font-semibold text-gray-800 max-w-sm">{message || 'Something went wrong.'}</p>
        {onRetry && (
            <button
                type="button"
                onClick={onRetry}
                className="mt-4 px-5 py-2.5 rounded-xl bg-brand text-white text-sm font-bold hover:opacity-90 active:scale-95 transition-all"
            >
                Try again
            </button>
        )}
    </div>
);

export const EmptyBlock = ({ icon, title, text, actionLabel, actionTo }) => (
    <div className="flex flex-col items-center text-center py-16 px-4">
        <div className="w-20 h-20 rounded-2xl bg-gray-50 flex items-center justify-center mb-5 text-gray-300">
            {icon}
        </div>
        <h3 className="text-lg font-bold text-gray-900">{title}</h3>
        {text && <p className="text-sm text-gray-400 mt-1.5 max-w-xs">{text}</p>}
        {actionLabel && actionTo && (
            <Link
                to={actionTo}
                className="mt-5 px-6 py-3 rounded-xl bg-brand text-white text-sm font-bold hover:opacity-90 active:scale-95 transition-all"
            >
                {actionLabel}
            </Link>
        )}
    </div>
);

export const PageButtons = ({ data, page, setPage }) => {
    if (!data || (!data.next && !data.previous)) return null;
    return (
        <div className="flex items-center justify-center gap-3 mt-8">
            <button
                type="button"
                disabled={!data.previous}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-4 py-2 rounded-xl text-sm font-bold bg-gray-100 text-gray-700 disabled:opacity-40 hover:bg-gray-200 transition-colors"
            >
                Previous
            </button>
            <span className="text-sm font-semibold text-gray-500">Page {page}</span>
            <button
                type="button"
                disabled={!data.next}
                onClick={() => setPage((p) => p + 1)}
                className="px-4 py-2 rounded-xl text-sm font-bold bg-gray-100 text-gray-700 disabled:opacity-40 hover:bg-gray-200 transition-colors"
            >
                Next
            </button>
        </div>
    );
};

/** Redirects signed-out visitors; returns true when the page may render. */
export const Thumb = ({ src, alt }) =>
    src ? (
        <img src={src} alt={alt} className="w-full h-full object-cover" />
    ) : (
        <div className="w-full h-full bg-gray-100" />
    );
