import { useEffect, useState } from 'react';
import { FaTruck, FaShieldAlt, FaUndoAlt, FaTag, FaChevronLeft, FaChevronRight } from 'react-icons/fa';

const MESSAGES = [
    { icon: FaTruck, title: 'Free delivery nationwide', subtitle: 'On eligible listings' },
    { icon: FaShieldAlt, title: 'Buyer protection', subtitle: 'Report issues, get support' },
    { icon: FaUndoAlt, title: 'Easy returns', subtitle: 'Within 7 days of purchase' },
    { icon: FaTag, title: 'Flash deals daily', subtitle: 'Discounts up to 70% off' },
];

const PromoBar = () => {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setIndex((prev) => (prev + 1) % MESSAGES.length);
        }, 4000);
        return () => clearInterval(timer);
    }, []);

    const current = MESSAGES[index];
    const Icon = current.icon;

    const step = (delta) => {
        setIndex((prev) => (prev + delta + MESSAGES.length) % MESSAGES.length);
    };

    return (
        <div className="bg-gray-900 text-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-9 flex items-center justify-center gap-3 text-xs">
                <button onClick={() => step(-1)} aria-label="Previous announcement" className="text-white/40 hover:text-white transition-colors">
                    <FaChevronLeft size={11} />
                </button>

                <span key={index} className="flex items-center gap-2">
                    <Icon size={13} className="text-amber-400 shrink-0" />
                    <span className="font-bold">{current.title}</span>
                    <span className="hidden sm:inline text-white/50 font-medium">{current.subtitle}</span>
                </span>

                <button onClick={() => step(1)} aria-label="Next announcement" className="text-white/40 hover:text-white transition-colors">
                    <FaChevronRight size={11} />
                </button>
            </div>
        </div>
    );
};

export default PromoBar;
