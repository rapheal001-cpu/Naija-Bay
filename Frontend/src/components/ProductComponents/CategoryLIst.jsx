import { useEffect, useState } from 'react';
import { FaChevronLeft, FaTimes } from 'react-icons/fa';
import { categoryIconsMap } from '@/dummyData.js';
import { setSubCategories } from '@/slice/CategorySlice.js';
import SkeletonCategories from '@/skeletons/SkeletonCategories.jsx';
import { useSelector, useDispatch } from 'react-redux';
import { useFetchCategories } from '../../hooks/UseQuery';
import { setCategories } from '@/slice/CategorySlice.js';
import { useNavigate } from 'react-router-dom';

const CategoryList = () => {
    const categories = useSelector((state) => state.categories.categories) || [];
    const sub_categories = useSelector((state) => state.categories.sub_categories)|| [];

    const dispatch = useDispatch();
    const navigate = useNavigate();

    const [openCategory, setOpenCategory] = useState(false);
    const [selectedCategory, setSelectedCategory] = useState(null);

    const fetchCategories = useFetchCategories(categories);

    useEffect(() => {
        if (fetchCategories.isSuccess && fetchCategories.data) {
            dispatch(setCategories(fetchCategories.data));
        }
    }, [fetchCategories.isSuccess, fetchCategories.data, dispatch]);

    const toggleSubCategories = (category_slug) => {
        const category = categories.find((c) => c.slug === category_slug);

        if (!category) {
            navigate('/products');
            return;
        }

        const isSameCategory = selectedCategory?.slug === category.slug;

        if (isSameCategory) {
            // Toggle open/close for the same category
            setOpenCategory((prev) => !prev);
        } else {
            // Open modal and switch to the new category
            setOpenCategory(true);
            setSelectedCategory(category);
            dispatch(setSubCategories(category.sub_categories ?? []));
        }
    };

    const activeSlug = selectedCategory?.slug;

    const handleSubCategory = (sub_category_slug) => {
        navigate(
            sub_category_slug
                ? `/products?sub_category=${encodeURIComponent(sub_category_slug)}`
                : '/products'
        );
        setOpenCategory(false);
    };

    return (
        <div className="relative border-b border-gray-100 bg-white">
            {/* Category Scroll Bar */}
            <div className="w-full flex lg:justify-center gap-2 sm:gap-4 overflow-x-auto scroll-smooth snap-x px-4 py-5 scrollbar-hide">
                {fetchCategories.isLoading ? (
                    <SkeletonCategories />
                ) : (
                    categories.map((category) => {
                        const Icon = categoryIconsMap[category.slug] ?? categoryIconsMap['default_icon'];
                        const isActive = activeSlug === category.slug;

                        return (
                            <button
                                key={category.slug}
                                onClick={() => toggleSubCategories(category.slug)}
                                aria-pressed={isActive}
                                className={`flex flex-col items-center gap-2.5 shrink-0 w-20 text-center snap-start group transition-all duration-200 ${
                                    isActive ? 'opacity-100' : 'opacity-70 hover:opacity-100'
                                }`}
                            >
                                <span
                                    className={`flex items-center justify-center w-12 h-12 rounded-2xl transition-all duration-200 shadow-sm ${
                                        isActive
                                            ? 'bg-brand text-white shadow-brand/25 scale-110'
                                            : 'bg-gray-100 text-gray-500 group-hover:bg-gray-200 group-hover:text-gray-700'
                                    }`}
                                >
                                    <Icon size={20} strokeWidth={1.5} />
                                </span>
                                <span
                                    className={`text-[10px] sm:text-xs font-medium leading-tight line-clamp-2 transition-colors ${
                                        isActive ? 'text-brand' : 'text-gray-500'
                                    }`}
                                >
                                    {category.name}
                                </span>
                            </button>
                        );
                    })
                )}
            </div>

            {/* Scroll fade edges */}
            <div className="pointer-events-none absolute left-0 top-0 h-full w-8 bg-linear-to-r from-white to-transparent z-10" />
            <div className="pointer-events-none absolute right-0 top-0 h-full w-8 bg-linear-to-l from-white to-transparent z-10" />

            {/* Sub Categories Overlay */}
            <div
                className={`fixed inset-0 z-50 flex items-start justify-center pt-10 sm:pt-20 px-4 pb-4 transition-all duration-300 ${
                    openCategory
                        ? 'opacity-100 pointer-events-auto'
                        : 'opacity-0 pointer-events-none'
                }`}
            >
                {/* Backdrop */}
                <div
                    className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
                    onClick={() => setOpenCategory(false)}
                />

                {/* Modal */}
                <div
                    className={`relative w-full max-w-3xl bg-white rounded-3xl shadow-2xl overflow-hidden transition-all duration-300 ${
                        openCategory ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
                    }`}
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100 bg-gray-50/50">
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => setOpenCategory(false)}
                                className="flex items-center justify-center w-9 h-9 rounded-full bg-white border border-gray-200 text-gray-600 hover:bg-gray-100 hover:border-gray-300 transition-all shadow-sm"
                                aria-label="Back"
                            >
                                <FaChevronLeft className="w-4 h-4" />
                            </button>

                            <div className="flex items-center gap-3">
                                {selectedCategory && (
                                    <span className="flex items-center justify-center w-10 h-10 rounded-xl bg-brand/10 text-brand">
                                        {(() => {
                                            const Icon =
                                                categoryIconsMap[selectedCategory.slug] ??
                                                categoryIconsMap['default_icon'];
                                            return <Icon size={20} strokeWidth={1.5} />;
                                        })()}
                                    </span>
                                )}
                                <div>
                                    <p className="text-[11px] text-gray-400 font-semibold uppercase tracking-wider">
                                        Browse Category
                                    </p>
                                    <h3 className="text-lg font-bold text-gray-900">
                                        {selectedCategory?.name}
                                    </h3>
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={() => setOpenCategory(false)}
                            className="flex items-center justify-center w-9 h-9 rounded-full bg-white border border-gray-200 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-all shadow-sm"
                            aria-label="Close"
                        >
                            <FaTimes className="w-4 h-4" />
                        </button>
                    </div>

                    {/* Subcategory Grid */}
                    <div className="max-h-[60vh] overflow-y-auto p-6 bg-white">
                        {sub_categories.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                                <p className="text-sm">No subcategories found</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                                {sub_categories.map((subCategory) => {
                                    const ParentIcon =
                                        categoryIconsMap[selectedCategory?.slug] ??
                                        categoryIconsMap['default_icon'];

                                    return (
                                        <button
                                            key={subCategory.slug}
                                            onClick={() => handleSubCategory(subCategory.slug)}
                                            aria-label={`Browse ${subCategory.name}`}
                                            className="group flex flex-col items-center gap-3.5 rounded-2xl border border-gray-100 bg-gray-50/30 p-5 hover:border-brand/20 hover:bg-brand/5 hover:shadow-md hover:shadow-brand/5 transition-all duration-200"
                                        >
                                            <span className="flex items-center justify-center w-14 h-14 rounded-2xl bg-white border border-gray-100 text-gray-300 group-hover:text-brand group-hover:border-brand/20 group-hover:bg-brand/5 shadow-sm transition-all duration-200">
                                                <ParentIcon size={24} strokeWidth={1.5} />
                                            </span>
                                            <span className="text-sm font-semibold text-gray-700 group-hover:text-brand line-clamp-2 text-center leading-snug">
                                                {subCategory.name}
                                            </span>
                                        </button>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* Footer hint */}
                    <div className="px-6 py-3 bg-gray-50 border-t border-gray-100 text-center">
                        <p className="text-[11px] text-gray-400 font-medium">
                            Select a subcategory to explore products
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CategoryList;