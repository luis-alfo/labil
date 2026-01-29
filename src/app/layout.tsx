import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Labil',
  description: 'AI-powered diagram generation for product documentation',
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
