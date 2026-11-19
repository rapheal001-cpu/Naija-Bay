import { useEffect, useRef, useState } from "react";
import {
    removeConversationFromCache,
    updateConversationInCache,
} from "../../../core/api/messagingApi.js";

const MAX_ATTEMPTS = 6;

const listSocketUrl = () => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}/ws/chat/`;
};

/** Inbox socket: live previews, unread counts, typing, clear and block events. */
export const useChatListSocket = ({ enabled, queryClient, onTyping, onBlocked }) => {
    const [status, setStatus] = useState("offline");
    const handlers = useRef({ onTyping, onBlocked });
    useEffect(() => {
        handlers.current = { onTyping, onBlocked };
    }, [onTyping, onBlocked]);

    useEffect(() => {
        if (!enabled) {
            return undefined;
        }

        let stopped = false;
        let attempt = 0;
        let timer = null;
        let socket = null;

        const handle = (frame) => {
            switch (frame.type) {
                case "message":
                    if (frame.message) {
                        updateConversationInCache(queryClient, frame.conversation_id, (conv) => ({
                            ...conv,
                            last_message: frame.message,
                            unread_count: frame.message.is_mine ? conv.unread_count : (conv.unread_count || 0) + 1,
                        }));
                    }
                    queryClient.invalidateQueries({ queryKey: ["conversations"] });
                    queryClient.invalidateQueries({ queryKey: ["unread-counts"] });
                    break;
                case "unread":
                    updateConversationInCache(queryClient, frame.conversation_id, (conv) => ({
                        ...conv,
                        unread_count: frame.unread_count,
                    }));
                    break;
                case "messages_read":
                    queryClient.invalidateQueries({ queryKey: ["conversations"] });
                    break;
                case "typing":
                    handlers.current.onTyping?.(frame);
                    break;
                case "conversation_cleared":
                case "conversation_blocked":
                    removeConversationFromCache(queryClient, frame.conversation_id);
                    if (frame.type === "conversation_blocked") handlers.current.onBlocked?.();
                    break;
                default:
                    break;
            }
        };

        const connect = () => {
            if (stopped) return;
            setStatus(attempt === 0 ? "connecting" : "reconnecting");
            socket = new WebSocket(listSocketUrl());
            socket.onopen = () => {
                attempt = 0;
                setStatus("connected");
            };
            socket.onmessage = (event) => {
                try {
                    handle(JSON.parse(event.data));
                } catch {
                    /* ignore malformed frames */
                }
            };
            socket.onclose = (event) => {
                if (stopped) return;
                if (event.code === 4401) {
                    setStatus("offline");
                    return;
                }
                if (attempt < MAX_ATTEMPTS) {
                    const delay = Math.min(1000 * 2 ** attempt, 30000);
                    attempt += 1;
                    setStatus("reconnecting");
                    timer = window.setTimeout(connect, delay);
                } else {
                    setStatus("offline");
                }
            };
        };

        timer = window.setTimeout(connect, 0);
        return () => {
            stopped = true;
            if (timer) window.clearTimeout(timer);
            if (socket) {
                socket.onclose = null;
                socket.close();
            }
        };
    }, [enabled, queryClient]);

    return { status };
};
