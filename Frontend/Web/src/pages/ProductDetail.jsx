import {useParams} from 'react-router-dom';
import Product from "../components/ProductComponents/Product.jsx";
import { useDispatch } from 'react-redux';
import { useFetchProductDetailData } from '../hooks/UseQuery.js';
import { useEffect } from 'react';
import { setProductDetail } from '../slice/ProductSlice.js';


const ProductDetail = () => {
    const { product_slug } = useParams();
    const dispatch = useDispatch();

    const fetchProductDetail = useFetchProductDetailData(product_slug);

    useEffect(() => {
        if (fetchProductDetail.isSuccess && fetchProductDetail.data) {
            dispatch(setProductDetail(fetchProductDetail.data));
        }
    }, [fetchProductDetail.isSuccess, fetchProductDetail.data, dispatch]);


    return (
        <Product/>
    )
};

export default ProductDetail;