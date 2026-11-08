import { useEffect, useRef } from 'react';

/**
 * Infinite-scroll sentinel (SkillStream ChatWindow pattern):
 * fires `onLoadMore` when the marker scrolls into view (400px ahead of the
 * bottom), while `hasMore` is true and a fetch is not already in flight.
 */
const InfiniteListSentinel = ({ hasMore, isFetching, onLoadMore, rootMargin = '400px 0px' }) => {
    const ref = useRef(null);

    useEffect(() => {
        const node = ref.current;
        if (!node) return undefined;
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries.some((entry) => entry.isIntersecting) && hasMore && !isFetching) {
                    onLoadMore();
                }
            },
            { rootMargin },
        );
        observer.observe(node);
        return () => observer.disconnect();
    }, [hasMore, isFetching, onLoadMore, rootMargin]);

    return <div ref={ref} aria-hidden="true" className="h-px" />;
};

export default InfiniteListSentinel;
