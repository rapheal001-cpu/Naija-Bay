import { useEffect, useRef } from 'react';

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
