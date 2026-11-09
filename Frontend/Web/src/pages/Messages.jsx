import { useEffect, useMemo, useRef, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { HiOutlineChatAlt2, HiOutlinePaperAirplane, HiOutlineArrowLeft, HiOutlineInbox, HiOutlinePaperClip, HiOutlineMicrophone, HiOutlineStop, HiOutlineX } from 'react-icons/hi';
import AppLayout from '../components/AppLayout.jsx';
import { uploadProductImages } from '../core/utils/uploadImages.js';
import {
    useFetchConversations,
    useFetchConversation,
} from '../hooks/UseQuery.js';
import {
    useSendMessageMutation,
    useMarkConversationReadMutation,
} from '../hooks/UseMutation.js';
import { fetchMessagesFn } from '../service/Endpoints.js';
import { useSelector } from 'react-redux';
import { formatDate } from '../dummyData.js';

const displayName = (user) =>
    user?.full_name || user?.username || 'Unknown user';

const Messages = () => {
    const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
    const user = useSelector((state) => state.user.user);
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    const [draft, setDraft] = useState('');
    const [sendError, setSendError] = useState('');
    const [socketOpen, setSocketOpen] = useState(false);
    const [mobileThreadOpen, setMobileThreadOpen] = useState(false);
    const [pendingImages, setPendingImages] = useState([]); // {id, name, size, url(blob)}
    const [recording, setRecording] = useState(false); // UI flag; payload lives in recorderRef
    const fileInputRef = useRef(null);
    const scrollRef = useRef(null);
    const socketRef = useRef(null);
    const recorderRef = useRef(null); // {stream, recorder, chunks, startedAt}
    const queryClient = useQueryClient();

    const activeId = useMemo(() => {
        const raw = searchParams.get('conversation');
        const parsed = raw ? Number(raw) : NaN;
        return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
    }, [searchParams]);

    // ---- Auth guard (same pattern as Notifications.jsx) ----
    useEffect(() => {
        if (!isAuthenticated && !user) {
            navigate('/sign-in');
        }
    }, [isAuthenticated, user, navigate]);

    // ---- Conversations list ----
    const conversationsQuery = useFetchConversations(isAuthenticated);
    const conversations = useMemo(
        () => conversationsQuery.data?.results || [],
        [conversationsQuery.data]
    );

    // Default to the most recent conversation when none is selected.
    const effectiveId = activeId || conversations[0]?.id || null;

    const selectConversation = (id) => {
        setSearchParams({ conversation: String(id) });
        setDraft('');
        setSendError('');
        setMobileThreadOpen(true);
    };

    const closeThreadOnMobile = () => {
        setMobileThreadOpen(false);
        setSearchParams({}, { replace: true });
    };

    // ---- Conversation detail (product context + counterpart) ----
    const conversationQuery = useFetchConversation(effectiveId);
    const conversation = conversationQuery.data || null;

    // ---- Messages ----
    // Fetch the full thread in one page (newest last on the server); the
    // hook default (24) cut long conversations off at the oldest page.
    const messagesQuery = useQuery({
        queryKey: ['messages', effectiveId, 1],
        queryFn: () => fetchMessagesFn({ conversationId: effectiveId, pageSize: 100 }),
        enabled: Boolean(effectiveId),
        staleTime: 1000 * 5,
        refetchInterval: 8000,
        refetchOnWindowFocus: true,
        retry: 1,
        meta: { hookName: 'useFetchMessages' },
    });
    const messages = useMemo(() => {
        const results = messagesQuery.data?.results || [];
        // Ascending order from the API: keep newest at the bottom.
        return [...results].sort(
            (a, b) => new Date(a.created_at) - new Date(b.created_at)
        );
    }, [messagesQuery.data]);

    // Socket readiness is derived (socket open AND a thread is selected
    // AND the user is signed in) — never mirrored through effect state, so
    // React never needs to "reset" it when auth or the thread changes.
    const socketReady = Boolean(effectiveId && isAuthenticated && socketOpen);

    // ---- Live chat socket (WebSocket; REST polling remains the fallback) ----
    useEffect(() => {
        if (!effectiveId || !isAuthenticated) {
            return undefined;
        }
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const socket = new WebSocket(`${protocol}//${window.location.host}/ws/chat/${effectiveId}/`);
        socketRef.current = socket;

        socket.onopen = () => setSocketOpen(true);
        socket.onclose = () => setSocketOpen(false);
        socket.onerror = () => {
            setSocketOpen(false);
        };
        socket.onmessage = (event) => {
            let frame;
            try {
                frame = JSON.parse(event.data);
            } catch {
                return;
            }
            if (frame.type === 'message' && frame.message) {
                const incoming = frame.message;
                queryClient.setQueryData(['messages', effectiveId, 1], (cached) => {
                    if (!cached) return cached;
                    const results = cached.results || [];
                    if (results.some((m) => m.id === incoming.id)) return cached;
                    return { ...cached, results: [...results, incoming], count: (cached.count || results.length) + 1 };
                });
                queryClient.invalidateQueries({ queryKey: ['conversations'] });
                queryClient.invalidateQueries({ queryKey: ['conversation', effectiveId] });
                queryClient.invalidateQueries({ queryKey: ['unread-counts'] });
            }
        };

        return () => {
            socket.onclose = null;
            socket.close();
            socketRef.current = null;
            setSocketOpen(false);
        };
    }, [effectiveId, isAuthenticated, queryClient]);

    // ---- Mark the open thread as read ----
    const markRead = useMarkConversationReadMutation(effectiveId);
    useEffect(() => {
        if (effectiveId) markRead.mutate();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [effectiveId]);

    // ---- Auto-scroll to the newest message ----
    useEffect(() => {
        const el = scrollRef.current;
        if (el) el.scrollTop = el.scrollHeight;
    }, [messages, effectiveId]);

    // ---- Send (WebSocket first; REST fallback when offline) ----
    const sendMessage = useSendMessageMutation(effectiveId);

    const addPendingImages = (files) => {
        const accepted = Array.from(files)
            .filter((f) => ['image/jpeg', 'image/jpg', 'image/png'].includes(f.type) && f.size <= 2 * 1024 * 1024)
            .slice(0, 10 - pendingImages.length);
        if (!accepted.length) {
            setSendError('Images must be JPG/PNG up to 2 MB (max 10 per message).');
            return;
        }
        setPendingImages((prev) => [
            ...prev,
            ...accepted.map((file) => ({ id: `${Date.now()}-${file.name}`, file, url: URL.createObjectURL(file) })),
        ]);
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream);
            const chunks = [];
            recorder.ondataavailable = (event) => chunks.push(event.data);
            recorder.start();
            recorderRef.current = { stream, recorder, chunks, startedAt: Date.now() };
            setRecording(true);
        } catch {
            setSendError('Microphone is unavailable. Voice notes are not supported on this device.');
        }
    };

    const stopRecording = (keep = true) => {
        const session = recorderRef.current;
        if (!session) return;
        const { stream, recorder, chunks, startedAt } = session;
        recorderRef.current = null;
        setRecording(false);
        stream.getTracks().forEach((track) => track.stop());
        recorder.onstop = () => {};
        recorder.stop();
        if (!keep || chunks.length === 0) return;
        const blob = new Blob(chunks, { type: MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm' });
        const durationMs = Date.now() - startedAt;
        // Treat the recording as one pending attachment slot (audio).
        setPendingImages((prev) => [
            ...prev.slice(0, 9),
            { id: `voice-${Date.now()}`, file: new File([blob], `voice-note.webm`, { type: blob.type }), url: URL.createObjectURL(blob), durationMs },
        ]);
    };

    const handleSend = async (event) => {
        event.preventDefault();
        const body = draft.trim();

        // Upload attachments first (direct-to-storage with progress).
        let attachmentUrls = [];
        if (pendingImages.length) {
            try {
                const { urls, files } = await uploadProductImages(pendingImages.map((p) => p.file));
                attachmentUrls = urls;
                if (files.length) {
                    // Fallback files can't be sent generically: attach their names as a notice.
                    attachmentUrls = attachmentUrls.concat(files.map((f) => f.name));
                }
            } catch (err) {
                setSendError(err?.response?.data?.detail || 'Could not upload attachments. Try again.');
                return;
            }
        }

        const text = body;
        const attachmentType = attachmentUrls.length ? (pendingImages.some((p) => p.file.type.startsWith('audio')) ? 'audio' : 'image') : '';
        const duration = pendingImages.find((p) => p.durationMs)?.durationMs || 0;

        if (!text && !attachmentType) return;
        setSendError('');

        const socket = socketRef.current;
        if (socket && socketReady && socket.readyState === WebSocket.OPEN) {
            try {
                socket.send(JSON.stringify({
                    type: 'message',
                    body: text,
                    attachment_type: attachmentType,
                    attachment_url: attachmentUrls[0] || '',
                    duration_ms: duration,
                }));
                setDraft('');
                setPendingImages([]);
                return;
            } catch {
                // fall through to the REST mutation below
            }
        }

        sendMessage.mutate(
            {
                conversationId: effectiveId,
                body: text,
                attachment_type: attachmentType,
                attachment_url: attachmentUrls[0] || '',
                duration_ms: duration,
            },
            {
                onSuccess: () => { setDraft(''); setPendingImages([]); },
                onError: (err) => {
                    const data = err?.response?.data;
                    setSendError(
                        data?.detail ||
                        data?.body?.[0] ||
                        data?.non_field_errors?.[0] ||
                        'Could not send the message. Please try again.'
                    );
                },
            }
        );
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSend(event);
        }
    };

    const counterpart = conversation?.counterpart;
    const product = conversation?.product;
    const unreadTotal = useMemo(
        () => conversations.reduce((sum, c) => sum + (c.unread_count || 0), 0),
        [conversations]
    );

    return (
        <AppLayout withSidebar={false}>
            <div className="min-h-screen pb-16">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    {/* Page header */}
                    <div className="flex items-center gap-3 mb-6">
                        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-brand/10 text-brand">
                            <HiOutlineChatAlt2 size={20} />
                        </div>
                        <div>
                            <h1 className="text-2xl font-black text-gray-900 tracking-tight">Messages</h1>
                            <p className="text-sm text-gray-500 mt-0.5">
                                {unreadTotal > 0
                                    ? `You have ${unreadTotal} unread message${unreadTotal !== 1 ? 's' : ''}`
                                    : 'Chat with buyers and sellers about your listings'}
                            </p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                        {/* ---- Conversation list ---- */}
                        <aside className={`${mobileThreadOpen ? 'hidden lg:block' : 'block'} lg:col-span-4 xl:col-span-3 bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden`}>
                            <div className="px-4 py-3 border-b border-gray-100">
                                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                                    Conversations ({conversationsQuery.data?.count ?? conversations.length})
                                </p>
                            </div>

                            {conversationsQuery.isLoading ? (
                                <div className="p-6 space-y-4">
                                    {[0, 1, 2].map((i) => (
                                        <div key={i} className="flex gap-3 animate-pulse">
                                            <div className="w-11 h-11 rounded-full bg-gray-100 shrink-0" />
                                            <div className="flex-1 space-y-2">
                                                <div className="h-3.5 bg-gray-100 rounded w-2/3" />
                                                <div className="h-3 bg-gray-100 rounded w-full" />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : conversations.length === 0 ? (
                                <div className="p-8 text-center">
                                    <div className="w-16 h-16 rounded-2xl bg-gray-50 flex items-center justify-center mx-auto mb-4">
                                        <HiOutlineInbox size={28} className="text-gray-300" />
                                    </div>
                                    <h2 className="text-sm font-bold text-gray-900">No conversations yet</h2>
                                    <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                                        When a buyer messages you about a listing — or you message a seller — the chat will appear here.
                                    </p>
                                    <Link
                                        to="/products"
                                        className="mt-4 inline-flex items-center gap-1.5 text-xs font-bold text-brand hover:underline"
                                    >
                                        Browse listings
                                    </Link>
                                </div>
                            ) : (
                                <ul className="divide-y divide-gray-50 max-h-[32rem] overflow-y-auto">
                                    {conversations.map((conv) => {
                                        const isActive = conv.id === effectiveId;
                                        return (
                                            <li key={conv.id}>
                                                <button
                                                    type="button"
                                                    onClick={() => selectConversation(conv.id)}
                                                    className={`w-full text-left flex gap-3 px-4 py-3.5 transition-colors ${isActive ? 'bg-brand/5' : 'hover:bg-gray-50'}`}
                                                >
                                                    <img
                                                        src={conv.counterpart?.avatar || null}
                                                        alt={displayName(conv.counterpart)}
                                                        className="w-11 h-11 rounded-full object-cover bg-gray-100 shrink-0"
                                                    />
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-center justify-between gap-2">
                                                            <p className={`text-sm truncate ${conv.unread_count > 0 ? 'font-black text-gray-900' : 'font-bold text-gray-800'}`}>
                                                                {displayName(conv.counterpart)}
                                                            </p>
                                                            <span className="text-[11px] text-gray-400 shrink-0">
                                                                {conv.last_message?.created_at
                                                                    ? formatDate(conv.last_message.created_at)
                                                                    : formatDate(conv.updated_at)}
                                                            </span>
                                                        </div>
                                                        {conv.product && (
                                                            <p className="text-[11px] text-brand font-semibold truncate mt-0.5">
                                                                {conv.product.product_name}
                                                            </p>
                                                        )}
                                                        <div className="flex items-center gap-2 mt-0.5 min-w-0">
                                                            {conv.last_message?.attachment_type === 'image' && conv.last_message.attachment_url && (
                                                                <img
                                                                    src={conv.last_message.attachment_url}
                                                                    alt=""
                                                                    className="h-7 w-7 rounded-md object-cover bg-gray-100 shrink-0"
                                                                />
                                                            )}
                                                            <p className={`text-xs truncate ${conv.unread_count > 0 ? 'text-gray-800 font-semibold' : 'text-gray-400'}`}>
                                                                {conv.last_message
                                                                    ? (conv.last_message.attachment_type === 'image'
                                                                        ? `${conv.last_message.is_mine ? 'You sent' : 'Photo'}`
                                                                        : conv.last_message.attachment_type === 'audio'
                                                                            ? `${conv.last_message.is_mine ? 'You sent' : 'Voice note'}`
                                                                            : `${conv.last_message.is_mine ? 'You: ' : ''}${conv.last_message.body}`)
                                                                    : 'Say hello...'}
                                                            </p>
                                                        </div>
                                                            {conv.unread_count > 0 && (
                                                                <span className="inline-flex items-center justify-center min-w-5 h-5 px-1.5 rounded-full bg-brand text-white text-[10px] font-bold shrink-0">
                                                                    {conv.unread_count}
                                                                </span>
                                                            )}
                                                    </div>
                                                </button>
                                            </li>
                                        );
                                    })}
                                </ul>
                            )}
                        </aside>

                        {/* ---- Thread ---- */}
                        <section className={`${mobileThreadOpen ? 'block' : 'hidden lg:block'} lg:col-span-8 xl:col-span-9 bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden flex flex-col h-[36rem] lg:h-[38rem]`}>
                            {!effectiveId ? (
                                <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
                                    <div className="w-16 h-16 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
                                        <HiOutlineChatAlt2 size={28} className="text-gray-300" />
                                    </div>
                                    <h2 className="text-sm font-bold text-gray-900">Select a conversation</h2>
                                    <p className="text-xs text-gray-500 mt-1.5 max-w-xs leading-relaxed">
                                        Pick a chat on the left to read and reply. Messages refresh automatically.
                                    </p>
                                </div>
                            ) : (
                                <>
                                    {/* Thread header: counterpart + product context */}
                                    <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-100 shrink-0">
                                        <button
                                            type="button"
                                            onClick={closeThreadOnMobile}
                                            aria-label="Back to conversations"
                                            className="lg:hidden flex items-center justify-center w-8 h-8 rounded-full text-gray-400 hover:bg-gray-100 transition-colors"
                                        >
                                            <HiOutlineArrowLeft size={16} />
                                        </button>
                                        <img
                                            src={counterpart?.avatar || null}
                                            alt={displayName(counterpart)}
                                            className="w-10 h-10 rounded-full object-cover bg-gray-100 shrink-0"
                                        />
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-bold text-gray-900 truncate">
                                                {displayName(counterpart) || 'Conversation'}
                                            </p>
                                            <p className="text-[11px] text-gray-400 flex items-center gap-1">
                                                <span
                                                    className={`inline-block h-1.5 w-1.5 rounded-full ${socketReady ? 'bg-emerald-500' : 'bg-gray-300'}`}
                                                    aria-hidden="true"
                                                />
                                                {socketReady ? 'Live' : 'Refreshing automatically'}
                                            </p>
                                            {counterpart?.store && (
                                                <p className="text-[11px] text-gray-400 truncate">
                                                    Store: {counterpart.store.name}
                                                    {counterpart.store.verified ? ' • Verified' : ''}
                                                </p>
                                            )}
                                        </div>
                                        {product && (
                                            <Link
                                                to={`/product/detail/${encodeURIComponent(product.product_slug)}`}
                                                className="flex items-center gap-2.5 max-w-56 sm:max-w-72 bg-gray-50 hover:bg-gray-100 border border-gray-100 rounded-xl px-2.5 py-1.5 transition-colors"
                                            >
                                                <img
                                                    src={product.image || null}
                                                    alt={product.product_name}
                                                    className="w-9 h-9 rounded-lg object-cover bg-gray-100 shrink-0"
                                                />
                                                <div className="min-w-0">
                                                    <p className="text-xs font-bold text-gray-800 truncate">{product.product_name}</p>
                                                    <p className="text-xs text-brand font-bold">₦{Number(product.price).toLocaleString()}</p>
                                                </div>
                                            </Link>
                                        )}
                                    </div>

                                    {/* Messages */}
                                    <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 bg-gray-50/50 space-y-3">
                                        {messagesQuery.isLoading ? (
                                            <div className="space-y-3">
                                                {[0, 1, 2].map((i) => (
                                                    <div key={i} className={`flex ${i % 2 ? 'justify-end' : 'justify-start'}`}>
                                                        <div className="h-9 w-44 bg-gray-100 rounded-2xl animate-pulse" />
                                                    </div>
                                                ))}
                                            </div>
                                        ) : messages.length === 0 ? (
                                            <div className="h-full flex flex-col items-center justify-center text-center py-16">
                                                <p className="text-sm font-bold text-gray-700">Say hello 👋</p>
                                                <p className="text-xs text-gray-400 mt-1">No messages yet — send the first one below.</p>
                                            </div>
                                        ) : (
                                            messages.map((message) => (
                                                <div key={message.id} className={`flex ${message.is_mine ? 'justify-end' : 'justify-start'}`}>
                                                    <div className={`max-w-[80%] sm:max-w-[65%] px-2 py-2 ${message.is_mine ? 'bg-brand text-white rounded-2xl rounded-br-md' : 'bg-white text-gray-800 border border-gray-100 rounded-2xl rounded-bl-md shadow-sm'}`}>
                                                        {message.attachment_type === 'image' && message.attachment_url && (
                                                            <img
                                                                src={message.attachment_url}
                                                                alt="Attachment"
                                                                className="mb-1.5 rounded-lg max-h-52 w-full object-cover"
                                                                loading="lazy"
                                                            />
                                                        )}
                                                        {message.attachment_type === 'audio' && message.attachment_url && (
                                                            <audio
                                                                controls
                                                                preload="metadata"
                                                                className="mb-1.5 h-9 w-44"
                                                                src={message.attachment_url}
                                                            />
                                                        )}
                                                        {message.body && <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{message.body}</p>}
                                                        <p className={`text-[10px] mt-1 text-right ${message.is_mine ? 'text-white/60' : 'text-gray-400'}`}>
                                                            {formatDate(message.created_at)}
                                                            {message.is_mine && (message.read ? ' • Read' : ' • Sent')}
                                                        </p>
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>

                                    {/* Composer */}
                                    <form onSubmit={handleSend} className="border-t border-gray-100 px-4 py-3 shrink-0 bg-white">
                                        {sendError && (
                                            <p className="text-xs font-semibold text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-2">
                                                {sendError}
                                            </p>
                                        )}
                                        {pendingImages.length > 0 && (
                                            <div className="flex gap-2 overflow-x-auto pb-2 mb-1">
                                                {pendingImages.map((p) => (
                                                    <div key={p.id} className="relative w-16 h-16 rounded-xl overflow-hidden border border-gray-100 bg-gray-50 shrink-0">
                                                        {p.file.type.startsWith('image/')
                                                            ? <img src={p.url} alt="" className="h-full w-full object-cover" />
                                                            : <span className="flex h-full w-full items-center justify-center text-gray-400"><HiOutlineMicrophone size={20} /></span>}
                                                        <button
                                                            type="button"
                                                            aria-label="Remove attachment"
                                                            onClick={() => setPendingImages((prev) => prev.filter((x) => x.id !== p.id))}
                                                            className="absolute top-0.5 right-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-black/60 text-white"
                                                        >
                                                            <HiOutlineX size={11} />
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                        <div className="flex items-end gap-2">
                                            <input
                                                ref={fileInputRef}
                                                type="file"
                                                accept="image/jpeg,image/jpg,image/png"
                                                multiple
                                                hidden
                                                aria-hidden="true"
                                                tabIndex={-1}
                                                onChange={(e) => { addPendingImages(e.target.files || []); e.target.value = ''; }}
                                            />
                                            <button
                                                type="button"
                                                aria-label="Attach image"
                                                onClick={() => fileInputRef.current?.click()}
                                                className="flex items-center justify-center w-11 h-11 rounded-xl text-gray-400 hover:text-brand hover:bg-brand/5 transition-colors shrink-0"
                                            >
                                                <HiOutlinePaperClip size={20} />
                                            </button>
                                            <button
                                                type="button"
                                                aria-label={recording ? 'Stop recording' : 'Record voice note'}
                                                onClick={() => (recording ? stopRecording(true) : startRecording())}
                                                className={`flex items-center justify-center w-11 h-11 rounded-xl transition-colors shrink-0 ${recording ? 'text-red-500 bg-red-50 animate-pulse' : 'text-gray-400 hover:text-brand hover:bg-brand/5'}`}
                                            >
                                                {recording ? <HiOutlineStop size={20} /> : <HiOutlineMicrophone size={20} />}
                                            </button>
                                            <textarea
                                                value={draft}
                                                onChange={(event) => setDraft(event.target.value)}
                                                onKeyDown={handleKeyDown}
                                                rows={2}
                                                maxLength={4000}
                                                placeholder="Type a message... (Enter to send, Shift+Enter for a new line)"
                                                className="flex-1 rounded-xl border border-gray-200 px-3.5 py-2.5 text-sm text-gray-800 resize-none focus:border-brand focus:outline-none"
                                            />
                                            <button
                                                type="submit"
                                                disabled={(!draft.trim() && pendingImages.length === 0) || sendMessage.isPending}
                                                aria-label="Send message"
                                                className="flex items-center justify-center w-11 h-11 rounded-xl bg-brand text-white hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity shrink-0"
                                            >
                                                <HiOutlinePaperAirplane size={18} className={sendMessage.isPending ? 'animate-pulse' : ''} />
                                            </button>
                                        </div>
                                        <p className="text-[11px] text-gray-400 mt-2">
                                            Keep the conversation on Naija-Bay so we can help if something goes wrong.
                                        </p>
                                    </form>
                                </>
                            )}
                        </section>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
};

export default Messages;
