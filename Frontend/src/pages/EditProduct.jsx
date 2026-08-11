import { useEffect } from 'react';
import { useNavigate, useParams } from "react-router-dom";
import { HiOutlineArrowLeft } from "react-icons/hi2";
import { HiOutlineShieldCheck } from "react-icons/hi";
import Header from "../components/HeaderComponents/Header.jsx";
import Spacer from "../components/Spacer.jsx";
import { useSelector, useDispatch } from 'react-redux';
import EditProductForm from '../components/ProductComponents/EditProductForm.jsx';
import { useFetchProductDetailData } from '../hooks/UseQuery.js';
import { setProductDetail } from '../slice/ProductSlice.js';


const EditProduct = () => {
    const { product_slug } = useParams();

    const dispatch = useDispatch();
    const navigate = useNavigate();

    const user = useSelector((state) => state.user.user);
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);

    const product = useSelector((state) => state.products?.productDetail);

    const fetchProductDetail = useFetchProductDetailData(product_slug);

    useEffect(() => {
        if (!isAuthenticated && !user) {
            navigate('/sign-in', { replace: true });
        }
    }, [isAuthenticated, user, navigate]);

    
    useEffect(() => {
        if (product && user) {
            const OwnerId = product?.product_user?.id;
            if (OwnerId && OwnerId !== user.id) {
                navigate('/', { replace: true });
            }
        }
    }, [product, user, navigate]);

    useEffect(() => {
        if (fetchProductDetail.isSuccess && fetchProductDetail.data) {
            dispatch(setProductDetail(fetchProductDetail.data));
        }
    }, [fetchProductDetail.isSuccess, fetchProductDetail.data, dispatch]);


    if (fetchProductDetail.isLoading) {
        return (
            <>
                <Header />
                <Spacer space={'mb-20'} />
                <div className="min-h-screen bg-linear-to-b from-gray-50 to-white flex items-center justify-center">
                    <div className="flex flex-col items-center gap-3">
                        <div className="w-10 h-10 border-4 border-brand/20 border-t-brand rounded-full animate-spin" />
                        <p className="text-sm text-gray-500 font-medium">Loading product...</p>
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
            <Header />
            <Spacer space={'mb-20'} />

            <div className="min-h-screen bg-linear-to-b from-gray-50 to-white py-10 sm:py-14 relative overflow-hidden">
                {/* Decorative background */}
                <div className="absolute top-0 left-0 w-96 h-96 bg-brand/5 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
                <div className="absolute bottom-0 right-0 w-120 h-120 bg-brand/5 rounded-full blur-3xl translate-x-1/3 translate-y-1/3 pointer-events-none" />

                <div className="relative max-w-3xl mx-auto px-4 sm:px-6">
                    {/* Top bar */}
                    <div className="flex items-center justify-between mb-8">
                        <button
                            type="button"
                            onClick={() => navigate(-1)}
                            className="group inline-flex items-center gap-2 text-sm font-semibold text-gray-500 hover:text-gray-900 transition-colors"
                        >
                            <span className="flex items-center justify-center w-9 h-9 rounded-full bg-white border border-gray-200 group-hover:border-gray-300 group-hover:shadow-md transition-all shadow-sm">
                                <HiOutlineArrowLeft size={16} />
                            </span>
                            <span className="hidden sm:inline">Back</span>
                        </button>

                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-brand flex items-center justify-center shadow-sm shadow-brand/20">
                                <HiOutlineShieldCheck className="text-white" size={16} />
                            </div>
                            <span className="text-lg font-black text-gray-900 tracking-tight">NaijaBay</span>
                        </div>
                    </div>

                    {/* Page header */}
                    <div className="mb-8">
                        <h1 className="text-3xl sm:text-4xl font-black text-gray-900 tracking-tight">
                            Edit Product
                        </h1>
                        <p className="text-sm sm:text-base text-gray-500 mt-2 leading-relaxed max-w-lg">
                            Update your product details, pricing, or photos. Your changes will go live immediately after saving.
                        </p>
                    </div>

                    {/* Form */}
                    <div className="bg-white rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100 p-6 sm:p-10">
                        <EditProductForm
                            productSlug={product_slug}
                            initialData={product}
                        />
                    </div>

                    {/* Footer hint */}
                    <p className="text-center text-xs text-gray-400 mt-8">
                        By saving changes, you confirm that all information provided is accurate and up to date.
                    </p>
                </div>
            </div>
        </>
    );
};

export default EditProduct;