import { useEffect, useState, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RiLoader3Line } from 'react-icons/ri';
import { HiOutlinePhotograph } from 'react-icons/hi';
import { HiOutlineArrowLeft, HiOutlineUser, HiOutlineUsers, HiOutlinePhone, HiOutlineMapPin, HiOutlineHome, HiOutlineCheckCircle, HiOutlineExclamationCircle } from 'react-icons/hi2';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';
import { STATE_CHOICES } from '@/dummyData.js';
import { useUpdateProfileMutation } from '../hooks/UseMutation.js';

const UpdateProfile = () => {
    const navigate = useNavigate();
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);
    const [serverMessage, setServerMessage] = useState('');
    const [serverError, setServerError] = useState('');
    const [avatarFile, setAvatarFile] = useState(null);
    const [avatarPreview, setAvatarPreview] = useState(null);
    const [imgError, setImgError] = useState(false);

    const { register, handleSubmit, reset, setError, setValue, watch, formState: { errors } } = useForm();
    const updateProfileMutation = useUpdateProfileMutation(setError, setServerError, setServerMessage);

    const watchedFirstName = watch('first_name');
    const watchedLastName = watch('last_name');

    // Strip +234 for display (backend stores international, user sees local)
    const stripCountryCode = (phone) => {
        if (!phone) return '';
        return String(phone).replace(/^\+234/, '0');
    };

    // Build full avatar URL if backend returns relative path
    const getAvatarUrl = (avatarPath) => {
        if (!avatarPath) return null;
        if (avatarPath.startsWith('http')) return avatarPath;
        // Adjust this to match your API base URL
        const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
        return `${baseUrl}${avatarPath}`;
    };

    useEffect(() => {
        if (!isAuthenticated && !user) {
            navigate('/sign-in');
            return;
        }

        if (user) {
            reset({
                first_name: user.first_name ?? '',
                last_name: user.last_name ?? '',
                username: user.username ?? '',
                phone_number: stripCountryCode(user.phone_number),
                state: user.state ?? '',
                address: user.address ?? '',
            });
            setAvatarPreview(getAvatarUrl(user.avatar));
            setImgError(false);
            setAvatarFile(null);
        }
    }, [isAuthenticated, navigate, reset, user]);

    const handleAvatarChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (file.size > 2 * 1024 * 1024) {
            setServerError('Avatar must be less than 2MB');
            return;
        }
        if (!file.type.startsWith('image/')) {
            setServerError('Please upload a valid image file');
            return;
        }

        setAvatarFile(file);
        setAvatarPreview(URL.createObjectURL(file));
        setImgError(false);
        setServerError('');
    };

    // Avatar fallback: initials from first + last name
    const initials = useMemo(() => {
        const f = watchedFirstName?.trim()?.[0] ?? '';
        const l = watchedLastName?.trim()?.[0] ?? '';
        return (f + l).toUpperCase();
    }, [watchedFirstName, watchedLastName]);

    const onSubmit = (data) => {
        setServerMessage('');
        setServerError('');

        // Clean payload to match backend expectations
        const payload = {
            ...data,
            phone_number: stripCountryCode(data.phone_number),
            first_name: data.first_name?.trim(),
            last_name: data.last_name?.trim(),
            username: data.username?.trim().toLowerCase(),
            address: data.address?.trim(),
        };

        if (avatarFile) {
            const formData = new FormData();
            Object.entries(payload).forEach(([key, value]) => {
                if (value !== undefined && value !== null && value !== '') {
                    formData.append(key, value);
                }
            });
            formData.append('avatar', avatarFile);
            updateProfileMutation.mutate(formData);
        } else {
            updateProfileMutation.mutate(payload);
        }
    };

    const inputBase = "w-full border rounded-xl pl-11 pr-4 py-3 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-4 transition-all";
    const inputError = "border-red-300 focus:border-red-400 bg-red-50/30 focus:ring-red-100";
    const inputNormal = "border-gray-200 focus:border-brand focus:ring-brand/10";

    const selectChevron = (
        <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
        </span>
    );

    return (
        <>
            <Header />
            <Spacer space="mb-20" />

            <div className="min-h-[85vh] bg-linear-to-b from-gray-50 to-white py-10 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-96 h-96 bg-brand/5 rounded-full blur-3xl translate-x-1/3 -translate-y-1/3 pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-72 h-72 bg-brand/5 rounded-full blur-3xl -translate-x-1/3 translate-y-1/3 pointer-events-none" />

                <div className="relative max-w-2xl mx-auto px-4 sm:px-6">
                    <Link
                        to="/settings"
                        className="group inline-flex items-center gap-2 text-sm font-semibold text-gray-500 hover:text-gray-900 transition-colors mb-6"
                    >
                        <span className="flex items-center justify-center w-9 h-9 rounded-full bg-white border border-gray-200 group-hover:border-gray-300 group-hover:shadow-sm transition-all shadow-sm">
                            <HiOutlineArrowLeft size={16} />
                        </span>
                        Back to settings
                    </Link>

                    <div className="mb-8">
                        <h1 className="text-3xl font-black text-gray-900 tracking-tight">Update profile</h1>
                        <p className="text-sm text-gray-500 mt-2 leading-relaxed">
                            Keep your details up to date so buyers and sellers can trust who they're dealing with.
                        </p>
                    </div>

                    <div className="bg-white rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100 p-8 sm:p-10">
                        {/* Success message */}
                        {serverMessage && (
                            <div className="flex items-start gap-3 p-4 rounded-2xl bg-emerald-50 border border-emerald-100 mb-6">
                                <HiOutlineCheckCircle size={20} className="text-emerald-600 shrink-0 mt-0.5" />
                                <p className="text-emerald-700 text-sm font-semibold leading-snug">{serverMessage}</p>
                            </div>
                        )}

                        {/* Server-level error */}
                        {serverError && (
                            <div className="flex items-start gap-3 p-4 rounded-2xl bg-red-50 border border-red-100 mb-6">
                                <HiOutlineExclamationCircle size={20} className="text-red-500 shrink-0 mt-0.5" />
                                <p className="text-red-600 text-sm font-semibold leading-snug">{serverError}</p>
                            </div>
                        )}

                        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">
                            {/* Avatar with initials fallback */}
                            <div className="flex flex-col items-center gap-3 mb-2">
                                <div className="relative">
                                    {avatarPreview && !imgError ? (
                                        <img
                                            src={avatarPreview}
                                            alt="Profile"
                                            className="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg bg-gray-100"
                                            onError={() => setImgError(true)}
                                        />
                                    ) : (
                                        <div className="w-24 h-24 rounded-full bg-brand/10 border-4 border-white shadow-lg flex items-center justify-center text-brand font-black text-xl select-none">
                                            {initials || <HiOutlineUser size={32} className="text-brand/40" />}
                                        </div>
                                    )}
                                    <label className="absolute bottom-0 right-0 w-8 h-8 bg-brand text-white rounded-full flex items-center justify-center cursor-pointer shadow-md hover:opacity-90 transition-opacity">
                                        <HiOutlinePhotograph size={16} />
                                        <input
                                            type="file"
                                            accept="image/jpeg, image/jpg, image/png, image/webp"
                                            className="hidden"
                                            onChange={handleAvatarChange}
                                        />
                                    </label>
                                </div>
                                <span className="text-xs text-gray-500 font-medium">Change profile photo</span>
                            </div>

                            {/* Name row */}
                            <div className="grid gap-4 sm:grid-cols-2">
                                <div className="space-y-1.5">
                                    <label htmlFor="first_name" className="text-[13px] font-bold text-gray-700 ml-1">First name</label>
                                    <div className="relative">
                                        <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                            <HiOutlineUser size={18} />
                                        </span>
                                        <input
                                            id="first_name"
                                            placeholder="Your first name"
                                            {...register('first_name')}
                                            className={`${inputBase} ${errors.first_name ? inputError : inputNormal}`}
                                        />
                                    </div>
                                    {errors.first_name && <p className="text-red-500 text-xs font-semibold ml-1">{errors.first_name.message}</p>}
                                </div>

                                <div className="space-y-1.5">
                                    <label htmlFor="last_name" className="text-[13px] font-bold text-gray-700 ml-1">Last name</label>
                                    <div className="relative">
                                        <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                            <HiOutlineUser size={18} />
                                        </span>
                                        <input
                                            id="last_name"
                                            placeholder="Your last name"
                                            {...register('last_name')}
                                            className={`${inputBase} ${errors.last_name ? inputError : inputNormal}`}
                                        />
                                    </div>
                                    {errors.last_name && <p className="text-red-500 text-xs font-semibold ml-1">{errors.last_name.message}</p>}
                                </div>
                            </div>

                            {/* Username — letters ONLY, no numbers/symbols */}
                            <div className="space-y-1.5">
                                <label htmlFor="username" className="text-[13px] font-bold text-gray-700 ml-1">Username</label>
                                <div className="relative">
                                    <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                        <HiOutlineUsers size={18} />
                                    </span>
                                    <input
                                        id="username"
                                        placeholder="Your username"
                                        {...register('username', {
                                            required: 'Username is required',
                                            pattern: {
                                                value: /^[a-zA-Z]+$/,
                                                message: 'Username must contain only letters (a-z), no numbers or symbols'
                                            },
                                            minLength: { value: 3, message: 'Username must be at least 3 characters' },
                                            maxLength: { value: 30, message: 'Username must be under 30 characters' },
                                            onChange: (e) => {
                                                const val = e.target.value;
                                                if (/^[a-zA-Z]*$/.test(val)) {
                                                    setValue('username', val.toLowerCase(), { shouldValidate: true });
                                                }
                                            }
                                        })}
                                        className={`${inputBase} ${errors.username ? inputError : inputNormal}`}
                                    />
                                </div>
                                {errors.username && <p className="text-red-500 text-xs font-semibold ml-1">{errors.username.message}</p>}
                            </div>

                            {/* Phone — no +234, digits only, 11 chars */}
                            <div className="space-y-1.5">
                                <label htmlFor="phone_number" className="text-[13px] font-bold text-gray-700 ml-1">Phone number</label>
                                <div className="relative">
                                    <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                        <HiOutlinePhone size={18} />
                                    </span>
                                    <input
                                        id="phone_number"
                                        type="tel"
                                        placeholder="e.g. 09012345678"
                                        maxLength={11}
                                        {...register('phone_number', {
                                            pattern: { value: /^[0-9]+$/, message: 'Numbers only' },
                                            minLength: { value: 11, message: 'Phone number must be 11 digits' },
                                            maxLength: { value: 11, message: 'Phone number must be 11 digits' }
                                        })}
                                        className={`${inputBase} ${errors.phone_number ? inputError : inputNormal}`}
                                    />
                                </div>
                                {errors.phone_number && <p className="text-red-500 text-xs font-semibold ml-1">{errors.phone_number.message}</p>}
                            </div>

                            {/* State */}
                            <div className="space-y-1.5">
                                <label htmlFor="state" className="text-[13px] font-bold text-gray-700 ml-1">State</label>
                                <div className="relative">
                                    <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                        <HiOutlineMapPin size={18} />
                                    </span>
                                    <select
                                        id="state"
                                        {...register('state')}
                                        className={`${inputBase} ${errors.state ? inputError : inputNormal} appearance-none`}
                                    >
                                        <option value="">Select your state</option>
                                        {STATE_CHOICES.map((state) => (
                                            <option key={state.value} value={state.value}>{state.label}</option>
                                        ))}
                                    </select>
                                    {selectChevron}
                                </div>
                                {errors.state && <p className="text-red-500 text-xs font-semibold ml-1">{errors.state.message}</p>}
                            </div>

                            {/* Address */}
                            <div className="space-y-1.5">
                                <label htmlFor="address" className="text-[13px] font-bold text-gray-700 ml-1">Address</label>
                                <div className="relative">
                                    <span className="absolute left-3.5 top-3.5 text-gray-400">
                                        <HiOutlineHome size={18} />
                                    </span>
                                    <textarea
                                        id="address"
                                        rows={4}
                                        placeholder="Your full address"
                                        {...register('address')}
                                        className={`${inputBase} ${errors.address ? inputError : inputNormal} resize-none pt-3!`}
                                    />
                                </div>
                                {errors.address && <p className="text-red-500 text-xs font-semibold ml-1">{errors.address.message}</p>}
                            </div>

                            <button
                                type="submit"
                                disabled={updateProfileMutation.isPending}
                                className="w-full flex items-center justify-center gap-2 bg-brand text-white font-bold text-[15px] rounded-xl py-3.5 mt-2 hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-brand/20"
                            >
                                {updateProfileMutation.isPending ? (
                                    <>
                                        <RiLoader3Line size={20} className="animate-spin" />
                                        Saving...
                                    </>
                                ) : (
                                    'Save changes'
                                )}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </>
    );
};

export default UpdateProfile;