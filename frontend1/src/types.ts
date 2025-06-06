// src/types.ts
export interface GenerateRequest {
  prompt: string;
  concept_label?: string;
  allowed_status?: string;
}

export interface GenerateResponse {
  result: string;
}
