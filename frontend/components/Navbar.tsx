import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="bg-slate-900 text-white shadow shadow-slate-200">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link href="/" className="flex items-center text-xl font-bold tracking-tight text-white hover:text-slate-200">
              PharmaToday
            </Link>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
              <Link
                href="/"
                className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-slate-300 text-sm font-medium"
              >
                Topics
              </Link>
              <Link
                href="/review-queue"
                className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-slate-300 text-sm font-medium"
              >
                Review Queue
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
