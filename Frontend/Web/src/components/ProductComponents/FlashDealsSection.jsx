import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FaBolt, FaArrowRight } from 'react-icons/fa';
import ProductCard from './ProductCard';
import SkeletonProductCard from '../../skeletons/SkeletonProductCard';
import { useFetchFlashDeals } from '../../hooks/UseQuery';

// Counts down to the next midnight, Temu "ends in" style.
const useMidnightCountdown = () => {
    const [remaining, setRemaining] = useState('');

    useEffect(() => {
        const tick = () => {
            const now = new Date();
            const midnight = new Date(now);
            midnight.setHours(24, 0, 0, 0);
            const diff = midnight - now;

            const hours = Math.floor(diff / 3600000);
            const minutes = Math.floor((diff % 3600000) / 60000);
            const seconds = Math.floor((diff % 60000) / 1000);

            setRemaining(
                `${String(hours).padStart(2, '0')}h : ${String(minutes).padStart(2, '0')}m : ${String(seconds).padStart(2, '0')}s`
            );
        };

        tick();
        const timer = setInterval(tick, 1000);
        return () => clearInterval(timer);
    }, []);

    return remaining;
};

const FlashDealsSection = () => {
    const fetchFlashDeals = useFetchFlashDeals();
    const countdown = useMidnightCountdown();

    const deals = fetchFlashDeals.data || [];

    if (!fetchFlashDeals.isLoading && deals.length === 0) return null;

    return (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="bg-linear-to-r from-red-500 via-orange-500 to-amber-400 rounded-3xl p-5 sm:p-7">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                    <div className="flex items-center gap-3">
                        <span className="flex items-center justify-center w-11 h-11 rounded-2xl bg-white/20 backdrop-blur-sm">
                            <FaBolt size={20} className="text-white" />
                        </span>
                        <div>
                            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                                Flash Deals
                            </h2>
                            <p className="text-white/70 text-xs font-semibold">
                                Limited-time offers — while stock lasts
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-2 text-center">
                            <p className="text-[9px] font-bold text-white/60 uppercase tracking-widest">Ends in</p>
                            <p className="text-sm font-black text-white tabular-nums">{countdown}</p>
                        </div>
                        <Link
                            to="/products?discounted=true"
                            className="group hidden sm:flex items-center gap-2 text-xs font-bold text-white/90 hover:text-white"
                        >
                            View all
                            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-white/20 group-hover:bg-white group-hover:text-red-500 transition-all">
                                <FaArrowRight size={10} />
                            </span>
                        </Link>
                    </div>
                </div>

                {fetchFlashDeals.isLoading ? (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                        {Array.from({ length: 5 }).map((_, i) => <SkeletonProductCard key={i} />)}
                    </div>
                ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                        {deals.slice(0, 10).map((product) => (
                            <ProductCard key={product.id} {...product} />
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
};

export default FlashDealsSection;
