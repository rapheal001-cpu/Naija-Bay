import { Link } from 'react-router-dom'
import Header from "../components/HeaderComponents/Header.jsx";
import PromoBar from "../components/HeaderComponents/PromoBar.jsx";
import Spacer from "../components/Spacer.jsx";
import Search from "../components/HeaderComponents/Search.jsx";
import ProductCard from "../components/ProductComponents/ProductCard";
import FlashDealsSection from "../components/ProductComponents/FlashDealsSection";
import { FaArrowRight, FaShieldAlt, FaHandshake, FaHeadset, FaClock, FaPlus } from "react-icons/fa";
import CategoryLIst from "../components/ProductComponents/CategoryLIst";
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useFetchFeaturedProductData, useFetchProducts, useFetchUserData } from '../hooks/UseQuery';
import { setUser } from '../slice/UserSlice.js';
import { setFeaturedProducts } from '../slice/ProductSlice.js';
import SkeletonProductCard from '../skeletons/SkeletonProductCard';
import Footer from '../components/FooterComponents/Footer.jsx';


const Home = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const featuredProducts = useSelector((state) => state.products.featuredProducts);

    const dispatch = useDispatch();

    const fetchUser = useFetchUserData(isAuthenticated);
    const fetchFeaturedProducts = useFetchFeaturedProductData();
    const fetchLatestProducts = useFetchProducts({ page: 1, page_size: 8 });

    const latestProducts = fetchLatestProducts.data?.results || [];

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
            <Spacer space={'mb-36 md:mb-28'} />

            <PromoBar />
            <Search />
            <CategoryLIst />

            <FlashDealsSection />

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

            {/* Latest Ads */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
                <div className="flex items-end justify-between mb-8">
                    <div>
                        <p className="text-xs font-bold text-brand uppercase tracking-[0.15em] mb-1.5 flex items-center gap-1.5">
                            <FaClock size={12} aria-hidden="true" />
                            Just posted
                        </p>
                        <h2 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">
                            Latest Ads
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

                {fetchLatestProducts.isLoading ? (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                        <SkeletonProductCard />
                        <SkeletonProductCard />
                        <SkeletonProductCard />
                        <SkeletonProductCard />
                    </div>
                ) : latestProducts.length === 0 ? (
                    <p className="text-center text-sm text-gray-500 py-10">
                        No listings yet — be the first to post an ad.
                    </p>
                ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                        {latestProducts.map((product) => (
                            <ProductCard key={product.id} {...product} />
                        ))}
                    </div>
                )}
            </section>

            {/* Promotional: sell CTA */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-14">
                <div className="relative overflow-hidden rounded-3xl bg-linear-to-r from-brand-green to-emerald-600 px-6 py-10 sm:px-10">
                    <div className="absolute -top-16 -right-16 w-56 h-56 bg-white/10 rounded-full blur-3xl" aria-hidden="true" />
                    <div className="relative flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                        <div>
                            <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                                Turn your stuff into cash
                            </h2>
                            <p className="text-white/80 text-sm sm:text-base mt-2 max-w-md leading-relaxed">
                                Post a free ad in minutes. Reach thousands of buyers across Nigeria — chat, negotiate and sell directly.
                            </p>
                        </div>
                        <Link
                            to={isAuthenticated ? "/sell" : "/sign-in"}
                            className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-white px-6 py-3.5 text-sm font-black text-brand-green shadow-lg transition-transform hover:scale-[1.03] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70"
                        >
                            <FaPlus size={14} aria-hidden="true" />
                            Post a free ad
                        </Link>
                    </div>
                </div>
            </section>

            {/* Why Naija-Bay trust strip */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-14">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {[
                        {
                            icon: FaShieldAlt,
                            title: 'Safe & secure trading',
                            text: 'Verified sellers, report abuse, and buyer safety tips on every listing.',
                        },
                        {
                            icon: FaHandshake,
                            title: 'Buy directly from sellers',
                            text: 'Chat, negotiate and agree on delivery — no middlemen, no hidden fees.',
                        },
                        {
                            icon: FaHeadset,
                            title: 'Support that shows up',
                            text: 'Real help when deals go wrong. Reach us anytime from the contact page.',
                        },
                    ].map(({ icon: Icon, title, text }) => (
                        <div key={title} className="flex items-start gap-4 bg-white border border-gray-100 rounded-2xl p-5 hover:shadow-lg hover:shadow-gray-200/50 transition-shadow">
                            <span className="flex items-center justify-center w-11 h-11 rounded-xl bg-brand/10 text-brand shrink-0">
                                <Icon size={20} />
                            </span>
                            <div>
                                <h3 className="text-sm font-bold text-gray-900">{title}</h3>
                                <p className="text-xs text-gray-500 mt-1 leading-relaxed">{text}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            <Spacer space={'mt-20'} />
            <Footer />
        </>
    )
}

export default Home;