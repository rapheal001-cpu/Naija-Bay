import { Link, useNavigate } from 'react-router-dom';
import { LuPackageCheck } from "react-icons/lu";
import { IoHome } from "react-icons/io5";
import { IoIosSearch } from "react-icons/io";
import { FaArrowLeft } from "react-icons/fa";

const NotFound = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-20 bg-linear-to-b from-gray-50 to-white relative overflow-hidden">
            {/* Decorative background */}
            <div className="absolute top-1/4 left-0 w-72 h-72 bg-brand/5 rounded-full blur-3xl -translate-x-1/2 pointer-events-none" />
            <div className="absolute bottom-1/4 right-0 w-96 h-96 bg-brand/5 rounded-full blur-3xl translate-x-1/3 pointer-events-none" />

            <div className="relative w-full max-w-lg text-center">
                {/* Icon */}
                <div className="mx-auto mb-8 flex items-center justify-center w-24 h-24 rounded-3xl bg-brand/10 border border-brand/10 shadow-sm shadow-brand/5">
                    <LuPackageCheck size={40} className="text-brand" strokeWidth={1.5} />
                </div>

                {/* 404 */}
                <p className="text-8xl sm:text-9xl font-black text-gray-100 tracking-tighter leading-none select-none">
                    404
                </p>

                {/* Content */}
                <div className="relative -mt-8 sm:-mt-10">
                    <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">
                        Page not found
                    </h1>
                    <p className="text-sm sm:text-base text-gray-500 mt-3 leading-relaxed max-w-sm mx-auto">
                        The page you're looking for doesn't exist, or the listing may have expired. Let's get you back to browsing.
                    </p>
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-3 mt-10 justify-center">
                    <Link
                        to="/"
                        className="flex items-center justify-center gap-2 bg-brand text-white font-bold rounded-xl px-6 py-3.5 hover:opacity-90 active:scale-[0.98] transition-all shadow-lg shadow-brand/20"
                    >
                        <IoHome size={18} />
                        Back to home
                    </Link>

                    <Link
                        to="/search"
                        className="flex items-center justify-center gap-2 bg-white border-2 border-gray-200 text-gray-700 font-bold rounded-xl px-6 py-3.5 hover:border-gray-300 hover:bg-gray-50 active:scale-[0.98] transition-all"
                    >
                        <IoIosSearch size={18} />
                        Search listings
                    </Link>
                </div>

                {/* Go back */}
                <button
                    type="button"
                    onClick={() => navigate(-1)}
                    className="group inline-flex items-center gap-2 mx-auto mt-8 text-sm font-semibold text-gray-400 hover:text-brand transition-colors"
                >
                    <span className="flex items-center justify-center w-7 h-7 rounded-full bg-gray-100 group-hover:bg-brand/10 transition-colors">
                        <FaArrowLeft size={12} />
                    </span>
                    Go back
                </button>
            </div>
        </div>
    );
};

export default NotFound;