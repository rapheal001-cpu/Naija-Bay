import { useEffect, useRef, useState } from "react";

const MAX_ATTEMPTS = 6;

const socketUrl = (conversationId) => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}/ws/chat/${conversationId}/`;
};

/** Per-conversation socket: messages, typing, read receipts, block events. */
export const useConversationSocket = ({
    conversationId,
    enabled,
    onMessage,
    onTyping,
    onRead,
    onBlocked,
    onRemoved,
    socketRef,
}) => {
    const [status, setStatus] = useState("offline");
    const [error, setError] = useState("");
    const handlers = useRef({ onMessage, onTyping, onRead, onBlocked, onRemoved });
    useEffect(() => {
        handlers.current = { onMessage, onTyping, onRead, onBlocked, onRemoved };
    }, [onMessage, onTyping, onRead, onBlocked, onRemoved]);

    useEffect(() => {
        if (!conversationId || !enabled) {
            return undefined;
        }

        let stopped = false;
        let attempt = 0;
        let timer = null;
        let socket = null;

        const connect = () => {
            if (stopped) return;
            setStatus(attempt === 0 ? "connecting" : "reconnecting");
            socket = new WebSocket(socketUrl(conversationId));
            if (socketRef) socketRef.current = socket;

            socket.onopen = () => {
                attempt = 0;
                setStatus("connected");
                setError("");
            };

            socket.onerror = () => setError("Live chat connection failed.");

            socket.onmessage = (event) => {
                let frame;
                try {
                    frame = JSON.parse(event.data);
                } catch {
                    return;
                }
                switch (frame.type) {
                    case "message":
                        handlers.current.onMessage?.(frame.message);
                        break;
                    case "typing":
                        handlers.current.onTyping?.(frame);
                        break;
                    case "messages_read":
                        handlers.current.onRead?.(frame);
                        break;
                    case "conversation_blocked":
                        handlers.current.onBlocked?.();
                        break;
                    case "error":
                        setError(frame.detail || "Live chat error.");
                        break;
                    default:
                        break;
                }
            };

            socket.onclose = (event) => {
                if (stopped) return;
                if (socketRef) socketRef.current = null;
                if (event.code === 4401) {
                    setStatus("offline");
                    setError("Sign in again to continue chatting.");
                    return;
                }
                if (event.code === 4403 || event.code === 4404) {
                    setStatus("offline");
                    handlers.current.onRemoved?.(event.code);
                    setError("You no longer have access to this conversation.");
                    return;
                }
                if (attempt < MAX_ATTEMPTS) {
                    const delay = Math.min(1000 * 2 ** attempt, 30000);
                    attempt += 1;
                    setStatus("reconnecting");
                    setError("Connection lost. Reconnecting…");
                    timer = window.setTimeout(connect, delay);
                } else {
                    setStatus("offline");
                    setError("Live chat is unavailable. Reload to retry.");
                }
            };
        };

        // Defer the first connect so status updates do not happen synchronously
        // inside the effect body.
        timer = window.setTimeout(connect, 0);
        return () => {
            stopped = true;
            if (timer) window.clearTimeout(timer);
            if (socket) {
                socket.onclose = null;
                socket.close();
            }
            if (socketRef) socketRef.current = null;
        };
    }, [conversationId, enabled, socketRef]);

    return { status, error };
};
