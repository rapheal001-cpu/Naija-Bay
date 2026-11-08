import { IoSearchOutline } from 'react-icons/io5';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Search = () => {
    const navigate = useNavigate();
    const [search, setSearch] = useState('');
    const [isFocused, setIsFocused] = useState(false);

    const handleSearch = () => {
        const trimmedSearch = search.trim();
        navigate(trimmedSearch ? `/products?search=${encodeURIComponent(trimmedSearch)}` : '/');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    return (
        <div className="relative w-full overflow-hidden bg-brand">
            {/* Decorative background shapes */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-24 -left-24 w-72 h-72 bg-white/5 rounded-full blur-3xl" />
                <div className="absolute top-1/2 -right-24 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
            </div>

            <div className="relative max-w-3xl mx-auto px-4 py-16 sm:py-20 lg:py-24 text-center">
                {/* Heading */}
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white mb-3 tracking-tight">
                    What are you looking for?
                </h1>
                <p className="text-white/70 text-sm sm:text-base mb-8 max-w-md mx-auto">
                    Discover amazing deals on products, brands, and more across Naija Bay.
                </p>

                {/* Search Bar */}
                <div 
                    className={`
                        relative flex items-center bg-white rounded-2xl shadow-xl transition-all duration-300
                        ${isFocused ? 'shadow-white/20 ring-4 ring-white/10 scale-[1.02]' : 'hover:shadow-2xl'}
                    `}
                >
                    <div className="pl-5 text-gray-400">
                        <IoSearchOutline size={20} />
                    </div>

                    <input
                        type="text"
                        placeholder="Search for products, brands, and more..."
                        className="w-full px-3 py-4 sm:py-5 text-sm sm:text-base text-gray-800 placeholder:text-gray-400 bg-transparent focus:outline-none"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        onKeyDown={handleKeyDown}
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                    />

                    <button
                        type="button"
                        aria-label="Search"
                        onClick={handleSearch}
                        className="flex items-center justify-center bg-brand text-white m-1.5 px-6 py-3 sm:py-3.5 rounded-xl font-semibold text-sm hover:bg-brand-hover active:scale-95 transition-all duration-200 shrink-0"
                    >
                        <span className="hidden sm:inline">Search</span>
                        <IoSearchOutline size={18} className="sm:hidden" />
                    </button>
                </div>
            </div>

            {/* Bottom curve */}
            <div className="absolute bottom-0 left-0 right-0">
                <svg viewBox="0 0 1440 60" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto block">
                    <path d="M0 60L1440 60L1440 0C1440 0 1140 60 720 60C300 60 0 0 0 0L0 60Z" fill="white" />
                </svg>
            </div>
        </div>
    );
};

export default Search;