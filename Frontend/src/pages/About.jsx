import { Link } from 'react-router-dom';
import {
    FaSearch,
    FaShieldAlt,
    FaHandshake,
    FaRocket,
    FaUsers,
    FaStore,
    FaTags,
    FaHeadset,
    FaArrowRight,
    FaCheckCircle,
} from 'react-icons/fa';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';

const stats = [
    { label: 'Active Users', value: '12,000+', icon: FaUsers },
    { label: 'Listed Products', value: '45,000+', icon: FaTags },
    { label: 'Verified Sellers', value: '3,500+', icon: FaStore },
    { label: 'Cities Covered', value: '36', icon: FaRocket },
];

const features = [
    {
        icon: FaSearch,
        title: 'Smart Discovery',
        desc: 'Find exactly what you need with powerful filters, category browsing, and location-based search across Nigeria.',
    },
    {
        icon: FaShieldAlt,
        title: 'Trusted & Secure',
        desc: 'Every seller profile is verified. Browse with confidence knowing you’re dealing with real people and real businesses.',
    },
    {
        icon: FaHandshake,
        title: 'Direct Contact',
        desc: 'Message sellers instantly. No middlemen, no hidden fees — just straightforward buyer-to-seller connection.',
    },
    {
        icon: FaHeadset,
        title: 'Local Support',
        desc: 'Our support team understands the Nigerian market. Get help that actually makes sense for your situation.',
    },
];

const values = [
    'Transparency in every transaction',
    'Empowering local entrepreneurs',
    'Affordability without compromising quality',
    'Community-driven marketplace growth',
];

const About = () => {
    return (
        <>
            <Header />
            <Spacer space="mb-20" />

            <div className="max-w-6xl mx-auto px-4 py-6 pb-16 space-y-16">
                {/* ── Hero ───────────────────────────────────────── */}
                <section className="text-center max-w-3xl mx-auto">
                    <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand/10 text-brand text-xs font-bold uppercase tracking-wider mb-5">
                        <FaRocket className="w-3 h-3" />
                        About NaijaBay
                    </span>
                    <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight leading-tight">
                        Nigeria’s marketplace for{' '}
                        <span className="text-brand">trusted deals</span>
                    </h1>
                    <p className="mt-5 text-base sm:text-lg text-gray-500 leading-relaxed max-w-2xl mx-auto">
                        NaijaBay was built to bridge the gap between buyers and sellers across Nigeria.
                        We believe finding great products at fair prices should be simple, safe, and local.
                    </p>
                    <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
                        <Link
                            to="/products"
                            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-brand text-white font-semibold rounded-xl px-7 py-3 hover:bg-brand/90 active:scale-[0.98] transition-all shadow-sm shadow-brand/20"
                        >
                            Start Browsing
                            <FaArrowRight className="w-4 h-4" />
                        </Link>
                        <Link
                            to="/register"
                            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-white text-gray-700 font-semibold rounded-xl px-7 py-3 border border-gray-200 hover:bg-gray-50 hover:border-gray-300 active:scale-[0.98] transition-all"
                        >
                            Become a Seller
                        </Link>
                    </div>
                </section>

                {/* ── Stats ──────────────────────────────────────── */}
                <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {stats.map((stat) => (
                        <div
                            key={stat.label}
                            className="bg-white rounded-2xl border border-gray-100 p-5 text-center shadow-sm hover:shadow-md hover:border-gray-200 transition-all"
                        >
                            <div className="mx-auto w-10 h-10 rounded-xl bg-brand/10 text-brand flex items-center justify-center mb-3">
                                <stat.icon className="w-5 h-5" />
                            </div>
                            <p className="text-xl sm:text-2xl font-extrabold text-gray-900">
                                {stat.value}
                            </p>
                            <p className="text-xs text-gray-500 font-medium mt-0.5">
                                {stat.label}
                            </p>
                        </div>
                    ))}
                </section>

                {/* ── How it works ───────────────────────────────── */}
                <section className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-10 shadow-sm">
                    <div className="text-center mb-10">
                        <h2 className="text-2xl font-bold text-gray-900">How NaijaBay works</h2>
                        <p className="text-sm text-gray-500 mt-2">
                            Three simple steps to buy or sell anything
                        </p>
                    </div>

                    <div className="grid sm:grid-cols-3 gap-6 relative">
                        {/* Connector line (desktop only) */}
                        <div className="hidden sm:block absolute top-8 left-[16.66%] right-[16.66%] h-0.5 bg-gray-100" />

                        {[
                            {
                                step: '01',
                                title: 'Discover',
                                desc: 'Browse thousands of listings across categories — from electronics to fashion to home goods.',
                            },
                            {
                                step: '02',
                                title: 'Connect',
                                desc: 'View seller profiles, check ratings, and reach out directly through our messaging system.',
                            },
                            {
                                step: '03',
                                title: 'Deal',
                                desc: 'Agree on price, arrange delivery or pickup, and complete your transaction with confidence.',
                            },
                        ].map((item) => (
                            <div key={item.step} className="relative text-center">
                                <div className="relative z-10 mx-auto w-16 h-16 rounded-2xl bg-brand text-white flex items-center justify-center text-lg font-bold shadow-lg shadow-brand/20 mb-4">
                                    {item.step}
                                </div>
                                <h3 className="text-base font-bold text-gray-900">{item.title}</h3>
                                <p className="text-sm text-gray-500 mt-2 leading-relaxed max-w-xs mx-auto">
                                    {item.desc}
                                </p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* ── Features ───────────────────────────────────── */}
                <section>
                    <div className="text-center mb-8">
                        <h2 className="text-2xl font-bold text-gray-900">Built for Nigerians</h2>
                        <p className="text-sm text-gray-500 mt-2">
                            Features designed around how we actually buy and sell
                        </p>
                    </div>

                    <div className="grid sm:grid-cols-2 gap-4">
                        {features.map((feature) => (
                            <div
                                key={feature.title}
                                className="flex gap-4 bg-white rounded-2xl border border-gray-100 p-5 shadow-sm hover:shadow-md hover:border-gray-200 transition-all"
                            >
                                <div className="shrink-0 w-11 h-11 rounded-xl bg-gray-50 text-brand flex items-center justify-center">
                                    <feature.icon className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="text-sm font-bold text-gray-900">
                                        {feature.title}
                                    </h3>
                                    <p className="text-sm text-gray-500 mt-1 leading-relaxed">
                                        {feature.desc}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* ── Mission & Values ─────────────────────────── */}
                <section className="grid lg:grid-cols-2 gap-6">
                    <div className="bg-brand rounded-3xl p-6 sm:p-8 text-white shadow-lg shadow-brand/20">
                        <h2 className="text-xl font-bold">Our Mission</h2>
                        <p className="mt-3 text-sm text-white/80 leading-relaxed">
                            To create the most accessible and trusted marketplace in Nigeria —
                            where anyone can start a business, find a bargain, or discover something
                            unique without barriers.
                        </p>
                        <div className="mt-6 flex items-center gap-3">
                            <div className="flex -space-x-2">
                                {[1, 2, 3, 4].map((i) => (
                                    <div
                                        key={i}
                                        className="w-8 h-8 rounded-full bg-white/20 border-2 border-brand flex items-center justify-center text-[10px] font-bold"
                                    >
                                        {String.fromCharCode(64 + i)}
                                    </div>
                                ))}
                            </div>
                            <p className="text-xs text-white/70 font-medium">
                                Join 12,000+ Nigerians already trading
                            </p>
                        </div>
                    </div>

                    <div className="bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-sm">
                        <h2 className="text-xl font-bold text-gray-900">Our Values</h2>
                        <ul className="mt-4 space-y-3">
                            {values.map((value) => (
                                <li
                                    key={value}
                                    className="flex items-center gap-3 text-sm text-gray-600"
                                >
                                    <FaCheckCircle className="w-4 h-4 text-emerald-500 shrink-0" />
                                    {value}
                                </li>
                            ))}
                        </ul>
                    </div>
                </section>

                {/* ── CTA ────────────────────────────────────────── */}
                <section className="text-center bg-gray-900 rounded-3xl p-8 sm:p-12 text-white relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-brand/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
                    <div className="absolute bottom-0 left-0 w-48 h-48 bg-brand/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />

                    <div className="relative z-10 max-w-xl mx-auto">
                        <h2 className="text-2xl sm:text-3xl font-bold">
                            Ready to start trading?
                        </h2>
                        <p className="mt-3 text-sm text-gray-400 leading-relaxed">
                            Whether you’re clearing out your closet or scaling a business,
                            NaijaBay is the place to reach real buyers across Nigeria.
                        </p>
                        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
                            <Link
                                to="/register"
                                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-brand text-white font-semibold rounded-xl px-7 py-3 hover:bg-brand/90 active:scale-[0.98] transition-all shadow-lg shadow-brand/25"
                            >
                                Create Free Account
                                <FaArrowRight className="w-4 h-4" />
                            </Link>
                            <Link
                                to="/products"
                                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-white/10 text-white font-semibold rounded-xl px-7 py-3 border border-white/10 hover:bg-white/20 active:scale-[0.98] transition-all"
                            >
                                Explore Products
                            </Link>
                        </div>
                    </div>
                </section>
            </div>
        </>
    );
};

export default About;