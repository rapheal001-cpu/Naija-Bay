import { useState } from 'react';
import { FaTag, FaPhoneAlt } from 'react-icons/fa';
import { useCreateOffer, useCreateCallback } from '../../hooks/useJiji.js';

const OfferPanel = ({ product, isAuthenticated, onSignIn }) => {
    const [mode, setMode] = useState(null); // 'offer' | 'callback'
    const [amount, setAmount] = useState('');
    const [message, setMessage] = useState('');
    const [phone, setPhone] = useState('');
    const [done, setDone] = useState('');

    const createOffer = useCreateOffer();
    const createCallback = useCreateCallback();

    const requireAuth = () => {
        if (!isAuthenticated) {
            onSignIn?.();
            return false;
        }
        return true;
    };

    const submitOffer = (e) => {
        e.preventDefault();
        if (!requireAuth()) return;
        createOffer.mutate(
            { slug: product.product_slug, payload: { amount, message: message.trim() } },
            { onSuccess: () => { setDone('Your offer has been sent to the seller.'); setMode(null); setAmount(''); setMessage(''); } }
        );
    };

    const submitCallback = (e) => {
        e.preventDefault();
        if (!requireAuth()) return;
        createCallback.mutate(
            { slug: product.product_slug, payload: { phone } },
            { onSuccess: () => { setDone('Callback requested. The seller will contact you.'); setMode(null); setPhone(''); } }
        );
    };

    return (
        <div className="mt-4">
            <div className="flex gap-2">
                <button
                    type="button"
                    onClick={() => { if (requireAuth()) setMode(mode === 'offer' ? null : 'offer'); }}
                    className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-xs font-bold text-slate-700 hover:border-brand hover:text-brand"
                >
                    <FaTag size={14} /> Make an offer
                </button>
                <button
                    type="button"
                    onClick={() => { if (requireAuth()) setMode(mode === 'callback' ? null : 'callback'); }}
                    className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-xs font-bold text-slate-700 hover:border-brand hover:text-brand"
                >
                    <FaPhoneAlt size={13} /> Request call back
                </button>
            </div>

            {mode === 'offer' && (
                <form onSubmit={submitOffer} className="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
                    <label className="text-xs font-bold text-slate-600">Your offer (₦)</label>
                    <input
                        type="number"
                        min="1"
                        required
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        placeholder={product.price}
                        className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
                    />
                    <textarea
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Add a short message (optional)"
                        rows={2}
                        className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
                    />
                    <button
                        type="submit"
                        disabled={createOffer.isPending || !amount}
                        className="mt-3 w-full rounded-lg bg-brand px-4 py-2 text-xs font-bold text-white hover:bg-brand-hover disabled:opacity-50"
                    >
                        {createOffer.isPending ? 'Sending…' : 'Send offer'}
                    </button>
                </form>
            )}

            {mode === 'callback' && (
                <form onSubmit={submitCallback} className="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
                    <label className="text-xs font-bold text-slate-600">Phone number</label>
                    <input
                        type="tel"
                        required
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="08012345678"
                        className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
                    />
                    <button
                        type="submit"
                        disabled={createCallback.isPending || !phone}
                        className="mt-3 w-full rounded-lg bg-brand px-4 py-2 text-xs font-bold text-white hover:bg-brand-hover disabled:opacity-50"
                    >
                        {createCallback.isPending ? 'Sending…' : 'Request callback'}
                    </button>
                </form>
            )}

            {done && <p className="mt-3 rounded-lg bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700">{done}</p>}
            {(createOffer.isError || createCallback.isError) && (
                <p className="mt-2 text-xs text-red-600">Something went wrong. Please try again.</p>
            )}
        </div>
    );
};

export default OfferPanel;
