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
