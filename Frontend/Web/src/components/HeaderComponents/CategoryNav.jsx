import { useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useFetchCategories } from '../../hooks/UseQuery.js';
import { setCategories } from '../../slice/CategorySlice.js';

/**
 * Secondary header row: SEO-friendly category links + core marketplace links.
 * Category clicks land on `/:category` (handled by the Products page).
 */
const CategoryNav = () => {
    const categories = useSelector((state) => state.categories.categories) || [];
    const dispatch = useDispatch();
    const location = useLocation();
    const fetchCategories = useFetchCategories();

    useEffect(() => {
        if (fetchCategories.isSuccess && fetchCategories.data) {
            dispatch(setCategories(fetchCategories.data));
        }
    }, [fetchCategories.isSuccess, fetchCategories.data, dispatch]);

    const isActive = (to) => location.pathname === to;

    const linkClass = (active) =>
        `flex shrink-0 items-center rounded-lg px-3 py-1.5 text-[13px] font-semibold transition-colors ${
            active
                ? 'bg-white text-brand shadow-sm'
                : 'text-white/85 hover:bg-white/10 hover:text-white'
        }`;

    return (
        <nav aria-label="Categories" className="border-t border-white/15 bg-brand">
            <div className="mx-auto flex max-w-7xl items-center gap-1 overflow-x-auto px-4 py-2 scrollbar-hide lg:px-8">
                <NavLink to="/products" className={linkClass(isActive('/products'))}>
                    All Ads
                </NavLink>
                {categories.map((category) => (
                    <NavLink
                        key={category.slug}
                        to={`/${category.slug}`}
                        className={linkClass(isActive(`/${category.slug}`))}
                    >
                        {category.name}
                    </NavLink>
                ))}
                <span className="mx-2 h-4 w-px shrink-0 bg-white/20" aria-hidden="true" />
                <NavLink to="/my-ads" className={linkClass(isActive('/my-ads'))}>
                    My Ads
                </NavLink>
            </div>
        </nav>
    );
};

export default CategoryNav;
