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
