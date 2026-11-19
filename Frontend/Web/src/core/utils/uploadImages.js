// Product image uploads now use the shared SkillStream-style direct upload
// client (Cloudinary / S3 / resumable multipart / local fallback).

import { uploadMediaFile as uploadFile } from "../api/mediaApi.js";
import { UPLOAD_PURPOSES } from "../constants/api.js";

/**
 * Upload one product image.
 * @returns {{key, url}|File|null} object key for direct uploads, File for fallback
 */
export const uploadMediaFileForProduct = async (file, { onProgress } = {}) =>
  uploadFile(file, UPLOAD_PURPOSES.PRODUCT_IMAGE, { onProgress });

/** Backwards-compatible name used by older components. */
export const uploadMediaFile = uploadMediaFileForProduct;

/**
 * Upload every selected file, mixing direct keys and fallback Files so the
 * existing product-image endpoints accept the result as-is.
 * @returns {{ keys: string[], urls: string[], files: File[] }}
 */
export const uploadProductImages = async (files, { onProgress } = {}) => {
  const keys = [];
  const urls = [];
  const fallbackFiles = [];
  const totalBytes = files.reduce((sum, f) => sum + f.size, 0);
  let completedBytes = 0;

  for (const file of files) {
    const result = await uploadMediaFileForProduct(file, {
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
