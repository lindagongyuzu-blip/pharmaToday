"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { ReviewQueueItem } from "@/lib/types";
import Navbar from "@/components/Navbar";
import { AlertTriangle, Activity, CheckCircle, Clock } from "lucide-react";

export default function ReviewQueuePage() {
  const [items, setItems] = useState<ReviewQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completingId, setCompletingId] = useState<number | null>(null);

  // MVP matching backend user_id=1 defaults
  const currentUserId = 1;

  const loadQueue = async () => {
    try {
      setLoading(true);
      const data = await api.getReviewQueue(currentUserId);
      setItems(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleComplete = async (id: number) => {
    try {
      setCompletingId(id);
      await api.completeReviewQueueItem(id);
      await loadQueue();
    } catch (err: any) {
       setError("Completion error: " + err.message);
    } finally {
      setCompletingId(null);
    }
  };

  return (
    <div>
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Review Queue</h1>
            <p className="mt-2 text-sm text-slate-600">Tasks requiring analyst secondary review (User #{currentUserId}).</p>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8">
            <div className="flex">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <p className="ml-3 text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <Activity className="animate-spin h-8 w-8 text-blue-500 mx-auto" />
            <p className="mt-2 text-sm text-slate-500">Loading your queue...</p>
          </div>
        ) : items.length === 0 ? (
           <div className="text-center bg-white border border-slate-200 rounded-lg py-12 px-4 shadow-sm">
            <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <h3 className="text-sm font-semibold text-slate-900">All caught up!</h3>
            <p className="mt-1 text-sm text-slate-500">Your review queue is currently empty.</p>
          </div>
        ) : (
          <div className="bg-white shadow-sm ring-1 ring-slate-200 sm:rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-slate-300">
              <thead className="bg-slate-50">
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-slate-900 sm:pl-6">Status</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Claim ID</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Review Date</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Generated</th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6"><span className="sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {items.map((item) => (
                  <tr key={item.id} className={item.status === 'COMPLETED' ? 'bg-slate-50 opacity-75' : ''}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm sm:pl-6">
                      {item.status === 'PENDING' ? (
                        <span className="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20">
                          <Clock className="mr-1 h-3 w-3" /> PENDING
                        </span>
                      ) : (
                        <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                          COMPLETED
                        </span>
                      )}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                      <Link href={`/claims/${item.claim_id}`} className="font-medium text-blue-600 hover:underline">
                        Claim #{item.claim_id}
                      </Link>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                      {new Date(item.review_date).toLocaleDateString()}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                       {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      {item.status === 'PENDING' && (
                        <button
                          onClick={() => handleComplete(item.id)}
                          disabled={completingId === item.id}
                          className="text-white bg-slate-900 hover:bg-slate-700 disabled:bg-slate-300 rounded px-3 py-1.5 transition"
                        >
                          {completingId === item.id ? "Working..." : "Mark Complete"}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
