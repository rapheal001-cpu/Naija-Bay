import axios from "axios";
import { axiosInstance } from "../../service/axiosInstance.js";

/**
 * Direct-to-storage image upload (SkillStream pattern):
 *  1. POST /api/v1/core/media/upload-initiate {filename, content_type, size}
 *  2. mode cloudinary/s3 → bytes travel straight from the browser to the
 *     storage provider with onUploadProgress (Django never sees the bytes).
 *  3. mode local / any failure → return the File so the caller can send it
 *     through the existing multipart endpoints (fallback, never a hard fail).
 *
 * Returns an object key (string) for direct uploads, or the File itself for
 * the fallback path.
 */
export const uploadMediaFile = async (file, { onProgress } = {}) => {
    if (!file) return null;

    let init;
    try {
        const { data } = await axiosInstance.post("/api/v1/core/media/upload-initiate/", {
            filename: file.name,
            content_type: file.type,
            size: file.size,
        });
        init = data;
    } catch {
        return file; // initiate failed: server-side multipart fallback
    }

    if (init.mode === "local") {
        return file;
    }

    if (init.mode === "cloudinary") {
        const form = new FormData();
        Object.entries(init.fields).forEach(([key, value]) => form.append(key, value));
        form.append("file", file);
        try {
            const response = await axios.post(init.url, form, {
                withCredentials: false,
                onUploadProgress: (event) => {
                    if (event.total) onProgress?.(Math.round((event.loaded * 100) / event.total));
                },
            });
            if (response?.data?.error) {
                throw new Error(response.data.error.message || "Cloudinary refused the upload.");
            }
            return { key: init.key, url: response?.data?.secure_url || init.key };
        } catch (error) {
            if (error?.response?.data?.error) {
                throw new Error(error.response.data.error.message || "Cloudinary refused the upload.", { cause: error });
            }
            if (!error?.response) return file; // network hiccup: server fallback
            throw error;
        }
    }

    if (init.mode === "s3" && init.strategy === "post") {
        const form = new FormData();
        Object.entries(init.upload.fields).forEach(([key, value]) => form.append(key, value));
        form.append("file", file);
        await axios.post(init.upload.url, form, {
            withCredentials: false,
            onUploadProgress: (event) => {
                if (event.total) onProgress?.(Math.round((event.loaded * 100) / event.total));
            },
        });
        return init.key;
    }

    return file;
};

/**
 * Upload every selected file, mixing direct keys and fallback Files so the
 * existing product-image endpoints accept the result as-is.
 * @returns {{ keys: string[], files: File[] }}
 */
export const uploadProductImages = async (files, { onProgress } = {}) => {
    const keys = [];
    const urls = [];
    const fallbackFiles = [];
    const totalBytes = files.reduce((sum, f) => sum + f.size, 0);
    let completedBytes = 0;

    for (const file of files) {
        const result = await uploadMediaFile(file, {
            onProgress: (percent) => {
                const part = (file.size * percent) / 100;
                onProgress?.(Math.round(((completedBytes + part) * 100) / Math.max(totalBytes, 1)));
            },
        });
        if (result && typeof result === "object" && result.key) {
            keys.push(result.key);
            urls.push(result.url || result.key);
        } else if (typeof result === "string") {
            keys.push(result);
            urls.push(result);
        } else if (result) {
            fallbackFiles.push(result);
        }
        completedBytes += file.size;
        onProgress?.(Math.round((completedBytes * 100) / Math.max(totalBytes, 1)));
    }

    return { keys, urls, files: fallbackFiles };
};
