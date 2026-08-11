import { useState } from 'react';
import Header from "../HeaderComponents/Header.jsx";
import Spacer from "../Spacer.jsx";
import ProductCard from "../ProductComponents/ProductCard.jsx";
import ProfileHeaderCard from "./ProfileHeaderCard.jsx";
import ProfileContactDetailCard from "./ProfileContactDetailCard.jsx";
import ProfileStatCard from "./ProfileStatCard.jsx";


const ProfileData = ({ profile, isOwnProfile }) => {
    const [activeTab, setActiveTab] = useState('active');

    const listings = profile?.products || [];
    const favoriteListings = profile?.favorite_products || [];

    const activeListings = listings.filter((p) => p.active && !p.sold);
    const soldListings = listings.filter((p) => p.sold && !p.active);
    const visibleListings = activeTab === 'active' ? activeListings : activeTab === 'sold' ? soldListings : favoriteListings;

    const tabs = [
        { key: 'active', label: 'Active', count: activeListings.length },
        { key: 'sold', label: 'Sold', count: soldListings.length },
        { key: 'favorite', label: favoriteListings.length === 1 ? 'Favorite' : 'Favorites', count: favoriteListings.length },
    ];

    return (
        <>
            <Header />
            <Spacer />

            <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <ProfileHeaderCard profile={profile} isOwnProfile={isOwnProfile} />

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
                    <div className="lg:col-span-2">
                        <ProfileContactDetailCard profile={profile} isOwnProfile={isOwnProfile} />
                    </div>
                    <div className="lg:col-span-1">
                        <ProfileStatCard 
                            activeListings={activeListings} 
                            soldListings={soldListings} 
                            favoriteListings={favoriteListings} 
                        />
                    </div>
                </div>

                <div className="mt-10">
                    <div className="flex items-center justify-between mb-1">
                        <h2 className="text-lg font-bold text-gray-900">Products</h2>
                        <span className="text-sm font-medium text-gray-400">
                            {visibleListings.length} {activeTab === 'favorite' ? (visibleListings.length === 1 ? 'Product' : 'Products') : (visibleListings.length === 1 ? 'Product' : 'Products')}
                        </span>
                    </div>

                    <div className="flex items-center gap-1 p-1 bg-gray-100 rounded-xl w-fit mt-4">
                        {tabs.map((tab) => (
                            <button
                                key={tab.key}
                                type="button"
                                onClick={() => setActiveTab(tab.key)}
                                className={`
                                    relative px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200
                                    ${activeTab === tab.key 
                                        ? 'bg-white text-brand shadow-sm' 
                                        : 'text-gray-500 hover:text-gray-700'
                                    }
                                `}
                            >
                                {tab.label}
                                <span className={`
                                    ml-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full transition-colors
                                    ${activeTab === tab.key ? 'bg-brand/10 text-brand' : 'bg-gray-200 text-gray-500'}
                                `}>
                                    {tab.count}
                                </span>
                            </button>
                        ))}
                    </div>

                    <div className="w-full h-px bg-gray-100 mt-6 mb-6" />

                    {visibleListings.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16 text-center">
                            <div className="w-16 h-16 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
                                <svg className="w-7 h-7 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                </svg>
                            </div>
                            <h3 className="text-base font-bold text-gray-900">
                                No {tabs.find(t => t.key === activeTab)?.label.toLowerCase()} yet
                            </h3>
                            <p className="text-sm text-gray-400 mt-1 max-w-xs">
                                {activeTab === 'favorite' 
                                    ? "Products you save will appear here for quick access." 
                                    : "Listings will show up here once they're published."}
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                            {visibleListings.map((product) => (
                                <ProductCard key={product.id} {...product} />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
};

export default ProfileData;