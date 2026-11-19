import { Link } from 'react-router-dom';
import AppLayout from '../components/AppLayout.jsx';

const GENERAL_TIPS = [
    ['Check feedback', 'People who dealt with a seller leave reviews to keep others informed. Take a minute to check feedback before making a deal.'],
    ['Avoid sending prepayments', 'Meet sellers face to face in a public place or request payment on delivery. Check the item before you pay.'],
    ['Ensure the packed item is the one you inspected', 'Inspect the item and pay only when you have it in your possession — don’t give a scammer the chance to swap it.'],
    ['Never give out financial information', 'Avoid fake payment services, fee requests or money-transfer links. Never share PIN codes or passwords.'],
    ['Use common sense', 'Avoid anything too good to be true — unrealistically low prices or promises of quick money.'],
];

const SPECIAL_TIPS = [
    ['Looking for a job?', [
        'Don’t pay fees for applying or interviewing.',
        'Avoid interviews at unofficial office addresses.',
        'Research the company before you go.',
        'Never disclose personal info before a job offer.',
    ]],
    ['Looking for a car?', [
        'Inspect the car to make sure it is what you need.',
        'Take a test drive and consider bringing a mechanic.',
        'Check all documents and only pay when satisfied.',
    ]],
    ['Looking for services?', [
        'Check feedback to make sure the person is reliable.',
        'Agree on the scope of work and payment in advance.',
        'Meet in person at a safe public place.',
    ]],
    ['Looking for property?', [
        'Avoid paying inspection fees.',
        'View with a friend where possible.',
        'Check everything carefully before paying.',
        'Don’t pay in advance if you can’t move in immediately.',
    ]],
];

const Safety = () => (
    <AppLayout>
        <div className="mx-auto max-w-5xl px-4 py-10 pb-16">
            <section className="text-center">
                <p className="text-xs font-bold uppercase tracking-[0.15em] text-brand">Buy and sell with confidence</p>
                <h1 className="mt-2 text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
                    Best deals are safe deals
                </h1>
                <p className="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-slate-500 sm:text-base">
                    We can&apos;t be with you at every stage of a deal, but these tips will help you
                    protect yourself from unpleasant situations.
                </p>
            </section>

            <section className="mt-10 rounded-2xl border border-slate-200 bg-white p-6">
                <h2 className="text-xl font-black text-slate-800">General safety tips</h2>
                <ul className="mt-4 space-y-4">
                    {GENERAL_TIPS.map(([title, text]) => (
                        <li key={title} className="flex gap-3">
                            <span className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-50 text-xs font-black text-emerald-600">✓</span>
                            <div>
                                <p className="text-sm font-bold text-slate-800">{title}</p>
                                <p className="mt-0.5 text-sm leading-relaxed text-slate-500">{text}</p>
                            </div>
                        </li>
                    ))}
                </ul>
            </section>

            <section className="mt-6 grid gap-4 sm:grid-cols-2">
                {SPECIAL_TIPS.map(([title, tips]) => (
                    <div key={title} className="rounded-2xl border border-slate-200 bg-white p-6">
                        <h2 className="text-base font-black text-slate-800">{title}</h2>
                        <ul className="mt-3 list-disc space-y-1.5 pl-5 text-sm leading-relaxed text-slate-500">
                            {tips.map((tip) => <li key={tip}>{tip}</li>)}
                        </ul>
                    </div>
                ))}
            </section>

            <section className="mt-8 rounded-2xl bg-brand p-6 text-white">
                <h2 className="text-xl font-black">Extra protection with Safe Deal</h2>
                <p className="mt-2 text-sm leading-relaxed text-white/80">
                    With Safe Deal, your payment is held by NaijaBay until the item is delivered and
                    you confirm it. If there is a problem, report it before the 24-hour window ends
                    and our support team will review.
                </p>
                <Link
                    to="/profile"
                    className="mt-4 inline-block rounded-lg bg-white px-5 py-2.5 text-sm font-bold text-brand hover:bg-white/90"
                >
                    View my Safe Deal orders
                </Link>
            </section>
        </div>
    </AppLayout>
);

export default Safety;
