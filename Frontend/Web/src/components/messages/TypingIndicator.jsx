const TypingIndicator = ({ names = [] }) => {
    if (!names.length) return null;
    const label = names.length === 1 ? `${names[0]} is typing` : `${names.length} people are typing`;
    return (
        <div className="flex justify-start px-4 pb-2" aria-live="polite">
            <div className="flex items-center gap-2 rounded-2xl rounded-bl-md bg-white border border-gray-100 px-3 py-2 shadow-sm">
                <span className="flex gap-1">
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400 [animation-delay:0ms]" />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400 [animation-delay:150ms]" />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400 [animation-delay:300ms]" />
                </span>
                <span className="text-[11px] text-gray-500">{label}…</span>
            </div>
        </div>
    );
};

export default TypingIndicator;
