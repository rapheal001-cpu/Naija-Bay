import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    HiBadgeCheck,
    HiOutlineLocationMarker,
    HiOutlinePhone,
    HiOutlineMail,
    HiOutlineUsers,
    HiOutlineCalendar,
    HiOutlinePencil,
    HiOutlineShare,
    HiOutlineExternalLink,
} from 'react-icons/hi';
import { RiStore2Line, RiLoader4Line } from 'react-icons/ri';
import { FaWhatsapp } from 'react-icons/fa';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';
import ProductCard from '../components/ProductComponents/ProductCard.jsx';
import { useFetchStoreDetail } from '../hooks/UseQuery.js';
import { setStoreDetail, storeDetail } from '../slice/StoreSlice.js'
import { formatDate } from '../dummyData.js';


const StoreDetail = () => {
    const { store_slug } = useParams();

    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);
    const store = useSelector((state) => state.store.storeDetail);

    const dispatch = useDispatch()

    const [activeTab, setActiveTab] = useState('products');

    const fetchStoreDetail = useFetchStoreDetail(store_slug)

    useEffect(() => {
        if (fetchStoreDetail.isSuccess && fetchStoreDetail.data) {
            dispatch(setStoreDetail(fetchStoreDetail.data));
        }
    }, [fetchStoreDetail.isSuccess, fetchStoreDetail.data, dispatch])

    const isOwnStore = user?.id === store?.store_user?.id;
    const isVerified = store?.store_user?.verified ?? false;

    const tabs = [
        { id: 'products', label: 'Products', count: store?.products?.length ?? 0 },
        { id: 'about', label: 'About' },
        { id: 'members', label: 'Members', count: store?.total_members ?? 0 },
    ];

    if (fetchStoreDetail.isLoading) {
        return (
            <>
                <Header />
                <Spacer space="mb-20" />
                <div className="min-h-[60vh] flex items-center justify-center">
                    <RiLoader4Line className="animate-spin text-brand" size={40} />
                </div>
            </>
        );
    }

    return (
        <>
            <Header />
            <Spacer space="mb-20" />

            <div className="min-h-screen bg-[#FAF9F6] pb-16">
                <div className="max-w-5xl mx-auto px-4">

                    {/* ==================== HERO SECTION ==================== */}
                    <div className="relative bg-white border border-gray-100 rounded-3xl shadow-sm overflow-hidden">
                        {/* Banner */}
                        <div className="h-40 sm:h-52 bg-gradient-to-r from-brand to-brand/80 relative">
                            {store.banner ? (
                                <img
                                    src={store.banner}
                                    alt={`${store.store_name} banner`}
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                <div className="w-full h-full bg-gradient-to-br from-brand to-brand/60" />
                            )}
                            <div className="absolute inset-0 bg-black/10" />
                        </div>

                        <div className="px-5 sm:px-8 pb-6 sm:pb-8">
                            {/* Logo + Name + Actions */}
                            <div className="flex flex-col sm:flex-row sm:items-end gap-4 -mt-12 sm:-mt-14">
                                {/* Logo */}
                                <div className="relative shrink-0">
                                    <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-white border-4 border-white shadow-lg overflow-hidden">
                                        {store.logo ? (
                                            <img
                                                src={store.logo}
                                                alt={store.store_name}
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center bg-gray-50">
                                                <RiStore2Line className="text-gray-300" size={36} />
                                            </div>
                                        )}
                                    </div>
                                    {isVerified && (
                                        <span className="absolute -bottom-1.5 -right-1.5 bg-emerald-500 text-white rounded-full p-1 border-2 border-white shadow-sm">
                                            <HiBadgeCheck size={16} />
                                        </span>
                                    )}
                                </div>

                                {/* Name & Meta */}
                                <div className="flex-1 min-w-0 sm:pb-1">
                                    <div className="flex items-center gap-2 flex-wrap">
                                        <h1 className="text-xl sm:text-2xl font-black text-gray-900 tracking-tight">
                                            {store.store_name}
                                        </h1>
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider bg-gray-100 text-gray-500 border border-gray-200">
                                            {store.store_type === 'registered' ? 'Registered Business' : 'Individual Seller'}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-400 font-medium mt-0.5">
                                        @{store.store_slug}
                                    </p>
                                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                                        <span className="inline-flex items-center gap-1">
                                            <HiOutlineLocationMarker size={13} />
                                            {store.city}, {store.state}
                                        </span>
                                        <span className="inline-flex items-center gap-1">
                                            <HiOutlineCalendar size={13} />
                                            Since {formatDate(store.created_at)}
                                        </span>
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex items-center gap-2 sm:pb-1 flex-wrap">
                                    {isOwnStore ? (
                                        <>
                                            <Link
                                                to={`/store/${store_slug}/edit`}
                                                className="flex items-center gap-2 font-semibold rounded-xl px-5 py-2.5 text-sm bg-brand text-white hover:opacity-90 active:scale-95 transition-all shadow-sm"
                                            >
                                                <HiOutlinePencil size={16} />
                                                Edit Store
                                            </Link>
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    navigator.clipboard.writeText(window.location.href);
                                                    // toast.success('Link copied!');
                                                }}
                                                className="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 text-gray-600 hover:bg-gray-100 transition-all"
                                            >
                                                <HiOutlineShare size={17} />
                                            </button>
                                        </>
                                    ) : (
                                        <>
                                            <a
                                                href={`https://wa.me/${store.store_whatsapp_number?.replace(/\D/g, '')}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="flex items-center gap-2 font-semibold rounded-xl px-5 py-2.5 text-sm bg-emerald-500 text-white hover:bg-emerald-600 active:scale-95 transition-all shadow-sm shadow-emerald-500/20"
                                            >
                                                <FaWhatsapp size={16} />
                                                Chat
                                            </a>
                                            <Link
                                                to={`/profile/${store.store_user?.id}`}
                                                className="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 text-gray-600 hover:bg-gray-100 transition-all"
                                                title="View Owner Profile"
                                            >
                                                <HiOutlineExternalLink size={17} />
                                            </Link>
                                        </>
                                    )}
                                </div>
                            </div>

                            {/* Contact Chips */}
                            <div className="flex flex-wrap items-center gap-2 mt-5">
                                {store.store_email && (
                                    <a
                                        href={`mailto:${store.store_email}`}
                                        className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-100 hover:bg-gray-100 transition-colors"
                                    >
                                        <HiOutlineMail size={12} className="text-gray-400" />
                                        {store.store_email}
                                    </a>
                                )}
                                {store.store_phone_number && (
                                    <a
                                        href={`tel:${store.store_phone_number}`}
                                        className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-100 hover:bg-gray-100 transition-colors"
                                    >
                                        <HiOutlinePhone size={12} className="text-gray-400" />
                                        {store.store_phone_number}
                                    </a>
                                )}
                                {store.store_whatsapp_number && (
                                    <a
                                        href={`https://wa.me/${store.store_whatsapp_number?.replace(/\D/g, '')}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100 hover:bg-emerald-100 transition-colors"
                                    >
                                        <FaWhatsapp size={12} />
                                        WhatsApp
                                    </a>
                                )}
                                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-100">
                                    <HiOutlineLocationMarker size={12} className="text-gray-400" />
                                    {store.address}
                                </span>
                            </div>

                            {/* Stats Row */}
                            <div className="flex items-center gap-6 mt-5 pt-5 border-t border-gray-100">
                                <div className="text-center sm:text-left">
                                    <p className="text-lg font-black text-gray-900">
                                        {store.products?.length?.toLocaleString() ?? 0}
                                    </p>
                                    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Products</p>
                                </div>
                                <div className="w-px h-8 bg-gray-100" />
                                <div className="text-center sm:text-left">
                                    <p className="text-lg font-black text-gray-900">
                                        {store.total_members?.toLocaleString() ?? 0}
                                    </p>
                                    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Members</p>
                                </div>
                                <div className="w-px h-8 bg-gray-100" />
                                <div className="text-center sm:text-left">
                                    <p className="text-lg font-black text-gray-900">
                                        {store.store_user?.followers_count?.toLocaleString() ?? 0}
                                    </p>
                                    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Followers</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* ==================== TABS ==================== */}
                    <div className="mt-6 bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
                        <div className="flex items-center gap-1 px-2 border-b border-gray-100 overflow-x-auto">
                            {tabs.map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`
                                        relative px-4 py-3 text-sm font-semibold whitespace-nowrap transition-colors
                                        ${activeTab === tab.id ? 'text-brand' : 'text-gray-500 hover:text-gray-700'}
                                    `}
                                >
                                    {tab.label}
                                    {tab.count !== undefined && (
                                        <span className={`
                                            ml-1.5 text-[10px] px-1.5 py-0.5 rounded-full font-bold
                                            ${activeTab === tab.id ? 'bg-brand/10 text-brand' : 'bg-gray-100 text-gray-400'}
                                        `}>
                                            {tab.count}
                                        </span>
                                    )}
                                    {activeTab === tab.id && (
                                        <span className="absolute bottom-0 left-2 right-2 h-0.5 bg-brand rounded-full" />
                                    )}
                                </button>
                            ))}
                        </div>

                        <div className="p-5 sm:p-8">
                            {/* PRODUCTS TAB */}
                            {activeTab === 'products' && (
                                <>
                                    {store.products?.length > 0 ? (
                                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                                            {store.products.map((product) => (
                                                <ProductCard key={product.id} {...product} />
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="py-16 flex flex-col items-center justify-center text-center">
                                            <div className="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-3">
                                                <RiStore2Line className="text-gray-300" size={28} />
                                            </div>
                                            <h3 className="text-sm font-bold text-gray-900">No products yet</h3>
                                            <p className="text-xs text-gray-400 mt-1 max-w-xs">
                                                {isOwnStore
                                                    ? "Start adding products to your store to attract buyers."
                                                    : "This store hasn't listed any products yet. Check back later!"}
                                            </p>
                                            {isOwnStore && (
                                                <Link
                                                    to="/create-product"
                                                    className="mt-4 px-5 py-2.5 bg-brand text-white text-sm font-semibold rounded-xl hover:opacity-90 transition-opacity"
                                                >
                                                    Add Product
                                                </Link>
                                            )}
                                        </div>
                                    )}
                                </>
                            )}

                            {/* ABOUT TAB */}
                            {activeTab === 'about' && (
                                <div className="max-w-2xl">
                                    <h3 className="text-sm font-bold text-gray-900 mb-3">About this store</h3>
                                    <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">
                                        {store.store_description || "No description provided."}
                                    </p>

                                    <div className="mt-8 space-y-4">
                                        <h3 className="text-sm font-bold text-gray-900">Contact Information</h3>
                                        <div className="grid sm:grid-cols-2 gap-3">
                                            {store.store_email && (
                                                <div className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 border border-gray-100">
                                                    <div className="w-9 h-9 rounded-lg bg-white flex items-center justify-center shadow-sm">
                                                        <HiOutlineMail size={16} className="text-gray-500" />
                                                    </div>
                                                    <div>
                                                        <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Email</p>
                                                        <p className="text-sm font-medium text-gray-900">{store.store_email}</p>
                                                    </div>
                                                </div>
                                            )}
                                            {store.store_phone_number && (
                                                <div className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 border border-gray-100">
                                                    <div className="w-9 h-9 rounded-lg bg-white flex items-center justify-center shadow-sm">
                                                        <HiOutlinePhone size={16} className="text-gray-500" />
                                                    </div>
                                                    <div>
                                                        <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Phone</p>
                                                        <p className="text-sm font-medium text-gray-900">{store.store_phone_number}</p>
                                                    </div>
                                                </div>
                                            )}
                                            {store.store_whatsapp_number && (
                                                <div className="flex items-center gap-3 p-3 rounded-xl bg-emerald-50 border border-emerald-100">
                                                    <div className="w-9 h-9 rounded-lg bg-white flex items-center justify-center shadow-sm">
                                                        <FaWhatsapp size={16} className="text-emerald-500" />
                                                    </div>
                                                    <div>
                                                        <p className="text-[11px] font-semibold text-emerald-600 uppercase tracking-wider">WhatsApp</p>
                                                        <p className="text-sm font-medium text-gray-900">{store.store_whatsapp_number}</p>
                                                    </div>
                                                </div>
                                            )}
                                            <div className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 border border-gray-100">
                                                <div className="w-9 h-9 rounded-lg bg-white flex items-center justify-center shadow-sm">
                                                    <HiOutlineLocationMarker size={16} className="text-gray-500" />
                                                </div>
                                                <div>
                                                    <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Address</p>
                                                    <p className="text-sm font-medium text-gray-900">{store.address}</p>
                                                    <p className="text-xs text-gray-400">{store.city}, {store.state}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* MEMBERS TAB */}
                            {activeTab === 'members' && (
                                <>
                                    {store.members?.length > 0 ? (
                                        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                                            {store.members.map((member) => (
                                                <Link
                                                    key={member.id}
                                                    to={`/user/${member.username}`}
                                                    className="flex items-center gap-3 p-3 rounded-xl border border-gray-100 hover:border-gray-200 hover:shadow-sm transition-all bg-white"
                                                >
                                                    <img
                                                        src={member.avatar || '/default-avatar.png'}
                                                        alt={member.full_name}
                                                        className="w-10 h-10 rounded-xl object-cover bg-gray-100"
                                                    />
                                                    <div className="min-w-0">
                                                        <p className="text-sm font-semibold text-gray-900 truncate">{member.full_name}</p>
                                                        <p className="text-xs text-gray-400 truncate">@{member.username}</p>
                                                    </div>
                                                </Link>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="py-16 flex flex-col items-center justify-center text-center">
                                            <div className="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-3">
                                                <HiOutlineUsers className="text-gray-300" size={28} />
                                            </div>
                                            <h3 className="text-sm font-bold text-gray-900">No members yet</h3>
                                            <p className="text-xs text-gray-400 mt-1">This store doesn't have any team members.</p>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default StoreDetail;