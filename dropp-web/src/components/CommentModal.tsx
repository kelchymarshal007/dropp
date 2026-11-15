'use client';
import { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaperPlane, faXmark, faHeart, faReply, faImage, faArrowLeft, faBookmark } from '@fortawesome/free-solid-svg-icons';
import { apiFetch } from '@/lib/api';

export function CommentModal({ isOpen, onClose, postId, commentCount, onCommentAdded }: any) {
  const [comments, setComments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeThread, setActiveThread] = useState<string | null>(null);
  const [fullScreenImage, setFullScreenImage] = useState<string | null>(null);
  
  const [comment, setComment] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [replyTo, setReplyTo] = useState<{ id: string, handle: string } | null>(null);
  
  // Local count to instantly update the header without waiting for parent
  const [localCount, setLocalCount] = useState(commentCount);

  useEffect(() => {
    setLocalCount(commentCount);
  }, [commentCount]);

  const fetchComments = () => {
    if (isOpen && postId) {
      setLoading(true);
      apiFetch(`/feed/${postId}/comments`)
        .then(data => { setComments(data); setLoading(false); })
        .catch(() => setLoading(false));
    }
  };

  useEffect(() => { fetchComments(); }, [isOpen, postId]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comment.trim() && files.length === 0) return;
    
    const token = localStorage.getItem('dropp_token');
    if (!token) return;

    const bodyToSend = comment;
    const replyId = replyTo?.id || null;
    setComment('');
    setFiles([]);
    setReplyTo(null);
    setLocalCount(prev => prev + 1); // Optimistic update
    
    try {
      const formData = new FormData();
      formData.append('body', bodyToSend || ' ');
      if (replyId) formData.append('parent_id', replyId);
      files.forEach(f => formData.append('files', f));

      const data = await apiFetch(`/feed/${postId}/comment`, {
        method: 'POST',
        body: formData,
      });
      
      setLocalCount(data.comments);
      if (onCommentAdded) onCommentAdded(data.comments);
      fetchComments(); 
    } catch (err) {
      setLocalCount(prev => prev - 1); // Revert on fail
      console.error(err);
    }
  };

  const toggleCommentLike = async (commentId: string, isLiked: boolean) => {
    setComments(prev => prev.map(c => c.id === commentId ? { ...c, is_liked: !isLiked, like_count: isLiked ? c.like_count - 1 : c.like_count + 1 } : c));
    try {
      const data = await apiFetch(`/feed/comments/${commentId}/like`, { method: 'POST' });
      setComments(prev => prev.map(c => c.id === commentId ? { ...c, like_count: data.likes, is_liked: data.status === 'liked' } : c));
    } catch (err) { console.error(err); }
  };

  const getReplies = (parentId: string) => comments.filter(c => c.parent_id === parentId);
  const getComment = (id: string) => comments.find(c => c.id === id);
  const isVideoUrl = (url: string) => url.endsWith('.mp4') || url.endsWith('.mov') || url.endsWith('.webm');

  const CommentRow = ({ c, depth = 0 }: { c: any, depth?: number }) => {
    const replies = getReplies(c.id);
    let replyContext = null;
    if (c.parent_id) {
      const parent = getComment(c.parent_id);
      if (parent) replyContext = <span className="text-gray-500 text-[10px] ml-1">replying to {parent.handle}</span>;
    }

    return (
      <div className={`flex gap-3 mt-4 ${depth > 0 ? 'ml-4 border-l border-border pl-3' : ''}`}>
        <div className="w-8 h-8 rounded-full bg-gray-700 flex-shrink-0 flex items-center justify-center text-xs font-bold text-white">
          {c.handle.charAt(1).toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 mb-1 flex-wrap">
            <span className="text-gray-300 text-xs font-semibold">{c.handle}</span>
            {replyContext}
          </div>
          <p className="text-white text-sm break-words">{c.body}</p>
          
          {c.media_urls && c.media_urls.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {c.media_urls.map((url: string) => (
                <div key={url} onClick={() => setFullScreenImage(url)} className="cursor-pointer overflow-hidden rounded-md border border-border">
                  {isVideoUrl(url) ? <video src={url} className="w-24 h-24 object-cover" /> : <img src={url} className="w-24 h-24 object-cover" alt="media" />}
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center gap-4 mt-2 text-gray-500 text-xs">
            <button onClick={() => toggleCommentLike(c.id, c.is_liked)} className={`flex items-center gap-1 ${c.is_liked ? 'text-red-500' : 'hover:text-white'}`}>
              <FontAwesomeIcon icon={faHeart} className="w-3 h-3" /> {c.like_count}
            </button>
            <button onClick={() => setReplyTo({ id: c.id, handle: c.handle })} className="flex items-center gap-1 hover:text-white">
              <FontAwesomeIcon icon={faReply} className="w-3 h-3" /> Reply
            </button>
            {!activeThread && replies.length > 0 && (
              <button onClick={() => setActiveThread(c.id)} className="ml-auto text-gray-400 hover:text-white font-medium">
                View {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
              </button>
            )}
          </div>

          {activeThread === c.id && replies.map(r => <CommentRow key={r.id} c={r} depth={depth + 1} />)}
        </div>
      </div>
    );
  };

  const activeComment = activeThread ? getComment(activeThread) : null;
  const activeCommentReplies = activeThread ? getReplies(activeThread) : [];
  const rootComments = comments.filter(c => !c.parent_id);

  return (
    <div className="fixed inset-0 z-[100] flex items-end justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="w-full max-w-md bg-surface border-t border-border rounded-t-3xl h-[80vh] flex flex-col" onClick={e => e.stopPropagation()}>
        
        {fullScreenImage && (
          <div className="fixed inset-0 z-[200] bg-black/95 flex items-center justify-center" onClick={(e) => { e.stopPropagation(); setFullScreenImage(null); }}>
            <button className="absolute top-6 right-6 text-white bg-black/50 p-2 rounded-full"><FontAwesomeIcon icon={faXmark} className="w-6 h-6" /></button>
            {isVideoUrl(fullScreenImage) ? <video src={fullScreenImage} controls autoPlay className="max-w-full max-h-[80vh] rounded-lg" /> : <img src={fullScreenImage} className="max-w-full max-h-[80vh] object-contain rounded-lg" alt="Full size" />}
          </div>
        )}

        {/* Header */}
        <div className="p-4 border-b border-border flex justify-between items-center relative shrink-0">
          <div className="w-12 h-1 bg-gray-600 rounded-full absolute top-2 left-1/2 -translate-x-1/2" />
          {activeThread ? (
            <button onClick={() => setActiveThread(null)} className="absolute left-4 top-4 text-white flex items-center gap-2 text-sm z-10"><FontAwesomeIcon icon={faArrowLeft} /> Back</button>
          ) : (
            <h2 className="text-white font-bold text-center w-full pt-2">{localCount} comments</h2>
          )}
          <button onClick={onClose} className="absolute right-4 top-4 text-gray-400 hover:text-white z-10"><FontAwesomeIcon icon={faXmark} className="w-5 h-5" /></button>
        </div>

        {/* Comment List */}
        <div className="flex-1 p-4 overflow-y-auto overflow-x-hidden">
          {loading ? (
            <p className="text-gray-500 text-center text-sm">Loading...</p>
          ) : activeThread ? (
            <>
              {activeComment && <CommentRow c={activeComment} />}
              {activeCommentReplies.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border">
                  {activeCommentReplies.map(r => <CommentRow key={r.id} c={r} depth={1} />)}
                </div>
              )}
            </>
          ) : (
            rootComments.length === 0 ? <p className="text-gray-500 text-center text-sm mt-10">No comments yet.</p> : rootComments.map(c => <CommentRow key={c.id} c={c} />)
          )}
        </div>

        {/* Input Area - FIXED PADDING */}
        <form onSubmit={handleSubmit} className="p-4 pb-20 md:pb-4 border-t border-border bg-surface shrink-0">
          {replyTo && (
            <div className="flex justify-between items-center text-xs text-gray-400 mb-2 bg-black p-2 rounded-lg">
              <span>Replying to {replyTo.handle}</span>
              <button type="button" onClick={() => setReplyTo(null)}><FontAwesomeIcon icon={faXmark} /></button>
            </div>
          )}
          
          {files.length > 0 && (
            <div className="flex gap-2 mb-2 overflow-x-auto">
              {files.map((f, i) => (
                <div key={i} className="w-12 h-12 rounded bg-black flex-shrink-0 border border-border overflow-hidden">
                  {f.type.startsWith('video') ? <video src={URL.createObjectURL(f)} className="w-full h-full object-cover" /> : <img src={URL.createObjectURL(f)} className="w-full h-full object-cover" />}
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2 items-center">
            <label className="text-gray-400 p-2 cursor-pointer hover:text-white">
              <FontAwesomeIcon icon={faImage} className="w-5 h-5" />
              <input type="file" accept="image/*,video/mp4,video/quicktime,image/gif" multiple className="hidden" onChange={e => setFiles(Array.from(e.target.files || []))} />
            </label>
            <input 
              type="text" placeholder="Add comment..." value={comment} onChange={e => setComment(e.target.value)}
              className="flex-1 bg-black border border-border rounded-full px-4 py-3 text-white focus:outline-none focus:border-white text-sm"
            />
            <button type="submit" className="text-dropp-orange p-2"><FontAwesomeIcon icon={faPaperPlane} className="w-5 h-5" /></button>
          </div>
        </form>
      </div>
    </div>
  );
}
