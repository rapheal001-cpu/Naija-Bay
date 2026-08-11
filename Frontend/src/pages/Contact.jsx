import { useState } from 'react';
import {
    FaEnvelope,
    FaPhone,
    FaClock,
    FaMapMarkerAlt,
    FaPaperPlane,
    FaHeadset,
    FaWhatsapp,
    FaChevronDown,
    FaChevronUp,
} from 'react-icons/fa';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';

const contactMethods = [
    {
        icon: FaEnvelope,
        label: 'Email us',
        value: 'support@naijabay.test',
        desc: 'We reply within 24 hours',
        href: 'mailto:support@naijabay.test',
        color: 'bg-blue-50 text-blue-600',
    },
    {
        icon: FaPhone,
        label: 'Call us',
        value: '+234 800 000 0000',
        desc: 'Mon - Fri • 8:00 AM - 5:00 PM',
        href: 'tel:+2348000000000',
        color: 'bg-emerald-50 text-emerald-600',
    },
    {
        icon: FaWhatsapp,
        label: 'WhatsApp',
        value: 'Chat on WhatsApp',
        desc: 'Fastest response time',
        href: 'https://wa.me/2348000000000',
        color: 'bg-green-50 text-green-600',
    },
    {
        icon: FaMapMarkerAlt,
        label: 'Visit us',
        value: 'Lagos, Nigeria',
        desc: 'By appointment only',
        href: '#',
        color: 'bg-orange-50 text-orange-600',
    },
];

const faqs = [
    {
        q: 'How do I create a seller account?',
        a: 'Sign up for a free account, complete your profile verification, and click "Sell" to publish your first listing. It takes less than 2 minutes.',
    },
    {
        q: 'What payment methods are supported?',
        a: 'We support bank transfers, USSD, card payments, and cash on delivery (where available). All transactions are secured with end-to-end encryption.',
    },
    {
        q: 'How does buyer protection work?',
        a: 'We verify all sellers and hold funds in escrow until you confirm delivery. If an item is not as described, our dispute team steps in within 24 hours.',
    },
    {
        q: 'Can I edit or delete my listing?',
        a: 'Yes. Go to your profile dashboard, navigate to "My Listings," and click the edit or delete icon next to any product.',
    },
];

const Contact = () => {
    const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
    const [openFaq, setOpenFaq] = useState(null);

    const handleChange = (e) => {
        setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Wire to your API later
        alert('Message sent! We will get back to you shortly.');
        setForm({ name: '', email: '', subject: '', message: '' });
    };

    return (
        <>
            <Header />
            <Spacer space="mb-20" />

            <div className="max-w-5xl mx-auto px-4 py-6 pb-16 space-y-14">
                {/* ── Hero ─────────────────────────────────────────── */}
                <section className="text-center max-w-2xl mx-auto">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand/10 text-brand text-xs font-bold uppercase tracking-wider mb-5">
                        <FaHeadset className="w-3 h-3" />
                        Get in touch
                    </div>
                    <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight">
                        We're here to <span className="text-brand">help</span>
                    </h1>
                    <p className="mt-4 text-base text-gray-500 leading-relaxed">
                        Have a question about a product, need help with your account, or want to partner with us?
                        Our team is ready to assist you.
                    </p>
                </section>

                {/* ── Contact Cards ────────────────────────────────── */}
                <section className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {contactMethods.map((method) => (
                        <a
                            key={method.label}
                            href={method.href}
                            className="group bg-white rounded-2xl border border-gray-100 p-5 shadow-sm hover:shadow-md hover:border-gray-200 transition-all text-center"
                        >
                            <div
                                className={`mx-auto w-12 h-12 rounded-xl flex items-center justify-center mb-3 ${method.color}`}
                            >
                                <method.icon className="w-5 h-5" />
                            </div>
                            <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider">
                                {method.label}
                            </p>
                            <p className="text-sm font-bold text-gray-900 mt-1 group-hover:text-brand transition-colors">
                                {method.value}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">{method.desc}</p>
                        </a>
                    ))}
                </section>

                {/* ── Form + Info ──────────────────────────────────── */}
                <section className="grid lg:grid-cols-5 gap-8">
                    {/* Form */}
                    <div className="lg:col-span-3 bg-white rounded-3xl border border-gray-200 p-6 sm:p-8 shadow-sm">
                        <h2 className="text-lg font-bold text-gray-900">Send us a message</h2>
                        <p className="text-sm text-gray-500 mt-1">
                            Fill out the form below and we'll respond as soon as possible.
                        </p>

                        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                            <div className="grid sm:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                                        Full name
                                    </label>
                                    <input
                                        type="text"
                                        name="name"
                                        required
                                        value={form.name}
                                        onChange={handleChange}
                                        placeholder="John Doe"
                                        className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand focus:bg-white transition-all"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                                        Email address
                                    </label>
                                    <input
                                        type="email"
                                        name="email"
                                        required
                                        value={form.email}
                                        onChange={handleChange}
                                        placeholder="john@example.com"
                                        className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand focus:bg-white transition-all"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                                    Subject
                                </label>
                                <select
                                    name="subject"
                                    required
                                    value={form.subject}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand focus:bg-white transition-all appearance-none"
                                >
                                    <option value="">Select a topic</option>
                                    <option value="general">General inquiry</option>
                                    <option value="support">Account support</option>
                                    <option value="seller">Seller help</option>
                                    <option value="report">Report a product/user</option>
                                    <option value="partnership">Business partnership</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                                    Message
                                </label>
                                <textarea
                                    name="message"
                                    required
                                    rows={5}
                                    value={form.message}
                                    onChange={handleChange}
                                    placeholder="Tell us how we can help you..."
                                    className="w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand focus:bg-white transition-all resize-none"
                                />
                            </div>

                            <button
                                type="submit"
                                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-brand text-white font-semibold rounded-xl px-6 py-3 hover:bg-brand/90 active:scale-[0.98] transition-all shadow-sm shadow-brand/20"
                            >
                                <FaPaperPlane className="w-4 h-4" />
                                Send message
                            </button>
                        </form>
                    </div>

                    {/* Side info */}
                    <div className="lg:col-span-2 space-y-4">
                        <div className="bg-brand rounded-3xl p-6 sm:p-8 text-white shadow-lg shadow-brand/20">
                            <h3 className="text-lg font-bold">Need urgent help?</h3>
                            <p className="mt-2 text-sm text-white/80 leading-relaxed">
                                For account security issues, payment disputes, or urgent seller concerns,
                                our priority support line is available during business hours.
                            </p>
                            <div className="mt-5 flex items-center gap-3">
                                <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                                    <FaPhone className="w-4 h-4" />
                                </div>
                                <div>
                                    <p className="text-xs text-white/70 font-medium">Priority line</p>
                                    <p className="text-sm font-bold">+234 800 000 0000</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-3xl border border-gray-200 p-6 shadow-sm">
                            <div className="flex items-center gap-2 mb-3">
                                <FaClock className="w-4 h-4 text-brand" />
                                <h3 className="text-sm font-bold text-gray-900">Business hours</h3>
                            </div>
                            <ul className="space-y-2 text-sm text-gray-600">
                                <li className="flex justify-between">
                                    <span>Monday - Friday</span>
                                    <span className="font-semibold text-gray-800">8:00 AM - 5:00 PM</span>
                                </li>
                                <li className="flex justify-between">
                                    <span>Saturday</span>
                                    <span className="font-semibold text-gray-800">9:00 AM - 2:00 PM</span>
                                </li>
                                <li className="flex justify-between">
                                    <span>Sunday</span>
                                    <span className="font-semibold text-gray-400">Closed</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </section>

                {/* ── FAQ ──────────────────────────────────────────── */}
                <section>
                    <div className="text-center mb-8">
                        <h2 className="text-2xl font-bold text-gray-900">Frequently asked questions</h2>
                        <p className="text-sm text-gray-500 mt-2">
                            Quick answers to common questions
                        </p>
                    </div>

                    <div className="max-w-3xl mx-auto space-y-3">
                        {faqs.map((faq, idx) => {
                            const isOpen = openFaq === idx;
                            return (
                                <div
                                    key={idx}
                                    className={`bg-white rounded-2xl border transition-all ${
                                        isOpen ? 'border-gray-200 shadow-sm' : 'border-gray-100'
                                    }`}
                                >
                                    <button
                                        onClick={() => setOpenFaq(isOpen ? null : idx)}
                                        className="w-full flex items-center justify-between p-5 text-left"
                                    >
                                        <span className={`text-sm font-semibold ${isOpen ? 'text-brand' : 'text-gray-800'}`}>
                                            {faq.q}
                                        </span>
                                        {isOpen ? (
                                            <FaChevronUp className="w-4 h-4 text-gray-400 shrink-0 ml-4" />
                                        ) : (
                                            <FaChevronDown className="w-4 h-4 text-gray-400 shrink-0 ml-4" />
                                        )}
                                    </button>
                                    {isOpen && (
                                        <div className="px-5 pb-5">
                                            <p className="text-sm text-gray-600 leading-relaxed">
                                                {faq.a}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </section>
            </div>
        </>
    );
};

export default Contact;