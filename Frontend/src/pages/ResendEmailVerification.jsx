import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { RiLoader3Line } from 'react-icons/ri';
import { HiOutlineExclamationCircle, HiOutlineArrowLeft } from 'react-icons/hi';
import { HiOutlineEnvelope } from "react-icons/hi2";
import { useResendVerificationEmailMutation } from '../hooks/UseMutation.js';

const ResendEmailVerification = () => {
    const { register, handleSubmit, formState: { errors }, setError } = useForm();
    const [serverMessage, setServerMessage] = useState('');
    const [serverError, setServerError] = useState('');


    const resendVerificationEmailData = useResendVerificationEmailMutation(setError, setServerError, setServerMessage);

    const onSubmit = (data) => {
        resendVerificationEmailData.mutate(data);
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-linear-to-b from-gray-50 to-white">
            <div className="w-full max-w-md">
                <div className="flex items-center justify-center gap-2.5 mb-8">
                    <div className="w-10 h-10 rounded-xl bg-brand flex items-center justify-center shadow-lg shadow-brand/20">
                        <HiOutlineEnvelope className="text-white" size={20} />
                    </div>
                    <span className="text-xl font-black text-gray-900 tracking-tight">NaijaBay</span>
                </div>

                <div className="bg-white rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100 p-8 sm:p-10">
                    <div className="mb-8 text-center">
                        <h1 className="text-2xl font-black text-gray-900 tracking-tight">
                            Resend verification email
                        </h1>
                        <p className="text-sm text-gray-500 mt-2 leading-relaxed">
                            Enter the email address you used to register and we'll send a fresh verification link.
                        </p>
                    </div>

                    {serverError && (
                        <div className="flex items-start gap-3 p-4 rounded-2xl bg-red-50 border border-red-100 mb-6">
                            <HiOutlineExclamationCircle size={20} className="text-red-500 shrink-0 mt-0.5" />
                            <div className="space-y-1">
                                <p className="text-red-600 text-sm font-medium leading-snug">{serverError}</p>
                            </div>
                        </div>
                    )}

                    {serverMessage && (
                        <div className="mb-6 p-4 rounded-2xl bg-emerald-50 border border-emerald-100">
                            <p className="text-sm font-bold text-emerald-700">{serverMessage}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">
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
                                    aria-invalid={errors.email ? 'true' : 'false'}
                                    {...register('email', {
                                        required: 'Email is required',
                                        pattern: {
                                            value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                                            message: 'Enter a valid email address'
                                        }
                                    })}
                                    className={`w-full border rounded-xl pl-11 pr-4 py-3 text-[15px] placeholder:text-gray-400 focus:outline-none focus:ring-4 transition-all ${errors.email ? 'border-red-300 focus:border-red-400 bg-red-50/30' : 'border-gray-200 focus:border-brand focus:ring-brand/10'}`}
                                />
                            </div>
                            {errors.email && (
                                <p className="text-red-500 text-xs font-semibold ml-1">{errors.email.message}</p>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={resendVerificationEmailData.isPending}
                            className="flex items-center justify-center gap-2 bg-brand text-white font-bold text-[15px] rounded-xl py-3.5 mt-2 hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-brand/20"
                        >
                            {resendVerificationEmailData.isPending ? (
                                <>
                                    <RiLoader3Line size={20} className="animate-spin" />
                                    Sending...
                                </>
                            ) : (
                                'Send verification link'
                            )}
                        </button>
                    </form>
                </div>

                <div className="text-center mt-6">
                    <Link
                        to="/sign-in"
                        className="group inline-flex items-center gap-2 text-sm font-bold text-brand hover:underline underline-offset-4 transition-all"
                    >
                        <span className="flex items-center justify-center w-7 h-7 rounded-full bg-brand/10 group-hover:bg-brand/20 transition-colors">
                            <HiOutlineArrowLeft size={14} />
                        </span>
                        Back to sign in
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default ResendEmailVerification;
