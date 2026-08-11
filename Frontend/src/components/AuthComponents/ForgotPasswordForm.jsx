import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { RiLoader3Line } from 'react-icons/ri';
import { HiOutlineShieldCheck, HiOutlineCheckCircle } from 'react-icons/hi';
import { HiOutlineEnvelope } from "react-icons/hi2";
import { useRequestPasswordResetMutation } from '../../hooks/UseMutation';

const ForgotPasswordForm = () => {
    const { register, handleSubmit, formState: { errors }, setError } = useForm();

    const [serverMessage, setServerMessage] = useState('');
    const [serverError, setServerError] = useState('');

    const requestPasswordReset = useRequestPasswordResetMutation(setError, setServerError, setServerMessage);

    const onSubmit = (data) => {
        setServerMessage('');
        requestPasswordReset.mutate(data);
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
                            Forgot your password?
                        </h1>
                        <p className="text-sm text-gray-500 mt-2 leading-relaxed">
                            Enter your email and we'll send you instructions to reset it.
                        </p>
                    </div>

                    {/* Server Message */}
                    {serverMessage && (
                        <div className="flex items-start gap-3 p-4 rounded-2xl bg-emerald-50 border border-emerald-100 mb-6">
                            <HiOutlineCheckCircle size={20} className="text-emerald-600 shrink-0 mt-0.5" />
                            <p className="text-emerald-700 text-sm font-semibold leading-snug">{serverMessage}</p>
                        </div>
                    )}

                    {/* Server Message */}
                    {serverError && (
                        <div className="flex items-start gap-3 p-4 rounded-2xl bg-red-500 border border-red-100 mb-6">
                            <HiOutlineCheckCircle size={20} className="text-red-600 shrink-0 mt-0.5" />
                            <p className="text-red-700 text-sm font-semibold leading-snug">{serverError}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">

                        {/* Email Field */}
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

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={requestPasswordReset.isPending}
                            className="flex items-center justify-center gap-2 bg-brand text-white font-bold text-[15px] rounded-xl py-3.5 mt-2 hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-brand/20"
                        >
                            {requestPasswordReset.isPending ? (
                                <>
                                    <RiLoader3Line size={20} className="animate-spin" />
                                    Sending...
                                </>
                            ) : (
                                'Send reset instructions'
                            )}
                        </button>

                    </form>
                </div>

                {/* Footer */}
                <p className="text-center text-sm text-gray-500 mt-8">
                    Remembered your password?{' '}
                    <Link to="/sign-in" className="text-brand font-bold hover:underline underline-offset-4">
                        Sign in
                    </Link>
                </p>

            </div>
        </div>
    )
}

export default ForgotPasswordForm;