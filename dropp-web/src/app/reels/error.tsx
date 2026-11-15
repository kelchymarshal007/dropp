'use client';
export default function ErrorBoundary({ error, reset }: { error: Error, reset: () => void }) {
  return (
    <div className="h-screen bg-black flex flex-col items-center justify-center text-white p-6 text-center">
      <p className="text-red-500 font-bold mb-2">Something went wrong</p>
      <p className="text-gray-400 text-xs mb-4 break-all max-w-sm">{error.message}</p>
      <button onClick={reset} className="bg-dropp-orange text-black px-6 py-2 rounded-full font-semibold">Try Again</button>
    </div>
  );
}
