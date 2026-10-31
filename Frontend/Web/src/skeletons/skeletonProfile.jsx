const SkeletonProfile = () => {
    return (
        <>
            {/* Header */}
            <div className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="bg-gray-100 h-8 w-28 rounded-lg" />
                    <div className="flex items-center gap-3">
                        <div className="bg-gray-100 h-9 w-9 rounded-xl" />
                        <div className="bg-gray-100 h-9 w-9 rounded-xl" />
                        <div className="bg-gray-100 h-9 w-9 rounded-full" />
                    </div>
                </div>
            </div>

            <div className="h-16" />

            <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Profile Header */}
                <div className="relative bg-white border border-gray-100 rounded-3xl shadow-sm overflow-hidden">
                    <div className="bg-gray-100 h-28 sm:h-36 w-full" />

                    <div className="px-5 sm:px-8 pb-6 sm:pb-8">
                        <div className="flex flex-col sm:flex-row sm:items-end gap-4 -mt-12 sm:-mt-14">
                            <div className="bg-gray-200 h-24 w-24 sm:h-28 sm:w-28 rounded-2xl border-4 border-white shadow-lg shrink-0" />
                            
                            <div className="flex-1 min-w-0 sm:pb-1 space-y-2">
                                <div className="bg-gray-100 h-7 sm:h-8 w-48 rounded-md" />
                                <div className="bg-gray-100 h-4 w-32 rounded-md" />
                            </div>

                            <div className="flex items-center gap-2 sm:pb-1">
                                <div className="bg-gray-100 h-10 w-10 rounded-xl" />
                                <div className="bg-gray-100 h-10 w-10 rounded-xl" />
                            </div>
                        </div>

                        <div className="flex flex-wrap items-center gap-2 mt-5">
                            <div className="bg-gray-100 h-7 w-28 rounded-full" />
                            <div className="bg-gray-100 h-7 w-32 rounded-full" />
                            <div className="bg-gray-100 h-7 w-36 rounded-full" />
                        </div>

                        <div className="flex items-center gap-6 mt-5 pt-5 border-t border-gray-100">
                            <div className="text-center sm:text-left space-y-1.5">
                                <div className="bg-gray-100 h-7 w-16 rounded-md mx-auto sm:mx-0" />
                                <div className="bg-gray-100 h-3 w-20 rounded-md mx-auto sm:mx-0" />
                            </div>
                            <div className="text-center sm:text-left space-y-1.5">
                                <div className="bg-gray-100 h-7 w-16 rounded-md mx-auto sm:mx-0" />
                                <div className="bg-gray-100 h-3 w-20 rounded-md mx-auto sm:mx-0" />
                            </div>
                            <div className="text-center sm:text-left space-y-1.5">
                                <div className="bg-gray-100 h-7 w-16 rounded-md mx-auto sm:mx-0" />
                                <div className="bg-gray-100 h-3 w-20 rounded-md mx-auto sm:mx-0" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Contact & Stats */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
                    {/* Contact Card */}
                    <div className="lg:col-span-2 bg-white border border-gray-100 rounded-3xl shadow-sm p-6 sm:p-7">
                        <div className="flex items-center gap-2.5 mb-5">
                            <div className="bg-gray-100 w-8 h-8 rounded-lg" />
                            <div className="bg-gray-100 h-4 w-32 rounded-md" />
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="flex items-center gap-3.5 p-3.5 rounded-2xl bg-gray-50/50 border border-gray-50">
                                <div className="bg-gray-100 w-10 h-10 rounded-xl shrink-0" />
                                <div className="min-w-0 space-y-1.5 flex-1">
                                    <div className="bg-gray-100 h-3 w-16 rounded-md" />
                                    <div className="bg-gray-100 h-4 w-full max-w-[140px] rounded-md" />
                                </div>
                            </div>
                            <div className="flex items-center gap-3.5 p-3.5 rounded-2xl bg-gray-50/50 border border-gray-50">
                                <div className="bg-gray-100 w-10 h-10 rounded-xl shrink-0" />
                                <div className="min-w-0 space-y-1.5 flex-1">
                                    <div className="bg-gray-100 h-3 w-16 rounded-md" />
                                    <div className="bg-gray-100 h-4 w-full max-w-[140px] rounded-md" />
                                </div>
                            </div>
                            <div className="flex items-center gap-3.5 p-3.5 rounded-2xl bg-gray-50/50 border border-gray-50">
                                <div className="bg-gray-100 w-10 h-10 rounded-xl shrink-0" />
                                <div className="min-w-0 space-y-1.5 flex-1">
                                    <div className="bg-gray-100 h-3 w-16 rounded-md" />
                                    <div className="bg-gray-100 h-4 w-full max-w-[140px] rounded-md" />
                                </div>
                            </div>
                            <div className="flex items-center gap-3.5 p-3.5 rounded-2xl bg-gray-50/50 border border-gray-50">
                                <div className="bg-gray-100 w-10 h-10 rounded-xl shrink-0" />
                                <div className="min-w-0 space-y-1.5 flex-1">
                                    <div className="bg-gray-100 h-3 w-16 rounded-md" />
                                    <div className="bg-gray-100 h-4 w-full max-w-[140px] rounded-md" />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="lg:col-span-1 grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 gap-3 sm:gap-4">
                        <div className="relative flex items-center gap-3 sm:gap-4 bg-white border border-gray-100 rounded-xl sm:rounded-2xl p-4 sm:p-5 overflow-hidden">
                            <div className="bg-gray-100 w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl shrink-0" />
                            <div className="min-w-0 space-y-1.5">
                                <div className="bg-gray-100 h-6 sm:h-7 w-12 rounded-md" />
                                <div className="bg-gray-100 h-3 w-24 rounded-md" />
                            </div>
                            <div className="bg-gray-100 absolute top-0 right-0 w-12 h-12 sm:w-16 sm:h-16 rounded-bl-[32px] sm:rounded-bl-[40px] opacity-30 hidden sm:block" />
                        </div>
                        <div className="relative flex items-center gap-3 sm:gap-4 bg-white border border-gray-100 rounded-xl sm:rounded-2xl p-4 sm:p-5 overflow-hidden">
                            <div className="bg-gray-100 w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl shrink-0" />
                            <div className="min-w-0 space-y-1.5">
                                <div className="bg-gray-100 h-6 sm:h-7 w-12 rounded-md" />
                                <div className="bg-gray-100 h-3 w-24 rounded-md" />
                            </div>
                            <div className="bg-gray-100 absolute top-0 right-0 w-12 h-12 sm:w-16 sm:h-16 rounded-bl-[32px] sm:rounded-bl-[40px] opacity-30 hidden sm:block" />
                        </div>
                        <div className="relative flex items-center gap-3 sm:gap-4 bg-white border border-gray-100 rounded-xl sm:rounded-2xl p-4 sm:p-5 overflow-hidden">
                            <div className="bg-gray-100 w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl shrink-0" />
                            <div className="min-w-0 space-y-1.5">
                                <div className="bg-gray-100 h-6 sm:h-7 w-12 rounded-md" />
                                <div className="bg-gray-100 h-3 w-24 rounded-md" />
                            </div>
                            <div className="bg-gray-100 absolute top-0 right-0 w-12 h-12 sm:w-16 sm:h-16 rounded-bl-[32px] sm:rounded-bl-[40px] opacity-30 hidden sm:block" />
                        </div>
                    </div>
                </div>

                {/* Listings */}
                <div className="mt-10">
                    <div className="flex items-center justify-between mb-1">
                        <div className="bg-gray-100 h-6 w-24 rounded-md" />
                        <div className="bg-gray-100 h-4 w-16 rounded-md" />
                    </div>

                    <div className="flex items-center gap-1 p-1 bg-gray-100 rounded-xl w-fit mt-4">
                        <div className="bg-white h-9 w-24 rounded-lg" />
                        <div className="bg-gray-100 h-9 w-24 rounded-lg" />
                        <div className="bg-gray-100 h-9 w-24 rounded-lg" />
                    </div>

                    <div className="w-full h-px bg-gray-100 mt-6 mb-6" />

                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
                        <div className="space-y-3">
                            <div className="bg-gray-100 aspect-[4/5] w-full rounded-2xl" />
                            <div className="bg-gray-100 h-4 w-3/4 rounded-md" />
                            <div className="flex items-center justify-between">
                                <div className="bg-gray-100 h-5 w-16 rounded-md" />
                                <div className="bg-gray-100 h-4 w-12 rounded-md" />
                            </div>
                        </div>
                        <div className="space-y-3">
                            <div className="bg-gray-100 aspect-[4/5] w-full rounded-2xl" />
                            <div className="bg-gray-100 h-4 w-3/4 rounded-md" />
                            <div className="flex items-center justify-between">
                                <div className="bg-gray-100 h-5 w-16 rounded-md" />
                                <div className="bg-gray-100 h-4 w-12 rounded-md" />
                            </div>
                        </div>
                        <div className="space-y-3">
                            <div className="bg-gray-100 aspect-[4/5] w-full rounded-2xl" />
                            <div className="bg-gray-100 h-4 w-3/4 rounded-md" />
                            <div className="flex items-center justify-between">
                                <div className="bg-gray-100 h-5 w-16 rounded-md" />
                                <div className="bg-gray-100 h-4 w-12 rounded-md" />
                            </div>
                        </div>
                        <div className="space-y-3">
                            <div className="bg-gray-100 aspect-[4/5] w-full rounded-2xl" />
                            <div className="bg-gray-100 h-4 w-3/4 rounded-md" />
                            <div className="flex items-center justify-between">
                                <div className="bg-gray-100 h-5 w-16 rounded-md" />
                                <div className="bg-gray-100 h-4 w-12 rounded-md" />
                            </div>
                        </div>
                        <div className="space-y-3">
                            <div className="bg-gray-100 aspect-[4/5] w-full rounded-2xl" />
                            <div className="bg-gray-100 h-4 w-3/4 rounded-md" />
                            <div className="flex items-center justify-between">
                                <div className="bg-gray-100 h-5 w-16 rounded-md" />
                                <div className="bg-gray-100 h-4 w-12 rounded-md" />
                            </div>
                        </div>
                        <div className="space-y-3">
                            <div className="bg-gray-100 aspect-[4/5] w-full rounded-2xl" />
                            <div className="bg-gray-100 h-4 w-3/4 rounded-md" />
                            <div className="flex items-center justify-between">
                                <div className="bg-gray-100 h-5 w-16 rounded-md" />
                                <div className="bg-gray-100 h-4 w-12 rounded-md" />
                            </div>
                        </div>
                        <div className="space-y-3">
                            <div className="bg-gray-100 aspect-[4/5] w-full rounded-2xl" />
                            <div className="bg-gray-100 h-4 w-3/4 rounded-md" />
                            <div className="flex items-center justify-between">
                                <div className="bg-gray-100 h-5 w-16 rounded-md" />
                                <div className="bg-gray-100 h-4 w-12 rounded-md" />
                            </div>
                        </div>
                        <div className="space-y-3">
                            <div className="bg-gray-100 aspect-[4/5] w-full rounded-2xl" />
                            <div className="bg-gray-100 h-4 w-3/4 rounded-md" />
                            <div className="flex items-center justify-between">
                                <div className="bg-gray-100 h-5 w-16 rounded-md" />
                                <div className="bg-gray-100 h-4 w-12 rounded-md" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default SkeletonProfile;