const SkeletonProductCard = () => {
    const skeletonCard = [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
    ];

    return (
        <>
            {skeletonCard.map((item) => (
                <div key={item} className="bg-white rounded-xl border border-gray-100 p-3 overflow-hidden">
                    <div className="bg-gray-100 aspect-4/4 w-full rounded-lg" />

                    <div className="mt-3 h-4 w-16 bg-gray-100 rounded-md" />

                    <div className="mt-2 h-4 w-32 bg-gray-100 rounded-md" />

                    <div className="mt-2 h-3 w-full bg-gray-100 rounded-md" />

                    <div className="mt-3 flex items-center justify-between">
                        <div className="h-5 w-20 bg-gray-100 rounded-md" />
                        <div className="h-3 w-10 bg-gray-100 rounded-md" />
                    </div>
                </div>
            ))}
        </>
    );
};

export default SkeletonProductCard;