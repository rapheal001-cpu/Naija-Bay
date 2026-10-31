import { FaChevronLeft, FaChevronRight } from 'react-icons/fa';

/**
 * Reusable page-number pagination for DRF paginated responses.
 *
 * @param {{ page?: number, count?: number, pageSize?: number, onChange: (page:number) => void, className?: string }} props
 */
const Pagination = ({ page = 1, count = 0, pageSize = 24, onChange, className = '' }) => {
    const totalPages = Math.max(1, Math.ceil(count / pageSize));

    if (totalPages <= 1) return null;

    const go = (target) => {
        if (target < 1 || target > totalPages || target === page) return;
        onChange(target);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const pages = [];
    const start = Math.max(1, page - 2);
    const end = Math.min(totalPages, start + 4);
    for (let i = start; i <= end; i += 1) pages.push(i);

    const baseButton =
        'inline-flex items-center justify-center min-w-9 h-9 px-3 rounded-lg text-sm font-semibold transition-all disabled:opacity-40 disabled:cursor-not-allowed';

    return (
        <nav
            aria-label="Pagination"
            className={`flex items-center justify-center gap-1.5 ${className}`}
        >
            <button
                type="button"
                onClick={() => go(page - 1)}
                disabled={page <= 1}
                aria-label="Previous page"
                className={`${baseButton} text-gray-500 hover:bg-gray-100`}
            >
                <FaChevronLeft size={12} />
            </button>

            {start > 1 && (
                <>
                    <button
                        type="button"
                        onClick={() => go(1)}
                        className={`${baseButton} text-gray-600 hover:bg-gray-100`}
                    >
                        1
                    </button>
                    {start > 2 && <span className="px-1 text-gray-400">…</span>}
                </>
            )}

            {pages.map((number) => (
                <button
                    key={number}
                    type="button"
                    onClick={() => go(number)}
                    aria-current={number === page ? 'page' : undefined}
                    className={`${baseButton} ${
                        number === page
                            ? 'bg-brand text-white shadow-sm shadow-brand/25'
                            : 'text-gray-600 hover:bg-gray-100'
                    }`}
                >
                    {number}
                </button>
            ))}

            {end < totalPages && (
                <>
                    {end < totalPages - 1 && <span className="px-1 text-gray-400">…</span>}
                    <button
                        type="button"
                        onClick={() => go(totalPages)}
                        className={`${baseButton} text-gray-600 hover:bg-gray-100`}
                    >
                        {totalPages}
                    </button>
                </>
            )}

            <button
                type="button"
                onClick={() => go(page + 1)}
                disabled={page >= totalPages}
                aria-label="Next page"
                className={`${baseButton} text-gray-500 hover:bg-gray-100`}
            >
                <FaChevronRight size={12} />
            </button>
        </nav>
    );
};

export default Pagination;
