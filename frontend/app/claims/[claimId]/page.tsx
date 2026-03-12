"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Claim, Evidence, UserJudgment, CounterQuery, ClaimInsight } from "@/lib/types";
import Navbar from "@/components/Navbar";
import { AlertTriangle, ChevronLeft, Activity, ShieldAlert, Award, Search, FileText } from "lucide-react";

export default function ClaimDetailPage() {
  const { claimId } = useParams() as { claimId: string };
  const router = useRouter();

  const [claim, setClaim] = useState<Claim | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [judgments, setJudgments] = useState<UserJudgment[]>([]);
  const [primarySource, setPrimarySource] = useState<Evidence | null>(null);
  const [counterQuery, setCounterQuery] = useState<CounterQuery | null>(null);
  const [insight, setInsight] = useState<ClaimInsight | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Evidence Form State
  const [sourceType, setSourceType] = useState<string>("CLINICAL");
  const [sourceUrl, setSourceUrl] = useState("");
  const [sourceTitle, setSourceTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [submittingEv, setSubmittingEv] = useState(false);
  const [deletingEv, setDeletingEv] = useState<number | null>(null);

  // Judgment Form State
  const MVP_USER_ID = 1; // Hardcoded ID for MVP
  const [decision, setDecision] = useState<string>("UNSURE");
  const [confidence, setConfidence] = useState<string>("HIGH");
  const [reasonTag, setReasonTag] = useState("");
  const [submittingJm, setSubmittingJm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const cId = Number(claimId);
      const [claimData, evData, jmData, psData, cqData, inData] = await Promise.all([
        api.getClaim(cId),
        api.getEvidenceByClaim(cId),
        api.getJudgmentsByClaim(cId),
        api.getPrimarySource(cId),
        api.getCounterQuery(cId),
        api.getClaimInsight(cId)
      ]);
      setClaim(claimData);
      setEvidence(evData);
      setJudgments(jmData);
      setPrimarySource(psData);
      setCounterQuery(cqData);
      setInsight(inData);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (claimId) loadData();
  }, [claimId]);

  const handleCreateEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sourceUrl.trim() || !summary.trim()) return;
    try {
      setSubmittingEv(true);
      await api.createEvidence(Number(claimId), {
        source_type: sourceType,
        source_url: sourceUrl,
        source_title: sourceTitle || undefined,
        extracted_summary: summary
      });
      setSourceUrl("");
      setSourceTitle("");
      setSummary("");
      await loadData();
    } catch (err: any) {
      setError("Evidence error: " + err.message);
    } finally {
      setSubmittingEv(false);
    }
  };

  const handleCreateJudgment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmittingJm(true);
      await api.createJudgment(Number(claimId), {
        user_id: MVP_USER_ID,
        decision: decision,
        confidence: confidence,
        reason_tag: reasonTag || undefined
      });
      setReasonTag("");
      await loadData();
    } catch (err: any) {
      setError("Judgment error: " + err.message);
    } finally {
      setSubmittingJm(false);
    }
  };

  const handleDeleteClaim = async () => {
    if (!window.confirm("Delete this claim and all related evidence, judgments, and review items?")) return;
    try {
      setDeleting(true);
      await api.deleteClaim(Number(claimId));
      router.push(`/topics/${claim?.topic_id}`);
    } catch (err: any) {
      setError("Delete claim error: " + err.message);
      setDeleting(false);
    }
  };

  const handleDeleteEvidence = async (id: number) => {
    if (!window.confirm("Delete this evidence item?")) return;
    try {
      setDeletingEv(id);
      await api.deleteEvidence(id);
      await loadData();
    } catch (err: any) {
      setError("Delete evidence error: " + err.message);
    } finally {
      setDeletingEv(null);
    }
  };

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="text-center py-20">
          <Activity className="animate-spin h-8 w-8 text-blue-500 mx-auto" />
          <p className="mt-2 text-sm text-slate-500">Loading claim details...</p>
        </div>
      </div>
    );
  }

  if (!claim) {
    return (
      <div>
        <Navbar />
        <div className="text-center py-20">
          <AlertTriangle className="h-8 w-8 text-red-500 mx-auto" />
          <h3 className="mt-2 text-sm font-semibold text-slate-900">Claim not found</h3>
          <button onClick={() => router.push("/")} className="mt-4 text-blue-600 hover:text-blue-500">
            &larr; Back home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col lg:flex-row gap-8">
        
        {/* Left Column: Data Display */}
        <div className="flex-1 space-y-8">
          <div>
            <Link href={`/topics/${claim.topic_id}`} className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-slate-700 mb-4">
              <ChevronLeft className="h-4 w-4 mr-1" /> Back to Topic
            </Link>
            
            <div className="bg-white px-4 py-5 sm:px-6 shadow sm:rounded-lg border border-slate-200 flex justify-between items-start">
              <div>
                <h2 className="text-xl font-bold leading-7 text-slate-900 sm:truncate sm:tracking-tight">
                  {claim.text}
                </h2>
                <p className="text-xs text-slate-400 mt-2">Claim ID: {claim.id} • Registered: {new Date(claim.created_at).toLocaleDateString()}</p>
              </div>
              <button 
                onClick={handleDeleteClaim} 
                disabled={deleting} 
                className="ml-4 flex-shrink-0 inline-flex items-center rounded-md bg-red-50 px-2.5 py-1.5 text-sm font-medium text-red-700 hover:bg-red-100 ring-1 ring-inset ring-red-600/20 transition-colors"
                title="Delete Claim"
              >
                {deleting ? "Deleting..." : "Delete Claim"}
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4">
              <div className="flex">
                <AlertTriangle className="h-5 w-5 text-red-500" />
                <p className="ml-3 text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Reasoning Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {/* Claim Insight */}
            <div className="bg-purple-50 shadow-sm rounded-lg border border-purple-100 overflow-hidden">
               <div className="px-4 py-3 bg-purple-100 border-b border-purple-200 flex items-center gap-2">
                <FileText className="h-5 w-5 text-purple-700" />
                <h3 className="text-sm font-semibold text-purple-900">Evidence Insight</h3>
              </div>
              <div className="p-4 flex flex-col justify-between h-[calc(100%-45px)]">
                {insight ? (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                       <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-bold ring-1 ring-inset ${
                         insight.guidance_label === 'STRONG_SUPPORT' ? 'bg-green-50 text-green-700 ring-green-600/20' : 
                         insight.guidance_label === 'LIMITED_SUPPORT' ? 'bg-yellow-50 text-yellow-800 ring-yellow-600/20' : 
                         insight.guidance_label === 'CONFLICTING_EVIDENCE' ? 'bg-red-50 text-red-700 ring-red-600/20' : 
                         'bg-gray-50 text-gray-600 ring-gray-500/10'}`}>
                         {insight.guidance_label.replace('_', ' ')}
                       </span>
                    </div>
                    
                    <div className="grid grid-cols-4 gap-2 text-center text-xs font-medium">
                      <div className="bg-white rounded border border-purple-100 p-1">
                        <div className="text-slate-500 text-[10px] uppercase">High</div>
                        <div className="text-purple-900">{insight.coverage.high}</div>
                      </div>
                      <div className="bg-white rounded border border-purple-100 p-1">
                        <div className="text-slate-500 text-[10px] uppercase">Med</div>
                        <div className="text-purple-900">{insight.coverage.medium}</div>
                      </div>
                      <div className="bg-white rounded border border-purple-100 p-1">
                        <div className="text-slate-500 text-[10px] uppercase">Low</div>
                        <div className="text-purple-900">{insight.coverage.low}</div>
                      </div>
                      <div className="bg-purple-100 rounded border border-purple-200 p-1 font-bold">
                        <div className="text-purple-700 text-[10px] uppercase">Tot</div>
                        <div className="text-purple-900">{insight.coverage.total}</div>
                      </div>
                    </div>

                    <p className="text-xs text-purple-900/80 bg-white/50 p-2 rounded border border-purple-50 italic">
                      {insight.guidance_text}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-purple-800/60 italic text-center py-4">Generating insights...</p>
                )}
              </div>
            </div>
            
            {/* Primary Source */}
            <div className="bg-blue-50 shadow-sm rounded-lg border border-blue-100 overflow-hidden">
              <div className="px-4 py-3 bg-blue-100 border-b border-blue-200 flex items-center gap-2">
                <Award className="h-5 w-5 text-blue-700" />
                <h3 className="text-sm font-semibold text-blue-900">Primary Source</h3>
              </div>
              <div className="p-4">
                {primarySource ? (
                   <div className="space-y-3">
                     <div className="flex justify-between items-start">
                       <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                         primarySource.evidence_strength === 'HIGH' ? 'bg-green-50 text-green-700 ring-green-600/20' : 
                         primarySource.evidence_strength === 'MEDIUM' ? 'bg-yellow-50 text-yellow-800 ring-yellow-600/20' : 
                         'bg-gray-50 text-gray-600 ring-gray-500/10'}`}>
                         {primarySource.evidence_strength} CONFIDENCE
                       </span>
                       <span className="text-xs text-blue-600 uppercase font-semibold">{primarySource.source_type}</span>
                     </div>
                     <div>
                       <a href={primarySource.source_url} target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-blue-800 hover:underline">
                         {primarySource.source_title || primarySource.source_url}
                       </a>
                     </div>
                     <p className="text-sm text-blue-900/80 bg-white/50 p-2 rounded border border-blue-50 italic">
                       "{primarySource.extracted_summary}"
                     </p>
                   </div>
                ) : (
                  <p className="text-sm text-blue-800/60 italic text-center py-4">No qualifying primary source available.</p>
                )}
              </div>
            </div>

            {/* Counter Query */}
            <div className="bg-slate-50 shadow-sm rounded-lg border border-slate-200 overflow-hidden">
               <div className="px-4 py-3 bg-slate-100 border-b border-slate-200 flex items-center gap-2">
                <Search className="h-5 w-5 text-slate-700" />
                <h3 className="text-sm font-semibold text-slate-900">Counter-Query Strategy</h3>
              </div>
              <div className="p-4 flex flex-col justify-between h-[calc(100%-45px)]">
                 {counterQuery ? (
                   <>
                    <p className="text-sm text-slate-700 mb-4 bg-white p-3 rounded border border-slate-200 font-mono text-xs">
                      {counterQuery.counter_query}
                    </p>
                    <a 
                      href={counterQuery.counter_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="mt-auto block w-full text-center rounded bg-white px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50"
                    >
                      Run Conflict Search
                    </a>
                   </>
                 ) : (
                    <p className="text-sm text-slate-500 italic text-center py-4">Query generation failing.</p>
                 )}
              </div>
            </div>

          </div>

          {/* Evidence List */}
          <div>
            <h3 className="text-lg font-medium leading-6 text-slate-900 mb-4">Evidence Repository</h3>
            {evidence.length === 0 ? (
              <div className="text-center bg-white border border-slate-200 rounded-lg py-8 px-4 shadow-sm">
                <p className="text-sm text-slate-500">No evidence recorded.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {evidence.map((ev) => (
                  <div key={ev.id} className="bg-white shadow sm:rounded-lg border border-slate-200 p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex gap-2">
                        <span className="inline-flex items-center rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
                          {ev.source_type}
                        </span>
                        <span className={`inline-flex items-center rounded px-2 py-1 text-xs font-semibold ${
                          ev.evidence_strength === 'HIGH' ? 'bg-green-100 text-green-700' : 
                          ev.evidence_strength === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-gray-100 text-gray-700'}`}>
                          {ev.evidence_strength}
                        </span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <a href={ev.source_url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline truncate max-w-[200px]">
                          {ev.source_title || 'Source Link'}
                        </a>
                        <button 
                          onClick={() => handleDeleteEvidence(ev.id)}
                          disabled={deletingEv === ev.id}
                          className="text-xs text-red-500 hover:text-red-700 font-medium disabled:opacity-50"
                        >
                          {deletingEv === ev.id ? "..." : "Delete"}
                        </button>
                      </div>
                    </div>
                    <p className="text-sm text-slate-700 mt-2">{ev.extracted_summary}</p>
                    <p className="text-xs text-slate-400 mt-3 text-right">Added {new Date(ev.created_at).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Judgments List */}
          <div>
            <h3 className="text-lg font-medium leading-6 text-slate-900 mb-4">Analyst Judgments</h3>
            {judgments.length === 0 ? (
               <div className="text-center bg-white border border-slate-200 rounded-lg py-8 px-4 shadow-sm">
                <p className="text-sm text-slate-500">No judgments recorded.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {judgments.map((jm) => (
                  <div key={jm.id} className={`bg-white shadow sm:rounded-lg border p-4 ${jm.warning ? 'border-red-300 bg-red-50/30' : 'border-slate-200'}`}>
                     <div className="flex justify-between items-start mb-2">
                       <div className="flex items-center gap-2">
                          <span className={`inline-flex items-center rounded px-2 py-1 text-xs font-bold ${
                             jm.decision === 'ACCEPT' ? 'bg-green-100 text-green-800' :
                             jm.decision === 'REJECT' ? 'bg-red-100 text-red-800' :
                             'bg-slate-100 text-slate-800'
                          }`}>
                            {jm.decision}
                          </span>
                          <span className="text-xs text-slate-500 font-medium">Conf: {jm.confidence}</span>
                          {jm.warning && (
                            <span className="flex items-center text-xs font-bold text-red-600 bg-red-100 px-2 py-1 rounded">
                              <ShieldAlert className="w-3 h-3 mr-1" /> WARNING FLAG
                            </span>
                          )}
                       </div>
                       <span className="text-xs text-slate-400">User ID: {jm.user_id}</span>
                     </div>
                     {jm.reason_tag && <p className="text-sm text-slate-700 mt-2 font-medium">Tag: {jm.reason_tag}</p>}
                     <p className="text-xs text-slate-400 mt-2 text-right">Added {new Date(jm.created_at).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Forms */}
        <div className="lg:w-80 flex-shrink-0 space-y-6">
           
           {/* Add Evidence Form */}
           <div className="bg-white shadow sm:rounded-lg border border-slate-200 p-5">
              <h3 className="text-sm font-semibold leading-6 text-slate-900 border-b pb-3 mb-4">Add Evidence Log</h3>
              <form onSubmit={handleCreateEvidence} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-700">Source Type</label>
                  <select 
                    value={sourceType} onChange={(e) => setSourceType(e.target.value)}
                    className="mt-1 block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-slate-900 ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-blue-600 sm:text-sm sm:leading-6"
                  >
                    <option value="REGULATORY">Regulatory (FDA, EMA)</option>
                    <option value="CLINICAL">Clinical Trial</option>
                    <option value="CORPORATE">Corporate PR</option>
                    <option value="PATENT">Patent Filing</option>
                    <option value="MEDIA">News Media</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700">Source URL</label>
                  <input type="url" required value={sourceUrl} onChange={(e) => setSourceUrl(e.target.value)} placeholder="https://..."
                    className="mt-1 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-xs sm:leading-6 px-3"
                  />
                </div>
                 <div>
                  <label className="block text-xs font-medium text-slate-700">Source Title (Optional)</label>
                  <input type="text" value={sourceTitle} onChange={(e) => setSourceTitle(e.target.value)} placeholder="Document Title"
                    className="mt-1 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-xs sm:leading-6 px-3"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700">Extracted Summary</label>
                  <textarea required rows={3} value={summary} onChange={(e) => setSummary(e.target.value)} placeholder="Key takeaways supporting or refuting the claim..."
                    className="mt-1 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-xs sm:leading-6 px-3"
                  />
                </div>
                <button type="submit" disabled={submittingEv} className="w-full justify-center inline-flex items-center rounded-md bg-slate-900 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-700">
                  {submittingEv ? "Saving..." : "Log Evidence"}
                </button>
              </form>
           </div>

           {/* Add Judgment Form */}
           <div className="bg-slate-50 shadow sm:rounded-lg border border-slate-200 p-5">
              <h3 className="text-sm font-semibold leading-6 text-slate-900 border-b border-slate-200 pb-3 mb-4">Submit Analyst Judgment</h3>
              <form onSubmit={handleCreateJudgment} className="space-y-4">
                 <div>
                  <label className="block text-xs font-medium text-slate-700">Decision</label>
                  <select 
                    value={decision} onChange={(e) => setDecision(e.target.value)}
                    className="mt-1 block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-slate-900 ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-slate-600 sm:text-sm sm:leading-6"
                  >
                    <option value="ACCEPT">ACCEPT</option>
                    <option value="UNSURE">UNSURE</option>
                    <option value="REJECT">REJECT</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700">Confidence</label>
                  <select 
                    value={confidence} onChange={(e) => setConfidence(e.target.value)}
                    className="mt-1 block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-slate-900 ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-slate-600 sm:text-sm sm:leading-6"
                  >
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                </div>
                 <div>
                  <label className="block text-xs font-medium text-slate-700">Reason Tag (required for ACCEPT/REJECT)</label>
                  <input type="text" value={reasonTag} onChange={(e) => setReasonTag(e.target.value)} placeholder="e.g. Needs trial data"
                    className="mt-1 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-slate-600 sm:text-xs sm:leading-6 px-3"
                  />
                </div>
                <button type="submit" disabled={submittingJm} className="w-full justify-center inline-flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500">
                  {submittingJm ? "Submitting..." : "Submit Judgment"}
                </button>
              </form>
           </div>

        </div>

      </main>
    </div>
  );
}
