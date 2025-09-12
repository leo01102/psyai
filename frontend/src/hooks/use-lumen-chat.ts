// frontend/src/hooks/use-lumen-chat.ts

import { useState, useEffect, useCallback } from 'react';
import { createNewSession, sendInteraction, InteractionResponse, LongTermMemory } from '@/services/api-client';

export const useLumenChat = () => {
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([]);
  const [longTermMemory, setLongTermMemory] = useState<LongTermMemory>({});
  
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [isUserSpeaking, setIsUserSpeaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeSession = async () => {
      try {
        const data = await createNewSession();
        setSessionId(data.session_id);
      } catch (e: unknown) {
        setError('Could not connect to the LumenAI backend.');
        console.error(e);
      }
    };
    initializeSession();
  }, []);

  const handleUserInteraction = useCallback(async (audioBlob: Blob) => {
    if (!sessionId || isProcessing) return;

    setIsUserSpeaking(false);
    setIsProcessing(true);
    setError(null);

    try {
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64Audio = (reader.result as string).split(',')[1];
        
        const mockFacialEmotion = {
            stable_dominant_emotion: "neutral",
            average_scores: {}
        };

        const response: InteractionResponse = await sendInteraction({
          session_id: sessionId,
          audio_b64: base64Audio,
          facial_emotion: mockFacialEmotion,
          chat_history: chatHistory,
          long_term_memory: longTermMemory,
        });

        setChatHistory(response.updated_chat_history);
        setLongTermMemory(prev => ({ ...prev, ...response.extracted_memory }));
        
        if (response.ai_audio_b64) {
          const audio = new Audio(`data:audio/mp3;base64,${response.ai_audio_b64}`);
          setIsAISpeaking(true);
          audio.play();
          audio.onended = () => setIsAISpeaking(false);
        }
      };
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message);
      } else {
        setError('An unknown error occurred.');
      }
      console.error(e);
    } finally {
      setIsProcessing(false);
    }
  }, [sessionId, isProcessing, chatHistory, longTermMemory]);

  return {
    isAISpeaking,
    isUserSpeaking,
    isProcessing,
    error,
    chatHistory,
    startUserSpeaking: () => setIsUserSpeaking(true),
    stopUserSpeaking: handleUserInteraction,
  };
};