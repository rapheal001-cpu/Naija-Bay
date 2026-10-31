import { useEffect, useState } from 'react';
import { HiOutlineX } from 'react-icons/hi';
import { HiOutlineChatAlt2 } from 'react-icons/hi';
import { useNavigate } from 'react-router-dom';
import { useStartConversationMutation } from '../../hooks/UseMutation';

/**
 * Compose the first message of a product conversation.
 *
 * @param {{ open: boolean, onClose: () => void, product: Object }} props
 */
const StartChatModal = ({ open, onClose, product }) => {
    const navigate = useNavigate();
    const [message, setMessage] = useState('Hi, is this still available?');
    const [error, setError] = useState('');

    const startConversation = useStartConversationMutation();

    useEffect(() => {
        if (open) {
            setMessage('Hi, is this still available?');
            setError('');
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

    if (!open || !product) return null;

    const handleSubmit = (event) => {
        event.preventDefault();
        setError('');

        const trimmed = message.trim();
        if (!trimmed) {
            setError('Write a message before sending.');
            return;
        }

        startConversation.mutate(
            { productId: product.id, message: trimmed },
            {
                onSuccess: (conversation) => {
                    onClose();
                    navigate(`/messages?conversation=${conversation.id}`);
                },
                onError: (err) => {
                    const data = err?.response?.data;
                    const detail =
                        data?.detail ||
                        data?.non_field_errors?.[0] ||
                        data?.message?.[0] ||
                        data?.product?.[0] ||
                        'Could not start the conversation. Please try again.';
                    setError(detail);
                },
            }
        );
    };

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4" role="dialog" aria-modal="true">
            <div className="absolute inset-0 bg-gray-900/50 backdrop-blur-sm" onClick={onClose} />

            <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
                <div className="flex items-start justify-between px-5 py-4 border-b border-gray-100">
                    <div className="flex items-center gap-2.5 min-w-0">
                        <span className="flex items-center justify-center w-9 h-9 rounded-full bg-brand/10 text-brand shrink-0">
                            <HiOutlineChatAlt2 size={18} />
                        </span>
                        <div className="min-w-0">
                            <h2 className="text-sm font-bold text-gray-900">Message seller</h2>
                            <p className="text-xs text-gray-400 truncate max-w-56">
                                {product.product_name}
                            </p>
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        aria-label="Close chat dialog"
                        className="flex items-center justify-center w-8 h-8 rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
                    >
                        <HiOutlineX size={16} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="px-5 py-4 space-y-3">
                    <div>
                        <label htmlFor="start-chat-message" className="text-xs font-bold text-gray-600">
                            Your message
                        </label>
                        <textarea
                            id="start-chat-message"
                            value={message}
                            onChange={(event) => setMessage(event.target.value)}
                            rows={4}
                            maxLength={4000}
                            className="mt-1.5 w-full rounded-xl border border-gray-200 px-3 py-2.5 text-sm text-gray-800 resize-none focus:border-brand focus:outline-none"
                        />
                    </div>

                    <div className="rounded-xl bg-gray-50 border border-gray-100 p-3">
                        <p className="text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-1">
                            Seller
                        </p>
                        <p className="text-sm font-bold text-gray-900">
                            {product.product_user?.full_name || product.product_user?.username}
                        </p>
                        <p className="text-xs text-gray-400">
                            Keep the conversation on Naija-Bay so we can help if something goes wrong.
                        </p>
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
                            disabled={startConversation.isPending}
                            className="px-4 py-2.5 rounded-xl bg-brand text-white text-sm font-bold hover:opacity-90 disabled:opacity-60 transition-opacity"
                        >
                            {startConversation.isPending ? 'Sending...' : 'Send message'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default StartChatModal;
