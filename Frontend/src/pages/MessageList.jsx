import { useState, useEffect, useMemo } from 'react';
import { FaSearch, FaEllipsisH, FaCheckDouble, FaCheck } from 'react-icons/fa';
import Header from '../components/HeaderComponents/Header.jsx';
import Spacer from '../components/Spacer.jsx';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useFetchChatList } from '../hooks/UseQuery.js';

const MessageList = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);

    const navigate = useNavigate();

    const [searchQuery, setSearchQuery] = useState('');

    const chatListQuery = useFetchChatList(isAuthenticated);

    useEffect(() => {
        if (!isAuthenticated && !user) {
            navigate('/sign-in');
        }
    }, [isAuthenticated, user, navigate]);

    const chatThreads = useMemo(() => {
        const messages = Array.isArray(chatListQuery.data) ? chatListQuery.data : [];
        const currentUserId = user?.id;
        const threads = new Map();

        messages.forEach((msg) => {
            const otherUserId = msg.sender === currentUserId ? msg.receiver : msg.sender;
            if (!otherUserId || otherUserId === currentUserId) return;

            const existing = threads.get(otherUserId) ?? {
                id: otherUserId,
                receiverId: otherUserId,
                lastMessage: msg.message,
                timestamp: msg.timestamp,
                unread: msg.read === false && msg.receiver === currentUserId ? 1 : 0,
                isMe: msg.sender === currentUserId,
                isRead: msg.read,
            };

            existing.lastMessage = msg.message;
            existing.timestamp = msg.timestamp;
            existing.isRead = msg.read;
            existing.isMe = msg.sender === currentUserId;
            existing.unread = existing.unread || (msg.read === false && msg.receiver === currentUserId ? 1 : 0);
            threads.set(otherUserId, existing);
        });

        return Array.from(threads.values());
    }, [chatListQuery.data, user]);

    const filteredChats = chatThreads.filter((chat) =>
        String(chat.receiverId).includes(searchQuery.toLowerCase()) ||
        String(chat.lastMessage ?? '').toLowerCase().includes(searchQuery.toLowerCase())
    );

    const totalUnread = chatThreads.reduce((sum, chat) => sum + Number(chat.unread || 0), 0);

    return (
        <>
            <Header />
            <Spacer space="mb-20" />

            <div className="max-w-3xl mx-auto px-4 py-6">
                <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm mb-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">Messages</h1>
                            <p className="text-xs text-gray-400 mt-0.5 font-medium">
                                {totalUnread > 0
                                    ? `${totalUnread} unread conversation${totalUnread !== 1 ? 's' : ''}`
                                    : 'All caught up'}
                            </p>
                        </div>
                        <button className="p-2.5 rounded-xl bg-gray-50 text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-all border border-gray-100">
                            <FaEllipsisH className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                <div className="relative mb-4">
                    <FaSearch className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search messages..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-11 pr-4 py-3 rounded-2xl border border-gray-200 bg-white text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand transition-all shadow-sm"
                    />
                </div>

                <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
                    {chatListQuery.isLoading ? (
                        <div className="p-8 text-sm text-gray-500">Loading messages...</div>
                    ) : filteredChats.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16 text-gray-400">
                            <div className="w-16 h-16 rounded-full bg-gray-50 flex items-center justify-center mb-4">
                                <FaSearch className="w-6 h-6 text-gray-300" />
                            </div>
                            <p className="text-sm font-medium">No messages found</p>
                            <p className="text-xs mt-1">Try a different search term</p>
                        </div>
                    ) : (
                        <div className="divide-y divide-gray-50">
                            {filteredChats.map((chat) => {
                                const hasUnread = Number(chat.unread) > 0;

                                return (
                                    <button
                                        key={chat.receiverId}
                                        onClick={() => navigate(`/message/${chat.receiverId}`)}
                                        className="w-full flex items-center gap-4 p-4 text-left transition-all duration-200 group hover:bg-gray-50/80 border-l-4 border-l-transparent"
                                    >
                                        <div className="relative shrink-0">
                                            <div className="w-12 h-12 rounded-2xl object-cover bg-gray-100 flex items-center justify-center font-bold text-gray-600">
                                                #{chat.receiverId}
                                            </div>
                                        </div>

                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center justify-between mb-0.5">
                                                <h3 className={`text-sm font-semibold truncate ${hasUnread ? 'text-gray-900' : 'text-gray-700'}`}>User #{chat.receiverId}</h3>
                                                <span className={`text-[11px] shrink-0 ml-2 ${hasUnread ? 'text-brand font-semibold' : 'text-gray-400'}`}>{chat.timestamp}</span>
                                            </div>

                                            <div className="flex items-center gap-1.5">
                                                {chat.isMe && (
                                                    <span className="shrink-0 text-gray-400">
                                                        {chat.isRead ? (
                                                            <FaCheckDouble className="w-3 h-3 text-blue-400" />
                                                        ) : (
                                                            <FaCheck className="w-3 h-3" />
                                                        )}
                                                    </span>
                                                )}
                                                <p className={`text-[13px] truncate ${hasUnread ? 'text-gray-800 font-medium' : 'text-gray-500'}`}>{chat.lastMessage}</p>
                                            </div>
                                        </div>

                                        {hasUnread && (
                                            <span className="shrink-0 flex items-center justify-center min-w-5 h-5 px-1.5 rounded-full bg-brand text-white text-[11px] font-bold">
                                                {chat.unread}
                                            </span>
                                        )}
                                    </button>
                                );
                            })}
                        </div>
                    )}
                </div>

                <p className="text-center text-[11px] text-gray-400 mt-4 font-medium">
                    Messages are end-to-end encrypted
                </p>
            </div>
        </>
    );
};

export default MessageList;