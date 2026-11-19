import { Link, useNavigate } from 'react-router-dom';
import { FaHeart, FaEye } from "react-icons/fa";
import { HiBadgeCheck } from "react-icons/hi";
import { LuMapPin } from "react-icons/lu";
import { useSelector } from "react-redux";
import { useToggleFavoriteMutation } from '../../hooks/UseMutation';
import { Stars } from './StarRating';
import { timeAgo } from '../../dummyData.js';

const BADGE_STYLES = {
    VIP: 'bg-amber-400 text-amber-950',
    PREMIUM: 'bg-sky-500 text-white',
    DIAMOND: 'bg-violet-600 text-white',
    ENTERPRISE: 'bg-rose-600 text-white',
};

const ProductCard = ({
    product_user,
    product_name,
    product_slug,
    images,
    price,
    original_price,
    discount_percent,
    average_rating,
    total_ratings,
    description,
    condition,
    state,
    city,
    views_count,
    is_favorited,
    promoted,
    badge,
    posted_ago,
    location_label,
    created_at,
}) => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);
    const navigate = useNavigate();
    const toggleFavoriteMutation = useToggleFavoriteMutation();

    const handleFavorite = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!isAuthenticated && !user) {
            navigate('/sign-in');
            return;
        }
        toggleFavoriteMutation.mutate(product_slug);
    };

    const isOwner = user?.id && product_user?.id && user.id === product_user.id;
    const tier = badge || (promoted ? 'PREMIUM' : null);
    const location = location_label || (city && state ? `${city}, ${state}` : city || state || '');
    const age = posted_ago || (created_at ? timeAgo(created_at) : '');

    return (
        <Link
            to={`/product/detail/${encodeURIComponent(product_slug)}`}
            className="group flex h-full flex-col overflow-hidden rounded-md border border-slate-200 bg-white transition-shadow hover:shadow-lg"
        >
            <div className="relative aspect-square w-full overflow-hidden bg-slate-100">
                <img
                    src={images?.[0] || null}
                    alt={product_name}
                    loading="lazy"
                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                />

                {tier && (
                    <span className={`absolute left-0 top-2 rounded-r px-2 py-1 text-[10px] font-extrabold uppercase tracking-wide shadow-sm ${BADGE_STYLES[tier] || BADGE_STYLES.PREMIUM}`}>
                        {tier}
                    </span>
                )}

                {Number(discount_percent) > 0 && (
                    <span className="absolute bottom-2 left-2 rounded bg-red-600 px-2 py-0.5 text-[10px] font-bold text-white">
                        -{discount_percent}%
                    </span>
                )}

                {isAuthenticated && !isOwner && (
                    <button
                        type="button"
                        onClick={handleFavorite}
                        aria-label="Save to favorites"
                        disabled={toggleFavoriteMutation.isPending}
                        className="absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-full bg-white/95 shadow-sm transition hover:scale-110 disabled:opacity-50"
                    >
                        <FaHeart
                            size={15}
                            className={is_favorited ? 'fill-red-500 text-red-500' : 'text-slate-400'}
                        />
                    </button>
                )}
            </div>

            <div className="flex flex-1 flex-col p-3">
                <div className="flex items-baseline gap-2">
                    <p className="text-base font-extrabold text-slate-900">
                        ₦{Number(price).toLocaleString()}
                    </p>
                    {Number(original_price) > Number(price) && (
                        <p className="text-[11px] text-slate-400 line-through">
                            ₦{Number(original_price).toLocaleString()}
                        </p>
                    )}
                </div>

                <h3 className="mt-1 line-clamp-2 min-h-[36px] text-[13px] font-semibold leading-snug text-slate-800 group-hover:text-brand">
                    {product_name}
                </h3>

                {description && (
                    <p className="mt-1 line-clamp-2 text-[11px] leading-relaxed text-slate-400">
                        {description}
                    </p>
                )}

                {Number(total_ratings) > 0 && (
                    <div className="mt-1.5 flex items-center gap-1.5">
                        <Stars value={Number(average_rating) || 0} size={11} />
                        <span className="text-[11px] font-semibold text-slate-600">
                            {Number(average_rating).toFixed(1)}
                        </span>
                        <span className="text-[10px] text-slate-400">({total_ratings})</span>
                    </div>
                )}

                <div className="mt-2 flex flex-wrap items-center gap-1.5">
                    {condition && (
                        <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-500">
                            {condition}
                        </span>
                    )}
                    {product_user?.verified && (
                        <span className="inline-flex items-center gap-0.5 text-[10px] font-semibold text-blue-600">
                            <HiBadgeCheck size={12} /> Verified ID
                        </span>
                    )}
                </div>

                {product_user && (
                    <p className="mt-2 truncate text-[11px] font-medium text-slate-500">
                        {product_user.store?.name || product_user.full_name || product_user.username}
                    </p>
                )}

                <div className="mt-auto flex items-center justify-between gap-1 border-t border-slate-100 pt-2 text-[10px] text-slate-400">
                    <span className="flex min-w-0 items-center gap-1 truncate">
                        <LuMapPin size={10} className="shrink-0" />
                        <span className="truncate">{location}</span>
                    </span>
                    <span className="flex shrink-0 items-center gap-2">
                        {typeof views_count === 'number' && (
                            <span className="flex items-center gap-0.5">
                                <FaEye size={10} /> {views_count.toLocaleString()}
                            </span>
                        )}
                        {age && <span>{age}</span>}
                    </span>
                </div>
            </div>
        </Link>
    );
};

export default ProductCard;
