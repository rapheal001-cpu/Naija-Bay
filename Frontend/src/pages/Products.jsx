import { useEffect, useState, useMemo } from 'react';
import { HiOutlineFunnel, HiOutlineAdjustmentsHorizontal } from 'react-icons/hi2';
import { HiOutlineSearch, HiOutlineX } from "react-icons/hi";
import { BiSolidCategory } from 'react-icons/bi';
import { FaChevronDown, FaChevronUp } from 'react-icons/fa';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';
import ProductCard from '../components/ProductComponents/ProductCard.jsx';
import Pagination from '../components/Pagination.jsx';
import SkeletonProductCard from '../skeletons/SkeletonProductCard.jsx';
import { useFetchCategories, useFetchProducts } from '../hooks/UseQuery.js';
import { useDispatch, useSelector } from 'react-redux';
import { setProducts } from '../slice/ProductSlice.js';
import { setCategories } from '../slice/CategorySlice.js';
import { useSearchParams } from 'react-router-dom';
import { categoryIconsMap, STATE_CHOICES, CONDITION_CHOICES } from '../dummyData.js';
import Footer from '../components/FooterComponents/Footer.jsx';


const PAGE_SIZE = 24;

const SORT_OPTIONS = [
    { value: '', label: 'Newest first' },
    { value: 'price_asc', label: 'Price: low to high' },
    { value: 'price_desc', label: 'Price: high to low' },
    { value: 'popular', label: 'Most viewed' },
    { value: 'favorites', label: 'Most saved' },
    { value: 'oldest', label: 'Oldest first' },
];

const FILTER_PARAM_KEYS = [
    'condition',
    'state',
    'city',
    'min_price',
    'max_price',
    'delivery_available',
    'verified_seller',
    'negotiable',
];

const buildFilters = (params) => {
    const filters = { page: Number(params.get('page')) || 1 };

    ['search', 'category', 'sub_category', 'condition', 'state', 'city', 'min_price', 'max_price', 'sort'].forEach((key) => {
        const value = params.get(key);
        if (value) filters[key] = value;
    });

    ['delivery_available', 'verified_seller', 'negotiable'].forEach((key) => {
        if (params.get(key) === 'true') filters[key] = true;
    });

    return filters;
};


const Products = () => {
    const dispatch = useDispatch();

    const [searchParams, setSearchParams] = useSearchParams();
    const [searchInput, setSearchInput] = useState(searchParams.get('search') || '');
    const [showFilters, setShowFilters] = useState(false);

    const queryString = searchParams.toString();
    const filters = useMemo(() => buildFilters(new URLSearchParams(queryString)), [queryString]);

    const [draft, setDraft] = useState({
        condition: filters.condition || '',
        state: filters.state || '',
        city: filters.city || '',
        minPrice: filters.min_price || '',
        maxPrice: filters.max_price || '',
        delivery: Boolean(filters.delivery_available),
        verified: Boolean(filters.verified_seller),
        negotiable: Boolean(filters.negotiable),
    });

    const searchQuery = filters.search || '';
    const activeCategory = filters.category || '';
    const activeSubCategory = filters.sub_category || '';
    const activeSort = filters.sort || '';
    const page = filters.page || 1;

    const categories = useSelector((state) => state.categories.categories);

    const fetchProducts = useFetchProducts(filters);
    const fetchCategories = useFetchCategories();

    // Keep local inputs in sync when the URL changes (back button, chip removal).
    useEffect(() => {
        setSearchInput(searchQuery);
        setDraft({
            condition: filters.condition || '',
            state: filters.state || '',
            city: filters.city || '',
            minPrice: filters.min_price || '',
            maxPrice: filters.max_price || '',
            delivery: Boolean(filters.delivery_available),
            verified: Boolean(filters.verified_seller),
            negotiable: Boolean(filters.negotiable),
        });
    }, [
        searchQuery,
        filters.condition,
        filters.state,
        filters.city,
        filters.min_price,
        filters.max_price,
        filters.delivery_available,
        filters.verified_seller,
        filters.negotiable,
    ]);

    useEffect(() => {
        if (fetchProducts.isSuccess && fetchProducts.data) {
            dispatch(setProducts(fetchProducts.data.results || []));
        }
    }, [fetchProducts.isSuccess, fetchProducts.data, dispatch]);

    useEffect(() => {
        if (fetchCategories.isSuccess && fetchCategories.data) {
            dispatch(setCategories(fetchCategories.data));
        }
    }, [fetchCategories.isSuccess, fetchCategories.data, dispatch]);

    const parentOfActiveSub = useMemo(() => {
        if (!activeSubCategory) return null;
        return categories.find(cat =>
            cat.sub_categories?.some(sub => sub.slug === activeSubCategory)
        );
    }, [categories, activeSubCategory]);

    const activeSubCategoryName = useMemo(() => {
        if (!activeSubCategory) return '';
        for (const cat of categories) {
            const sub = cat.sub_categories?.find(s => s.slug === activeSubCategory);
            if (sub) return sub.name;
        }
        return activeSubCategory;
    }, [categories, activeSubCategory]);

    // -------------------------------------------------------------------------
    // URL helpers
    // -------------------------------------------------------------------------

    const updateParams = (updates, { resetPage = true } = {}) => {
        const newParams = new URLSearchParams(searchParams);

        Object.entries(updates).forEach(([key, value]) => {
            if (value === undefined || value === null || value === '' || value === false) {
                newParams.delete(key);
            } else {
                newParams.set(key, value === true ? 'true' : String(value));
            }
        });

        if (resetPage) newParams.delete('page');
        setSearchParams(newParams);
    };

    const handleSearch = (e) => {
        e.preventDefault();
        updateParams({ search: searchInput.trim() });
    };

    const handleCategoryClick = (slug) => {
        updateParams({
            category: activeCategory === slug ? '' : slug,
            sub_category: '',
        });
    };

    const applyFilters = (e) => {
        e.preventDefault();
        updateParams({
            condition: draft.condition,
            state: draft.state,
            city: draft.city.trim().toLowerCase().replace(/\s+/g, '_'),
            min_price: draft.minPrice,
            max_price: draft.maxPrice,
            delivery_available: draft.delivery,
            verified_seller: draft.verified,
            negotiable: draft.negotiable,
        });
    };

    const resetFilters = () => {
        const keep = new URLSearchParams();
        if (filters.search) keep.set('search', filters.search);
        if (filters.category) keep.set('category', filters.category);
        if (filters.sub_category) keep.set('sub_category', filters.sub_category);
        setSearchParams(keep);
    };

    const clearAll = () => {
        setSearchParams(new URLSearchParams());
        setSearchInput('');
    };

    const removeParam = (key) => updateParams({ [key]: '' });

    const handlePageChange = (nextPage) => {
        const newParams = new URLSearchParams(searchParams);
        if (nextPage <= 1) {
            newParams.delete('page');
        } else {
            newParams.set('page', String(nextPage));
        }
        setSearchParams(newParams);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const results = fetchProducts.data?.results || [];
    const totalCount = fetchProducts.data?.count ?? 0;
    const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));
    const activeFilterCount = FILTER_PARAM_KEYS.filter((key) => filters[key]).length;

    const stateLabel = (value) => STATE_CHOICES.find((s) => s.value === value)?.label || value?.replace(/[-_]/g, ' ');

    return (
        <>
            <Header />
            <Spacer space="mb-20" />

            <div className="min-h-screen bg-linear-to-b from-gray-50 to-white pb-16">
                {/* Search Hero */}
                <div className="relative bg-brand overflow-hidden">
                    <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4xKSIvPjwvc3ZnPg==')] opacity-30" />
                    <div className="absolute -top-24 -right-24 w-72 h-72 bg-white/10 rounded-full blur-3xl" />

                    <div className="relative max-w-4xl mx-auto px-4 sm:px-6 py-10 sm:py-14 text-center">
                        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight mb-2">
                            {(searchQuery || activeSubCategory || activeCategory)
                                ? `Results for "${(searchQuery || activeSubCategoryName || activeCategory).replace(/-/g, ' ').replace(/_/g, ' ')}"`
                                : 'Browse all products'
                            }
                        </h1>
                        <p className="text-white/70 text-sm sm:text-base mb-6">
                            {totalCount > 0
                                ? `${totalCount.toLocaleString()} product${totalCount !== 1 ? 's' : ''} available`
                                : 'Find exactly what you need'
                            }
                        </p>

                        <form onSubmit={handleSearch} className="relative max-w-xl mx-auto">
                            <div className="flex items-center bg-white rounded-2xl shadow-xl shadow-black/10 overflow-hidden">
                                <span className="pl-4 text-gray-400">
                                    <HiOutlineSearch size={20} />
                                </span>
                                <input
                                    type="text"
                                    placeholder="Search for products, brands, and more..."
                                    className="w-full px-3 py-3.5 text-sm text-gray-800 placeholder:text-gray-400 bg-transparent focus:outline-none"
                                    value={searchInput}
                                    onChange={(e) => setSearchInput(e.target.value)}
                                />
                                {searchInput && (
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setSearchInput('');
                                            updateParams({ search: '' });
                                        }}
                                        className="p-2 text-gray-400 hover:text-gray-600"
                                    >
                                        <HiOutlineX size={18} />
                                    </button>
                                )}
                                <button
                                    type="submit"
                                    className="bg-gray-900 text-white font-semibold text-sm px-6 py-3.5 hover:bg-gray-800 transition-colors"
                                >
                                    Search
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* Bottom curve */}
                    <div className="absolute bottom-0 left-0 right-0">
                        <svg viewBox="0 0 1440 60" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto block">
                            <path d="M0 60L1440 60L1440 0C1440 0 1140 60 720 60C300 60 0 0 0 0L0 60Z" fill="white" />
                        </svg>
                    </div>
                </div>

                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-2">
                    {/* Category Filter Bar */}
                    <div className="relative mb-6">
                        <div className="flex gap-2 sm:gap-3 overflow-x-auto scroll-smooth snap-x py-4 scrollbar-hide">
                            {/* All button */}
                            <button
                                type="button"
                                onClick={() => handleCategoryClick('')}
                                className={`flex flex-col items-center gap-2 shrink-0 w-16 sm:w-20 text-center snap-start group transition-all duration-200 ${
                                    !activeCategory && !activeSubCategory ? 'opacity-100' : 'opacity-60 hover:opacity-100'
                                }`}
                            >
                                <span className={`flex items-center justify-center w-12 h-12 rounded-2xl transition-all duration-200 shadow-sm ${
                                    !activeCategory && !activeSubCategory
                                        ? 'bg-brand text-white shadow-brand/25 scale-110'
                                        : 'bg-gray-100 text-gray-500 group-hover:bg-gray-200 group-hover:text-gray-700'
                                }`}>
                                    <BiSolidCategory size={20} />
                                </span>
                                <span className={`text-[10px] sm:text-xs font-medium leading-tight line-clamp-2 transition-colors ${
                                    !activeCategory && !activeSubCategory ? 'text-brand' : 'text-gray-500'
                                }`}>
                                    All
                                </span>
                            </button>

                            {/* Categories from Redux */}
                            {categories.map((category) => {
                                const Icon = categoryIconsMap[category.slug] || categoryIconsMap['default_icon'];
                                const isActive = activeCategory === category.slug || parentOfActiveSub?.slug === category.slug;

                                return (
                                    <button
                                        key={category.slug}
                                        type="button"
                                        onClick={() => handleCategoryClick(category.slug)}
                                        className={`flex flex-col items-center gap-2 shrink-0 w-16 sm:w-20 text-center snap-start group transition-all duration-200 ${
                                            isActive ? 'opacity-100' : 'opacity-60 hover:opacity-100'
                                        }`}
                                    >
                                        <span className={`flex items-center justify-center w-12 h-12 rounded-2xl transition-all duration-200 shadow-sm ${
                                            isActive
                                                ? 'bg-brand text-white shadow-brand/25 scale-110'
                                                : 'bg-gray-100 text-gray-500 group-hover:bg-gray-200 group-hover:text-gray-700'
                                        }`}>
                                            <Icon size={20} />
                                        </span>
                                        <span className={`text-[10px] sm:text-xs font-medium leading-tight line-clamp-2 transition-colors ${
                                            isActive ? 'text-brand' : 'text-gray-500'
                                        }`}>
                                            {category.name}
                                        </span>
                                    </button>
                                );
                            })}
                        </div>

                        {/* Scroll fade edges */}
                        <div className="pointer-events-none absolute left-0 top-0 h-full w-8 bg-linear-to-r from-white to-transparent z-10" />
                        <div className="pointer-events-none absolute right-0 top-0 h-full w-8 bg-linear-to-l from-white to-transparent z-10" />
                    </div>

                    {/* Toolbar: filters toggle + sort */}
                    <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
                        <button
                            type="button"
                            onClick={() => setShowFilters((prev) => !prev)}
                            className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold border transition-all ${
                                showFilters || activeFilterCount
                                    ? 'bg-brand/5 border-brand/20 text-brand'
                                    : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            <HiOutlineAdjustmentsHorizontal size={16} />
                            Filters
                            {activeFilterCount > 0 && (
                                <span className="inline-flex items-center justify-center min-w-5 h-5 px-1.5 rounded-full bg-brand text-white text-[10px] font-bold">
                                    {activeFilterCount}
                                </span>
                            )}
                            {showFilters ? <FaChevronUp size={11} /> : <FaChevronDown size={11} />}
                        </button>

                        <label className="flex items-center gap-2 text-sm">
                            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Sort</span>
                            <select
                                value={activeSort}
                                onChange={(e) => updateParams({ sort: e.target.value })}
                                className="rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm font-semibold text-gray-700 focus:border-brand focus:outline-none"
                            >
                                {SORT_OPTIONS.map((option) => (
                                    <option key={option.value || 'default'} value={option.value}>
                                        {option.label}
                                    </option>
                                ))}
                            </select>
                        </label>
                    </div>

                    {/* Advanced filters */}
                    {showFilters && (
                        <form
                            onSubmit={applyFilters}
                            className="bg-white border border-gray-100 rounded-2xl shadow-sm p-5 mb-6"
                        >
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                                <div>
                                    <label htmlFor="min_price" className="text-xs font-bold text-gray-600">Min price (₦)</label>
                                    <input
                                        id="min_price"
                                        type="number"
                                        min="0"
                                        value={draft.minPrice}
                                        onChange={(e) => setDraft({ ...draft, minPrice: e.target.value })}
                                        placeholder="0"
                                        className="mt-1.5 w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-brand focus:outline-none"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="max_price" className="text-xs font-bold text-gray-600">Max price (₦)</label>
                                    <input
                                        id="max_price"
                                        type="number"
                                        min="0"
                                        value={draft.maxPrice}
                                        onChange={(e) => setDraft({ ...draft, maxPrice: e.target.value })}
                                        placeholder="Any"
                                        className="mt-1.5 w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-brand focus:outline-none"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="filter_condition" className="text-xs font-bold text-gray-600">Condition</label>
                                    <select
                                        id="filter_condition"
                                        value={draft.condition}
                                        onChange={(e) => setDraft({ ...draft, condition: e.target.value })}
                                        className="mt-1.5 w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-brand focus:outline-none"
                                    >
                                        <option value="">Any condition</option>
                                        {CONDITION_CHOICES.map((option) => (
                                            <option key={option.value} value={option.value}>{option.label}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label htmlFor="filter_state" className="text-xs font-bold text-gray-600">State</label>
                                    <select
                                        id="filter_state"
                                        value={draft.state}
                                        onChange={(e) => setDraft({ ...draft, state: e.target.value, city: '' })}
                                        className="mt-1.5 w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-brand focus:outline-none"
                                    >
                                        <option value="">All states</option>
                                        {STATE_CHOICES.map((option) => (
                                            <option key={option.value} value={option.value}>{option.label}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label htmlFor="filter_city" className="text-xs font-bold text-gray-600">City</label>
                                    <input
                                        id="filter_city"
                                        type="text"
                                        value={draft.city}
                                        onChange={(e) => setDraft({ ...draft, city: e.target.value })}
                                        placeholder="e.g. Ikeja"
                                        className="mt-1.5 w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm focus:border-brand focus:outline-none"
                                    />
                                </div>

                                <div className="sm:col-span-2 lg:col-span-3 flex flex-wrap items-center gap-x-6 gap-y-2 self-end">
                                    <label className="inline-flex items-center gap-2 text-sm font-medium text-gray-600">
                                        <input
                                            type="checkbox"
                                            checked={draft.delivery}
                                            onChange={(e) => setDraft({ ...draft, delivery: e.target.checked })}
                                            className="h-4 w-4 rounded border-gray-300 text-brand focus:ring-brand"
                                        />
                                        Delivery available
                                    </label>
                                    <label className="inline-flex items-center gap-2 text-sm font-medium text-gray-600">
                                        <input
                                            type="checkbox"
                                            checked={draft.verified}
                                            onChange={(e) => setDraft({ ...draft, verified: e.target.checked })}
                                            className="h-4 w-4 rounded border-gray-300 text-brand focus:ring-brand"
                                        />
                                        Verified sellers only
                                    </label>
                                    <label className="inline-flex items-center gap-2 text-sm font-medium text-gray-600">
                                        <input
                                            type="checkbox"
                                            checked={draft.negotiable}
                                            onChange={(e) => setDraft({ ...draft, negotiable: e.target.checked })}
                                            className="h-4 w-4 rounded border-gray-300 text-brand focus:ring-brand"
                                        />
                                        Negotiable
                                    </label>
                                </div>
                            </div>

                            <div className="flex items-center justify-end gap-2 mt-5 pt-4 border-t border-gray-100">
                                <button
                                    type="button"
                                    onClick={resetFilters}
                                    className="px-4 py-2.5 rounded-xl text-sm font-bold text-gray-500 hover:bg-gray-100 transition-colors"
                                >
                                    Reset filters
                                </button>
                                <button
                                    type="submit"
                                    className="px-5 py-2.5 rounded-xl bg-brand text-white text-sm font-bold hover:opacity-90 transition-opacity"
                                >
                                    Apply filters
                                </button>
                            </div>
                        </form>
                    )}

                    {/* Active Filters */}
                    {(searchQuery || activeCategory || activeSubCategory || activeFilterCount > 0) && (
                        <div className="flex items-center gap-2 mb-6 flex-wrap">
                            <span className="flex items-center gap-1.5 text-xs font-bold text-gray-400 uppercase tracking-wider">
                                <HiOutlineFunnel size={14} />
                                Filters:
                            </span>

                            {searchQuery && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brand/10 text-brand text-xs font-bold">
                                    Search: {searchQuery}
                                    <button onClick={() => removeParam('search')} className="hover:text-gray-700">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            {activeCategory && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brand/10 text-brand text-xs font-bold">
                                    {activeCategory.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                    <button onClick={() => removeParam('category')} className="hover:text-gray-700">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            {activeSubCategory && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100 text-xs font-bold">
                                    {activeSubCategoryName}
                                    <button onClick={() => removeParam('sub_category')} className="hover:text-gray-700">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            {filters.condition && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-100 text-gray-700 text-xs font-bold capitalize">
                                    {filters.condition}
                                    <button onClick={() => removeParam('condition')} className="hover:text-gray-900">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            {filters.state && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-100 text-gray-700 text-xs font-bold capitalize">
                                    {stateLabel(filters.state)}
                                    <button onClick={() => removeParam('state')} className="hover:text-gray-900">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            {filters.city && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-100 text-gray-700 text-xs font-bold capitalize">
                                    {filters.city.replace(/_/g, ' ')}
                                    <button onClick={() => removeParam('city')} className="hover:text-gray-900">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            {(filters.min_price || filters.max_price) && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-100 text-gray-700 text-xs font-bold">
                                    ₦{Number(filters.min_price || 0).toLocaleString()} – {filters.max_price ? `₦${Number(filters.max_price).toLocaleString()}` : 'Any'}
                                    <button
                                        onClick={() => updateParams({ min_price: '', max_price: '' })}
                                        className="hover:text-gray-900"
                                    >
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            {filters.delivery_available && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100 text-xs font-bold">
                                    Delivery
                                    <button onClick={() => removeParam('delivery_available')} className="hover:text-emerald-900">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            {filters.verified_seller && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100 text-xs font-bold">
                                    Verified sellers
                                    <button onClick={() => removeParam('verified_seller')} className="hover:text-emerald-900">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            {filters.negotiable && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-100 text-gray-700 text-xs font-bold">
                                    Negotiable
                                    <button onClick={() => removeParam('negotiable')} className="hover:text-gray-900">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            <button
                                onClick={clearAll}
                                className="text-xs font-bold text-gray-400 hover:text-red-500 transition-colors ml-1"
                            >
                                Clear all
                            </button>
                        </div>
                    )}

                    {/* Results count */}
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold text-gray-900">
                            {activeSubCategory
                                ? activeSubCategoryName
                                : activeCategory
                                    ? activeCategory.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                                    : 'All Products'
                            }
                        </h2>
                        {!fetchProducts.isLoading && (
                            <span className="text-sm font-medium text-gray-400">
                                {totalCount.toLocaleString()} product{totalCount !== 1 ? 's' : ''}
                            </span>
                        )}
                    </div>

                    {/* Grid */}
                    {fetchProducts.isLoading ? (
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                            <SkeletonProductCard />
                            <SkeletonProductCard />
                            <SkeletonProductCard />
                            <SkeletonProductCard />
                        </div>
                    ) : results.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20 text-center">
                            <div className="w-20 h-20 rounded-2xl bg-gray-50 flex items-center justify-center mb-5">
                                <HiOutlineSearch size={32} className="text-gray-300" />
                            </div>
                            <h3 className="text-lg font-bold text-gray-900">No products found</h3>
                            <p className="text-sm text-gray-500 mt-1.5 max-w-sm">
                                {searchQuery
                                    ? `We couldn't find anything matching "${searchQuery}". Try different keywords or browse by category.`
                                    : activeSubCategory || activeCategory || activeFilterCount
                                        ? 'No listings match these filters right now. Try removing a filter or browsing another category.'
                                        : 'No listings available right now. Check back later.'
                                }
                            </p>
                            {(searchQuery || activeCategory || activeSubCategory || activeFilterCount > 0) && (
                                <button
                                    onClick={clearAll}
                                    className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-brand hover:underline"
                                >
                                    Clear filters and try again
                                </button>
                            )}
                        </div>
                    ) : (
                        <>
                            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                                {results.map((product) => (
                                    <ProductCard key={product.id} {...product} />
                                ))}
                            </div>

                            <Pagination
                                page={page}
                                count={totalCount}
                                pageSize={PAGE_SIZE}
                                onChange={handlePageChange}
                                className="mt-10"
                            />

                            {totalPages > 1 && (
                                <p className="text-center text-xs text-gray-400 mt-3">
                                    Page {page} of {totalPages}
                                </p>
                            )}
                        </>
                    )}
                </div>
            </div>

            <Spacer space={'mt-20'} />
            <Footer />
        </>
    );
};

export default Products;
