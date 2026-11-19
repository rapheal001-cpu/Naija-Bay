
import axios from "axios";
import { axiosInstance } from "../../service/axiosInstance.js";
import { API } from "../constants/api.js";
import {
  fingerprint,
  loadUploadSession,
  pruneUploadSessions,
  recordPart,
  removeUploadSession,
  saveUploadSession,
} from "./resumableUploads.js";

export const uploadMediaFile = async (file, purpose, { onProgress, onFallback } = {}) => {
  if (!file) return null;
  pruneUploadSessions().catch(() => {});
  const fp = fingerprint(file, purpose);
  const stored = await loadUploadSession(fp).catch(() => null);

  const initiate = (resume) =>
    axiosInstance.post(API.MEDIA.UPLOAD_INITIATE, {
      purpose,
      filename: file.name,
      content_type: file.type,
      size: file.size,
      ...(resume ? { resume: { key: resume.key, upload_id: resume.upload_id } } : {}),
    });

  let init;
  if (stored) {
    try {
      init = await initiate(stored);
    } catch {
      await removeUploadSession(fp).catch(() => {});
      init = await initiate(null);
    }
  } else {
    try {
      init = await initiate(null);
    } catch (error) {
      onFallback?.();
      if (error?.response?.status === 503 || !error?.response) return file;
      throw error;
    }
  }
  const upload = init.data;

  if (upload.mode === "local") {
    onFallback?.();
    return file;
  }

  if (upload.mode === "cloudinary") {
    const form = new FormData();
    Object.entries(upload.fields).forEach(([key, value]) => form.append(key, value));
    form.append("file", file);
    try {
      const response = await axios.post(upload.url, form, {
        withCredentials: false,
        onUploadProgress: (e) => e.total && onProgress?.(Math.round((e.loaded * 100) / e.total)),
      });
      if (response?.data?.error) {
        throw new Error(response.data.error.message || "Cloudinary refused the upload.");
      }
      return { key: upload.key, url: response?.data?.secure_url || upload.key };
    } catch (error) {
      if (error?.response?.data?.error) {
        throw new Error(error.response.data.error.message || "Cloudinary refused the upload.", { cause: error });
      }
      if (!error?.response) {
        onFallback?.();
        return file;
      }
      throw error;
    }
  }

  if (upload.mode === "s3" && upload.strategy === "post") {
    const form = new FormData();
    Object.entries(upload.upload.fields).forEach(([key, value]) => form.append(key, value));
    form.append("file", file);
    await axios.post(upload.upload.url, form, {
      withCredentials: false,
      onUploadProgress: (e) => e.total && onProgress?.(Math.round((e.loaded * 100) / e.total)),
    });
    return { key: upload.key, url: upload.key };
  }

  if (upload.mode === "s3" && upload.strategy === "multipart") {
    await saveUploadSession({
      fingerprint: fp,
      purpose,
      key: upload.key,
      upload_id: upload.upload_id,
      part_size: upload.part_size,
      fileSize: file.size,
      parts: stored?.parts || {},
    }).catch(() => {});
    return uploadS3Multipart(file, purpose, upload, { onProgress, onFallback });
  }

  onFallback?.();
  return file;
};

const uploadS3Multipart = async (file, purpose, upload, { onProgress, onFallback } = {}) => {
  const fp = fingerprint(file, purpose);
  const partSize = upload.part_size;
  const totalBytes = file.size;
  const totalParts = Math.ceil(totalBytes / partSize);
  const chunkSize = (index) => Math.min(partSize, totalBytes - index * partSize);

  let completedParts;
  try {
    const response = await axiosInstance.post(API.MEDIA.UPLOAD_PARTS, {
      key: upload.key,
      upload_id: upload.upload_id,
    });
    completedParts = new Map((response.data?.parts || []).map((p) => [p.PartNumber, p.ETag]));
  } catch {
    const session = await loadUploadSession(fp);
    completedParts = new Map(Object.entries(session?.parts || {}).map(([n, tag]) => [Number(n), tag]));
  }

  const uploadedBytes = () => {
    let done = 0;
    for (let n = 1; n <= totalParts; n += 1) {
      if (completedParts.has(n)) done += chunkSize(n - 1);
    }
    return done;
  };
  onProgress?.(Math.round((uploadedBytes() / totalBytes) * 100));

  const parts = [];
  let completedBytes = uploadedBytes();
  for (let start = 0, partNumber = 1; start < totalBytes; start += partSize, partNumber += 1) {
    const existing = completedParts.get(partNumber);
    if (existing) {
      parts.push({ PartNumber: partNumber, ETag: existing });
      continue;
    }
    const signed = await axiosInstance.post(API.MEDIA.UPLOAD_PART_URL, {
      key: upload.key,
      upload_id: upload.upload_id,
      part_number: partNumber,
    });
    const response = await axios.put(
      signed.data.url,
      file.slice(start, Math.min(start + partSize, totalBytes)),
      {
        headers: { "Content-Type": file.type },
        withCredentials: false,
        onUploadProgress: (e) => {
          const loaded = completedBytes + (e.loaded || 0);
          onProgress?.(Math.round((loaded * 100) / totalBytes));
        },
      }
    );
    const etag = response.headers.etag || response.headers.ETag;
    if (!etag) {
      await axiosInstance.post(API.MEDIA.UPLOAD_ABORT, {
        key: upload.key,
        upload_id: upload.upload_id,
      }).catch(() => {});
      await removeUploadSession(fp).catch(() => {});
      onFallback?.();
      return file;
    }
    completedParts.set(partNumber, etag);
    parts.push({ PartNumber: partNumber, ETag: etag });
    await recordPart(fp, partNumber, etag).catch(() => {});
    completedBytes += chunkSize(partNumber - 1);
    onProgress?.(Math.round((completedBytes * 100) / totalBytes));
  }

  const result = await axiosInstance.post(API.MEDIA.UPLOAD_COMPLETE, {
    key: upload.key,
    upload_id: upload.upload_id,
    parts,
  });
  await removeUploadSession(fp).catch(() => {});
  return { key: result.data.key, url: result.data.key };
};
