import LeftComponent from "./LeftComponent.jsx";
import RightComponent from "./RightComponent.jsx";
import GlobalSearch from "./GlobalSearch.jsx";
import CategoryNav from "./CategoryNav.jsx";
import MobileBottomNav from "./MobileBottomNav.jsx";
import { Link } from "react-router-dom";
import { useSelector } from "react-redux";
import { FaPlus } from "react-icons/fa";

const Header = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);

    return (
        <>
            <header className="fixed top-0 z-50 w-full bg-brand shadow-md">
                {/* Row 1: brand + search + account + post ad */}
                <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-2.5 lg:gap-5 lg:px-8">
                    <LeftComponent />

                    <div className="hidden min-w-0 flex-1 md:block">
                        <GlobalSearch />
                    </div>

                    <div className="ml-auto flex items-center gap-2 md:ml-0">
                        <Link
                            to={isAuthenticated ? "/sell" : "/sign-in"}
                            className="hidden items-center gap-1.5 rounded-xl bg-brand px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-colors hover:bg-brand/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 lg:flex"
                        >
                            <FaPlus size={13} aria-hidden="true" />
                            Post Ad
                        </Link>
                        <RightComponent />
                    </div>
                </div>

                {/* Mobile search row */}
                <div className="px-4 pb-2.5 md:hidden">
                    <GlobalSearch compact />
                </div>

                {/* Row 2: category navigation (desktop) */}
                <div className="hidden md:block">
                    <CategoryNav />
                </div>
            </header>

            <MobileBottomNav />
        </>
    );
};

export default Header;
