import { MdOutlineCancel } from "react-icons/md";

const ProductImagePreview = ({ src, index, removeImage }) => {
    const isMain = index === 0;

    return (
        <div className="group relative aspect-square rounded-2xl overflow-hidden bg-gray-100 ring-1 ring-black/5 shadow-sm hover:shadow-lg transition-all duration-300 ease-out">
            {/* Image */}
            <img
                src={src}
                alt={`Product preview ${index + 1}`}
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 ease-out group-hover:scale-110"
            />

            {/* Gradient overlay on hover */}
            <div className="absolute inset-0 bg-linear-to-t from-black/40 via-black/0 to-black/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

            {/* Main image badge */}
            {isMain && (
                <div className="absolute top-3 left-3 px-2.5 py-1 rounded-full bg-brand/90 backdrop-blur-md text-white text-[10px] font-bold uppercase tracking-wider shadow-lg">
                    Main
                </div>
            )}

            {/* Index badge (hidden for main, shown for others) */}
            {!isMain && (
                <div className="absolute top-3 left-3 flex items-center justify-center w-7 h-7 rounded-full bg-white/90 backdrop-blur-md text-gray-700 text-xs font-bold shadow-md border border-white/60">
                    {index + 1}
                </div>
            )}

            {/* Remove button */}
            <button
                type="button"
                onClick={() => removeImage(index)}
                aria-label={`Remove image ${index + 1}`}
                className="absolute top-3 right-3 flex items-center justify-center w-8 h-8 rounded-full bg-white/90 backdrop-blur-md text-gray-500 hover:text-white hover:bg-red-500 shadow-md border border-white/60 transition-all duration-200 ease-out hover:scale-110 active:scale-90 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2"
            >
                <MdOutlineCancel size={18} />
            </button>

            {/* Bottom hint */}
            <div className="absolute bottom-0 inset-x-0 py-2.5 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out">
                <p className="text-center text-white text-[11px] font-semibold drop-shadow-md">
                    {isMain ? 'Main photo' : `Photo ${index + 1}`}
                </p>
            </div>
        </div>
    );
};

export default ProductImagePreview;