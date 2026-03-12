import { Topic, Claim, Evidence, UserJudgment, ReviewQueueItem, CounterQuery, CreateTopicInput, CreateClaimInput, CreateEvidenceInput, CreateJudgmentInput, ClaimInsight } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  data?: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    let errorData = null;
    try {
      errorData = await res.json();
    } catch (err) {
      // Ignored if response is not JSON
    }
    const message = errorData?.detail || `API request failed: ${res.statusText}`;
    throw new ApiError(res.status, message, errorData);
  }
  return res.json();
}

export const api = {
  // Topics
  getTopics: () => fetchApi<Topic[]>("/topics"),
  getTopic: (id: number) => fetchApi<Topic>(`/topics/${id}`),
  createTopic: (data: CreateTopicInput) => 
    fetchApi<Topic>("/topics", { method: "POST", body: JSON.stringify(data) }),

  // Claims
  getClaimsByTopic: (topicId: number) => fetchApi<Claim[]>(`/topics/${topicId}/claims`),
  getClaim: (id: number) => fetchApi<Claim>(`/claims/${id}`),
  createClaim: (topicId: number, data: CreateClaimInput) => 
    fetchApi<Claim>(`/topics/${topicId}/claims`, { method: "POST", body: JSON.stringify(data) }),

  // Evidence
  getEvidenceByClaim: (claimId: number) => fetchApi<Evidence[]>(`/claims/${claimId}/evidence`),
  createEvidence: (claimId: number, data: CreateEvidenceInput) => 
    fetchApi<Evidence>(`/claims/${claimId}/evidence`, { method: "POST", body: JSON.stringify(data) }),
  
  // Logic endpoints
  getPrimarySource: async (claimId: number) => {
    try {
      return await fetchApi<Evidence>(`/claims/${claimId}/primary_source`);
    } catch (e) {
      if (e instanceof ApiError && e.status === 404) return null;
      throw e;
    }
  },
  getCounterQuery: (claimId: number) => fetchApi<CounterQuery>(`/claims/${claimId}/counter_query`),
  getClaimInsight: async (claimId: number): Promise<ClaimInsight> => {
    return fetchApi(`/claims/${claimId}/insight`);
  },

  deleteTopic: async (topicId: number): Promise<void> => {
    return fetchApi(`/topics/${topicId}`, {
      method: 'DELETE',
    });
  },

  deleteClaim: async (claimId: number): Promise<void> => {
    return fetchApi(`/claims/${claimId}`, {
      method: 'DELETE',
    });
  },

  deleteEvidence: async (evidenceId: number): Promise<void> => {
    return fetchApi(`/evidence/${evidenceId}`, {
      method: 'DELETE',
    });
  },

  reopenReviewQueueItem: async (queueId: number): Promise<ReviewQueueItem> => {
    return fetchApi(`/review_queue/${queueId}/reopen`, {
      method: 'POST',
    });
  },

  // Judgments & Review Queue
  getJudgmentsByClaim: (claimId: number) => fetchApi<UserJudgment[]>(`/claims/${claimId}/judgments`),
  createJudgment: (claimId: number, data: CreateJudgmentInput) => 
    fetchApi<UserJudgment>(`/claims/${claimId}/judgment`, { method: "POST", body: JSON.stringify(data) }),
  
  getReviewQueue: (userId?: number) => 
    fetchApi<ReviewQueueItem[]>(`/review_queue${userId ? `?user_id=${userId}` : ''}`),
  completeReviewQueueItem: (queueId: number) => 
    fetchApi<ReviewQueueItem>(`/review_queue/${queueId}/complete`, { method: "POST" })
};
