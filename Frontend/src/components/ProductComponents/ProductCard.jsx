import { Link, useNavigate } from 'react-router-dom';
import { FaHeart, FaEye } from "react-icons/fa";
import { LuMapPin } from "react-icons/lu";
import { HiBadgeCheck } from "react-icons/hi";
import { useSelector } from "react-redux";
import { useToggleFavoriteMutation } from '../../hooks/UseMutation';


const ProductCard = ({ 
    product_user, 
    product_name,  
    product_slug, 
    images, 
    price, 
    description, 
    condition, 
    state, 
    city, 
    views_count,
    favorites_count,
    is_favorited, 
    color, 
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
            alert('Please sign in to save this product to your favorites.');
            return;
        }

        toggleFavoriteMutation.mutate(product_slug);
    };

    // Check if user is the owner (hide favorite button)
    const isOwner = user?.id && product_user?.id && user.id === product_user.id;

    return (
        <Link
            to={`/product/detail/${encodeURIComponent(product_slug)}`}
            className="group flex flex-col h-full bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-xl hover:shadow-gray-200/50 hover:-translate-y-1 transition-all duration-300"
        >
            {/* Image Container */}
            <div className="relative w-full aspect-5/5 bg-gray-100 overflow-hidden">
                <img
                    src={images?.[0] || null}
                    alt={product_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />

                {/* Overlay gradient */}
                <div className="absolute inset-0 bg-linear-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                {/* Favorite Button — hidden for owner */}
                {isAuthenticated && !isOwner && (
                    <button
                        type="button"
                        onClick={handleFavorite}
                        aria-label="Save to favorites"
                        disabled={toggleFavoriteMutation.isPending}
                        className="absolute top-3 right-3 flex items-center justify-center w-9 h-9 rounded-full bg-white/95 backdrop-blur-sm shadow-sm hover:shadow-md hover:scale-110 active:scale-90 transition-all duration-200 disabled:opacity-50"
                    >
                        <FaHeart
                            size={16}
                            className={`transition-colors duration-200 ${is_favorited ? 'fill-red-500 text-red-500' : 'text-gray-400 hover:text-red-400'}`}
                        />
                    </button>
                )}

                {/* Condition Badge */}
                {condition && (
                    <span className="absolute top-3 left-3 bg-white/95 backdrop-blur-sm text-gray-800 text-[10px] font-bold px-2.5 py-1 rounded-lg shadow-sm uppercase tracking-normal">
                        {condition}
                    </span>
                )}

                {/* Color Badge */}
                {color && (
                    <span
                        className="absolute bottom-3 right-3 w-5 h-5 rounded-full border-2 border-white shadow-md ring-1 ring-black/5"
                        style={{ backgroundColor: color }}
                        aria-label={`Color: ${color}`}
                    />
                )}
            </div>

            {/* Content */}
            <div className="flex flex-col flex-1 p-4">
                {/* Price Row */}
                <div className="flex items-start justify-between gap-2">
                    <p className="text-lg font-extrabold text-gray-900 tracking-tight">
                        ₦{Number(price).toLocaleString()}
                    </p>
                    
                    {product_user?.verified && (
                        <span className="inline-flex items-center gap-0.5 text-emerald-600 text-[11px] font-bold bg-emerald-50 px-2 py-0.5 rounded-full shrink-0 mt-0.5">
                            <HiBadgeCheck size={12} />
                            Verified
                        </span>
                    )}
                </div>

                {/* Product Name */}
                <h3 className="text-sm font-semibold text-gray-800 line-clamp-1 mt-1.5 group-hover:text-brand transition-colors duration-200">
                    {product_name}
                </h3>

                {/* Description */}
                {description && (
                    <p className="text-xs text-gray-400 line-clamp-2 mt-1 leading-relaxed">
                        {description}
                    </p>
                )}

                {/* Seller Row */}
                {product_user && (
                    <div className="flex items-center gap-2 mt-3">
                        <img
                            src={product_user?.avatar || null}
                            alt={product_user.full_name || product_user.username}
                            className="w-5 h-5 rounded-full object-cover bg-gray-100 ring-1 ring-gray-100"
                        />
                        <span className="text-xs text-gray-500 font-medium truncate">
                            {product_user.full_name || product_user.username}
                        </span>
                        {product_user.verified && (
                            <HiBadgeCheck size={12} className="text-emerald-500 shrink-0" />
                        )}
                    </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between mt-auto pt-3 border-t border-gray-50">
                    {(city || state) && (
                        <p className="flex items-center gap-1 text-[11px] text-gray-400 line-clamp-1">
                            <LuMapPin size={11} className="shrink-0 text-gray-300" />
                            <span className="truncate">{city && state ? `${city}, ${state}` : city || state}</span>
                        </p>
                    )}

                    <div className="flex items-center gap-3 shrink-0 ml-2">
                        {typeof favorites_count === 'number' && (
                            <span className="flex items-center gap-1 text-[11px] text-gray-400">
                                <FaHeart size={10} className={is_favorited ? 'text-red-500 fill-red-500' : 'text-gray-300'} />
                                {favorites_count.toLocaleString()}
                            </span>
                        )}
                        {typeof views_count === 'number' && (
                            <span className="flex items-center gap-1 text-[11px] text-gray-400">
                                <FaEye size={11} className="text-gray-300" />
                                {views_count.toLocaleString()}
                            </span>
                        )}
                    </div>
                </div>
            </div>
        </Link>
    );
};

export default ProductCard;