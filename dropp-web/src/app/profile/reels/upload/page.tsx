'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faCloudUploadAlt, faFileVideo, faImages } from '@fortawesome/free-solid-svg-icons';

export default function UploadReelPage() {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [caption, setCaption] = useState('');
  const [price, setPrice] = useState('');
  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isImagePreview, setIsImagePreview] = useState(false);
  const [isCarousel, setIsCarousel] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (fileList && fileList.length > 0) {
      const selected: File[] = Array.from(fileList);
      setFiles(selected);
      
      const firstIsImage = selected[0].type.startsWith('image/');
      setIsImagePreview(firstIsImage);
      
      const allImages = selected.every((f) => f.type.startsWith('image/'));
      setIsCarousel(allImages && selected.length > 1);

      try {
        const url = URL.createObjectURL(selected[0]);
        setPreviewUrl(url);
      } catch (err) {
        console.error('Failed to create preview URL', err);
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (files.length === 0) return alert('Please select at least one file.');
    
    setLoading(true);
    const token = localStorage.getItem('dropp_token');
    
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));
    formData.append('caption', caption || 'Check out this item!');
    formData.append('price_minor', ((parseFloat(price) || 0) * 100).toString());
    formData.append('currency', 'USD');
    if (category) formData.append('category', category);
    if (subcategory) formData.append('subcategory', subcategory);

    try {
      const res = await fetch('/api/v1/posts/upload', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token },
        body: formData,
      });
      
      const contentType = res.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Upload failed');
      } else {
        const text = await res.text();
        if (!res.ok) throw new Error(text || 'Server error: ' + res.status);
      }
      
      alert('Posted successfully!');
      router.push('/profile/reels');
    } catch (err: any) {
      console.error('Upload error:', err);
      alert('Failed to post: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="bg-black min-h-screen text-white flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-border">
        <Link href="/profile" className="text-white">
          <FontAwesomeIcon icon={faArrowLeft} className="w-5 h-5" />
        </Link>
        <h1 className="text-lg font-bold">New Post</h1>
        <button onClick={handleUpload} disabled={files.length === 0 || loading} className="text-dropp-orange font-bold text-sm disabled:opacity-50">
          {loading ? 'Posting...' : 'Post'}
        </button>
      </div>

      <div className="flex-1 p-4 pb-32 space-y-6 max-w-md mx-auto w-full overflow-y-auto">
        <div className="relative aspect-[9/16] bg-surface rounded-2xl overflow-hidden border border-border flex flex-col items-center justify-center text-center">
          <input 
            type="file" 
            accept="video/mp4,video/quicktime,image/*"
            multiple
            onChange={handleFileChange}
            className={'absolute inset-0 w-full h-full cursor-pointer z-20 opacity-0 ' + (previewUrl ? 'hidden' : '')}
          />

          {previewUrl ? (
            <>
              {isImagePreview ? (
                <img src={previewUrl} className="absolute inset-0 w-full h-full object-cover z-10" alt="Preview" />
              ) : (
                <video src={previewUrl} className="absolute inset-0 w-full h-full object-cover z-10" controls autoPlay muted loop playsInline />
              )}
              <div className="absolute bottom-4 left-4 right-4 z-30 flex justify-center">
                <label className="bg-black/70 backdrop-blur-md text-white text-xs px-4 py-2 rounded-full cursor-pointer border border-white/20 hover:bg-black/90 transition">
                  Change Media
                  <input type="file" accept="video/mp4,video/quicktime,image/*" multiple onChange={handleFileChange} className="hidden" />
                </label>
              </div>
            </>
          ) : (
            <div className="z-10 flex flex-col items-center pointer-events-none">
              <FontAwesomeIcon icon={faCloudUploadAlt} className="w-12 h-12 text-gray-500 mb-4" />
              <p className="text-white font-semibold">Tap to select media</p>
              <p className="text-gray-500 text-xs mt-1">Video or multiple images.</p>
            </div>
          )}
        </div>

        {files.length > 0 && (
          <div className="flex items-center gap-2 text-sm text-green-400 bg-green-500/10 p-3 rounded-xl border border-green-500/20">
            <FontAwesomeIcon icon={isCarousel ? faImages : faFileVideo} />
            <span className="truncate">
              {isCarousel ? files.length + ' images selected' : files[0].name} 
              {' '}({(files.reduce((acc, f) => acc + f.size, 0) / 1024 / 1024).toFixed(2)} MB)
            </span>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Caption</label>
            <input type="text" placeholder="Describe your item..." value={caption} onChange={(e) => setCaption(e.target.value)} className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white" />
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Price (USD)</label>
            <input type="number" placeholder="0.00" value={price} onChange={(e) => setPrice(e.target.value)} className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white" />
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Category</label>
            <select value={category} onChange={(e) => setCategory(e.target.value)} className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white appearance-none">
              <option value="">Select Category</option>
              <option value="Shoes">Shoes</option>
              <option value="Fashion">Fashion & Apparel</option>
              <option value="Electronics">Electronics</option>
              <option value="Furniture">Furniture</option>
              <option value="Beauty">Beauty & Personal Care</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-400 mb-1 block">Subcategory (Optional)</label>
            <input type="text" placeholder="e.g. Sneakers, Sofa, TV..." value={subcategory} onChange={(e) => setSubcategory(e.target.value)} className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-white focus:outline-none focus:border-white" />
          </div>
        </div>
      </div>
    </main>
  );
}
