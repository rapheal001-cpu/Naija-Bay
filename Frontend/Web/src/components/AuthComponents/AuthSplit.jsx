import { Link } from 'react-router-dom';
import { HiOutlineShieldCheck, HiOutlineLockClosed, HiOutlineChatAlt2 } from 'react-icons/hi';

/**
 * Professional split-screen shell for all auth pages.
 * Desktop: brand panel (left) + form (right). Mobile: form only.
 * Blue-only palette (Jiji direction), no green accent.
 */
const AuthSplit = ({ children, heading, subheading }) => {
    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Brand panel (desktop) */}
            <div className="hidden lg:flex w-[42%] flex-col justify-between bg-brand p-10 text-white relative overflow-hidden">
                <div className="absolute -top-24 -left-24 w-80 h-80 bg-white/10 rounded-full blur-3xl" aria-hidden="true" />
                <div className="absolute bottom-0 right-0 w-96 h-96 bg-white/5 rounded-full blur-3xl" aria-hidden="true" />

                <Link to="/" className="relative flex items-center gap-2.5 w-fit">
                    <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center shadow-lg">
                        <HiOutlineShieldCheck className="text-brand" size={20} />
                    </div>
                    <span className="text-xl font-black tracking-tight">NaijaBay</span>
                </Link>

                <div className="relative">
                    <h2 className="text-4xl font-black tracking-tight leading-tight">
                        Nigeria's marketplace for everything you need.
                    </h2>
                    <p className="mt-4 text-white/75 leading-relaxed max-w-md">
                        Buy and sell verified products from trusted Nigerian sellers — chat directly, inspect first, pay only when you're sure.
                    </p>

                    <ul className="mt-8 space-y-4">
                        {[
                            { icon: HiOutlineShieldCheck, text: 'Verified sellers on every listing' },
                            { icon: HiOutlineChatAlt2, text: 'Chat with sellers before you buy' },
                            { icon: HiOutlineLockClosed, text: 'Report abuse and stay safe with safety checks' },
                        ].map(({ icon: Icon, text }) => (
                            <li key={text} className="flex items-center gap-3 text-sm font-semibold text-white/90">
                                <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
                                    <Icon size={17} aria-hidden="true" />
                                </span>
                                {text}
                            </li>
                        ))}
                    </ul>
                </div>

                <p className="relative text-sm text-white/50">© {new Date().getFullYear()} NaijaBay. All rights reserved.</p>
            </div>

            {/* Form side */}
            <div className="flex-1 flex items-center justify-center px-4 py-12">
                <div className="w-full max-w-md">
                    <div className="lg:hidden flex items-center justify-center gap-2.5 mb-8">
                        <div className="w-10 h-10 rounded-xl bg-brand flex items-center justify-center shadow-lg shadow-brand/20">
                            <HiOutlineShieldCheck className="text-white" size={20} />
                        </div>
                        <span className="text-xl font-black text-gray-900 tracking-tight">NaijaBay</span>
                    </div>

                    <div className="mb-7">
                        <h1 className="text-2xl font-black text-gray-900 tracking-tight">{heading}</h1>
                        <p className="text-sm text-gray-500 mt-2 leading-relaxed">{subheading}</p>
                    </div>

                    {children}
                </div>
            </div>
        </div>
    );
};

export default AuthSplit;
