import { useState } from 'react';
import { useSelector } from 'react-redux';
import { useSafeDeals, useSafeDealAction } from '../../hooks/useJiji.js';

const SafeDealPanel = () => {
    const user = useSelector((state) => state.user.user);
    const [deliveryService, setDeliveryService] = useState({});
    const [tracking, setTracking] = useState({});
    const [reason, setReason] = useState({});

    const { data, isLoading } = useSafeDeals();
    const action = useSafeDealAction();

    const orders = data?.results || [];

    const run = (reference, name, payload) => action.mutate({ reference, action: name, payload });

    if (isLoading) return <section className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-400">Loading Safe Deal orders…</section>;

    return (
        <section className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="text-base font-black text-slate-800">Safe Deal orders</h2>
            <p className="mt-1 text-xs text-slate-400">Payment is held until the buyer confirms delivery.</p>

            {orders.length === 0 ? (
                <p className="mt-4 text-sm text-slate-400">No Safe Deal orders yet.</p>
            ) : (
                <ul className="mt-4 space-y-4">
                    {orders.map((o) => {
                        const isSeller = o.seller === user?.id;
                        const isBuyer = o.buyer === user?.id;
                        return (
                            <li key={o.id} className="rounded-lg border border-slate-200 p-4">
                                <div className="flex flex-wrap items-center justify-between gap-2">
                                    <span className="text-sm font-bold text-slate-700">{o.reference}</span>
                                    <span className="rounded-full bg-amber-50 px-2.5 py-1 text-[11px] font-bold uppercase text-amber-700">
                                        {o.escrow_status}
                                    </span>
                                </div>
                                <p className="mt-1 text-xs text-slate-500">₦{Number(o.total).toLocaleString()} · {o.recipient_name}</p>
                                {o.tracking_number && <p className="mt-1 text-xs text-slate-500">Tracking: {o.tracking_number}</p>}
                                {o.confirm_deadline && (
                                    <p className="mt-1 text-xs text-slate-500">
                                        Confirm by {new Date(o.confirm_deadline).toLocaleString()}
                                    </p>
                                )}
                                {o.dispute_reason && (
                                    <p className="mt-2 rounded bg-red-50 px-3 py-2 text-xs text-red-700">Problem: {o.dispute_reason}</p>
                                )}

                                <div className="mt-3 flex flex-wrap gap-2">
                                    {isSeller && o.escrow_status === 'paid' && (
                                        <>
                                            <input
                                                placeholder="Delivery service"
                                                value={deliveryService[o.reference] || ''}
                                                onChange={(e) => setDeliveryService({ ...deliveryService, [o.reference]: e.target.value })}
                                                className="rounded border border-slate-200 px-2 py-1.5 text-xs"
                                            />
                                            <button
                                                onClick={() => run(o.reference, 'accept', { delivery_service: deliveryService[o.reference] || '' })}
                                                className="rounded bg-brand px-3 py-1.5 text-xs font-bold text-white"
                                            >
                                                Accept order
                                            </button>
                                        </>
                                    )}
                                    {isSeller && o.escrow_status === 'shipped' && (
                                        <>
                                            <input
                                                placeholder="Tracking number"
                                                value={tracking[o.reference] || ''}
                                                onChange={(e) => setTracking({ ...tracking, [o.reference]: e.target.value })}
                                                className="rounded border border-slate-200 px-2 py-1.5 text-xs"
                                            />
                                            <button
                                                onClick={() => run(o.reference, 'tracking', { tracking_number: tracking[o.reference] || '' })}
                                                className="rounded bg-brand px-3 py-1.5 text-xs font-bold text-white"
                                            >
                                                Submit tracking
                                            </button>
                                            <button
                                                onClick={() => run(o.reference, 'delivered', {})}
                                                className="rounded border border-slate-300 px-3 py-1.5 text-xs font-bold text-slate-700"
                                            >
                                                Mark delivered
                                            </button>
                                        </>
                                    )}
                                    {isSeller && o.escrow_status === 'delivered' && (
                                        <button onClick={() => run(o.reference, 'extend', {})} className="rounded border border-slate-300 px-3 py-1.5 text-xs font-bold text-slate-700">
                                            Extend deadline (once)
                                        </button>
                                    )}
                                    {isBuyer && o.escrow_status === 'delivered' && (
                                        <>
                                            <button onClick={() => run(o.reference, 'confirm', {})} className="rounded bg-emerald-600 px-3 py-1.5 text-xs font-bold text-white">
                                                I&apos;ve received my order
                                            </button>
                                            <input
                                                placeholder="Describe the problem"
                                                value={reason[o.reference] || ''}
                                                onChange={(e) => setReason({ ...reason, [o.reference]: e.target.value })}
                                                className="rounded border border-slate-200 px-2 py-1.5 text-xs"
                                            />
                                            <button onClick={() => run(o.reference, 'problem', { reason: reason[o.reference] || '' })} className="rounded border border-red-300 px-3 py-1.5 text-xs font-bold text-red-600">
                                                There is a problem
                                            </button>
                                        </>
                                    )}
                                </div>
                            </li>
                        );
                    })}
                </ul>
            )}
            {action.isError && <p className="mt-3 text-xs text-red-600">Action failed. Please check the details and try again.</p>}
        </section>
    );
};

export default SafeDealPanel;
