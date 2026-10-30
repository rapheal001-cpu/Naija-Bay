import { useEffect, useState } from 'react';
import { HiOutlineX } from 'react-icons/hi';
import { TbAlertTriangleFilled } from 'react-icons/tb';
import { useReportProductMutation } from '../hooks/UseMutation';

const REASONS = [
    { value: 'scam', label: 'Scam or fraud' },
    { value: 'prohibited', label: 'Prohibited item' },
    { value: 'wrong_category', label: 'Wrong category' },
    { value: 'counterfeit', label: 'Counterfeit product' },
    { value: 'offensive', label: 'Offensive content' },
    { value: 'duplicate', label: 'Duplicate listing' },
    { value: 'other', label: 'Something else' },
];

/**
 * Report-abuse dialog for a single listing.
 *
 * @param {{ open: boolean, onClose: () => void, productSlug: string, productName?: string }} props
 */
const ReportModal = ({ open, onClose, productSlug, productName = 'this listing' }) => {
    const [reason, setReason] = useState('');
    const [details, setDetails] = useState('');
    const [error, setError] = useState('');
    const [submitted, setSubmitted] = useState(false);

    const reportMutation = useReportProductMutation(
        (field, { message }) => setError(message),
        (message) => setError(message)
    );

    useEffect(() => {
        if (open) {
            setReason('');
            setDetails('');
            setError('');
            setSubmitted(false);
        }
    }, [open]);

    useEffect(() => {
        if (!open) return undefined;
        const onKeyDown = (event) => {
            if (event.key === 'Escape') onClose();
        };
        document.addEventListener('keydown', onKeyDown);
        return () => document.removeEventListener('keydown', onKeyDown);
    }, [open, onClose]);

    if (!open) return null;

    const handleSubmit = (event) => {
        event.preventDefault();
        setError('');

        if (!reason) {
            setError('Please choose a reason.');
            return;
        }

        reportMutation.mutate(
            { productSlug, reason, details },
            {
                onSuccess: () => setSubmitted(true),
                onError: (err) => {
                    const data = err?.response?.data;
                    const message =
                        data?.detail ||
                        data?.non_field_errors?.[0] ||
                        data?.reason?.[0] ||
                        data?.details?.[0] ||
                        'Could not submit the report. Please try again.';
                    setError(message);
                },
            }
        );
    };

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4" role="dialog" aria-modal="true">
            <div className="absolute inset-0 bg-gray-900/50 backdrop-blur-sm" onClick={onClose} />

            <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
                <div className="flex items-start justify-between px-5 py-4 border-b border-gray-100">
                    <div className="flex items-center gap-2.5">
                        <span className="flex items-center justify-center w-9 h-9 rounded-full bg-amber-50 text-amber-500">
                            <TbAlertTriangleFilled size={18} />
                        </span>
                        <div>
                            <h2 className="text-sm font-bold text-gray-900">Report abuse</h2>
                            <p className="text-xs text-gray-400 truncate max-w-56">{productName}</p>
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        aria-label="Close report dialog"
                        className="flex items-center justify-center w-8 h-8 rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
                    >
                        <HiOutlineX size={16} />
                    </button>
                </div>

                {submitted ? (
                    <div className="px-5 py-8 text-center">
                        <p className="text-sm font-bold text-gray-900">Report received</p>
                        <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                            Thanks for helping keep Naija-Bay safe. Our moderation team will review
                            this listing shortly.
                        </p>
                        <button
                            type="button"
                            onClick={onClose}
                            className="mt-5 px-5 py-2.5 rounded-xl bg-brand text-white text-sm font-bold hover:opacity-90 transition-opacity"
                        >
                            Done
                        </button>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit} className="px-5 py-4 space-y-3">
                        <div>
                            <label htmlFor="report-reason" className="text-xs font-bold text-gray-600">
                                What is wrong?
                            </label>
                            <select
                                id="report-reason"
                                value={reason}
                                onChange={(event) => setReason(event.target.value)}
                                className="mt-1.5 w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm text-gray-800 focus:border-brand focus:outline-none"
                            >
                                <option value="">Select a reason</option>
                                {REASONS.map((option) => (
                                    <option key={option.value} value={option.value}>
                                        {option.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label htmlFor="report-details" className="text-xs font-bold text-gray-600">
                                More details <span className="text-gray-400 font-normal">(optional)</span>
                            </label>
                            <textarea
                                id="report-details"
                                value={details}
                                onChange={(event) => setDetails(event.target.value)}
                                rows={3}
                                maxLength={2000}
                                placeholder="Tell us what happened..."
                                className="mt-1.5 w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm text-gray-800 resize-none focus:border-brand focus:outline-none"
                            />
                        </div>

                        {error && (
                            <p className="text-xs font-semibold text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                                {error}
                            </p>
                        )}

                        <div className="flex items-center justify-end gap-2 pt-1">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2.5 rounded-xl text-sm font-bold text-gray-500 hover:bg-gray-100 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={reportMutation.isPending}
                                className="px-4 py-2.5 rounded-xl bg-brand text-white text-sm font-bold hover:opacity-90 disabled:opacity-60 transition-opacity"
                            >
                                {reportMutation.isPending ? 'Sending...' : 'Submit report'}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
};

export default ReportModal;
