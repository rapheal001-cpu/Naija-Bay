import { FaArrowLeft, FaHome, FaSearch } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

const ProductNotFound = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-gray-50/50">
            <div className="max-w-md w-full text-center">
                {/* Illustration */}
                <div className="relative mx-auto w-40 h-40 mb-8">
                    <div className="absolute inset-0 bg-brand/5 rounded-full animate-pulse" />
                    <div className="relative w-full h-full rounded-3xl bg-white border border-gray-100 shadow-sm flex items-center justify-center">
                        <svg
                            className="w-20 h-20 text-gray-300"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z" />
                            <line x1="3" y1="6" x2="21" y2="6" />
                            <path d="M16 10a4 4 0 01-8 0" />
                            <line x1="9" y1="14" x2="15" y2="20" />
                            <line x1="15" y1="14" x2="9" y2="20" />
                        </svg>
                    </div>
                    {/* Floating badge */}
                    <div className="absolute -top-2 -right-2 w-10 h-10 bg-brand text-white rounded-xl flex items-center justify-center shadow-lg shadow-brand/20">
                        <span className="text-lg font-bold">?</span>
                    </div>
                </div>

                {/* Text content */}
                <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
                    Product not found
                </h1>
                <p className="mt-3 text-sm text-gray-500 leading-relaxed max-w-xs mx-auto">
                    The product you're looking for may have been removed, renamed, or is temporarily unavailable.
                </p>

                {/* Action buttons */}
                <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
                    <button
                        onClick={() => navigate(-1)}
                        className="w-full sm:w-auto flex items-center justify-center gap-2 bg-brand text-white font-semibold rounded-xl px-6 py-3 hover:bg-brand/90 active:scale-[0.98] transition-all shadow-sm shadow-brand/20"
                    >
                        <FaArrowLeft className="w-4 h-4" />
                        Go Back
                    </button>

                    <button
                        onClick={() => navigate('/products')}
                        className="w-full sm:w-auto flex items-center justify-center gap-2 bg-white text-gray-700 font-semibold rounded-xl px-6 py-3 border border-gray-200 hover:bg-gray-50 hover:border-gray-300 active:scale-[0.98] transition-all"
                    >
                        <FaSearch className="w-4 h-4 text-gray-400" />
                        Browse Products
                    </button>
                </div>

                {/* Home link */}
                <button
                    onClick={() => navigate('/')}
                    className="mt-6 inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-brand transition-colors font-medium"
                >
                    <FaHome className="w-3.5 h-3.5" />
                    Return to homepage
                </button>
            </div>
        </div>
    );
};

export default ProductNotFound;