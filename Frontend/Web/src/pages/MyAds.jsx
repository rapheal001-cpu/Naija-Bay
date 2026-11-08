import { useEffect, useMemo, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { HiOutlineCollection, HiOutlineEye, HiOutlineHeart, HiOutlinePencilAlt, HiOutlineTrash, HiOutlineCheckCircle, HiOutlinePlusCircle } from 'react-icons/hi';
import Header from '../components/HeaderComponents/Header.jsx';
import AppLayout from '../components/AppLayout.jsx';
import InfiniteListSentinel from '../components/InfiniteListSentinel.jsx';
import Spacer from '../components/Spacer.jsx';
import Footer from '../components/FooterComponents/Footer.jsx';
import { useSelector } from 'react-redux';
import { useFetchMyListings, useInfiniteMyListings } from '../hooks/UseQuery.js';
import { deleteProductFn, updateProductFn } from '../service/Endpoints.js';
import { formatDate } from '../dummyData.js';

const TABS = [
    { value: '', label: 'All Ads' },
    { value: 'active', label: 'Active' },
    { value: 'sold', label: 'Sold' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'expired', label: 'Expired' },
];

const STATUS_STYLES = {
    active: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    sold: 'bg-red-50 text-red-600 border-red-200',
    inactive: 'bg-gray-100 text-gray-600 border-gray-200',
    expired: 'bg-amber-50 text-amber-700 border-amber-200',
};

const MyAds = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [status, setStatus] = useState('');
    const [confirmDelete, setConfirmDelete] = useState(null);
    const [actionError, setActionError] = useState('');

    useEffect(() => {
        if (!isAuthenticated && !user) navigate('/sign-in');
    }, [isAuthenticated, user, navigate]);

    const listings = useInfiniteMyListings(isAuthenticated, status);
    const allListings = useFetchMyListings(isAuthenticated, '', 1);
    const ads = useMemo(
        () => listings.data?.pages.flatMap((p) => p.results || []) || [],
        [listings.data]
    );

    const stats = useMemo(() => {
        const all = allListings.data?.results || [];
        return {
            total: allListings.data?.count ?? all.length,
            active: all.filter((p) => p.listing_status === 'active').length,
            sold: all.filter((p) => p.listing_status === 'sold').length,
            views: all.reduce((sum, p) => sum + (p.views_count || 0), 0),
            favorites: all.reduce((sum, p) => sum + (p.favorites_count || 0), 0),
        };
    }, [allListings.data]);

    const invalidate = () => {
        queryClient.invalidateQueries({ queryKey: ['my-listings'] });
        queryClient.invalidateQueries({ queryKey: ['products'] });
    };

    const deleteMutation = useMutation({
        mutationFn: (slug) => deleteProductFn(slug),
        onSuccess: () => {
            setConfirmDelete(null);
            invalidate();
        },
        onError: (err) => setActionError(err?.response?.data?.detail || 'Could not delete the ad.'),
    });

    const markSoldMutation = useMutation({
        mutationFn: (slug) => updateProductFn({ productSlug: slug, payload: { sold: true } }),
        onSuccess: invalidate,
        onError: (err) => setActionError(err?.response?.data?.detail || 'Could not mark the ad as sold.'),
    });

    return (
        <AppLayout>
            <div className="min-h-screen pb-16">
                <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                    <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand/10 text-brand">
                                <HiOutlineCollection size={20} />
                            </div>
                            <div>
                                <h1 className="text-2xl font-black tracking-tight text-gray-900">My Ads</h1>
                                <p className="mt-0.5 text-sm text-gray-500">Manage, edit and boost your listings</p>
                            </div>
                        </div>
                        <Link
                            to="/sell"
                            className="inline-flex items-center gap-1.5 rounded-xl bg-brand px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-colors hover:bg-brand/90"
                        >
                            <HiOutlinePlusCircle size={16} aria-hidden="true" />
                            Post a new ad
                        </Link>
                    </div>

                    {/* Stats */}
                    <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
                        {[
                            { label: 'Total ads', value: stats.total },
                            { label: 'Active', value: stats.active },
                            { label: 'Total views', value: stats.views.toLocaleString() },
                            { label: 'Total favourites', value: stats.favorites.toLocaleString() },
                        ].map((stat) => (
                            <div key={stat.label} className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
                                <p className="text-2xl font-black text-gray-900">{stat.value}</p>
                                <p className="mt-0.5 text-xs font-semibold uppercase tracking-wider text-gray-400">{stat.label}</p>
                            </div>
                        ))}
                    </div>

                    {/* Status tabs */}
                    <div className="mb-5 flex gap-2 overflow-x-auto pb-1 scrollbar-hide" role="tablist" aria-label="Filter ads by status">
                        {TABS.map((tab) => (
                            <button
                                key={tab.value || 'all'}
                                type="button"
                                role="tab"
                                aria-selected={status === tab.value}
                                onClick={() => setStatus(tab.value)}
                                className={`shrink-0 rounded-full border px-4 py-2 text-xs font-bold transition-all ${
                                    status === tab.value
                                        ? 'border-brand bg-brand text-white'
                                        : 'border-gray-200 bg-white text-gray-600 hover:border-brand/40 hover:text-brand'
                                }`}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>

                    {actionError && (
                        <p className="mb-4 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-xs font-semibold text-red-600">
                            {actionError}
                        </p>
                    )}

                    {/* Ads list */}
                    {listings.isLoading ? (
                        <div className="space-y-3">
                            {[0, 1, 2].map((i) => (
                                <div key={i} className="flex animate-pulse gap-4 rounded-2xl border border-gray-100 bg-white p-4">
                                    <div className="h-20 w-20 shrink-0 rounded-xl bg-gray-100" />
                                    <div className="flex-1 space-y-2 py-1">
                                        <div className="h-4 w-2/3 rounded bg-gray-100" />
                                        <div className="h-3 w-1/3 rounded bg-gray-100" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : ads.length === 0 ? (
                        <div className="rounded-2xl border border-dashed border-gray-200 bg-white px-6 py-16 text-center">
                            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-50">
                                <HiOutlineCollection size={28} className="text-gray-300" />
                            </div>
                            <h2 className="text-base font-bold text-gray-900">No ads here yet</h2>
                            <p className="mx-auto mt-1.5 max-w-sm text-sm leading-relaxed text-gray-500">
                                {status
                                    ? 'No ads match this status. Try another tab.'
                                    : 'Post your first free ad and reach thousands of buyers across Nigeria.'}
                            </p>
                            <Link
                                to="/sell"
                                className="mt-5 inline-flex items-center gap-1.5 rounded-xl bg-brand px-5 py-2.5 text-sm font-bold text-white transition-opacity hover:opacity-90"
                            >
                                <HiOutlinePlusCircle size={16} aria-hidden="true" />
                                Post a free ad
                            </Link>
                        </div>
                    ) : (
                        <>
                        <ul className="space-y-3">
                            {ads.map((ad) => (
                                <li key={ad.id} className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm sm:flex-row">
                                    <Link
                                        to={`/product/detail/${encodeURIComponent(ad.product_slug)}`}
                                        className="block h-28 w-full shrink-0 overflow-hidden rounded-xl bg-gray-100 sm:h-24 sm:w-28"
                                    >
                                        <img src={ad.images?.[0] || null} alt={ad.product_name} className="h-full w-full object-cover" />
                                    </Link>
                                    <div className="min-w-0 flex-1">
                                        <div className="flex flex-wrap items-center gap-2">
                                            <Link
                                                to={`/product/detail/${encodeURIComponent(ad.product_slug)}`}
                                                className="line-clamp-1 text-sm font-bold text-gray-900 hover:text-brand sm:text-base"
                                            >
                                                {ad.product_name}
                                            </Link>
                                            <span className={`rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase ${STATUS_STYLES[ad.listing_status] || STATUS_STYLES.inactive}`}>
                                                {ad.listing_status}
                                            </span>
                                            {ad.is_boosted && (
                                                <span className="rounded-full bg-amber-400 px-2 py-0.5 text-[10px] font-black uppercase text-gray-900">Boosted</span>
                                            )}
                                        </div>
                                        <p className="mt-1 text-base font-black text-gray-900">₦{Number(ad.price).toLocaleString()}</p>
                                        <div className="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-400">
                                            <span className="flex items-center gap-1"><HiOutlineEye size={13} aria-hidden="true" /> {ad.views_count?.toLocaleString() || 0} views</span>
                                            <span className="flex items-center gap-1"><HiOutlineHeart size={13} aria-hidden="true" /> {ad.favorites_count?.toLocaleString() || 0} saved</span>
                                            <span>Posted {formatDate(ad.created_at)}</span>
                                        </div>
                                    </div>
                                    <div className="flex shrink-0 flex-wrap items-center gap-2">
                                        <Link
                                            to={`/product/${encodeURIComponent(ad.product_slug)}/edit`}
                                            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-2 text-xs font-bold text-gray-700 transition-colors hover:border-brand hover:text-brand"
                                        >
                                            <HiOutlinePencilAlt size={13} aria-hidden="true" /> Edit
                                        </Link>
                                        {ad.listing_status === 'active' && (
                                            <button
                                                type="button"
                                                disabled={markSoldMutation.isPending}
                                                onClick={() => markSoldMutation.mutate(ad.product_slug)}
                                                className="inline-flex items-center gap-1.5 rounded-lg bg-brand px-3 py-2 text-xs font-bold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                                            >
                                                <HiOutlineCheckCircle size={13} aria-hidden="true" /> Mark sold
                                            </button>
                                        )}
                                        {confirmDelete === ad.product_slug ? (
                                            <span className="inline-flex items-center gap-1.5">
                                                <button
                                                    type="button"
                                                    disabled={deleteMutation.isPending}
                                                    onClick={() => deleteMutation.mutate(ad.product_slug)}
                                                    className="rounded-lg bg-red-600 px-3 py-2 text-xs font-bold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                                                >
                                                    Confirm
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => setConfirmDelete(null)}
                                                    className="rounded-lg border border-gray-200 px-3 py-2 text-xs font-bold text-gray-600"
                                                >
                                                    Keep
                                                </button>
                                            </span>
                                        ) : (
                                            <button
                                                type="button"
                                                onClick={() => setConfirmDelete(ad.product_slug)}
                                                className="inline-flex items-center gap-1.5 rounded-lg border border-red-200 px-3 py-2 text-xs font-bold text-red-600 transition-colors hover:bg-red-50"
                                            >
                                                <HiOutlineTrash size={13} aria-hidden="true" /> Delete
                                            </button>
                                        )}
                                    </div>
                                </li>
                            ))}
                        </ul>
                        {ads.length > 0 && listings.hasNextPage && (
                            <>
                                <InfiniteListSentinel hasMore={listings.hasNextPage} isFetching={listings.isFetchingNextPage} onLoadMore={() => listings.fetchNextPage()} />
                                {listings.isFetchingNextPage && (
                                    <div className="space-y-3 mt-3" aria-hidden="true">
                                        {[0, 1].map((i) => (
                                            <div key={i} className="flex animate-pulse gap-4 rounded-2xl border border-gray-100 bg-white p-4">
                                                <div className="h-20 w-20 shrink-0 rounded-xl bg-gray-100" />
                                                <div className="flex-1 space-y-2 py-1">
                                                    <div className="h-4 w-1/2 bg-gray-100 rounded" />
                                                    <div className="h-3 w-1/4 bg-gray-100 rounded" />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </>
                        )}
                        </>
                    )}
                </div>
            </div>
        </AppLayout>
    );
};

export default MyAds;
