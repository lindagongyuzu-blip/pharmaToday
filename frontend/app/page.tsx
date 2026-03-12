"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Topic } from "@/lib/types";
import Navbar from "@/components/Navbar";
import { AlertTriangle, Plus, Activity } from "lucide-react";

export default function TopicListPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadTopics = async () => {
    try {
      setLoading(true);
      const data = await api.getTopics();
      setTopics(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTopics();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    try {
      setSubmitting(true);
      await api.createTopic({ name: newName, description: newDesc });
      setNewName("");
      setNewDesc("");
      await loadTopics();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Active Topics</h1>
            <p className="mt-2 text-sm text-slate-600">Monitor and analyze pharmaceutical claims.</p>
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

        {/* Create Topic Form */}
        <div className="bg-white shadow sm:rounded-lg mb-8 overflow-hidden border border-slate-200">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-base font-semibold leading-6 text-slate-900 mb-4 flex items-center">
              <Plus className="mr-2 h-5 w-5 text-slate-400" />
              Track New Topic
            </h3>
            <form onSubmit={handleCreate} className="space-y-4 sm:flex sm:items-start sm:gap-4 sm:space-y-0">
              <div className="w-full sm:max-w-xs">
                <input
                  type="text"
                  required
                  placeholder="Topic Name (e.g. Aspirin)"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 px-3"
                />
              </div>
              <div className="w-full sm:max-w-md">
                <input
                  type="text"
                  placeholder="Description (Optional)"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 px-3"
                />
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="mt-3 inline-flex w-full items-center justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 sm:mt-0 sm:w-auto sm:shrink-0"
              >
                {submitting ? "Adding..." : "Add Topic"}
              </button>
            </form>
          </div>
        </div>

        {/* Topc List */}
        {loading ? (
          <div className="text-center py-12">
            <Activity className="animate-spin h-8 w-8 text-blue-500 mx-auto" />
            <p className="mt-2 text-sm text-slate-500">Loading topics...</p>
          </div>
        ) : topics.length === 0 ? (
          <div className="text-center bg-white border border-slate-200 rounded-lg py-12 px-4 shadow-sm">
            <h3 className="mt-2 text-sm font-semibold text-slate-900">No topics tracked</h3>
            <p className="mt-1 text-sm text-slate-500">Get started by creating a new topic above.</p>
          </div>
        ) : (
          <ul role="list" className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {topics.map((topic) => (
              <li key={topic.id} className="col-span-1 divide-y divide-slate-200 rounded-lg bg-white shadow transition hover:shadow-md border border-slate-200">
                <Link href={`/topics/${topic.id}`} className="block w-full p-6 h-full flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-medium text-slate-900 truncate">{topic.name}</h3>
                      {topic.conflict_flag && (
                        <span className="inline-flex flex-shrink-0 items-center rounded-full bg-red-50 px-1.5 py-0.5 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/20">
                          Conflict Detected
                        </span>
                      )}
                    </div>
                    <p className="mt-2 text-sm text-slate-500 line-clamp-2">
                       {topic.description || "No description provided."}
                    </p>
                  </div>
                  <div className="mt-4 flex text-xs text-slate-400">
                     <span>Added {new Date(topic.created_at).toLocaleDateString()}</span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
