'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHouse, 
  faWallet, 
  faVideo, 
  faCommentDots, 
  faUser 
} from '@fortawesome/free-solid-svg-icons';

export function BottomNav() {
  const pathname = usePathname();
  if (pathname === '/' || pathname.includes('/auth') || pathname.includes('/upload')) return null;

  const navItems = [
    { name: 'Home', path: '/reels', icon: faHouse },
    { name: 'Card', path: '/profile/wallet', icon: faWallet },
    { name: 'Reels', path: '/reels', icon: faVideo },
    { name: 'Inbox', path: '/chat', icon: faCommentDots },
    { name: 'Profile', path: '/profile', icon: faUser },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 pb-safe bg-black border-t border-border">
      <div className="flex justify-around items-center h-14 max-w-md mx-auto">
        {navItems.map((item) => {
          // Check if the current path matches the item path
          const isActive = pathname === item.path || (item.path === '/reels' && pathname === '/');

          return (
            <Link 
              key={item.name} 
              href={item.path} 
              className={`flex flex-col items-center justify-center w-full h-full space-y-1 transition-colors ${
                isActive ? 'text-white' : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              <FontAwesomeIcon 
                icon={item.icon} 
                className={`w-5 h-5 ${isActive ? 'drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]' : ''}`} 
              />
              <span className={`text-[10px] font-medium ${isActive ? 'font-bold' : ''}`}>
                {item.name}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
