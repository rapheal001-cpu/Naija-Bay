import { Link } from 'react-router-dom';
import { TbMailForward } from 'react-icons/tb';
import { HiOutlineArrowLeft } from 'react-icons/hi2';

const EmailVerificationSent = () => {
    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-linear-to-b from-gray-50 to-white relative overflow-hidden">
            {/* Decorative blobs */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-brand/5 rounded-full blur-3xl translate-x-1/3 -translate-y-1/3 pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-72 h-72 bg-brand/5 rounded-full blur-3xl -translate-x-1/3 translate-y-1/3 pointer-events-none" />

            <div className="relative w-full max-w-md">
                {/* Brand hint */}
                <div className="flex items-center justify-center gap-2 mb-8">
                    <div className="w-10 h-10 rounded-xl bg-brand flex items-center justify-center shadow-lg shadow-brand/20">
                        <TbMailForward className="text-white" size={20} />
                    </div>
                    <span className="text-xl font-black text-gray-900 tracking-tight">NaijaBay</span>
                </div>

                <div className="bg-white rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100 p-8 sm:p-10 text-center">
                    {/* Icon */}
                    <div className="mx-auto w-20 h-20 rounded-2xl bg-brand/10 flex items-center justify-center mb-6 border border-brand/10">
                        <TbMailForward className="w-10 h-10 text-brand" strokeWidth={1.5} />
                    </div>

                    {/* Heading */}
                    <h1 className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">
                        Verify your email
                    </h1>
                    <p className="mt-3 text-sm text-gray-500 leading-relaxed max-w-xs mx-auto">
                        We've sent a verification link to your email address. Click the link to activate your account.
                    </p>

                    {/* Email placeholder highlight */}
                    <div className="mt-5 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-50 border border-gray-100">
                        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        <span className="text-sm font-semibold text-gray-600">Check your inbox</span>
                    </div>

                    <div className="mt-8">
                        <p className="text-xs text-gray-400 mb-3">
                            Didn't receive it? Check your spam folder, then request a fresh link from the sign-in verification page.
                        </p>
                        <Link
                            to="/resend-email-verification"
                            className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-bold text-gray-700 bg-gray-100 hover:bg-gray-200 active:scale-[0.98] transition-all"
                        >
                            Request a fresh verification link
                        </Link>
                    </div>

                    {/* Divider */}
                    <div className="w-full h-px bg-gray-100 my-6" />

                    {/* Back to Log in */}
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

                {/* Footer hint */}
                <p className="text-center text-xs text-gray-400 mt-6">
                    Need help? Contact our support team.
                </p>
            </div>
        </div>
    );
};

export default EmailVerificationSent;