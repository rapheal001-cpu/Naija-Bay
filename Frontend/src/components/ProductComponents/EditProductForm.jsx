import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { RiUploadCloud2Fill, RiLoader3Line, RiCheckLine, RiCloseLine } from "react-icons/ri";
import {
    HiOutlinePhotograph, HiOutlineTag, HiOutlineDocumentText,
    HiOutlineCollection, HiOutlineColorSwatch, HiOutlineLocationMarker,
    HiOutlineChatAlt2, HiOutlineExclamationCircle, HiOutlineEye, HiOutlineCheckCircle
} from 'react-icons/hi';
import {
    HiOutlineCube, HiOutlineScale, HiOutlineBanknotes, HiOutlinePhone
} from "react-icons/hi2";
import {
    categories, CATEGORY_SUBCATEGORY_MAP, CONDITION_CHOICES,
    CONTACT_METHOD_CHOICES, MAX_IMAGES, STATE_CHOICES, STATE_CITY_MAP
} from "../../dummyData.js";
import ProductImagePreview from "./ProductImagePreview.jsx";
import {
    useUpdateProductImagesMutation,
    useUpdateProductMutation,
    useDeleteProductImageMutation,
} from '../../hooks/UseMutation.js';


const toBackendSlug = (str) => {
    if (!str) return '';
    return str.toLowerCase().trim().replace(/[\s\-/]/g, '_');
};

const buildDefaultValues = (data) => ({
    product_name: data?.product_name || '',
    description: data?.description || '',
    price: data?.price ?? '',
    category: data?.category || '',
    sub_category: data?.sub_category || '',
    condition: data?.condition || '',
    color: data?.color || '#000000',
    quantity: data?.quantity ?? 1,
    negotiable: !!data?.negotiable,
    state: data?.state || '',
    city: data?.city || '',
    contact_methods: data?.contact_methods || [],
    contact_number: data?.contact_number || '',
    active: data?.active ?? true,
    sold: data?.sold ?? false,
});

const EditProductForm = ({ productSlug, initialData }) => {
    const navigate = useNavigate();

    // --- Images state ---
    const [imageFiles, setImageFiles] = useState([]);
    const [imagePreviews, setImagePreviews] = useState([]);
    const [existingImages, setExistingImages] = useState([]);
    const [removedImageIds, setRemovedImageIds] = useState([]);
    const [imageError, setImageError] = useState('');

    // --- Form & UI state ---
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState('');
    const [serverError, setServerError] = useState([]);
    const [success, setSuccess] = useState(false);

    // Initialize form WITH defaultValues
    const { register, handleSubmit, watch, reset, setValue, formState: { errors }, setError } = useForm({
        defaultValues: buildDefaultValues(initialData),
    });

    const selectedMethods = watch('contact_methods') || [];
    const isActive = watch('active');
    const isSold = watch('sold');

    // Mutual exclusivity: sold ↔ active
    useEffect(() => {
        if (isSold && isActive) {
            setValue('active', false, { shouldValidate: false });
        }
    }, [isSold, isActive, setValue]);

    useEffect(() => {
        if (isActive && isSold) {
            setValue('sold', false, { shouldValidate: false });
        }
    }, [isActive, isSold, setValue]);

    const needsPhone = selectedMethods.some(m =>
        ['phone_call', 'whatsapp'].includes(m)
    );
    const hasPhoneCall = selectedMethods.includes('phone_call');
    const hasWhatsapp = selectedMethods.includes('whatsapp');

    const selectedState = watch('state');
    const cities = selectedState ? STATE_CITY_MAP[selectedState] : [];

    const selectedCategory = watch('category');
    const subCategories = selectedCategory ? CATEGORY_SUBCATEGORY_MAP[selectedCategory] : [];

    const remainingExistingCount = existingImages.filter(img => !removedImageIds.includes(img.id)).length;
    const totalImageCount = remainingExistingCount + imageFiles.length;

    useEffect(() => {
        if (initialData?.images && Array.isArray(initialData.images)) {
            setExistingImages(initialData.images);
        }
    }, [initialData]);

    useEffect(() => {
        if (initialData) {
            reset(buildDefaultValues(initialData));
        }
    }, [initialData, reset]);

    // --- Image handlers ---
    const handleImageChange = (e) => {
        const files = Array.from(e.target.files);
        if (totalImageCount + files.length > MAX_IMAGES) {
            setImageError(`You can have a maximum of ${MAX_IMAGES} images.`);
            return;
        }
        const newFiles = [...imageFiles, ...files];
        const newPreviews = [...imagePreviews, ...files.map((f) => URL.createObjectURL(f))];
        setImageFiles(newFiles);
        setImagePreviews(newPreviews);
        setImageError('');
        e.target.value = '';
    };

    const removeNewImage = (index) => {
        URL.revokeObjectURL(imagePreviews[index]);
        setImageFiles((prev) => prev.filter((_, i) => i !== index));
        setImagePreviews((prev) => prev.filter((_, i) => i !== index));
    };

    const removeExistingImage = (imageId) => {
        setRemovedImageIds((prev) => [...prev, imageId]);
        setImageError('');
    };

    const restoreExistingImage = (imageId) => {
        setRemovedImageIds((prev) => prev.filter(id => id !== imageId));
    };

    // --- Mutations ---
    const updateProductData = useUpdateProductMutation(setError, setServerError);
    const updateProductImagesData = useUpdateProductImagesMutation(setServerError);
    const deleteProductImageData = useDeleteProductImageMutation(setServerError);

    const onSubmit = async (data) => {
        if (totalImageCount === 0) {
            setImageError('At least one product image is required.');
            return;
        }

        try {
            setIsSubmitting(true);
            setImageError('');
            setSubmitError('');
            setServerError([]);

            const payload = {
                product_name: data.product_name,
                description: data.description,
                price: data.price,
                category: data.category,
                sub_category: data.sub_category,
                condition: data.condition,
                color: data.color,
                quantity: data.quantity,
                negotiable: !!data.negotiable,
                state: data.state,
                city: data.city,
                active: data.active,
                sold: data.sold,
                contact_methods: data.contact_methods,
                ...(needsPhone && data.contact_number ? { contact_number: data.contact_number } : {}),
            };

            const updatedProduct = await updateProductData.mutateAsync({
                slug: productSlug,
                payload,
            });

            if (removedImageIds.length > 0) {
                await Promise.all(
                    removedImageIds.map((imageId) => deleteProductImageData.mutateAsync(imageId))
                );
            }

            if (imageFiles.length > 0) {
                await updateProductImagesData.mutateAsync({
                    product: {
                        id: updatedProduct?.id ?? initialData?.id,
                    },
                    images: imageFiles,
                });
            }

            setSuccess(true);

            setTimeout(() => {
                navigate(`/product/detail/${productSlug}`);
            }, 1500);

        } catch (error) {
            setSubmitError(error?.message || 'Unable to update your listing right now. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const inputBase = "w-full border rounded-xl pl-11 pr-4 py-3 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-4 transition-all";
    const inputError = "border-red-300 focus:border-red-400 bg-red-50/30 focus:ring-red-100";
    const inputNormal = "border-gray-200 focus:border-brand focus:ring-brand/10";

    if (success) {
        return (
            <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mb-4">
                    <RiCheckLine size={32} className="text-emerald-600" />
                </div>
                <h2 className="text-xl font-bold text-gray-900">Changes saved!</h2>
                <p className="text-sm text-gray-500 mt-1">Redirecting to your listing...</p>
            </div>
        );
    }

    return (
        <>
            {(submitError || serverError.length > 0) && (
                <div className="flex items-start gap-3 p-4 rounded-2xl bg-red-50 border border-red-100 mb-6">
                    <HiOutlineExclamationCircle size={20} className="text-red-500 shrink-0 mt-0.5" />
                    <div className="space-y-1">
                        {submitError && <p className="text-red-600 text-sm font-semibold leading-snug">{submitError}</p>}
                        {serverError.map((err, i) => (
                            <p key={i} className="text-red-600 text-sm font-semibold leading-snug">
                                {typeof err === 'string' ? err : JSON.stringify(err)}
                            </p>
                        ))}
                    </div>
                </div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-8">

                {/* Section: Photos */}
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <HiOutlinePhotograph size={18} className="text-brand" />
                        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Photos</h3>
                        <span className="text-xs text-gray-400 font-medium">
                            ({totalImageCount}/{MAX_IMAGES})
                        </span>
                    </div>

                    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                        {existingImages.map((img) => {
                            const isRemoved = removedImageIds.includes(img.id);
                            if (isRemoved) return null;
                            return (
                                <div key={img.id} className="relative aspect-square rounded-2xl overflow-hidden border border-gray-200 group">
                                    <img
                                        src={img.image || img.url || img.image_url}
                                        alt="Product"
                                        className="w-full h-full object-cover"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => removeExistingImage(img.id)}
                                        className="absolute top-1.5 right-1.5 w-7 h-7 bg-black/60 hover:bg-black/80 text-white rounded-full flex items-center justify-center backdrop-blur-sm transition-colors"
                                        title="Remove image"
                                    >
                                        <RiCloseLine size={16} />
                                    </button>
                                </div>
                            );
                        })}

                        {imagePreviews.map((src, index) => (
                            <ProductImagePreview key={`new-${index}`} src={src} index={index} removeImage={removeNewImage} />
                        ))}

                        {totalImageCount < MAX_IMAGES && (
                            <label className="group flex flex-col items-center justify-center gap-2 aspect-square rounded-2xl border-2 border-dashed border-gray-200 text-gray-400 hover:border-brand hover:text-brand hover:bg-brand/3 cursor-pointer transition-all">
                                <RiUploadCloud2Fill size={28} className="group-hover:scale-110 transition-transform" />
                                <span className="text-xs font-bold">Add photo</span>
                                <input
                                    type="file"
                                    accept="image/jpeg, image/jpg, image/png"
                                    multiple
                                    onChange={handleImageChange}
                                    className="hidden"
                                />
                            </label>
                        )}
                    </div>

                    {removedImageIds.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                            {existingImages
                                .filter(img => removedImageIds.includes(img.id))
                                .map(img => (
                                    <button
                                        key={img.id}
                                        type="button"
                                        onClick={() => restoreExistingImage(img.id)}
                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-brand bg-brand/5 border border-brand/10 rounded-lg hover:bg-brand/10 transition-colors"
                                    >
                                        <RiUploadCloud2Fill size={12} />
                                        Restore image
                                    </button>
                                ))}
                        </div>
                    )}

                    {imageError && <p className="text-red-500 text-xs font-semibold">{imageError}</p>}
                </div>

                <div className="w-full h-px bg-gray-100" />

                {/* Section: Status (Active / Sold) */}
                <div className="space-y-5">
                    <div className="flex items-center gap-2">
                        <HiOutlineCheckCircle size={18} className="text-brand" />
                        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Listing Status</h3>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {/* Active Switch */}
                        <label className="flex items-center justify-between p-4 rounded-2xl bg-gray-50 border border-gray-100 cursor-pointer hover:bg-gray-100 transition-colors select-none">
                            <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${isActive ? 'bg-brand/10 text-brand' : 'bg-gray-200 text-gray-400'}`}>
                                    <HiOutlineEye size={20} />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-gray-900">Active</p>
                                    <p className="text-xs text-gray-500">Buyers can see this listing</p>
                                </div>
                            </div>
                            <div className="relative inline-flex items-center">
                                <input
                                    type="checkbox"
                                    className="sr-only peer"
                                    {...register('active')}
                                />
                                <div className="w-12 h-7 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-brand/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-brand" />
                            </div>
                        </label>

                        {/* Sold Switch */}
                        <label className="flex items-center justify-between p-4 rounded-2xl bg-gray-50 border border-gray-100 cursor-pointer hover:bg-gray-100 transition-colors select-none">
                            <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${isSold ? 'bg-emerald-500/10 text-emerald-600' : 'bg-gray-200 text-gray-400'}`}>
                                    <HiOutlineCheckCircle size={20} />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-gray-900">Sold</p>
                                    <p className="text-xs text-gray-500">Mark this item as sold</p>
                                </div>
                            </div>
                            <div className="relative inline-flex items-center">
                                <input
                                    type="checkbox"
                                    className="sr-only peer"
                                    {...register('sold')}
                                />
                                <div className="w-12 h-7 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-emerald-500" />
                            </div>
                        </label>
                    </div>
                </div>

                <div className="w-full h-px bg-gray-100" />

                {/* Section: Basic Info */}
                <div className="space-y-5">
                    <div className="flex items-center gap-2">
                        <HiOutlineTag size={18} className="text-brand" />
                        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Basic Info</h3>
                    </div>

                    <div className="space-y-1.5">
                        <label htmlFor="product_name" className="text-[13px] font-bold text-gray-700 ml-1">Product name</label>
                        <div className="relative">
                            <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"><HiOutlineTag size={18} /></span>
                            <input
                                id="product_name"
                                type="text"
                                placeholder="e.g. iPhone 13 Pro Max 256GB"
                                {...register('product_name', {
                                    required: 'Product name is required.',
                                    minLength: { value: 3, message: 'Product name must be at least 3 characters.' }
                                })}
                                className={`${inputBase} ${errors.product_name ? inputError : inputNormal}`}
                            />
                        </div>
                        {errors.product_name && <p className="text-red-500 text-xs font-semibold ml-1">{errors.product_name.message}</p>}
                    </div>

                    <div className="space-y-1.5">
                        <label htmlFor="description" className="text-[13px] font-bold text-gray-700 ml-1">Description</label>
                        <div className="relative">
                            <span className="absolute left-3.5 top-3.5 text-gray-400"><HiOutlineDocumentText size={18} /></span>
                            <textarea
                                id="description"
                                rows={5}
                                placeholder="Describe the item's condition, features, and any other details buyers should know..."
                                {...register('description', {
                                    required: 'Product description is required.',
                                    minLength: { value: 20, message: 'Description must be at least 20 characters.' }
                                })}
                                className={`${inputBase} ${errors.description ? inputError : inputNormal} resize-none pt-3!`}
                            />
                        </div>
                        {errors.description && <p className="text-red-500 text-xs font-semibold ml-1">{errors.description.message}</p>}
                    </div>
                </div>

                <div className="w-full h-px bg-gray-100" />

                {/* Section: Pricing */}
                <div className="space-y-5">
                    <div className="flex items-center gap-2">
                        <HiOutlineBanknotes size={18} className="text-brand" />
                        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Pricing</h3>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                            <label htmlFor="price" className="text-[13px] font-bold text-gray-700 ml-1">Price (₦)</label>
                            <div className="relative">
                                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"><HiOutlineBanknotes size={18} /></span>
                                <input
                                    id="price"
                                    type="number"
                                    step="0.01"
                                    placeholder="1000"
                                    {...register('price', {
                                        required: 'Price is required.',
                                        min: { value: 1000, message: 'Price must be at least ₦1,000.' },
                                        max: { value: 999999999, message: 'Price seems too high.' },
                                        valueAsNumber: true
                                    })}
                                    className={`${inputBase} ${errors.price ? inputError : inputNormal}`}
                                />
                            </div>
                            {errors.price && <p className="text-red-500 text-xs font-semibold ml-1">{errors.price.message}</p>}
                        </div>

                        <div className="space-y-1.5">
                            <label htmlFor="quantity" className="text-[13px] font-bold text-gray-700 ml-1">Quantity</label>
                            <div className="relative">
                                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"><HiOutlineCube size={18} /></span>
                                <input
                                    id="quantity"
                                    type="number"
                                    {...register('quantity', {
                                        required: 'Quantity is required.',
                                        min: { value: 1, message: 'Quantity must be at least 1.' },
                                        max: { value: 10000, message: 'Quantity seems too high.' },
                                        valueAsNumber: true
                                    })}
                                    className={`${inputBase} ${errors.quantity ? inputError : inputNormal}`}
                                />
                            </div>
                            {errors.quantity && <p className="text-red-500 text-xs font-semibold ml-1">{errors.quantity.message}</p>}
                        </div>
                    </div>

                    <label className="inline-flex items-center gap-3 p-3.5 rounded-xl bg-gray-50 border border-gray-100 cursor-pointer hover:bg-gray-100 transition-colors select-none">
                        <input type="checkbox" {...register('negotiable')} className="w-5 h-5 accent-brand rounded cursor-pointer" />
                        <span className="text-sm font-semibold text-gray-700">Price is negotiable</span>
                    </label>
                </div>

                <div className="w-full h-px bg-gray-100" />

                {/* Section: Categorization */}
                <div className="space-y-5">
                    <div className="flex items-center gap-2">
                        <HiOutlineCollection size={18} className="text-brand" />
                        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Categorization</h3>
                    </div>

                    <div className={`grid gap-4 ${selectedCategory ? 'grid-cols-1 sm:grid-cols-2' : 'grid-cols-1'}`}>
                        <div className="space-y-1.5">
                            <label htmlFor="category" className="text-[13px] font-bold text-gray-700 ml-1">Category</label>
                            <div className="relative">
                                <select
                                    id="category"
                                    {...register('category', { required: 'Select category for your product.' })}
                                    className={`${inputBase} ${errors.category ? inputError : inputNormal} appearance-none`}
                                >
                                    <option value="">Select category</option>
                                    {categories.map((c) => (
                                        <option key={c.slug} value={c.slug}>{c.label}</option>
                                    ))}
                                </select>
                                <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
                                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                                </span>
                            </div>
                            {errors.category && <p className="text-red-500 text-xs font-semibold ml-1">{errors.category.message}</p>}
                        </div>

                        <div className={`space-y-1.5 ${selectedCategory ? 'block' : 'hidden'}`}>
                            <label htmlFor="sub_category" className="text-[13px] font-bold text-gray-700 ml-1">Sub Category</label>
                            <div className="relative">
                                <select
                                    id="sub_category"
                                    {...register('sub_category', { required: 'Select sub category' })}
                                    className={`${inputBase} ${errors.sub_category ? inputError : inputNormal} appearance-none`}
                                >
                                    <option value="">Select sub category</option>
                                    {subCategories.map((sub_category) => (
                                        <option key={sub_category} value={sub_category}>
                                            {sub_category.charAt(0).toUpperCase() + sub_category.slice(1).replace(/_/g, ' ')}
                                        </option>
                                    ))}
                                </select>
                                <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
                                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                                </span>
                            </div>
                            {errors.sub_category && <p className="text-red-500 text-xs font-semibold ml-1">{errors.sub_category.message}</p>}
                        </div>
                    </div>

                    <div className="space-y-1.5">
                        <label htmlFor="condition" className="text-[13px] font-bold text-gray-700 ml-1">Condition</label>
                        <div className="relative">
                            <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"><HiOutlineScale size={18} /></span>
                            <select
                                id="condition"
                                {...register('condition', { required: 'Select product condition.' })}
                                className={`${inputBase} ${errors.condition ? inputError : inputNormal} appearance-none`}
                            >
                                <option value="">Select condition</option>
                                {CONDITION_CHOICES.map((c) => (
                                    <option key={c.value} value={c.value}>{c.label}</option>
                                ))}
                            </select>
                            <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
                                <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                            </span>
                        </div>
                        {errors.condition && <p className="text-red-500 text-xs font-semibold ml-1">{errors.condition.message}</p>}
                    </div>

                    <div className="space-y-1.5">
                        <label htmlFor="color" className="text-[13px] font-bold text-gray-700 ml-1">Product color</label>
                        <div className="flex items-center gap-4">
                            <input
                                id="color"
                                type="color"
                                {...register('color', { required: 'Select a color for your product.' })}
                                className="w-14 h-12 rounded-xl border border-gray-200 cursor-pointer p-1 bg-white"
                            />
                            <div className="flex-1">
                                <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-gray-50 border border-gray-100">
                                    <HiOutlineColorSwatch size={18} className="text-gray-400" />
                                    <span className="text-sm font-semibold text-gray-600 uppercase">{watch('color') || 'Select a color'}</span>
                                </div>
                            </div>
                        </div>
                        {errors.color && <p className="text-red-500 text-xs font-semibold ml-1">{errors.color.message}</p>}
                    </div>
                </div>

                <div className="w-full h-px bg-gray-100" />

                {/* Section: Location */}
                <div className="space-y-5">
                    <div className="flex items-center gap-2">
                        <HiOutlineLocationMarker size={18} className="text-brand" />
                        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Location</h3>
                    </div>

                    <div className={`grid gap-4 ${selectedState ? 'grid-cols-1 sm:grid-cols-2' : 'grid-cols-1'}`}>
                        <div className="space-y-1.5">
                            <label htmlFor="state" className="text-[13px] font-bold text-gray-700 ml-1">State</label>
                            <div className="relative">
                                <select
                                    id="state"
                                    {...register('state', { required: 'State selection is required.' })}
                                    className={`${inputBase} ${errors.state ? inputError : inputNormal} appearance-none`}
                                >
                                    <option value="">Select state</option>
                                    {STATE_CHOICES.map((state) => (
                                        <option key={state.value} value={state.value}>{state.label}</option>
                                    ))}
                                </select>
                                <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
                                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                                </span>
                            </div>
                            {errors.state && <p className="text-red-500 text-xs font-semibold ml-1">{errors.state.message}</p>}
                        </div>

                        <div className={`space-y-1.5 ${selectedState ? 'block' : 'hidden'}`}>
                            <label htmlFor="city" className="text-[13px] font-bold text-gray-700 ml-1">City</label>
                            <div className="relative">
                                <select
                                    id="city"
                                    disabled={!selectedState}
                                    {...register('city', { required: 'Select your city.' })}
                                    className={`${inputBase} ${errors.city ? inputError : inputNormal} appearance-none disabled:bg-gray-50 disabled:text-gray-400`}
                                >
                                    <option value="">{selectedState ? 'Select city' : 'Select a state first'}</option>
                                    {cities.map((city) => {
                                        const citySlug = toBackendSlug(city);
                                        return (
                                            <option key={citySlug} value={citySlug}>{city}</option>
                                        );
                                    })}
                                </select>
                                <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
                                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                                </span>
                            </div>
                            {errors.city && <p className="text-red-500 text-xs font-semibold ml-1">{errors.city.message}</p>}
                        </div>
                    </div>
                </div>

                <div className="w-full h-px bg-gray-100" />

                {/* Section: Contact */}
                <div className="space-y-5">
                    <div className="flex items-center gap-2">
                        <HiOutlineChatAlt2 size={18} className="text-brand" />
                        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Contact</h3>
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-[13px] font-bold text-gray-700 ml-1">How should buyers contact you?</label>
                        <div className="grid grid-cols-3 gap-3">
                            {CONTACT_METHOD_CHOICES.map((c) => {
                                const isChecked = selectedMethods.includes(c.value);
                                return (
                                    <label
                                        key={c.value}
                                        className={`flex flex-col items-center justify-center gap-2 p-4 rounded-xl border-2 cursor-pointer transition-all select-none ${
                                            isChecked
                                                ? 'border-brand bg-brand/5 text-brand'
                                                : 'border-gray-200 text-gray-500 hover:border-gray-300 hover:bg-gray-50'
                                        }`}
                                    >
                                        <input
                                            type="checkbox"
                                            value={c.value}
                                            className="sr-only"
                                            {...register('contact_methods', {
                                                required: 'Select at least one contact method',
                                                validate: (value) => (value && value.length > 0) || 'Select at least one contact method'
                                            })}
                                        />
                                        <span className="text-xs font-bold text-center leading-tight">{c.label}</span>
                                        {isChecked && (
                                            <span className="flex items-center justify-center w-5 h-5 rounded-full bg-brand text-white">
                                                <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                                                    <path d="M2 6L5 9L10 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                                </svg>
                                            </span>
                                        )}
                                    </label>
                                );
                            })}
                        </div>
                        {errors.contact_methods && <p className="text-red-500 text-xs font-semibold ml-1">{errors.contact_methods.message}</p>}
                    </div>

                    {needsPhone && (
                        <div className="space-y-1.5">
                            <label htmlFor="contact_number" className="text-[13px] font-bold text-gray-700 ml-1">
                                {hasPhoneCall && hasWhatsapp
                                    ? 'Phone / WhatsApp Number'
                                    : hasWhatsapp
                                    ? 'WhatsApp Number'
                                    : 'Phone Number'}
                            </label>
                            <div className="relative">
                                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                    <HiOutlinePhone size={18} />
                                </span>
                                <input
                                    id="contact_number"
                                    type="tel"
                                    placeholder="Enter your phone number e.g. 09012345678"
                                    {...register('contact_number', {
                                        required: needsPhone ? 'Phone number is required for the selected contact methods' : false,
                                        minLength: { value: 11, message: 'Phone number must be exactly 11 digits' },
                                        maxLength: { value: 11, message: 'Phone number must be exactly 11 digits' },
                                        pattern: { value: /^[0-9]+$/, message: 'Phone number must contain only digits' }
                                    })}
                                    className={`${inputBase} ${errors.contact_number ? inputError : inputNormal}`}
                                />
                            </div>
                            {errors.contact_number && <p className="text-red-500 text-xs font-semibold ml-1">{errors.contact_number.message}</p>}
                        </div>
                    )}
                </div>

                <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full flex items-center justify-center gap-2 bg-brand text-white font-bold text-[15px] rounded-xl py-3.5 hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-brand/20 mt-2"
                >
                    {isSubmitting ? (
                        <><RiLoader3Line size={20} className="animate-spin" /> Saving changes...</>
                    ) : (
                        'Save changes'
                    )}
                </button>
            </form>
        </>
    );
};

export default EditProductForm;