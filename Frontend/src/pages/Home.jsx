import { Link } from 'react-router-dom'
import Header from "../components/HeaderComponents/Header.jsx";
import Spacer from "../components/Spacer.jsx";
import Search from "../components/HeaderComponents/Search.jsx";
import ProductCard from "../components/ProductComponents/ProductCard";
import { FaArrowRight } from "react-icons/fa";
import CategoryLIst from "../components/ProductComponents/CategoryLIst";
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useFetchFeaturedProductData, useFetchUserData } from '../hooks/UseQuery';
import { setUser } from '../slice/UserSlice.js';
import { setFeaturedProducts } from '../slice/ProductSlice.js';
import SkeletonProductCard from '../skeletons/SkeletonProductCard';


const Home = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const featuredProducts = useSelector((state) => state.products.featuredProducts);

    const dispatch = useDispatch();

    const fetchUser = useFetchUserData(isAuthenticated);
    const fetchFeaturedProducts = useFetchFeaturedProductData();

    useEffect(() => {
        if (fetchUser.isSuccess && fetchUser.data) {
            dispatch(setUser(fetchUser.data));
        }
    }, [fetchUser.isSuccess, fetchUser.data, dispatch]);

    useEffect(() => {
        if (fetchFeaturedProducts.isSuccess && fetchFeaturedProducts.data) {
            dispatch(setFeaturedProducts(fetchFeaturedProducts.data));
        }
    }, [fetchFeaturedProducts.isSuccess, fetchFeaturedProducts.data, dispatch]);

    return (
        <>
            <Header />
            <Spacer space={'mb-20'} />

            <Search />
            <CategoryLIst />

            {/* Featured Section */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
                {/* Section Header */}
                <div className="flex items-end justify-between mb-8">
                    <div>
                        <p className="text-xs font-bold text-brand uppercase tracking-[0.15em] mb-1.5">
                            Curated for you
                        </p>
                        <h2 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">
                            Featured Ads
                            <span className="ml-2 text-lg font-medium text-gray-400">
                                ({featuredProducts.length})
                            </span>
                        </h2>
                    </div>

                    <Link
                        to="/products"
                        className="group flex items-center gap-2 text-sm font-bold text-brand hover:gap-3 transition-all duration-300"
                    >
                        Browse all
                        <span className="flex items-center justify-center w-7 h-7 rounded-full bg-brand/10 group-hover:bg-brand group-hover:text-white transition-all duration-300">
                            <FaArrowRight size={12} />
                        </span>
                    </Link>
                </div>

                <div className="w-full h-px bg-gray-100 mb-8" />

                {/* Grid */}
                {fetchFeaturedProducts.isLoading ? (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                        <SkeletonProductCard />
                    </div>
                ) : featuredProducts.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 text-center">
                        <div className="w-20 h-20 rounded-2xl bg-gray-50 flex items-center justify-center mb-5">
                            <svg className="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-bold text-gray-900">No featured ads yet</h3>
                        <p className="text-sm text-gray-500 mt-1.5 max-w-sm">
                            We're curating the best listings for you. Check back soon for amazing deals.
                        </p>
                        <Link
                            to="/products"
                            className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-brand hover:underline"
                        >
                            Explore all products <FaArrowRight size={12} />
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                        {featuredProducts.map((product) => (
                            <ProductCard key={product.id} {...product} />
                        ))}
                    </div>
                )}

            </section>
        </>
    )
}

export default Home;