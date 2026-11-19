import { useState } from 'react';
import { HiBadgeCheck } from 'react-icons/hi';
import { useMyVerification, useSubmitVerification } from '../../hooks/useJiji.js';
import { uploadMediaFile } from '../../core/api/mediaApi.js';
import { UPLOAD_PURPOSES } from '../../core/constants/api.js';

const ID_TYPES = [
    ['nin', 'NIN'],
    ['bvn', 'BVN'],
    ['passport', 'International Passport'],
    ['drivers_license', "Driver's Licence"],
    ['voters_card', "Voter's Card"],
];

const VerifiedIdCard = ({ isAuthenticated, onSignIn }) => {
    const [idType, setIdType] = useState('nin');
    const [idNumber, setIdNumber] = useState('');
    const [selfie, setSelfie] = useState(null);
    const [document, setDocument] = useState(null);

    const { data, isLoading } = useMyVerification(isAuthenticated);
    const submit = useSubmitVerification();

    if (!isAuthenticated) {
        return (
            <section className="rounded-xl border border-slate-200 bg-white p-5">
                <h2 className="text-base font-black text-slate-800">Verified ID</h2>
                <p className="mt-2 text-sm text-slate-500">Sign in to verify your identity and build buyer trust.</p>
                <button onClick={onSignIn} className="mt-3 rounded-lg bg-brand px-4 py-2 text-xs font-bold text-white">Sign in</button>
            </section>
        );
    }

    const status = data?.status || 'none';

    return (
        <section className="rounded-xl border border-slate-200 bg-white p-5">
            <div className="flex items-center gap-2">
                <HiBadgeCheck size={20} className="text-blue-500" />
                <h2 className="text-base font-black text-slate-800">Verified ID</h2>
            </div>

            {isLoading ? (
                <p className="mt-3 text-sm text-slate-400">Loading…</p>
            ) : status === 'approved' || data?.verified ? (
                <p className="mt-3 rounded-lg bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">
                    Your identity is verified. Your ads show the Verified ID badge.
                </p>
            ) : status === 'pending' ? (
                <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-700">
                    Your verification is under review. We&apos;ll update you soon.
                </p>
            ) : (
                <form
                    onSubmit={async (e) => {
                        e.preventDefault();
                        const fd = new FormData();
                        fd.append('id_type', idType);
                        fd.append('id_number', idNumber);
                        if (selfie) {
                            const result = await uploadMediaFile(selfie, UPLOAD_PURPOSES.VERIFICATION_SELFIE);
                            fd.append(result?.key ? 'selfie_key' : 'selfie', result?.key || selfie);
                        }
                        if (document) {
                            const result = await uploadMediaFile(document, UPLOAD_PURPOSES.VERIFICATION_DOCUMENT);
                            fd.append(result?.key ? 'document_key' : 'document', result?.key || document);
                        }
                        submit.mutate(fd);
                    }}
                    className="mt-4 space-y-3"
                >
                    {status === 'rejected' && data?.reviewer_note && (
                        <p className="rounded bg-red-50 px-3 py-2 text-xs text-red-700">Previous submission: {data.reviewer_note}</p>
                    )}
                    <div>
                        <label className="text-xs font-bold text-slate-600">ID type</label>
                        <select
                            value={idType}
                            onChange={(e) => setIdType(e.target.value)}
                            className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
                        >
                            {ID_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="text-xs font-bold text-slate-600">ID number</label>
                        <input
                            type="text"
                            required
                            value={idNumber}
                            onChange={(e) => setIdNumber(e.target.value)}
                            className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="text-xs font-bold text-slate-600">Selfie</label>
                            <input type="file" accept="image/*" required onChange={(e) => setSelfie(e.target.files[0])} className="mt-1 w-full text-xs" />
                        </div>
                        <div>
                            <label className="text-xs font-bold text-slate-600">ID document</label>
                            <input type="file" accept="image/*" required onChange={(e) => setDocument(e.target.files[0])} className="mt-1 w-full text-xs" />
                        </div>
                    </div>
                    <button
                        type="submit"
                        disabled={submit.isPending}
                        className="w-full rounded-lg bg-brand px-4 py-2 text-xs font-bold text-white hover:bg-brand-hover disabled:opacity-50"
                    >
                        {submit.isPending ? 'Submitting…' : 'Submit for verification'}
                    </button>
                    {submit.isError && <p className="text-xs text-red-600">Submission failed. Check the files and try again.</p>}
                </form>
            )}
        </section>
    );
};

export default VerifiedIdCard;
