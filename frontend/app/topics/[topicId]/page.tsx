"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Topic, Claim } from "@/lib/types";
import Navbar from "@/components/Navbar";
import { AlertTriangle, Plus, ChevronLeft, FileText, Activity } from "lucide-react";

export default function TopicDetailPage() {
  const { topicId } = useParams() as { topicId: string };
  const router = useRouter();

  const [topic, setTopic] = useState<Topic | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [newClaimText, setNewClaimText] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [topicData, claimsData] = await Promise.all([
        api.getTopic(Number(topicId)),
        api.getClaimsByTopic(Number(topicId))
      ]);
      setTopic(topicData);
      setClaims(claimsData);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (topicId) loadData();
  }, [topicId]);

  const handleCreateClaim = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newClaimText.trim()) return;
    try {
      setSubmitting(true);
      await api.createClaim(Number(topicId), { text: newClaimText });
      setNewClaimText("");
      await loadData();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="text-center py-20">
          <Activity className="animate-spin h-8 w-8 text-blue-500 mx-auto" />
          <p className="mt-2 text-sm text-slate-500">Loading topic details...</p>
        </div>
      </div>
    );
  }

  if (!topic) {
    return (
      <div>
        <Navbar />
        <div className="text-center py-20">
          <AlertTriangle className="h-8 w-8 text-red-500 mx-auto" />
          <h3 className="mt-2 text-sm font-semibold text-slate-900">Topic not found</h3>
          <button onClick={() => router.push("/")} className="mt-4 text-blue-600 hover:text-blue-500">
            &larr; Back to topics
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <Link href="/" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-slate-700 mb-6">
          <ChevronLeft className="h-4 w-4 mr-1" /> Back to Topics
        </Link>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8">
            <div className="flex">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <p className="ml-3 text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Topic Header */}
        <div className="bg-white px-4 py-5 sm:px-6 shadow sm:rounded-lg border border-slate-200 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold leading-7 text-slate-900 sm:truncate sm:text-3xl sm:tracking-tight">
                {topic.name}
              </h2>
              {topic.description && <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-500">{topic.description}</p>}
            </div>
            {topic.conflict_flag && (
              <span className="inline-flex items-center rounded-md bg-red-50 px-2.5 py-1.5 text-sm font-medium text-red-700 ring-1 ring-inset ring-red-600/20">
                <AlertTriangle className="h-4 w-4 mr-1.5" /> Conflict Detected in Evidence
              </span>
            )}
          </div>
        </div>

        {/* Create Claim Form */}
        <div className="bg-white shadow sm:rounded-lg mb-8 overflow-hidden border border-slate-200">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-base font-semibold leading-6 text-slate-900 flex items-center mb-4">
              <Plus className="mr-2 h-5 w-5 text-slate-400" /> Track New Claim
            </h3>
            <form onSubmit={handleCreateClaim} className="flex gap-4 items-start">
              <div className="flex-1">
                <textarea
                  required
                  rows={2}
                  placeholder="Enter the specific pharmaceutical claim..."
                  value={newClaimText}
                  onChange={(e) => setNewClaimText(e.target.value)}
                  className="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 px-3"
                />
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="inline-flex items-center justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 sm:shrink-0"
              >
                {submitting ? "Tracking..." : "Add Claim"}
              </button>
            </form>
          </div>
        </div>

        {/* Claims List */}
        <div>
          <h3 className="text-lg font-medium leading-6 text-slate-900 mb-4">Tracked Claims</h3>
          {claims.length === 0 ? (
            <div className="text-center bg-white border border-slate-200 rounded-lg py-12 px-4 shadow-sm">
              <FileText className="h-8 w-8 text-slate-300 mx-auto mb-2" />
              <p className="text-sm text-slate-500">No claims have been tracked for this topic yet.</p>
            </div>
          ) : (
            <ul role="list" className="space-y-4">
              {claims.map((claim) => (
                <li key={claim.id} className="overflow-hidden rounded-lg bg-white shadow border border-slate-200 transition hover:shadow-md">
                   <div className="px-4 py-5 sm:p-6 flex justify-between items-center gap-6">
                      <div className="flex-1">
                         <p className="text-sm font-medium text-slate-900">{claim.text}</p>
                         <p className="text-xs text-slate-400 mt-1">ID: {claim.id} • Added {new Date(claim.created_at).toLocaleDateString()}</p>
                      </div>
                      <Link 
                        href={`/claims/${claim.id}`}
                        className="rounded bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-100 whitespace-nowrap"
                      >
                        Analyze Evidence
                      </Link>
                   </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  );
}
