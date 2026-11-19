import { useState } from 'react';
import { useVideos, useUploadVideo } from '../../hooks/useJiji.js';
import { uploadMediaFile } from '../../core/api/mediaApi.js';
import { UPLOAD_PURPOSES } from '../../core/constants/api.js';

const VideoUploader = ({ slug }) => {
    const [file, setFile] = useState(null);
    const [title, setTitle] = useState('');
    const { data } = useVideos(slug);
    const upload = useUploadVideo();

    const videos = data?.results || (Array.isArray(data) ? data : []);

    return (
        <section className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="text-base font-black text-slate-800">Ad video</h2>
            <p className="mt-1 text-xs text-slate-400">Add a short video to make your ad stand out.</p>

            {videos.length > 0 && (
                <ul className="mt-3 space-y-2">
                    {videos.map((v) => (
                        <li key={v.id}>
                            <video controls src={v.video} className="w-full rounded-lg bg-slate-100" />
                            {v.title && <p className="mt-1 text-xs text-slate-500">{v.title}</p>}
                        </li>
                    ))}
                </ul>
            )}

            <form
                onSubmit={async (e) => {
                    e.preventDefault();
                    if (!file) return;
                    const result = await uploadMediaFile(file, UPLOAD_PURPOSES.AD_VIDEO);
                    const fd = new FormData();
                    fd.append(result?.key ? 'video_key' : 'video', result?.key || file);
                    fd.append('title', title);
                    upload.mutate({ slug, formData: fd }, { onSuccess: () => { setFile(null); setTitle(''); } });
                }}
                className="mt-4 space-y-2"
            >
                <input type="file" accept="video/*" required onChange={(e) => setFile(e.target.files[0])} className="w-full text-xs" />
                <input
                    type="text"
                    placeholder="Video title (optional)"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                />
                <button
                    type="submit"
                    disabled={upload.isPending || !file}
                    className="rounded-lg bg-brand px-4 py-2 text-xs font-bold text-white hover:bg-brand-hover disabled:opacity-50"
                >
                    {upload.isPending ? 'Uploading…' : 'Upload video'}
                </button>
            </form>
        </section>
    );
};

export default VideoUploader;
