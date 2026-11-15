import './globals.css'
import type { Metadata } from 'next'
import { BottomNav } from '@/components/BottomNav'

export const metadata: Metadata = {
  title: 'Dropp - Chat. Pay. Trust.',
  description: 'Global Social Commerce OS with Escrow',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans antialiased bg-black text-white">
        <div className="mx-auto max-w-md min-h-screen bg-black relative">
          {children}
          <BottomNav />
        </div>
      </body>
    </html>
  )
}
