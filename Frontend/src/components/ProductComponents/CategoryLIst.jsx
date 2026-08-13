import { useEffect, useState } from 'react';
import { FaChevronLeft, FaTimes } from 'react-icons/fa';
import { BiSolidCategory } from 'react-icons/bi';
import { categoryIconsMap, subcategoryIconsMap } from '../../dummyData';
import { setSubCategories, setCategories } from '@/slice/CategorySlice.js';
import SkeletonCategories from '@/skeletons/SkeletonCategories.jsx';
import { useSelector, useDispatch } from 'react-redux';
import { useFetchCategories } from '../../hooks/UseQuery';
import { useNavigate } from 'react-router-dom';

const DEFAULT_ICON = BiSolidCategory;

const CategoryList = () => {
    const categories = useSelector((state) => state.categories.categories) || [];
    const sub_categories = useSelector((state) => state.categories.subCategories) || [];

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

    const activeSlug = selectedCategory?.slug;

    const toggleSubCategories = (category_slug) => {
        const category = categories.find((c) => c.slug === category_slug);

        if (!category) {
            navigate('/products');
            return;
        }

        const isSameCategory = activeSlug === category.slug;

        if (isSameCategory) {
            setOpenCategory((prev) => !prev);
        } else {
            setOpenCategory(true);
            setSelectedCategory(category);
            dispatch(setSubCategories(category.sub_categories ?? []));
        }
    };

    const handleSubCategory = (sub_category_slug) => {
        navigate(
            sub_category_slug
                ? `/products?sub_category=${encodeURIComponent(sub_category_slug)}`
                : '/products'
        );
        setOpenCategory(false);
    };

    const getCategoryIcon = (slug) => categoryIconsMap[slug] ?? DEFAULT_ICON;
    const getSubCategoryIcon = (slug) => subcategoryIconsMap[slug] ?? DEFAULT_ICON;

    return (
        <div className="relative border-b border-gray-100 bg-white">
            {/* Category Scroll Bar */}
            <div className="relative">
                <div className="w-full flex lg:justify-center gap-3 sm:gap-5 overflow-x-auto scroll-smooth snap-x px-4 py-5 scrollbar-hide">
                    {fetchCategories.isLoading ? (
                        <SkeletonCategories />
                    ) : (
                        categories.map((category) => {
                            const Icon = getCategoryIcon(category.slug);
                            const isActive = activeSlug === category.slug && openCategory;

                            return (
                                <button
                                    key={category.slug}
                                    onClick={() => toggleSubCategories(category.slug)}
                                    aria-pressed={isActive}
                                    className="flex flex-col items-center gap-2 shrink-0 w-[76px] text-center snap-start group"
                                >
                                    <span
                                        className={`flex items-center justify-center w-12 h-12 rounded-full border transition-all duration-200 ${
                                            isActive
                                                ? 'bg-brand border-brand text-white shadow-lg shadow-brand/20'
                                                : 'bg-white border-gray-200 text-gray-500 group-hover:border-brand/40 group-hover:text-brand group-hover:shadow-sm'
                                        }`}
                                    >
                                        <Icon size={19} strokeWidth={1.6} />
                                    </span>
                                    <span
                                        className={`text-[11px] font-medium leading-tight line-clamp-2 transition-colors ${
                                            isActive ? 'text-brand' : 'text-gray-600 group-hover:text-gray-900'
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
                <div className="pointer-events-none absolute left-0 top-0 h-full w-10 bg-linear-to-r from-white to-transparent" />
                <div className="pointer-events-none absolute right-0 top-0 h-full w-10 bg-linear-to-l from-white to-transparent" />
            </div>

            {/* Sub Categories Overlay */}
            {openCategory && (
                <div
                    className="fixed inset-0 z-50 flex items-start justify-center pt-10 sm:pt-20 px-4 pb-4"
                    role="dialog"
                    aria-modal="true"
                >
                    {/* Backdrop */}
                    <div
                        className="absolute inset-0 bg-gray-900/40 backdrop-blur-[2px] animate-in fade-in duration-200"
                        onClick={() => setOpenCategory(false)}
                    />

                    {/* Modal */}
                    <div className="relative w-full max-w-3xl bg-white rounded-2xl shadow-xl ring-1 ring-black/5 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                        {/* Header */}
                        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                            <div className="flex items-center gap-3 min-w-0">
                                <button
                                    onClick={() => setOpenCategory(false)}
                                    className="flex items-center justify-center w-9 h-9 rounded-full text-gray-500 hover:bg-gray-100 transition-colors shrink-0"
                                    aria-label="Back"
                                >
                                    <FaChevronLeft className="w-3.5 h-3.5" />
                                </button>

                                <div className="flex items-center gap-3 min-w-0">
                                    {selectedCategory && (
                                        <span className="flex items-center justify-center w-9 h-9 rounded-full bg-brand/10 text-brand shrink-0">
                                            {(() => {
                                                const Icon = getCategoryIcon(selectedCategory.slug);
                                                return <Icon size={18} strokeWidth={1.6} />;
                                            })()}
                                        </span>
                                    )}
                                    <div className="min-w-0">
                                        <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">
                                            Browse category
                                        </p>
                                        <h3 className="text-base font-bold text-gray-900 truncate">
                                            {selectedCategory?.name}
                                        </h3>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={() => setOpenCategory(false)}
                                className="flex items-center justify-center w-9 h-9 rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors shrink-0"
                                aria-label="Close"
                            >
                                <FaTimes className="w-3.5 h-3.5" />
                            </button>
                        </div>

                        {/* Subcategory Grid */}
                        <div className="max-h-[60vh] overflow-y-auto p-5">
                            {sub_categories.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-14 text-gray-400 gap-2">
                                    <BiSolidCategory size={28} className="text-gray-300" />
                                    <p className="text-sm">No subcategories found</p>
                                </div>
                            ) : (
                                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                                    {sub_categories.map((subCategory) => {
                                        const SubIcon = getSubCategoryIcon(subCategory?.slug);

                                        return (
                                            <button
                                                key={subCategory.slug}
                                                onClick={() => handleSubCategory(subCategory.slug)}
                                                aria-label={`Browse ${subCategory.name}`}
                                                className="group flex flex-col items-center gap-3 rounded-xl border border-gray-100 p-4 hover:border-brand/30 hover:bg-brand/[0.03] transition-all duration-150"
                                            >
                                                <span className="flex items-center justify-center w-11 h-11 rounded-full bg-gray-50 text-gray-400 group-hover:bg-brand/10 group-hover:text-brand transition-colors duration-150">
                                                    <SubIcon size={20} strokeWidth={1.6} />
                                                </span>
                                                <span className="text-[13px] font-medium text-gray-700 group-hover:text-brand line-clamp-2 text-center leading-snug">
                                                    {subCategory.name}
                                                </span>
                                            </button>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CategoryList;