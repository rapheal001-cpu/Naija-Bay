import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { HiOutlineSearch, HiOutlineLocationMarker } from 'react-icons/hi';
import { STATE_CHOICES } from '../../dummyData.js';

/**
 * Professional header search: keyword + Nigerian state selector.
 * Preserves the existing `/products` query-param contract (search, state).
 */
const GlobalSearch = ({ compact = false }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [keyword, setKeyword] = useState('');
    const [state, setState] = useState('');

    const handleSubmit = (event) => {
        event.preventDefault();
        const params = new URLSearchParams(location.search);
        // Start a fresh browse context for header searches.
        params.delete('page');
        if (keyword.trim()) params.set('search', keyword.trim());
        else params.delete('search');
        if (state) params.set('state', state);
        else params.delete('state');
        const qs = params.toString();
        navigate(qs ? `/products?${qs}` : '/products');
    };

    const selectedState = STATE_CHOICES.find((s) => s.value === state);

    return (
        <form
            onSubmit={handleSubmit}
            role="search"
            aria-label="Search listings"
            className={`flex w-full items-stretch overflow-hidden rounded-xl bg-white shadow-sm focus-within:ring-2 focus-within:ring-white/60 ${compact ? 'h-10' : 'h-11'}`}
        >
            <label className="flex min-w-0 flex-1 items-center pl-3">
                <span className="sr-only">What are you looking for?</span>
                <HiOutlineSearch size={18} className="shrink-0 text-gray-400" aria-hidden="true" />
                <input
                    type="text"
                    value={keyword}
                    onChange={(event) => setKeyword(event.target.value)}
                    placeholder="What are you looking for?"
                    className="w-full min-w-0 bg-transparent px-2 text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none"
                />
            </label>

            <div className="relative hidden items-center border-l border-gray-200 sm:flex">
                <HiOutlineLocationMarker size={16} className="ml-2 shrink-0 text-gray-400" aria-hidden="true" />
                <span className="sr-only">Location</span>
                <select
                    value={state}
                    onChange={(event) => setState(event.target.value)}
                    className="h-full max-w-32 cursor-pointer appearance-none bg-transparent px-2 pr-1 text-sm font-medium text-gray-700 focus:outline-none"
                >
                    <option value="">All Nigeria</option>
                    {STATE_CHOICES.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
            </div>

            <button
                type="submit"
                className="hidden shrink-0 items-center gap-1.5 bg-brand-green px-4 text-sm font-bold text-white transition-colors hover:bg-brand-green/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 sm:flex"
            >
                <HiOutlineSearch size={16} aria-hidden="true" />
                Search
            </button>
        </form>
    );
};

export default GlobalSearch;
