import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    useCredit, useCreditTransactions, useReferrals,
    useAutoRenewals, useCreateAutoRenewal, useDeleteAutoRenewal,
    useProSales, useCreateProSales, useUpdateProSales, useDeleteProSales,
} from '../../hooks/useJiji.js';
import { fetchBoostPlansFn } from '../../service/ShopEndpoints.js';

const TABS = [
    ['wallet', 'Wallet'],
    ['renew', 'Auto-renewal'],
    ['pro', 'Pro Sales'],
    ['referrals', 'Referrals'],
];

const SellerTools = ({ isAuthenticated }) => {
    const [tab, setTab] = useState('wallet');
    const [planId, setPlanId] = useState('');
    const [productId, setProductId] = useState('');
    const [campaign, setCampaign] = useState({ product: '', name: '', daily_budget: '1000', bid_amount: '20' });

    const { data: credit } = useCredit(isAuthenticated);
    const { data: transactions } = useCreditTransactions(isAuthenticated);
    const { data: referrals } = useReferrals(isAuthenticated);
    const { data: renewals } = useAutoRenewals(isAuthenticated);
    const { data: proSales } = useProSales(isAuthenticated);
    const { data: plans } = useQuery({ queryKey: ['boost-plans'], queryFn: fetchBoostPlansFn, enabled: isAuthenticated });

    const createRenewal = useCreateAutoRenewal();
    const deleteRenewal = useDeleteAutoRenewal();
    const createPro = useCreateProSales();
    const updatePro = useUpdateProSales();
    const deletePro = useDeleteProSales();

    if (!isAuthenticated) {
        return (
            <section className="rounded-xl border border-slate-200 bg-white p-5">
                <h2 className="text-base font-black text-slate-800">Seller tools</h2>
                <p className="mt-2 text-sm text-slate-500">Sign in to manage your wallet, boosts and campaigns.</p>
            </section>
        );
    }

    const planList = plans?.results || (Array.isArray(plans) ? plans : []);

    return (
        <section className="rounded-xl border border-slate-200 bg-white">
            <div className="flex gap-1 overflow-x-auto border-b border-slate-100 px-3 pt-3">
                {TABS.map(([key, label]) => (
                    <button
                        key={key}
                        type="button"
                        onClick={() => setTab(key)}
                        className={`shrink-0 rounded-t-lg px-3 py-2 text-xs font-bold ${tab === key ? 'bg-brand/10 text-brand' : 'text-slate-500 hover:text-slate-800'}`}
                    >
                        {label}
                    </button>
                ))}
            </div>

            <div className="p-5">
                {tab === 'wallet' && (
                    <div>
                        <p className="text-xs font-bold uppercase tracking-wide text-slate-400">Available balance</p>
                        <p className="mt-1 text-2xl font-black text-slate-900">
                            ₦{Number(credit?.balance || 0).toLocaleString()}
                        </p>
                        <p className="mt-1 text-xs text-slate-400">1 Credit = ₦1. Used only for premium services.</p>
                        <ul className="mt-4 divide-y divide-slate-100">
                            {(transactions?.results || []).slice(0, 8).map((tx) => (
                                <li key={tx.id} className="flex items-center justify-between py-2 text-sm">
                                    <span className="capitalize text-slate-600">{tx.transaction_type}</span>
                                    <span className={`font-bold ${tx.amount >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                                        {tx.amount >= 0 ? '+' : ''}₦{Number(tx.amount).toLocaleString()}
                                    </span>
                                </li>
                            ))}
                            {!transactions?.results?.length && <li className="py-3 text-sm text-slate-400">No transactions yet.</li>}
                        </ul>
                    </div>
                )}

                {tab === 'renew' && (
                    <div>
                        <form
                            onSubmit={(e) => {
                                e.preventDefault();
                                createRenewal.mutate({ plan: planId, product: productId });
                            }}
                            className="grid grid-cols-1 gap-3 sm:grid-cols-3"
                        >
                            <select value={planId} onChange={(e) => setPlanId(e.target.value)} required className="rounded-lg border border-slate-200 px-3 py-2 text-sm">
                                <option value="">Select plan</option>
                                {planList.map((p) => <option key={p.id} value={p.id}>{p.name} — ₦{p.price}</option>)}
                            </select>
                            <input type="number" placeholder="Product ID" value={productId} onChange={(e) => setProductId(e.target.value)} required className="rounded-lg border border-slate-200 px-3 py-2 text-sm" />
                            <button type="submit" disabled={createRenewal.isPending} className="rounded-lg bg-brand px-4 py-2 text-xs font-bold text-white disabled:opacity-50">
                                Set up auto-renewal
                            </button>
                        </form>
                        <ul className="mt-4 divide-y divide-slate-100">
                            {(renewals?.results || []).map((r) => (
                                <li key={r.id} className="flex items-center justify-between py-2 text-sm">
                                    <span className="text-slate-600">Plan #{r.plan} on product #{r.product} — <span className="font-bold">{r.status}</span></span>
                                    <button onClick={() => deleteRenewal.mutate(r.id)} className="text-xs font-bold text-red-600">Cancel</button>
                                </li>
                            ))}
                            {!renewals?.results?.length && <li className="py-3 text-sm text-slate-400">No auto-renewals set up.</li>}
                        </ul>
                    </div>
                )}

                {tab === 'pro' && (
                    <div>
                        <form
                            onSubmit={(e) => {
                                e.preventDefault();
                                createPro.mutate(campaign);
                            }}
                            className="grid grid-cols-1 gap-3 sm:grid-cols-2"
                        >
                            <input placeholder="Product ID" type="number" required value={campaign.product} onChange={(e) => setCampaign({ ...campaign, product: e.target.value })} className="rounded-lg border border-slate-200 px-3 py-2 text-sm" />
                            <input placeholder="Campaign name" required value={campaign.name} onChange={(e) => setCampaign({ ...campaign, name: e.target.value })} className="rounded-lg border border-slate-200 px-3 py-2 text-sm" />
                            <input placeholder="Daily budget (₦)" type="number" min="100" value={campaign.daily_budget} onChange={(e) => setCampaign({ ...campaign, daily_budget: e.target.value })} className="rounded-lg border border-slate-200 px-3 py-2 text-sm" />
                            <input placeholder="Bid per click (₦)" type="number" min="1" value={campaign.bid_amount} onChange={(e) => setCampaign({ ...campaign, bid_amount: e.target.value })} className="rounded-lg border border-slate-200 px-3 py-2 text-sm" />
                            <button type="submit" disabled={createPro.isPending} className="rounded-lg bg-brand px-4 py-2 text-xs font-bold text-white sm:col-span-2 disabled:opacity-50">
                                Create campaign
                            </button>
                        </form>
                        <ul className="mt-4 divide-y divide-slate-100">
                            {(proSales?.results || []).map((c) => (
                                <li key={c.id} className="flex flex-wrap items-center justify-between gap-2 py-3 text-sm">
                                    <span className="font-bold text-slate-700">{c.name}</span>
                                    <span className="text-slate-500">{c.clicks} clicks · ₦{Number(c.spend).toLocaleString()} spent · {c.status}</span>
                                    <span className="flex gap-2">
                                        <button onClick={() => updatePro.mutate({ id: c.id, payload: { status: c.status === 'active' ? 'paused' : 'active' } })} className="text-xs font-bold text-brand">
                                            {c.status === 'active' ? 'Pause' : 'Resume'}
                                        </button>
                                        <button onClick={() => deletePro.mutate(c.id)} className="text-xs font-bold text-red-600">End</button>
                                    </span>
                                </li>
                            ))}
                            {!proSales?.results?.length && <li className="py-3 text-sm text-slate-400">No campaigns yet.</li>}
                        </ul>
                    </div>
                )}

                {tab === 'referrals' && (
                    <div>
                        <p className="text-sm text-slate-500">
                            Earn a bonus for every friend who creates an account and confirms their phone number.
                        </p>
                        <ul className="mt-4 divide-y divide-slate-100">
                            {(referrals?.results || []).map((r) => (
                                <li key={r.id} className="flex items-center justify-between py-2 text-sm">
                                    <span className="text-slate-600">{r.referred_username}</span>
                                    <span className="font-bold text-slate-700">₦{Number(r.amount).toLocaleString()} · {r.status}</span>
                                </li>
                            ))}
                            {!referrals?.results?.length && <li className="py-3 text-sm text-slate-400">No referrals yet.</li>}
                        </ul>
                    </div>
                )}
            </div>
        </section>
    );
};

export default SellerTools;
