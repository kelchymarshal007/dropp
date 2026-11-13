#!/bin/bash

echo "Building Stage 4: The Next.js Dropp Card UI..."

# 1. Global CSS (Tailwind Setup)
cat > dropp-web/src/app/globals.css << 'CSS'
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #0f172a; /* Slate 900 */
  color: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
CSS

# 2. Root Layout
cat > dropp-web/src/app/layout.tsx << 'TSX'
import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Dropp - Social Commerce Escrow',
  description: 'Chat. Pay. Trust.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
TSX

# 3. The Homepage
cat > dropp-web/src/app/page.tsx << 'TSX'
import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 text-center">
      <h1 className="text-5xl font-extrabold mb-4 text-white">Dropp</h1>
      <p className="text-xl text-slate-400 mb-8">Don't DM and pray. Get it protected.</p>
      <Link 
        href="/d/PuJPaBoK" 
        className="px-6 py-3 bg-blue-600 text-white rounded-full font-semibold hover:bg-blue-500 transition"
      >
        Test a Dropp Card
      </Link>
    </main>
  )
}
TSX

# 4. The Dynamic Dropp Card Page (/d/[code])
mkdir -p dropp-web/src/app/d/\[code\]
cat > dropp-web/src/app/d/\[code\]/page.tsx << 'TSX'
'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'

interface DroppData {
  id: string
  code: string
  title: string
  status: string
  currency: string
  offer_minor: number
}

export default function DroppCardPage() {
  const params = useParams()
  const code = params.code as string
  const [dropp, setDropp] = useState<DroppData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!code) return;
    
    // Fetch from our FastAPI backend (Port 8001)
    fetch(`http://localhost:8001/v1/dropps/${code}`)
      .then(res => {
        if (!res.ok) throw new Error('Dropp not found')
        return res.json()
      })
      .then(data => setDropp(data))
      .catch(err => setError(err.message))
  }, [code])

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="p-6 bg-red-900/50 rounded-xl border border-red-500">
          <h2 className="text-xl text-white font-bold">Error</h2>
          <p className="text-red-200">{error}</p>
        </div>
      </div>
    )
  }

  if (!dropp) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-400 animate-pulse">Loading secure escrow...</p>
      </div>
    )
  }

  // Format price dynamically (e.g., KES 50,000.00)
  const formattedPrice = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: dropp.currency,
  }).format(dropp.offer_minor / 100)

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-800 rounded-3xl shadow-2xl overflow-hidden border border-slate-700">
        
        {/* Header */}
        <div className="bg-blue-600 p-4 flex justify-between items-center">
          <span className="text-white font-bold tracking-widest">DROPP</span>
          <span className="text-blue-200 text-sm flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
            Escrow Protected
          </span>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          <div>
            <h2 className="text-sm text-slate-400 uppercase tracking-wider mb-1">Item</h2>
            <h1 className="text-2xl font-bold text-white">{dropp.title}</h1>
          </div>

          <div className="bg-slate-900 rounded-xl p-4 border border-slate-700">
            <h2 className="text-sm text-slate-400 uppercase tracking-wider mb-1">Offer Amount</h2>
            <p className="text-3xl font-extrabold text-white">{formattedPrice}</p>
          </div>

          <div className="flex justify-between text-sm text-slate-400">
            <span>Status: <span className="text-blue-400 font-semibold uppercase">{dropp.status}</span></span>
            <span>Code: <span className="text-white font-mono">{dropp.code}</span></span>
          </div>

          {/* Actions */}
          <div className="space-y-3 pt-4">
            <button className="w-full py-4 bg-green-500 hover:bg-green-400 text-slate-900 font-bold rounded-xl transition">
              Accept & Pay Safely
            </button>
            <button className="w-full py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-xl transition">
              Counter Offer
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}
TSX

echo "Stage 4 files created successfully."
