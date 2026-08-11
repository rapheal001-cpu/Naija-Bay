import { useState, useRef, useEffect, useMemo } from 'react';
import {
    FaArrowLeft,
    FaPhone,
    FaVideo,
    FaEllipsisV,
    FaPaperclip,
    FaPaperPlane,
    FaCheckDouble,
    FaCheck,
    FaSmile,
} from 'react-icons/fa';
import { useNavigate, useParams } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';
import { useFetchChatConversation } from '../hooks/UseQuery.js';
import { useSendChatMessageMutation } from '../hooks/UseMutation.js';

const groupByDate = (messages) => {
    const groups = {};
    messages.forEach((msg) => {
        const date = msg.date || 'Today';
        if (!groups[date]) groups[date] = [];
        groups[date].push(msg);
    });
    return Object.entries(groups);
};

const Message = () => {
    const navigate = useNavigate();
    const { receiverId } = useParams();

    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);

    const receiver = Number(receiverId);
    const conversationQuery = useFetchChatConversation(receiver, isAuthenticated);
    const sendChatMessageMutation = useSendChatMessageMutation();

    const [inputText, setInputText] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (!isAuthenticated && !user) {
            navigate('/sign-in');
        }
    }, [isAuthenticated, user, navigate]);

    const messages = useMemo(() => {
        const data = Array.isArray(conversationQuery.data) ? conversationQuery.data : [];
        return data.map((msg) => ({
            id: msg.id,
            text: msg.message,
            sender: Number(msg.sender) === Number(user?.id) ? 'me' : 'them',
            time: new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            status: msg.read ? 'read' : 'sent',
            date: 'Today',
        }));
    }, [conversationQuery.data, user]);

    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    const handleSend = () => {
        if (!inputText.trim()) return;
        sendChatMessageMutation.mutate({ receiverId, message: inputText.trim() });
        setInputText('');
        setIsTyping(true);
        setTimeout(() => setIsTyping(false), 600);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const groupedMessages = groupByDate(messages);

    if (!receiverId) {
        return (
            <>
                <Header />
                <Spacer space="mb-20" />
                <div className="max-w-3xl mx-auto px-4 py-16 text-center">
                    <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
                        <h2 className="text-lg font-bold text-gray-900">Conversation not found</h2>
                        <p className="text-sm text-gray-500 mt-2">
                            The user with ID <span className="font-mono text-brand">#{receiverId}</span> doesn't have any messages yet.
                        </p>
                        <button
                            onClick={() => navigate(-1)}
                            className="mt-6 px-5 py-2.5 rounded-xl bg-brand text-white text-sm font-semibold hover:bg-brand/90 transition-all"
                        >
                            Back to Inbox
                        </button>
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
            <Header />
            <Spacer space="mb-20" />

            <div className="max-w-3xl mx-auto h-[calc(100vh-5rem)] flex flex-col bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-100 shrink-0">
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => navigate(-1)}
                            className="p-2 rounded-xl text-gray-500 hover:bg-gray-100 transition-all"
                            aria-label="Back"
                        >
                            <FaArrowLeft className="w-4 h-4" />
                        </button>

                        <div className="relative">
                            <div className="w-10 h-10 rounded-xl object-cover bg-gray-100 flex items-center justify-center font-bold text-gray-600">
                                #{receiverId}
                            </div>
                        </div>

                        <div>
                            <h2 className="text-sm font-bold text-gray-900 leading-tight">
                                User #{receiverId}
                            </h2>
                            <p className="text-[11px] text-emerald-600 font-medium">
                                Online
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-1">
                        <button className="p-2.5 rounded-xl text-gray-400 hover:bg-gray-50 hover:text-gray-600 transition-all">
                            <FaPhone className="w-4 h-4" />
                        </button>
                        <button className="p-2.5 rounded-xl text-gray-400 hover:bg-gray-50 hover:text-gray-600 transition-all">
                            <FaVideo className="w-4 h-4" />
                        </button>
                        <button className="p-2.5 rounded-xl text-gray-400 hover:bg-gray-50 hover:text-gray-600 transition-all">
                            <FaEllipsisV className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto px-4 py-6 bg-gray-50/50 space-y-6">
                    {conversationQuery.isLoading ? (
                        <div className="text-sm text-gray-500">Loading conversation...</div>
                    ) : groupedMessages.map(([date, msgs]) => (
                        <div key={date} className="space-y-4">
                            <div className="flex justify-center">
                                <span className="px-3 py-1 rounded-full bg-gray-100 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                                    {date}
                                </span>
                            </div>

                            {msgs.map((msg) => {
                                const isMe = msg.sender === 'me';

                                return (
                                    <div
                                        key={msg.id}
                                        className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}
                                    >
                                        <div
                                            className={`max-w-[80%] sm:max-w-[70%] ${
                                                isMe ? 'items-end' : 'items-start'
                                            } flex flex-col gap-1`}
                                        >
                                            <div
                                                className={`relative px-4 py-2.5 rounded-2xl text-[13px] leading-relaxed shadow-sm ${
                                                    isMe
                                                        ? 'bg-brand text-white rounded-br-md'
                                                        : 'bg-white text-gray-800 border border-gray-100 rounded-bl-md'
                                                }`}
                                            >
                                                <p>{msg.text}</p>
                                            </div>

                                            <div
                                                className={`flex items-center gap-1.5 px-1 ${
                                                    isMe ? 'flex-row-reverse' : ''
                                                }`}
                                            >
                                                <span className="text-[10px] text-gray-400 font-medium">
                                                    {msg.time}
                                                </span>
                                                {isMe && (
                                                    <span className="text-gray-400">
                                                        {msg.status === 'read' ? (
                                                            <FaCheckDouble className="w-3 h-3 text-blue-400" />
                                                        ) : msg.status === 'delivered' ? (
                                                            <FaCheckDouble className="w-3 h-3" />
                                                        ) : (
                                                            <FaCheck className="w-3 h-3" />
                                                        )}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    ))}

                    {isTyping && (
                        <div className="flex justify-start">
                            <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                                <div className="flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" />
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={scrollRef} />
                </div>

                <div className="shrink-0 px-4 py-3 bg-white border-t border-gray-100">
                    <div className="flex items-end gap-2">
                        <button className="p-2.5 rounded-xl text-gray-400 hover:bg-gray-50 hover:text-gray-600 transition-all shrink-0 mb-0.5">
                            <FaPaperclip className="w-4 h-4" />
                        </button>

                        <div className="flex-1 relative">
                            <textarea
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Type a message..."
                                rows={1}
                                className="w-full pl-4 pr-10 py-3 rounded-2xl border border-gray-200 bg-gray-50 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand focus:bg-white transition-all resize-none max-h-32"
                                style={{ minHeight: '44px' }}
                            />
                            <button className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors">
                                <FaSmile className="w-4 h-4" />
                            </button>
                        </div>

                        <button
                            onClick={handleSend}
                            disabled={!inputText.trim() || sendChatMessageMutation.isPending}
                            className={`p-3 rounded-xl transition-all shrink-0 shadow-sm ${
                                inputText.trim()
                                    ? 'bg-brand text-white hover:bg-brand/90 shadow-brand/25'
                                    : 'bg-gray-100 text-gray-300 cursor-not-allowed'
                            }`}
                            aria-label="Send"
                        >
                            <FaPaperPlane className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
};

export default Message;