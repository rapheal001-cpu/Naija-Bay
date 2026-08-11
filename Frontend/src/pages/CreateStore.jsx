import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RiLoader3Line, RiUploadCloud2Fill, RiStore2Line } from 'react-icons/ri';
import { FaArrowLeft } from 'react-icons/fa';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';
import { useCreateStoreMutation } from '../hooks/UseMutation.js';
import { STATE_CHOICES, STATE_CITY_MAP, STORE_TYPE_CHOICES } from '../dummyData.js';


const CreateStore = () => {
    const navigate = useNavigate();
    const user = useSelector((state) => state.user.user);
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);

    const [serverMessage, setServerMessage] = useState('');
    const [serverErrors, setServerErrors] = useState([]);
    const [logoFile, setLogoFile] = useState(null);
    const [logoPreview, setLogoPreview] = useState(null);
    const [bannerFile, setBannerFile] = useState(null);
    const [bannerPreview, setBannerPreview] = useState(null);

    const { register, handleSubmit, watch, formState: { errors }, setError, reset } = useForm();

    const createUserStore = useCreateStoreMutation(setError, setServerErrors, setServerMessage, reset);

    const selectedState = watch('state');
    const cities = selectedState ? STATE_CITY_MAP[selectedState] : [];

    useEffect(() => {
        if (!isAuthenticated && !user) {
            navigate('/sign-in');
        }
    }, [isAuthenticated, user, navigate]);

    const handleLogoChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (logoPreview) URL.revokeObjectURL(logoPreview);
            setLogoFile(file);
            setLogoPreview(URL.createObjectURL(file));
        }
    };

    const handleBannerChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (bannerPreview) URL.revokeObjectURL(bannerPreview);
            setBannerFile(file);
            setBannerPreview(URL.createObjectURL(file));
        }
    };

    const onSubmit = (data) => {
        setServerMessage('');
        setServerErrors([]);

        const formData = new FormData();

        // Append all text fields
        formData.append('store_name', data.store_name);
        formData.append('store_description', data.store_description || '');
        formData.append('store_type', data.store_type);
        formData.append('store_email', data.store_email || '');
        formData.append('store_phone_number', data.store_phone_number);
        formData.append('store_whatsapp_number', data.store_whatsapp_number || '');
        formData.append('state', data.state);
        formData.append('city', data.city);
        formData.append('address', data.address);

        // Append files ONLY if user selected them (model allows blank/null)
        if (logoFile) {
            formData.append('logo', logoFile);
        }
        if (bannerFile) {
            formData.append('banner', bannerFile);
        }

        createUserStore.mutate(formData);
    };

    return (
        <>
            <Header />
            <Spacer space="mb-20" />

            <div className="min-h-[85vh] bg-[#FAF9F6] py-8">
                <div className="max-w-2xl mx-auto px-4">

                    <Link to={(-1)} className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-brand transition-colors mb-4">
                        <FaArrowLeft size={14} />
                        Back
                    </Link>

                    <div className="bg-white rounded-2xl shadow-[0_1px_2px_rgba(0,0,0,0.04),0_12px_32px_-12px_rgba(0,0,0,0.12)] border border-gray-100 overflow-hidden">

                        {/* Banner */}
                        <div className="relative h-36 bg-gray-100">
                            {bannerPreview && (
                                <img src={bannerPreview} alt="Store banner" className="w-full h-full object-cover" />
                            )}
                            <label className="absolute bottom-3 right-3 flex items-center gap-1.5 bg-white/95 hover:bg-white text-gray-700 text-xs font-semibold px-3 py-1.5 rounded-lg cursor-pointer shadow-sm transition-colors">
                                <RiUploadCloud2Fill size={14} />
                                {bannerPreview ? 'Change banner' : 'Add banner'}
                                <input 
                                    type="file" 
                                    accept="image/jpeg, image/jpg, image/png, image/webp" 
                                    onChange={handleBannerChange} 
                                    className="hidden" 
                                />
                            </label>

                            {/* Logo overlaps banner */}
                            <div className="absolute -bottom-8 left-6">
                                <label className="relative block w-20 h-20 rounded-2xl bg-white border-4 border-white shadow-md cursor-pointer overflow-hidden">
                                    {logoPreview ? (
                                        <img src={logoPreview} alt="Store logo" className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-gray-50">
                                            <RiStore2Line className="text-gray-300" size={28} />
                                        </div>
                                    )}
                                    <div className="absolute inset-0 bg-black/0 hover:bg-black/30 flex items-center justify-center transition-colors">
                                        <RiUploadCloud2Fill className="text-white opacity-0 hover:opacity-100 transition-opacity" size={20} />
                                    </div>
                                    <input 
                                        type="file" 
                                        accept="image/jpeg, image/jpg, image/png, image/webp" 
                                        onChange={handleLogoChange} 
                                        className="hidden" 
                                    />
                                </label>
                            </div>
                        </div>

                        <div className="pt-12 px-8 pb-8">

                            <div className="mb-7">
                                <h1 className="text-[22px] font-bold text-gray-900 tracking-tight">Create Store</h1>
                                <p className="text-sm text-gray-500 mt-1.5">
                                    Set up your store so buyers know who they're dealing with.
                                </p>
                            </div>

                            {/* Success message */}
                            {serverMessage && (
                                <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-100 mb-5">
                                    <p className="text-emerald-600 text-sm font-medium leading-snug">{serverMessage}</p>
                                </div>
                            )}

                            {/* Non-field server errors */}
                            {serverErrors.length > 0 && (
                                <div className="p-3 rounded-xl bg-red-50 border border-red-100 mb-5 space-y-1">
                                    {serverErrors.map((err, idx) => (
                                        <p key={idx} className="text-red-600 text-sm font-medium leading-snug">{err}</p>
                                    ))}
                                </div>
                            )}

                            <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">

                                {/* Store name */}
                                <div className="flex flex-col gap-1.5">
                                    <label htmlFor="store_name" className="text-[13px] font-semibold text-gray-700">
                                        Store name
                                    </label>
                                    <input
                                        id="store_name"
                                        placeholder="e.g. Adaeze Fashion Hub"
                                        {...register('store_name', {
                                            required: 'Store name is required',
                                            minLength: { value: 3, message: 'Store name must be at least 3 characters' },
                                        })}
                                        className="border border-gray-200 rounded-xl px-4 py-2.5 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-colors"
                                    />
                                    {errors.store_name && <p className="text-red-500 text-xs font-medium">{errors.store_name.message}</p>}
                                </div>

                                {/* Store description */}
                                <div className="flex flex-col gap-1.5">
                                    <label htmlFor="store_description" className="text-[13px] font-semibold text-gray-700">
                                        Store description
                                    </label>
                                    <textarea
                                        id="store_description"
                                        rows={3}
                                        placeholder="Tell buyers what you sell and what makes your store different..."
                                        {...register('store_description')}
                                        className="border border-gray-200 rounded-xl px-4 py-2.5 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-colors resize-none"
                                    />
                                </div>

                                {/* Store type */}
                                <div className="flex flex-col gap-1.5">
                                    <label htmlFor="store_type" className="text-[13px] font-semibold text-gray-700">
                                        Store type
                                    </label>
                                    <select
                                        id="store_type"
                                        {...register('store_type', { required: 'Select a store type' })}
                                        className="border border-gray-200 rounded-xl px-4 py-2.5 text-[15px] focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-colors bg-white"
                                    >
                                        <option value="">Select store type</option>
                                        {STORE_TYPE_CHOICES.map((c) => (
                                            <option key={c.value} value={c.value}>{c.label}</option>
                                        ))}
                                    </select>
                                    {errors.store_type && <p className="text-red-500 text-xs font-medium">{errors.store_type.message}</p>}
                                </div>

                                {/* Contact */}
                                <div className="grid gap-4 sm:grid-cols-2">
                                    <div className="flex flex-col gap-1.5">
                                        <label htmlFor="store_email" className="text-[13px] font-semibold text-gray-700">
                                            Store email
                                        </label>
                                        <input
                                            id="store_email"
                                            type="email"
                                            placeholder="store@example.com"
                                            {...register('store_email', {
                                                pattern: {
                                                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                                                    message: 'Enter a valid email address',
                                                },
                                            })}
                                            className="border border-gray-200 rounded-xl px-4 py-2.5 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-colors"
                                        />
                                        {errors.store_email && <p className="text-red-500 text-xs font-medium">{errors.store_email.message}</p>}
                                    </div>

                                    <div className="flex flex-col gap-1.5">
                                        <label htmlFor="store_phone_number" className="text-[13px] font-semibold text-gray-700">
                                            Store phone number
                                        </label>
                                        <input
                                            id="store_phone_number"
                                            type="tel"
                                            placeholder="090xxxxxxxx"
                                            {...register('store_phone_number', {
                                                required: 'Business phone is required',
                                                pattern: { value: /^[0-9]+$/, message: 'Numbers only' },
                                                minLength: { value: 11, message: 'Invalid phone number' },
                                            })}
                                            className="border border-gray-200 rounded-xl px-4 py-2.5 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-colors"
                                        />
                                        {errors.store_phone_number && <p className="text-red-500 text-xs font-medium">{errors.store_phone_number.message}</p>}
                                    </div>
                                </div>

                                <div className="flex flex-col gap-1.5">
                                    <label htmlFor="store_whatsapp_number" className="text-[13px] font-semibold text-gray-700">
                                        WhatsApp number <span className="text-gray-400 font-normal">(optional)</span>
                                    </label>
                                    <input
                                        id="store_whatsapp_number"
                                        type="tel"
                                        placeholder="090xxxxxxxx"
                                        {...register('store_whatsapp_number', {
                                            pattern: { value: /^[0-9]*$/, message: 'Numbers only' },
                                        })}
                                        className="border border-gray-200 rounded-xl px-4 py-2.5 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-colors"
                                    />
                                    {errors.store_whatsapp_number && <p className="text-red-500 text-xs font-medium">{errors.store_whatsapp_number.message}</p>}
                                </div>

                                {/* State + City */}
                                <div className={`grid gap-4 ${selectedState ? 'sm:grid-cols-2' : 'sm:grid-cols-1'}`}>
                                    <div className="flex flex-col gap-1.5">
                                        <label htmlFor="state" className="text-[13px] font-semibold text-gray-700">
                                            State
                                        </label>
                                        <select
                                            id="state"
                                            {...register('state', { required: 'State is required' })}
                                            className="border border-gray-200 rounded-xl px-4 py-2.5 text-[15px] focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-colors bg-white"
                                        >
                                            <option value="">Select state</option>
                                            {STATE_CHOICES.map((state) => (
                                                <option key={state.value} value={state.value}>{state.label}</option>
                                            ))}
                                        </select>
                                        {errors.state && <p className="text-red-500 text-xs font-medium">{errors.state.message}</p>}
                                    </div>

                                    {selectedState && (
                                        <div className="flex flex-col gap-1.5">
                                            <label htmlFor="city" className="text-[13px] font-semibold text-gray-700">
                                                City
                                            </label>
                                            <select
                                                id="city"
                                                {...register('city', { required: 'City is required' })}
                                                className="border border-gray-200 rounded-xl px-4 py-2.5 text-[15px] focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-colors bg-white"
                                            >
                                                <option value="">Select city</option>
                                                {cities.map((city) => (
                                                    <option key={city.toLowerCase()} value={city.toLowerCase()}>{city}</option>
                                                ))}
                                            </select>
                                            {errors.city && <p className="text-red-500 text-xs font-medium">{errors.city.message}</p>}
                                        </div>
                                    )}
                                </div>

                                {/* Address */}
                                <div className="flex flex-col gap-1.5">
                                    <label htmlFor="address" className="text-[13px] font-semibold text-gray-700">
                                        Store address
                                    </label>
                                    <textarea
                                        id="address"
                                        rows={3}
                                        placeholder="Street address, landmark, or pickup location"
                                        {...register('address', { required: 'Store address is required' })}
                                        className="border border-gray-200 rounded-xl px-4 py-2.5 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-colors resize-none"
                                    />
                                    {errors.address && <p className="text-red-500 text-xs font-medium">{errors.address.message}</p>}
                                </div>

                                {/* Submit */}
                                <button
                                    type="submit"
                                    disabled={createUserStore.isPending}
                                    className="flex items-center justify-center gap-2 bg-brand text-white font-semibold text-[15px] rounded-xl py-3 mt-2 hover:opacity-90 active:scale-[0.99] transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                                >
                                    {createUserStore.isPending ? (
                                        <>
                                            <RiLoader3Line size={18} className="animate-spin" />
                                            Creating Store...
                                        </>
                                    ) : (
                                        'Create Store'
                                    )}
                                </button>

                            </form>

                        </div>

                    </div>

                </div>
            </div>
        </>
    );
};

export default CreateStore;