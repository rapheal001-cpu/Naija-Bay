import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { RiLoader3Line } from 'react-icons/ri';
import { HiOutlineArrowLeft, HiOutlineEye, HiOutlineEyeSlash, HiOutlineCheckCircle, HiOutlineExclamationCircle, HiOutlineLockClosed, HiOutlineShieldCheck } from 'react-icons/hi2';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';
import { useChangePasswordMutation } from '../hooks/UseMutation.js';
import { useSelector } from 'react-redux';

const ChangePassword = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);
    const navigate = useNavigate();

    const { register, handleSubmit, watch, setError, reset, formState: { errors } } = useForm();

    const [serverMessage, setServerMessage] = useState('');
    const [serverError, setServerError] = useState('');
    const [showOld, setShowOld] = useState(false);
    const [showNew1, setShowNew1] = useState(false);
    const [showNew2, setShowNew2] = useState(false);

    const newPassword1 = watch('new_password1');

    // Pass all error handlers to the mutation hook
    const changePasswordMutation = useChangePasswordMutation(setError, setServerError, setServerMessage);

    useEffect(() => {
        if (!isAuthenticated && !user) {
            navigate("/sign-in");
        }
    }, [isAuthenticated, user, navigate]);

    const onSubmit = (data) => {
        setServerMessage('');
        setServerError('');
        changePasswordMutation.mutate(data, {
            onSuccess: () => reset(),
        });
    };

    // Password strength
    const getStrength = (pwd) => {
        if (!pwd) return 0;
        let score = 0;
        if (pwd.length >= 8) score++;
        if (/[A-Z]/.test(pwd)) score++;
        if (/[0-9]/.test(pwd)) score++;
        if (/[^A-Za-z0-9]/.test(pwd)) score++;
        return score;
    };

    const strength = getStrength(newPassword1);
    const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong'];
    const strengthColors = ['bg-red-500', 'bg-amber-500', 'bg-blue-500', 'bg-emerald-500'];

    const inputBase = "w-full border rounded-xl pl-11 pr-11 py-3 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-4 transition-all";
    const inputError = "border-red-300 focus:border-red-400 bg-red-50/30 focus:ring-red-100";
    const inputNormal = "border-gray-200 focus:border-brand focus:ring-brand/10";

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
                        <h1 className="text-3xl font-black text-gray-900 tracking-tight">Change password</h1>
                        <p className="text-sm text-gray-500 mt-2 leading-relaxed">
                            Choose a strong password you don't use anywhere else.
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

                        {/* Server-level error (non-field) */}
                        {serverError && (
                            <div className="flex items-start gap-3 p-4 rounded-2xl bg-red-50 border border-red-100 mb-6">
                                <HiOutlineExclamationCircle size={20} className="text-red-500 shrink-0 mt-0.5" />
                                <p className="text-red-600 text-sm font-semibold leading-snug">{serverError}</p>
                            </div>
                        )}

                        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">

                            {/* Current Password */}
                            <div className="space-y-1.5">
                                <label htmlFor="old_password" className="text-[13px] font-bold text-gray-700 ml-1">Current password</label>
                                <div className="relative">
                                    <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                        <HiOutlineLockClosed size={18} />
                                    </span>
                                    <input
                                        type={showOld ? "text" : "password"}
                                        id="old_password"
                                        placeholder="Enter your current password"
                                        aria-invalid={errors.old_password ? "true" : "false"}
                                        {...register('old_password', { required: 'Current password is required' })}
                                        className={`${inputBase} ${errors.old_password ? inputError : inputNormal}`}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowOld(!showOld)}
                                        className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                                    >
                                        {showOld ? <HiOutlineEyeSlash size={18} /> : <HiOutlineEye size={18} />}
                                    </button>
                                </div>
                                {errors.old_password && (
                                    <p className="text-red-500 text-xs font-semibold ml-1">{errors.old_password.message}</p>
                                )}
                            </div>

                            {/* New Password */}
                            <div className="space-y-1.5">
                                <label htmlFor="new_password1" className="text-[13px] font-bold text-gray-700 ml-1">New password</label>
                                <div className="relative">
                                    <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                        <HiOutlineShieldCheck size={18} />
                                    </span>
                                    <input
                                        type={showNew1 ? "text" : "password"}
                                        id="new_password1"
                                        placeholder="Min. 8 characters"
                                        aria-invalid={errors.new_password1 ? "true" : "false"}
                                        {...register('new_password1', {
                                            required: 'New password is required',
                                            minLength: { value: 8, message: 'Password must be at least 8 characters' },
                                            maxLength: { value: 16, message: 'Password must not be more than 16 characters' },
                                            validate: (value) =>
                                                value !== watch('old_password') || 'New password must be different from current password'
                                        })}
                                        className={`${inputBase} ${errors.new_password1 ? inputError : inputNormal}`}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowNew1(!showNew1)}
                                        className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                                    >
                                        {showNew1 ? <HiOutlineEyeSlash size={18} /> : <HiOutlineEye size={18} />}
                                    </button>
                                </div>
                                {errors.new_password1 && (
                                    <p className="text-red-500 text-xs font-semibold ml-1">{errors.new_password1.message}</p>
                                )}

                                {newPassword1 && !errors.new_password1 && (
                                    <div className="flex items-center gap-2 mt-2">
                                        <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full transition-all duration-300 ${strengthColors[Math.min(strength - 1, 3)]}`}
                                                style={{ width: `${(strength / 4) * 100}%` }}
                                            />
                                        </div>
                                        <span className="text-[11px] font-bold text-gray-400 uppercase">
                                            {strength > 0 ? strengthLabels[Math.min(strength - 1, 3)] : ''}
                                        </span>
                                    </div>
                                )}
                            </div>

                            {/* Confirm New Password */}
                            <div className="space-y-1.5">
                                <label htmlFor="new_password2" className="text-[13px] font-bold text-gray-700 ml-1">Confirm new password</label>
                                <div className="relative">
                                    <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                        <HiOutlineShieldCheck size={18} />
                                    </span>
                                    <input
                                        type={showNew2 ? "text" : "password"}
                                        id="new_password2"
                                        placeholder="Re-enter your new password"
                                        aria-invalid={errors.new_password2 ? "true" : "false"}
                                        {...register('new_password2', {
                                            required: 'Please confirm your new password',
                                            validate: (value) =>
                                                value === newPassword1 || 'Passwords do not match'
                                        })}
                                        className={`${inputBase} ${errors.new_password2 ? inputError : inputNormal}`}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowNew2(!showNew2)}
                                        className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                                    >
                                        {showNew2 ? <HiOutlineEyeSlash size={18} /> : <HiOutlineEye size={18} />}
                                    </button>
                                </div>
                                {errors.new_password2 && (
                                    <p className="text-red-500 text-xs font-semibold ml-1">{errors.new_password2.message}</p>
                                )}
                            </div>

                            <button
                                type="submit"
                                disabled={changePasswordMutation.isPending}
                                className="w-full flex items-center justify-center gap-2 bg-brand text-white font-bold text-[15px] rounded-xl py-3.5 mt-2 hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-brand/20"
                            >
                                {changePasswordMutation.isPending ? (
                                    <>
                                        <RiLoader3Line size={20} className="animate-spin" />
                                        Updating...
                                    </>
                                ) : (
                                    'Update password'
                                )}
                            </button>

                        </form>
                    </div>
                </div>
            </div>
        </>
    );
};

export default ChangePassword;