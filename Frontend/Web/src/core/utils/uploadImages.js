
import { uploadMediaFile as uploadFile } from "../api/mediaApi.js";
import { UPLOAD_PURPOSES } from "../constants/api.js";

export const uploadMediaFileForProduct = async (file, { onProgress } = {}) =>
  uploadFile(file, UPLOAD_PURPOSES.PRODUCT_IMAGE, { onProgress });

export const uploadMediaFile = uploadMediaFileForProduct;

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
