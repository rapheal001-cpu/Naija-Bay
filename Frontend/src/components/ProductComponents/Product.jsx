import { FaHeart, FaPhoneAlt, FaRegCalendarAlt, FaArrowLeft, FaChevronLeft, FaChevronRight, FaEdit, FaTrash } from 'react-icons/fa';
import { LuMapPin, LuMessageCircleMore } from 'react-icons/lu';
import { IoIosEye, IoLogoWhatsapp } from 'react-icons/io';
import { HiBadgeCheck } from 'react-icons/hi';
import { TbAlertTriangleFilled } from 'react-icons/tb';
import Header from '../HeaderComponents/Header.jsx';
import Spacer from '../Spacer.jsx';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { formatDate } from '../../dummyData.js';
import { useToggleFavoriteMutation, useDeleteProductMutation } from '../../hooks/UseMutation.js';
import { useSelector } from 'react-redux';


const Product = () => {
    const user = useSelector((state) => state.user.user);
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const product = useSelector((state) => state.products.productDetail);

    const [activeImage, setActiveImage] = useState(0);

    const navigate = useNavigate();

    const toggleFavoriteMutation = useToggleFavoriteMutation();
    const deleteProductMutation = useDeleteProductMutation();

    const nextImage = () => {
        const len = product?.images?.length || 0;
        if (len === 0) return;
        setActiveImage((prev) => (prev + 1) % len);
    };

    const prevImage = () => {
        const len = product?.images?.length || 0;
        if (len === 0) return;
        setActiveImage((prev) => (prev - 1 + len) % len);
    };

    const handleFavorite = (e, product_slug) => {
        e.preventDefault();
        e.stopPropagation();

        if (!isAuthenticated && !user) {
            navigate('/sign-in');
            alert('Please sign in to save this product to your favorites.');
            return;
        }

        toggleFavoriteMutation.mutate(product_slug);
    };

    const isOwner = user?.id && product?.product_user?.id && user.id === product.product_user.id;

    const handleDelete = (e, product_slug) => {
        e.preventDefault();
        e.stopPropagation();

        if (isOwner) {
            deleteProductMutation.mutate(product_slug);
        }

        if (!window.confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
            return;
        }
    };

    const contactNumber = product?.contact_number || '';
    const cleanNumber = contactNumber.replace(/\D/g, '');

    return (
        <>
            <Header />
            <Spacer space={'mb-18'} />

            <div className="max-w-7xl mx-auto px-4 py-6">
                {/* Back link */}
                <button
                    type="button"
                    onClick={() => navigate(-1)}
                    className="inline-flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-brand transition-colors mb-6 group"
                >
                    <span className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 group-hover:bg-brand/10 transition-colors">
                        <FaArrowLeft size={14} />
                    </span>
                    Back to results
                </button>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
                    {/* Left: Image gallery */}
                    <div className="lg:col-span-7 xl:col-span-8">
                        <div className="relative w-full aspect-4/3 bg-gray-100 rounded-2xl overflow-hidden shadow-sm group">
                            <img
                                src={product?.images?.[activeImage] || null}
                                alt={`${product?.product_name} photo`}
                                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.02]"
                            />

                            {product?.sold && (
                                <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px] flex items-center justify-center">
                                    <span className="bg-white text-red-600 font-black text-xl px-6 py-3 rounded-2xl shadow-2xl tracking-wide uppercase">
                                        Sold Out
                                    </span>
                                </div>
                            )}

                            {/* Nav arrows */}
                            {product?.images?.length > 1 && (
                                <>
                                    <button
                                        type="button"
                                        onClick={prevImage}
                                        aria-label="Previous image"
                                        className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center justify-center w-11 h-11 rounded-full bg-white/90 backdrop-blur-sm shadow-lg hover:bg-white hover:scale-110 active:scale-95 transition-all opacity-0 group-hover:opacity-100"
                                    >
                                        <FaChevronLeft size={18} className="text-gray-700" />
                                    </button>
                                    <button
                                        type="button"
                                        onClick={nextImage}
                                        aria-label="Next image"
                                        className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center justify-center w-11 h-11 rounded-full bg-white/90 backdrop-blur-sm shadow-lg hover:bg-white hover:scale-110 active:scale-95 transition-all opacity-0 group-hover:opacity-100"
                                    >
                                        <FaChevronRight size={18} className="text-gray-700" />
                                    </button>
                                </>
                            )}

                            {/* Favorite — hidden for owner */}
                            {isAuthenticated && !isOwner && (
                                <button
                                    type="button"
                                    onClick={(e) => handleFavorite(e, product?.product_slug)}
                                    aria-label="Save to favorites"
                                    disabled={toggleFavoriteMutation.isPending}
                                    className="absolute top-4 right-4 flex items-center justify-center w-10 h-10 rounded-full bg-white/95 backdrop-blur-sm shadow-md hover:shadow-lg hover:scale-110 active:scale-90 transition-all disabled:opacity-50"
                                >
                                    <FaHeart
                                        size={18}
                                        className={`transition-colors duration-200 ${product?.is_favorited ? 'fill-red-500 text-red-500' : 'text-gray-400 hover:text-red-400'}`}
                                    />
                                </button>
                            )}

                            {/* Image counter */}
                            {product?.images?.length > 1 && (
                                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-black/50 backdrop-blur-sm text-white text-xs font-semibold">
                                    {activeImage + 1} / {product?.images?.length}
                                </div>
                            )}
                        </div>

                        {/* Thumbnails */}
                        <div className="flex gap-2.5 mt-4 overflow-x-auto pb-1 scrollbar-hide">
                            {product.images?.map((img, index) => (
                                <button
                                    key={index}
                                    type="button"
                                    onClick={() => setActiveImage(index)}
                                    className={`shrink-0 w-20 h-20 rounded-xl overflow-hidden border-2 transition-all duration-200 ${
                                        activeImage === index
                                            ? 'border-brand ring-2 ring-brand/20 scale-105'
                                            : 'border-transparent opacity-60 hover:opacity-100'
                                    }`}
                                >
                                    <img 
                                        src={img || null} 
                                        alt={`${product?.product_name} - ${index}`} 
                                        className="w-full h-full object-cover"
                                    />
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Right: Info panel */}
                    <div className="lg:col-span-5 xl:col-span-4">
                        {/* Price & Status */}
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-3xl font-black text-gray-900 tracking-tight">
                                    ₦{Number(product?.price).toLocaleString()}
                                </p>
                                {product?.negotiable && (
                                    <span className="inline-block mt-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-100 px-3 py-1 rounded-full">
                                        Negotiable
                                    </span>
                                )}
                            </div>
                            {product?.product_user?.verified && (
                                <span className="inline-flex items-center gap-1 text-emerald-600 text-xs font-bold bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100">
                                    <HiBadgeCheck size={14} />
                                    Verified
                                </span>
                            )}
                        </div>

                        {/* Owner Actions: Edit & Delete */}
                        {isOwner && (
                            <div className="flex items-center gap-2.5 mt-4">
                                <Link
                                    to={`/product/${product?.product_slug}/edit`}
                                    className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-bold text-brand bg-brand/5 border border-brand/10 rounded-xl hover:bg-brand/10 active:scale-[0.98] transition-all"
                                >
                                    <FaEdit size={14} />
                                    Edit
                                </Link>
                                <button
                                    type="button"
                                    onClick={(e) => handleDelete(e, product?.product_slug)}
                                    disabled={deleteProductMutation.isPending}
                                    className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-bold text-red-600 bg-red-50 border border-red-100 rounded-xl hover:bg-red-100 active:scale-[0.98] transition-all disabled:opacity-50"
                                >
                                    <FaTrash size={14} />
                                    {deleteProductMutation.isPending ? 'Deleting...' : 'Delete'}
                                </button>
                            </div>
                        )}

                        {/* Title */}
                        <h1 className="text-xl font-bold text-gray-900 mt-4 leading-snug">
                            {product?.product_name}
                        </h1>

                        {/* Meta row */}
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 mt-3">
                            <div className="flex items-center gap-1 text-sm text-gray-500">
                                <LuMapPin size={14} className="text-gray-400" />
                                {product?.city}, {product?.state}
                            </div>
                            <span className="flex items-center gap-1 text-xs text-gray-400">
                                <IoIosEye size={13} /> {Number(product?.views_count).toLocaleString()}
                            </span>
                            <span className="flex items-center gap-1 text-xs text-gray-400">
                                <FaHeart size={12} /> {Number(product?.favorites_count).toLocaleString()}
                            </span>
                            <span className="flex items-center gap-1 text-xs text-gray-400">
                                <FaRegCalendarAlt size={12} /> {formatDate(product?.created_at)}
                            </span>
                        </div>

                        {/* Attributes */}
                        <div className="grid grid-cols-2 gap-3 mt-6">
                            {product?.condition && (
                                <div className="bg-gray-50 rounded-xl p-3.5 border border-gray-100">
                                    <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1">Condition</p>
                                    <p className="text-sm font-bold text-gray-800 capitalize">{product?.condition}</p>
                                </div>
                            )}
                            {product?.color && (
                                <div className="bg-gray-50 rounded-xl p-3.5 border border-gray-100">
                                    <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1">Color</p>
                                    <div className="flex items-center gap-2">
                                        <span
                                            className="w-5 h-5 rounded-full border-2 border-white shadow-sm ring-1 ring-gray-200"
                                            style={{ backgroundColor: product?.color }}
                                        />
                                        <span className="text-sm font-bold text-gray-800">{product?.color}</span>
                                    </div>
                                </div>
                            )}
                            <div className="bg-gray-50 rounded-xl p-3.5 border border-gray-100">
                                <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1">Quantity</p>
                                <p className="text-sm font-bold text-gray-800">{product?.quantity} available</p>
                            </div>
                            <div className="bg-gray-50 rounded-xl p-3.5 border border-gray-100">
                                <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1">Category</p>
                                <p className="text-sm font-bold text-gray-800 capitalize">{product?.category?.replace(/_/g, ' ')}</p>
                            </div>
                            {product?.sub_category && (
                                <div className="bg-gray-50 rounded-xl p-3.5 border border-gray-100 col-span-2">
                                    <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1">Sub Category</p>
                                    <p className="text-sm font-bold text-gray-800 capitalize">{product?.sub_category?.replace(/_/g, ' ')}</p>
                                </div>
                            )}
                        </div>

                        {/* Description */}
                        <div className="mt-6 bg-white rounded-2xl border border-gray-100 p-5 shadow-sm">
                            <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Description</p>
                            <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">{product?.description}</p>
                        </div>

                        {/* Seller Card */}
                        {product?.product_user && (
                            <Link
                                to={`/profile/${encodeURIComponent(product.product_user.id)}`}
                                className="mt-6 flex items-center gap-4 bg-white rounded-2xl border border-gray-100 p-4 shadow-sm hover:shadow-md hover:border-gray-200 transition-all group"
                            >
                                <div className="relative">
                                    <img
                                        src={product?.product_user?.avatar || null}
                                        alt={product?.product_user?.full_name || product?.product_user?.username}
                                        className="w-14 h-14 rounded-2xl object-cover bg-gray-100"
                                    />
                                    {product?.product_user?.verified && (
                                        <span className="absolute -bottom-1 -right-1 bg-emerald-500 text-white rounded-full p-0.5 border-2 border-white">
                                            <HiBadgeCheck size={12} />
                                        </span>
                                    )}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-bold text-gray-900 truncate group-hover:text-brand transition-colors">
                                        {product?.product_user?.full_name || product?.product_user?.username}
                                    </p>
                                    <p className="text-xs text-gray-400 mt-0.5">View seller profile</p>
                                </div>
                                <FaChevronRight size={14} className="text-gray-300 group-hover:text-brand transition-colors" />
                            </Link>
                        )}

                        {/* Safety Warning */}
                        <div className="mt-6 flex gap-3.5 bg-amber-50/70 border border-amber-100 rounded-2xl p-4">
                            <TbAlertTriangleFilled size={22} className="text-amber-500 shrink-0 mt-0.5" />
                            <div>
                                <p className="text-sm font-bold text-amber-800">Stay safe when buying</p>
                                <p className="text-xs text-amber-700/80 leading-relaxed mt-1">
                                    Meet at a public location and inspect the item before payment. Never transfer money before confirming the product.
                                </p>
                            </div>
                        </div>

                        {/* Contact Actions — MULTI-METHOD */}
                        {!product?.sold && product?.product_user && !isOwner && (
                            <div className="flex flex-col gap-3 mt-6">
                                {product.contact_methods?.includes('phone_call') && contactNumber && (
                                    <a
                                        href={`tel:${cleanNumber}`}
                                        className="flex items-center justify-center gap-2.5 bg-brand text-white font-bold rounded-xl py-3.5 hover:opacity-90 active:scale-[0.98] transition-all shadow-lg shadow-brand/20"
                                    >
                                        <FaPhoneAlt size={18} />
                                        Call Seller
                                    </a>
                                )}
                                
                                {product.contact_methods?.includes('whatsapp') && contactNumber && (
                                    <a
                                        href={`https://wa.me/+${cleanNumber.replace(/^0/, '')}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center justify-center gap-2.5 bg-emerald-500 text-white font-bold rounded-xl py-3.5 hover:opacity-90 active:scale-[0.98] transition-all shadow-lg shadow-emerald-500/20"
                                    >
                                        <IoLogoWhatsapp size={20} />
                                        Chat on WhatsApp
                                    </a>
                                )}
                                
                                {product.contact_methods?.includes('message') && (
                                    <Link
                                        to={`/messages/${encodeURIComponent(product.product_user.username)}`}
                                        className="flex items-center justify-center gap-2.5 bg-brand text-white font-bold rounded-xl py-3.5 hover:opacity-90 active:scale-[0.98] transition-all shadow-lg shadow-brand/20"
                                    >
                                        <LuMessageCircleMore size={20} />
                                        Message Seller
                                    </Link>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
};

export default Product;