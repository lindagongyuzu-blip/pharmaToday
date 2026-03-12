export interface Topic {
  id: number;
  name: string;
  description?: string;
  conflict_flag: boolean;
  created_at: string;
}

export interface Claim {
  id: number;
  topic_id: number;
  text: string;
  created_at: string;
}

export interface Evidence {
  id: number;
  claim_id: number;
  source_type: "REGULATORY" | "CLINICAL" | "CORPORATE" | "PATENT" | "MEDIA";
  source_url: string;
  source_title?: string;
  evidence_strength: "HIGH" | "MEDIUM" | "LOW";
  extracted_summary: string;
  published_date?: string;
  created_at: string;
}

export interface UserJudgment {
  id: number;
  user_id: number;
  claim_id: number;
  decision: "ACCEPT" | "UNSURE" | "REJECT";
  confidence: "HIGH" | "MEDIUM" | "LOW";
  reason_tag?: string;
  warning: boolean;
  created_at: string;
}

export interface ReviewQueueItem {
  id: number;
  user_id: number;
  claim_id: number;
  review_date: string;
  status: "PENDING" | "COMPLETED";
  created_at: string;
}

export interface CounterQuery {
  counter_query: string;
  counter_url: string;
}

export interface CreateTopicInput {
  name: string;
  description?: string;
}

export interface CreateClaimInput {
  text: string;
}

export interface CreateEvidenceInput {
  source_type: string;
  source_url: string;
  source_title?: string;
  extracted_summary: string;
  published_date?: string;
}

export interface CreateJudgmentInput {
  user_id: number;
  decision: string;
  confidence: string;
  reason_tag?: string;
}

export interface ClaimInsight {
  claim_id: number;
  coverage: {
    high: number;
    medium: number;
    low: number;
    total: number;
  };
  has_conflict: boolean;
  guidance_label: string;
  guidance_text: string;
}
