// Shared loading-state primitives (show placeholders, not spinners).

export const SkeletonBlock = ({ className = '' }) => (
    <div className={`bg-gray-100 animate-pulse rounded-xl ${className}`} aria-hidden="true" />
);

export const SkeletonProductCard = () => (
    <div className="flex flex-col h-full bg-white rounded-2xl border border-gray-100 overflow-hidden" aria-hidden="true">
        <div className="w-full aspect-square bg-gray-100 animate-pulse" />
        <div className="flex flex-col flex-1 p-4 gap-2.5">
            <div className="h-5 w-24 bg-gray-100 animate-pulse rounded-md" />
            <div className="h-4 w-full bg-gray-100 animate-pulse rounded-md" />
            <div className="h-4 w-2/3 bg-gray-100 animate-pulse rounded-md" />
            <div className="mt-auto flex items-center justify-between pt-3 border-t border-gray-50">
                <div className="h-3 w-20 bg-gray-100 animate-pulse rounded" />
                <div className="h-3 w-8 bg-gray-100 animate-pulse rounded" />
            </div>
        </div>
    </div>
);

export const SkeletonCardRow = ({ rows = 3 }) => (
    <div className="space-y-3" aria-hidden="true">
        {Array.from({ length: rows }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 bg-white border border-gray-100 rounded-2xl p-4 animate-pulse">
                <div className="w-14 h-14 rounded-full bg-gray-100 shrink-0" />
                <div className="flex-1 space-y-2.5">
                    <div className="h-4 w-1/3 bg-gray-100 rounded" />
                    <div className="h-3 w-2/3 bg-gray-100 rounded" />
                </div>
                <div className="h-4 w-16 bg-gray-100 rounded" />
            </div>
        ))}
    </div>
);

export const SkeletonGrid = ({ count = 8 }) => (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5" aria-hidden="true">
        {Array.from({ length: count }).map((_, i) => (
            <SkeletonProductCard key={i} />
        ))}
    </div>
);

export const LoadingLabel = ({ children }) => (
    <span className="sr-only" role="status" aria-live="polite">
        {children}
    </span>
);
