import { useState } from 'react';
import { FaStar } from 'react-icons/fa';


export const Stars = ({ value = 0, size = 12, className = '' }) => {
    return (
        <span className={`inline-flex items-center gap-0.5 ${className}`} aria-label={`${value} out of 5 stars`}>
            {[1, 2, 3, 4, 5].map((star) => (
                <FaStar
                    key={star}
                    size={size}
                    className={star <= Math.round(value) ? 'text-amber-400' : 'text-gray-200'}
                />
            ))}
        </span>
    );
};


const StarRating = ({ initialValue = 0, onRate, disabled = false, size = 26 }) => {
    const [hover, setHover] = useState(0);

    return (
        <div className="inline-flex items-center gap-1.5">
            {[1, 2, 3, 4, 5].map((star) => (
                <button
                    key={star}
                    type="button"
                    disabled={disabled}
                    onMouseEnter={() => setHover(star)}
                    onMouseLeave={() => setHover(0)}
                    onClick={() => onRate?.(star)}
                    aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
                    className={`transition-transform duration-150 ${disabled ? 'opacity-60 cursor-not-allowed' : 'hover:scale-125 active:scale-95 cursor-pointer'}`}
                >
                    <FaStar
                        size={size}
                        className={(hover || initialValue) >= star
                            ? 'text-amber-400 fill-amber-400'
                            : 'text-gray-300 fill-gray-200'}
                    />
                </button>
            ))}
        </div>
    );
};

export default StarRating;
