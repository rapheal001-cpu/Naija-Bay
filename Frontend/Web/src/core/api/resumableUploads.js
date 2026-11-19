// S3 MULTIPART RESUMABLE UPLOADS (IndexedDB — small session records, never bytes).
// Ported from SkillStream: a session is saved after initiate and after every
// part, so a retry with the same file resumes instead of starting over.

const DB_NAME = "naijabay-uploads";
const STORE = "sessions";
const VERSION = 1;

const openDb = () =>
  new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, VERSION);
    request.onupgradeneeded = () => {
      if (!request.result.objectStoreNames.contains(STORE)) {
        request.result.createObjectStore(STORE, { keyPath: "fingerprint" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
    request.onblocked = () => reject(new Error("Upload session database is blocked."));
  });

const withStore = async (mode, action) => {
  const db = await openDb();
  try {
    return await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, mode);
      const store = tx.objectStore(STORE);
      const request = action(store);
      tx.oncomplete = () => resolve(request ? request.result : undefined);
      tx.onerror = () => reject(tx.error);
      tx.onabort = () => reject(tx.error || new Error("Upload session transaction aborted."));
    });
  } finally {
    db.close();
  }
};

export const fingerprint = (file, purpose) =>
  [purpose, file?.name || "", file?.size || 0, file?.lastModified || 0].join("::");

export const loadUploadSession = (fp) => withStore("readonly", (store) => store.get(fp));

export const saveUploadSession = (session) =>
  withStore("readwrite", (store) => store.put({ ...session, updatedAt: Date.now() }));

export const recordPart = async (fp, partNumber, etag) => {
  const session = await loadUploadSession(fp);
  if (!session) return;
  await saveUploadSession({ ...session, parts: { ...(session.parts || {}), [partNumber]: etag } });
};

export const removeUploadSession = (fp) => withStore("readwrite", (store) => store.delete(fp));

export const loadAllUploadSessions = async () =>
  (await withStore("readonly", (store) => store.getAll())) || [];

export const pruneUploadSessions = async (maxAgeMs = 7 * 24 * 60 * 60 * 1000) => {
  const sessions = await loadAllUploadSessions();
  const cutoff = Date.now() - maxAgeMs;
  await Promise.all(
    sessions
      .filter((session) => (session.updatedAt || 0) < cutoff)
      .map((session) => removeUploadSession(session.fingerprint))
  );
};
