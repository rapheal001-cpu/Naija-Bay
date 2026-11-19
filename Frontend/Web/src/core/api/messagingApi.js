// Messaging API + TanStack cache helpers shared by the chat hooks and page.

import { axiosInstance } from "../../service/axiosInstance.js";

export const blockUserFn = async (userId) => {
    const { data } = await axiosInstance.post("/api/v1/messaging/blocks/", { user: userId });
    return data;
};

export const unblockUserFn = async (blockId) => {
    const { data } = await axiosInstance.delete(`/api/v1/messaging/blocks/${blockId}/`);
    return data;
};

export const fetchBlocksFn = async () => {
    const { data } = await axiosInstance.get("/api/v1/messaging/blocks/");
    return data;
};

export const clearConversationFn = async (conversationId) => {
    const { data } = await axiosInstance.post(`/api/v1/messaging/${conversationId}/clear/`);
    return data;
};

// ---- cache helpers -------------------------------------------------------

export const prependChatMessage = (cached, message) => {
    if (!cached) return cached;
    const results = cached.results || [];
    if (results.some((m) => m.id === message.id)) return cached;
    return {
        ...cached,
        results: [...results, message],
        count: (cached.count || results.length) + 1,
    };
};

export const upsertConversationInCache = (queryClient, conversation) => {
    queryClient.setQueriesData({ queryKey: ["conversations"] }, (cached) => {
        if (!cached) return cached;
        const list = cached.results || [];
        const exists = list.some((c) => c.id === conversation.id);
        const results = exists
            ? list.map((c) => (c.id === conversation.id ? { ...c, ...conversation } : c))
            : [conversation, ...list];
        return { ...cached, results, count: cached.count ?? results.length };
    });
};

export const updateConversationInCache = (queryClient, conversationId, updater) => {
    queryClient.setQueriesData({ queryKey: ["conversations"] }, (cached) => {
        if (!cached) return cached;
        return {
            ...cached,
            results: (cached.results || []).map((c) =>
                c.id === conversationId ? updater(c) : c
            ),
        };
    });
};

export const removeConversationFromCache = (queryClient, conversationId) => {
    queryClient.setQueriesData({ queryKey: ["conversations"] }, (cached) => {
        if (!cached) return cached;
        const results = (cached.results || []).filter((c) => c.id !== conversationId);
        return { ...cached, results, count: results.length };
    });
};

export const markMessagesReadInCache = (queryClient, conversationId) => {
    queryClient.setQueriesData({ queryKey: ["messages", conversationId] }, (cached) => {
        if (!cached) return cached;
        return {
            ...cached,
            results: (cached.results || []).map((m) =>
                m.is_mine ? { ...m, read: true } : m
            ),
        };
    });
};
