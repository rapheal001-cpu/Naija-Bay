import { AiOutlineLoading3Quarters } from "react-icons/ai";


const SkeletonCategories = () => {
    const skeletonItems = [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
    ]

    return (
        <>
            {skeletonItems.map((item) => (
                <div key={item} className="flex flex-col items-center gap-2 shrink-0 w-16 text-center snap-start group opacity-80 hover:opacity-100 transition-opacity">
                    <span className="flex items-center justify-center w-11 h-11 rounded-full bg-gray-200 text-gray-600 group-hover:bg-brand group-hover:text-white transition-colors">
                        <AiOutlineLoading3Quarters size={16} className="animate-spin" />
                    </span>
                </div>
            ))}
        </>
    )
}

export default SkeletonCategories;