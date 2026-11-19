import { useState } from 'react';
import { FaStar } from 'react-icons/fa';
import { useFeedback, useCreateFeedback } from '../../hooks/useJiji.js';
import { Stars } from '../ProductComponents/StarRating.jsx';

const FeedbackSection = ({ sellerId, currentUserId, canReview = false }) => {
    const [rating, setRating] = useState(5);
    const [comment, setComment] = useState('');
    const [showForm, setShowForm] = useState(false);

    const { data, isLoading } = useFeedback(sellerId);
    const createFeedback = useCreateFeedback();

    const items = data?.results || (Array.isArray(data) ? data : []);
    const alreadyReviewed = items.some((f) => f.author === currentUserId);
    const average = items.length
        ? (items.reduce((sum, f) => sum + Number(f.rating || 0), 0) / items.length).toFixed(1)
        : null;

    const submit = (e) => {
        e.preventDefault();
        createFeedback.mutate(
            { seller: sellerId, rating, comment: comment.trim() },
            { onSuccess: () => { setComment(''); setShowForm(false); } }
        );
    };

    return (
        <section className="rounded-xl border border-slate-200 bg-white p-5">
            <div className="flex items-center justify-between gap-3">
                <div>
                    <h2 className="text-base font-black text-slate-800">Feedback ({items.length})</h2>
                    {average && (
                        <div className="mt-1 flex items-center gap-2">
                            <Stars value={Number(average)} size={13} />
                            <span className="text-xs font-semibold text-slate-600">{average} / 5</span>
                        </div>
                    )}
                </div>
                {canReview && !alreadyReviewed && (
                    <button
                        type="button"
                        onClick={() => setShowForm((v) => !v)}
                        className="rounded-lg border border-brand px-3 py-2 text-xs font-bold text-brand hover:bg-brand/5"
                    >
                        {showForm ? 'Cancel' : 'Leave feedback'}
                    </button>
                )}
            </div>

            {showForm && (
                <form onSubmit={submit} className="mt-4 rounded-lg bg-slate-50 p-4">
                    <div className="flex items-center gap-1">
                        {[1, 2, 3, 4, 5].map((n) => (
                            <button
                                type="button"
                                key={n}
                                onClick={() => setRating(n)}
                                aria-label={`${n} star${n > 1 ? 's' : ''}`}
                            >
                                <FaStar
                                    size={20}
                                    className={n <= rating ? 'text-amber-400' : 'text-slate-300'}
                                />
                            </button>
                        ))}
                    </div>
                    <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="How was your experience with this seller?"
                        rows={3}
                        className="mt-3 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
                    />
                    <button
                        type="submit"
                        disabled={createFeedback.isPending || !rating}
                        className="mt-3 rounded-lg bg-brand px-4 py-2 text-xs font-bold text-white hover:bg-brand-hover disabled:opacity-50"
                    >
                        {createFeedback.isPending ? 'Sending…' : 'Submit feedback'}
                    </button>
                    {createFeedback.isError && (
                        <p className="mt-2 text-xs text-red-600">Could not submit. You may have already reviewed this seller.</p>
                    )}
                </form>
            )}

            {isLoading ? (
                <p className="mt-4 text-sm text-slate-400">Loading feedback…</p>
            ) : items.length === 0 ? (
                <p className="mt-4 text-sm text-slate-400">
                    No feedback yet. Be the first to share your experience.
                </p>
            ) : (
                <ul className="mt-4 divide-y divide-slate-100">
                    {items.map((fb) => (
                        <li key={fb.id} className="py-3">
                            <div className="flex items-center justify-between">
                                <span className="text-sm font-bold text-slate-700">
                                    {fb.author_username || 'Buyer'}
                                </span>
                                <span className="flex items-center gap-1">
                                    <Stars value={Number(fb.rating)} size={12} />
                                </span>
                            </div>
                            {fb.comment && (
                                <p className="mt-1 text-sm text-slate-500">{fb.comment}</p>
                            )}
                            {fb.response && (
                                <p className="mt-2 rounded bg-slate-50 px-3 py-2 text-xs text-slate-600">
                                    <span className="font-bold">Seller: </span>{fb.response}
                                </p>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </section>
    );
};

export default FeedbackSection;
