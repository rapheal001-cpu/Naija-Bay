import { useEffect, useState, useMemo } from 'react';
import { HiOutlineFunnel } from 'react-icons/hi2';
import { HiOutlineSearch, HiOutlineX } from "react-icons/hi";
import { BiSolidCategory } from 'react-icons/bi';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';
import ProductCard from '../components/ProductComponents/ProductCard.jsx';
import SkeletonProductCard from '../skeletons/SkeletonProductCard.jsx';
import { useFetchCategories, useFetchProducts } from '../hooks/UseQuery.js';
import { useDispatch, useSelector } from 'react-redux';
import { setProducts } from '../slice/ProductSlice.js';
import { setCategories } from '../slice/CategorySlice.js';
import { useSearchParams } from 'react-router-dom';
import { categoryIconsMap } from '../dummyData.js';
import Footer from '../components/FooterComponents/Footer.jsx';


const Products = () => {
    const dispatch = useDispatch();

    const [searchParams, setSearchParams] = useSearchParams();
    const [searchInput, setSearchInput] = useState('');
    
    const searchQuery = searchParams.get('search') || '';
    const activeCategory = searchParams.get('category') || '';
    const activeSubCategory = searchParams.get('sub_category') || '';

    const products = useSelector((state) => state.products.products);
    const categories = useSelector((state) => state.categories.categories);
    
    const fetchProducts = useFetchProducts( searchQuery, activeCategory, activeSubCategory);
    const fetchCategories = useFetchCategories();

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

    useEffect(() => {
        if (fetchProducts.isSuccess && fetchProducts.data) {
            dispatch(setProducts(fetchProducts.data));
        }
    }, [fetchProducts.isSuccess, fetchProducts.data, dispatch]);

    useEffect(() => {
        if (fetchCategories.isSuccess && fetchCategories.data) {
            dispatch(setCategories(fetchCategories.data));
        }
    }, [fetchCategories.isSuccess, fetchCategories.data, dispatch]);

    const handleSearch = (e) => {
        e.preventDefault();
        const trimmed = searchInput.trim();
        const newParams = new URLSearchParams(searchParams);
        if (trimmed) {
            newParams.set('search', trimmed);
        } else {
            newParams.delete('search');
        }
        setSearchParams(newParams);
    };

    const handleCategoryClick = (slug) => {
        const newParams = new URLSearchParams(searchParams);
        if (activeCategory === slug) {
            newParams.delete('category');
        } else {
            newParams.set('category', slug);
        }
        // Changing parent category clears sub_category
        newParams.delete('sub_category');
        setSearchParams(newParams);
    };

    const clearFilters = () => {
        setSearchParams(new URLSearchParams());
        setSearchInput('');
    };

    const removeSearchFilter = () => {
        setSearchInput('');
        const newParams = new URLSearchParams(searchParams);
        newParams.delete('search');
        setSearchParams(newParams);
    };

    const removeCategoryFilter = () => {
        const newParams = new URLSearchParams(searchParams);
        newParams.delete('category');
        setSearchParams(newParams);
    };

    const removeSubCategoryFilter = () => {
        const newParams = new URLSearchParams(searchParams);
        newParams.delete('sub_category');
        setSearchParams(newParams);
    };

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
                            {products.length > 0 
                                ? `${products.length} product${products.length !== 1 ? 's' : ''} available` 
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
                                    onKeyDown={handleSearch}
                                />
                                {searchInput && (
                                    <button
                                        type="button"
                                        onClick={removeSearchFilter}
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
                    <div className="relative mb-8">
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

                    {/* Active Filters */}
                    {(searchQuery || activeCategory || activeSubCategory) && (
                        <div className="flex items-center gap-2 mb-6 flex-wrap">
                            <span className="flex items-center gap-1.5 text-xs font-bold text-gray-400 uppercase tracking-wider">
                                <HiOutlineFunnel size={14} />
                                Filters:
                            </span>
                            
                            {searchQuery && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brand/10 text-brand text-xs font-bold">
                                    Search: {searchQuery}
                                    <button onClick={removeSearchFilter} className="hover:text-gray-700">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}
                            
                            {activeCategory && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brand/10 text-brand text-xs font-bold">
                                    {activeCategory.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                    <button onClick={removeCategoryFilter} className="hover:text-gray-700">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}

                            {activeSubCategory && (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100 text-xs font-bold">
                                    {activeSubCategoryName}
                                    <button onClick={removeSubCategoryFilter} className="hover:text-gray-700">
                                        <HiOutlineX size={12} />
                                    </button>
                                </span>
                            )}
                            
                            <button
                                onClick={clearFilters}
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
                                    ? activeCategory.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                                    : 'All Products'
                            }
                        </h2>
                        {!fetchProducts.isLoading && (
                            <span className="text-sm font-medium text-gray-400">
                                {products.length} product{products.length !== 1 ? 's' : ''}
                            </span>
                        )}
                    </div>

                    {/* Grid */}
                    {fetchProducts.isLoading ? (
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                            <SkeletonProductCard />
                        </div>
                    ) : products.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20 text-center">
                            <div className="w-20 h-20 rounded-2xl bg-gray-50 flex items-center justify-center mb-5">
                                <HiOutlineSearch size={32} className="text-gray-300" />
                            </div>
                            <h3 className="text-lg font-bold text-gray-900">No products found</h3>
                            <p className="text-sm text-gray-500 mt-1.5 max-w-sm">
                                {searchQuery 
                                    ? `We couldn't find anything matching "${searchQuery}". Try different keywords or browse by category.`
                                    : activeSubCategory || activeCategory
                                        ? 'No listings available in this category right now. Check back later or browse other categories.'
                                        : 'No listings available right now. Check back later.'
                                }
                            </p>
                            {(searchQuery || activeCategory || activeSubCategory) && (
                                <button
                                    onClick={clearFilters}
                                    className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-brand hover:underline"
                                >
                                    Clear filters and try again
                                </button>
                            )}
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                            {products.map((product) => (
                                <ProductCard key={product.id} {...product} />
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <Spacer space={'mt-20'} />
            <Footer />
        </>
    );
};

export default Products;