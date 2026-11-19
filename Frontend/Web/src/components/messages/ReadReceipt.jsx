const ReadReceipt = ({ isMine, read }) => {
    if (!isMine) return null;
    return (
        <span
            className={read ? 'text-sky-200' : 'text-white/60'}
            title={read ? 'Read' : 'Sent'}
            aria-label={read ? 'Read' : 'Sent'}
        >
            {read ? '✓✓' : '✓'}
        </span>
    );
};

export default ReadReceipt;
