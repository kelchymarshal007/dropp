'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faXmark, faPlay, faComment } from '@fortawesome/free-solid-svg-icons';
import { apiFetch } from '@/lib/api';

export function BookmarksModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [data, setData] = useState<{posts: any[], comments: any[]}>({ posts: [], comments: [] });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'posts' | 'comments'>('posts');

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      apiFetch('/feed/bookmarks').then(res => {
        setData(res);
        setLoading(false);
      }).catch(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4" onClick={onClose}>
      <div className="w-full max-w-md bg-surface border border-border rounded-3xl h-[80vh] flex flex-col" onClick={e => e.stopPropagation()}>
        
        <div className="flex justify-between items-center p-6 pb-4 border-b border-border">
          <h2 className="text-xl font-bold text-white">Saved Items</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white"><FontAwesomeIcon icon={faXmark} className="w-5 h-5" /></button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border">
          <button onClick={() => setActiveTab('posts')} className={`flex-1 py-3 text-sm font-semibold transition-colors ${activeTab === 'posts' ? 'text-dropp-orange border-b-2 border-dropp-orange' : 'text-gray-400 hover:text-white'}`}>Posts</button>
          <button onClick={() => setActiveTab('comments')} className={`flex-1 py-3 text-sm font-semibold transition-colors ${activeTab === 'comments' ? 'text-dropp-orange border-b-2 border-dropp-orange' : 'text-gray-400 hover:text-white'}`}>Comments</button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <p className="text-center text-gray-500 mt-10">Loading bookmarks...</p>
          ) : activeTab === 'posts' ? (
            data.posts.length === 0 ? <p className="text-center text-gray-500 mt-10">No saved posts.</p> : (
              <div className="grid grid-cols-3 gap-1">
                {data.posts.map(post => (
                  <Link href={`/reels?start=${post.id}`} key={post.id} onClick={onClose} className="relative aspect-[9/16] bg-black">
                    {post.media_type === 'video' ? (
                      <video src={post.media_urls[0]} className="w-full h-full object-cover opacity-80" />
                    ) : (
                      <img src={post.media_urls[0]} className="w-full h-full object-cover opacity-80" />
                    )}
                    <div className="absolute bottom-1 left-1 text-white text-xs"><FontAwesomeIcon icon={faPlay} /> </div>
                  </Link>
                ))}
              </div>
            )
          ) : (
            data.comments.length === 0 ? <p className="text-center text-gray-500 mt-10">No saved comments.</p> : (
              <div className="space-y-3">
                {data.comments.map(comment => (
                  <Link href={`/reels?start=${comment.post_id}`} key={comment.id} onClick={onClose} className="block bg-black border border-border rounded-xl p-3 hover:border-gray-600 transition">
                    <p className="text-white text-sm mb-2 line-clamp-3">{comment.body}</p>
                    <div className="flex items-center gap-1 text-xs text-dropp-orange">
                      <FontAwesomeIcon icon={faComment} /> View in Reel
                    </div>
                  </Link>
                ))}
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}
