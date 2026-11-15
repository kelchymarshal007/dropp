'use client';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faLock } from '@fortawesome/free-solid-svg-icons';

export function AuthWallModal({ isOpen }: { isOpen: boolean }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-end justify-center bg-black/60 backdrop-blur-sm pb-20">
      <div className="w-full max-w-md bg-surface border-t border-border rounded-t-3xl p-6 space-y-6 animate-slide-up">
        
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-dropp-orange/10 rounded-full flex items-center justify-center">
            <FontAwesomeIcon icon={faLock} className="w-6 h-6 text-dropp-orange" />
          </div>
        </div>

        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-white">Create an account to keep watching</h2>
          <p className="text-gray-400 text-sm">
            Join Dropp to like, comment, and securely buy items from sellers worldwide.
          </p>
        </div>

        <div className="space-y-3 pt-2">
          <Link href="/signup" className="block w-full">
            <button className="w-full py-4 rounded-full font-semibold text-[15px] bg-dropp-orange text-black hover:bg-dropp-orange/90 transition-all">
              Sign Up
            </button>
          </Link>
          <Link href="/login" className="block w-full">
            <button className="w-full py-4 rounded-full font-semibold text-[15px] bg-transparent text-white border border-border hover:bg-white/5 transition-all">
              Log In
            </button>
          </Link>
        </div>

      </div>
    </div>
  );
}
