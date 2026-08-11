import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { RiLoader3Line } from "react-icons/ri";
import { HiOutlineShieldCheck, HiOutlineEye, HiOutlineEyeOff } from "react-icons/hi";
import { HiOutlineUser, HiOutlineEnvelope, HiOutlineLockClosed, HiOutlineExclamationCircle } from "react-icons/hi2";
import { useState } from 'react';
import { useRegisterMutation } from '@/hooks/UseMutation.js';

const RegisterForm = () => {
    const { register, handleSubmit, watch, formState: { errors }, setError } = useForm();

    const password1 = watch('password1');

    const [serverError, setServerError] = useState([]);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const registerUser = useRegisterMutation(setError, setServerError);

    const onSubmit = (data) => {
        setServerError([]);
        registerUser.mutate(data);
    };

    // Simple password strength check
    const getPasswordStrength = (pwd) => {
        if (!pwd) return 0;
        let score = 0;
        if (pwd.length >= 8) score++;
        if (/[A-Z]/.test(pwd)) score++;
        if (/[0-9]/.test(pwd)) score++;
        if (/[^A-Za-z0-9]/.test(pwd)) score++;
        return score;
    };

    const strength = getPasswordStrength(password1);
    const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong'];
    const strengthColors = ['bg-red-500', 'bg-amber-500', 'bg-blue-500', 'bg-emerald-500'];

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-linear-to-b from-gray-50 to-white">
            <div className="w-full max-w-md">

                {/* Brand mark */}
                <div className="flex items-center justify-center gap-2.5 mb-8">
                    <div className="w-10 h-10 rounded-xl bg-brand flex items-center justify-center shadow-lg shadow-brand/20">
                        <HiOutlineShieldCheck className="text-white" size={20} />
                    </div>
                    <span className="text-xl font-black text-gray-900 tracking-tight">NaijaBay</span>
                </div>

                <div className="bg-white rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100 p-8 sm:p-10">

                    <div className="mb-8 text-center sm:text-left">
                        <h1 className="text-2xl font-black text-gray-900 tracking-tight">
                            Create your account
                        </h1>
                        <p className="text-sm text-gray-500 mt-2 leading-relaxed">
                            Join thousands buying and selling safely on NaijaBay.
                        </p>
                    </div>

                    {/* Server Errors */}
                    {serverError.length > 0 && (
                        <div className="flex items-start gap-3 p-4 rounded-2xl bg-red-50 border border-red-100 mb-6">
                            <HiOutlineExclamationCircle size={20} className="text-red-500 shrink-0 mt-0.5" />
                            <div className="space-y-1">
                                {serverError.map((errorMsg, i) => (
                                    <p key={i} className="text-red-600 text-sm font-medium leading-snug">{errorMsg}</p>
                                ))}
                            </div>
                        </div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">

                        {/* Username */}
                        <div className="space-y-1.5">
                            <label htmlFor="username" className="text-[13px] font-bold text-gray-700 ml-1">
                                Username
                            </label>
                            <div className="relative">
                                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                    <HiOutlineUser size={18} />
                                </span>
                                <input
                                    type="text"
                                    id="username"
                                    placeholder="e.g. adaeze_fashion"
                                    aria-invalid={errors.username ? "true" : "false"}
                                    {...register('username', {
                                        required: 'Username is required',
                                        minLength: { value: 3, message: 'At least 3 characters' },
                                        maxLength: { value: 15, message: 'Max 15 characters' },
                                        pattern: { value: /^[a-zA-Z]+$/, message: 'Only letters.' }
                                    })}
                                    className={`
                                        w-full border rounded-xl pl-11 pr-4 py-3 text-[15px] placeholder:text-gray-400
                                        focus:outline-none focus:ring-4 focus:ring-brand/10 transition-all
                                        ${errors.username ? 'border-red-300 focus:border-red-400 bg-red-50/30' : 'border-gray-200 focus:border-brand focus:ring-brand/10'}
                                    `}
                                />
                            </div>
                            {errors.username && (
                                <p className="text-red-500 text-xs font-semibold ml-1">{errors.username.message}</p>
                            )}
                        </div>

                        {/* Email */}
                        <div className="space-y-1.5">
                            <label htmlFor="email" className="text-[13px] font-bold text-gray-700 ml-1">
                                Email address
                            </label>
                            <div className="relative">
                                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                    <HiOutlineEnvelope size={18} />
                                </span>
                                <input
                                    type="email"
                                    id="email"
                                    placeholder="name@example.com"
                                    aria-invalid={errors.email ? "true" : "false"}
                                    {...register('email', {
                                        required: 'Email is required',
                                        pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Enter a valid email' }
                                    })}
                                    className={`
                                        w-full border rounded-xl pl-11 pr-4 py-3 text-[15px] placeholder:text-gray-400
                                        focus:outline-none focus:ring-4 transition-all
                                        ${errors.email ? 'border-red-300 focus:border-red-400 bg-red-50/30' : 'border-gray-200 focus:border-brand focus:ring-brand/10'}
                                    `}
                                />
                            </div>
                            {errors.email && (
                                <p className="text-red-500 text-xs font-semibold ml-1">{errors.email.message}</p>
                            )}
                        </div>

                        {/* Password */}
                        <div className="space-y-1.5">
                            <label htmlFor="password1" className="text-[13px] font-bold text-gray-700 ml-1">
                                Password
                            </label>
                            <div className="relative">
                                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                    <HiOutlineLockClosed size={18} />
                                </span>
                                <input
                                    type={showPassword ? "text" : "password"}
                                    id="password1"
                                    placeholder="Min. 8 characters"
                                    aria-invalid={errors.password1 ? "true" : "false"}
                                    {...register('password1', {
                                        required: 'Password is required',
                                        minLength: { value: 8, message: 'At least 8 characters' },
                                        maxLength: { value: 16, message: 'Max 16 characters' }
                                    })}
                                    className={`
                                        w-full border rounded-xl pl-11 pr-11 py-3 text-[15px] placeholder:text-gray-400
                                        focus:outline-none focus:ring-4 transition-all
                                        ${errors.password1 ? 'border-red-300 focus:border-red-400 bg-red-50/30' : 'border-gray-200 focus:border-brand focus:ring-brand/10'}
                                    `}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                                >
                                    {showPassword ? <HiOutlineEyeOff size={18} /> : <HiOutlineEye size={18} />}
                                </button>
                            </div>
                            {errors.password1 && (
                                <p className="text-red-500 text-xs font-semibold ml-1">{errors.password1.message}</p>
                            )}

                            {/* Strength meter */}
                            {password1 && !errors.password1 && (
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

                        {/* Confirm Password */}
                        <div className="space-y-1.5">
                            <label htmlFor="password2" className="text-[13px] font-bold text-gray-700 ml-1">
                                Confirm password
                            </label>
                            <div className="relative">
                                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                    <HiOutlineLockClosed size={18} />
                                </span>
                                <input
                                    type={showConfirmPassword ? "text" : "password"}
                                    id="password2"
                                    placeholder="Re-enter your password"
                                    aria-invalid={errors.password2 ? "true" : "false"}
                                    {...register('password2', {
                                        required: 'Please confirm your password',
                                        validate: (value) => value === password1 || 'Passwords do not match'
                                    })}
                                    className={`
                                        w-full border rounded-xl pl-11 pr-11 py-3 text-[15px] placeholder:text-gray-400
                                        focus:outline-none focus:ring-4 transition-all
                                        ${errors.password2 ? 'border-red-300 focus:border-red-400 bg-red-50/30' : 'border-gray-200 focus:border-brand focus:ring-brand/10'}
                                    `}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                                >
                                    {showConfirmPassword ? <HiOutlineEyeOff size={18} /> : <HiOutlineEye size={18} />}
                                </button>
                            </div>
                            {errors.password2 && (
                                <p className="text-red-500 text-xs font-semibold ml-1">{errors.password2.message}</p>
                            )}
                        </div>

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={registerUser.isPending}
                            className="flex items-center justify-center gap-2 bg-brand text-white font-bold text-[15px] rounded-xl py-3.5 mt-2 hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-brand/20"
                        >
                            {registerUser.isPending ? (
                                <>
                                    <RiLoader3Line size={20} className="animate-spin" />
                                    Creating account...
                                </>
                            ) : (
                                'Create account'
                            )}
                        </button>

                    </form>
                </div>

                {/* Footer */}
                <p className="text-center text-sm text-gray-500 mt-8">
                    Already have an account?{' '}
                    <Link to="/sign-in" className="text-brand font-bold hover:underline underline-offset-4">
                        Sign in
                    </Link>
                </p>

            </div>
        </div>
    )
}

export default RegisterForm;