import { NavLink } from "react-router-dom";

const LeftComponent = () => {
    return (
        <NavLink 
            to="/" 
            className="flex items-center gap-2.5 group focus:outline-none"
        >
            {/* Logo Mark */}
            <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-white text-brand font-black text-sm shadow-sm group-hover:scale-105 group-hover:shadow-md transition-all duration-200">
                NB
            </div>
            
            {/* Brand Name */}
            <div className="flex items-baseline">
                <span className="text-white font-extrabold text-2xl tracking-tight group-hover:opacity-90 transition-opacity">
                    Naija
                </span>
                <span className="text-white/70 font-extrabold text-2xl tracking-tight group-hover:text-white transition-colors duration-200">
                    Bay
                </span>
            </div>
        </NavLink>
    );
};

export default LeftComponent;