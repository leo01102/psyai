// frontend/src/services/api-client.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type LongTermMemory = {
  nombre?: string;
  edad?: number | string;
  tema_recurrente?: string;
  preferencia_personal?: string;
  meta_u_objetivo?: string;
};

interface EmotionPayload {
  stable_dominant_emotion: string | null;
  average_scores: Record<string, number> | null;
}

interface InteractionRequest {
  session_id: number;
  audio_b64: string;
  facial_emotion: EmotionPayload | null;
  chat_history: { role: string; content: string }[];
  long_term_memory: LongTermMemory;
}

export interface InteractionResponse {
  ai_text: string;
  ai_audio_b64: string | null;
  extracted_memory: LongTermMemory;
  updated_chat_history: { role: string; content: string }[];
}

/**
 * Crea una nueva sesión en el backend.
 */
export const createNewSession = async (): Promise<{ session_id: number }> => {
  const response = await fetch(`${API_BASE_URL}/session`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to create a new session');
  return response.json();
};

/**
 * Envía una interacción completa al backend.
 */
export const sendInteraction = async (payload: InteractionRequest): Promise<InteractionResponse> => {
  const response = await fetch(`${API_BASE_URL}/interact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to process interaction');
  }
  return response.json();
};