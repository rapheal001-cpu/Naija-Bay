import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { RiLoader3Line } from 'react-icons/ri';
import { HiOutlineShieldCheck, HiOutlineEye, HiOutlineEyeOff, HiOutlineExclamationCircle } from 'react-icons/hi';
import { HiOutlineEnvelope, HiOutlineLockClosed } from "react-icons/hi2";
import { useSignInMutation } from '../../hooks/UseMutation';

const SignInForm = () => {
    const { register, handleSubmit, formState: { errors }, setError } = useForm();

    const [serverError, setServerError] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const signInUser = useSignInMutation(setError, setServerError);

    const onSubmit = (data) => {
        setServerError('');
        signInUser.mutate(data);
    };

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
                            Welcome back
                        </h1>
                        <p className="text-sm text-gray-500 mt-2 leading-relaxed">
                            Sign in to continue buying and selling on NaijaBay.
                        </p>
                    </div>

                    {/* Server Errors */}
                    {serverError && (
                        <div className="flex items-start gap-3 p-4 rounded-2xl bg-red-50 border border-red-100 mb-6">
                            <HiOutlineExclamationCircle size={20} className="text-red-500 shrink-0 mt-0.5" />
                            <div className="space-y-1">
                                <p  className="text-red-600 text-sm font-medium leading-snug">
                                    {serverError}
                                </p>
                            </div>
                        </div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">

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
                                        pattern: {
                                            value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                                            message: 'Enter a valid email address'
                                        }
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
                            <div className="flex items-center justify-between ml-1">
                                <label htmlFor="password" className="text-[13px] font-bold text-gray-700">
                                    Password
                                </label>
                                <div className="flex items-center gap-3">
                                    <Link to="/forgot-password" className="text-xs text-brand font-bold hover:underline underline-offset-4">
                                        Forgot password?
                                    </Link>
                                    <Link to="/resend-email-verification" className="text-xs text-brand font-bold hover:underline underline-offset-4">
                                        Verify email
                                    </Link>
                                </div>
                            </div>
                            <div className="relative">
                                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                                    <HiOutlineLockClosed size={18} />
                                </span>
                                <input
                                    type={showPassword ? "text" : "password"}
                                    id="password"
                                    placeholder="Enter your password"
                                    aria-invalid={errors.password ? "true" : "false"}
                                    {...register('password', {
                                        required: 'Password is required',
                                        minLength: {
                                            value: 8,
                                            message: 'Password must be at least 8 characters'
                                        }
                                    })}
                                    className={`
                                        w-full border rounded-xl pl-11 pr-11 py-3 text-[15px] placeholder:text-gray-400
                                        focus:outline-none focus:ring-4 transition-all
                                        ${errors.password ? 'border-red-300 focus:border-red-400 bg-red-50/30' : 'border-gray-200 focus:border-brand focus:ring-brand/10'}
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
                            {errors.password && (
                                <p className="text-red-500 text-xs font-semibold ml-1">{errors.password.message}</p>
                            )}
                        </div>

                        {/* Sign In Button */}
                        <button
                            type="submit"
                            disabled={signInUser.isPending}
                            className="flex items-center justify-center gap-2 bg-brand text-white font-bold text-[15px] rounded-xl py-3.5 mt-2 hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-brand/20"
                        >
                            {signInUser.isPending ? (
                                <>
                                    <RiLoader3Line size={20} className="animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                'Sign in'
                            )}
                        </button>

                    </form>
                </div>

                {/* Footer */}
                <p className="text-center text-sm text-gray-500 mt-8">
                    Don't have an account?{' '}
                    <Link to="/register" className="text-brand font-bold hover:underline underline-offset-4">
                        Create an account
                    </Link>
                </p>

            </div>
        </div>
    )
}

export default SignInForm;