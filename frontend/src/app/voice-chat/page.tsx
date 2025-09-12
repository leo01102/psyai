// frontend/src/app/voice-chat/page.tsx

"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Mic, Video, VideoOff, MoreHorizontal, X, Settings, LoaderCircle, Square } from "lucide-react"
import VoiceChatOrb from "@/components/chat/voice-chat-orb"
import VoiceSelectionModal from "@/components/chat/voice-selection-modal"
import { useLumenChat } from "@/hooks/use-lumen-chat"

export default function VoiceChatPage() {
  // --- Lógica del Hook ---
  // isAISpeaking ahora también nos sirve para saber cuándo reactivar la grabación.
  const {
    isAISpeaking,
    isUserSpeaking,
    isProcessing,
    error,
    startUserSpeaking,
    stopUserSpeaking
  } = useLumenChat();

  // --- Estado de la UI Local ---
  const [isVideoOn, setIsVideoOn] = useState(false)
  const [showVoiceSelection, setShowVoiceSelection] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [isFirstTime, setIsFirstTime] = useState(true)

  // --- LÓGICA DE GRABACIÓN AUTOMÁTICA ---
  useEffect(() => {
    // Al cargar la página, iniciar la grabación
    startUserSpeaking();
  }, [startUserSpeaking]); // Dependencia para asegurar que la función del hook esté disponible

  useEffect(() => {
    // Cuando la IA termina de hablar, volver a activar la grabación para el usuario
    if (!isAISpeaking && !isProcessing && !isUserSpeaking) {
      startUserSpeaking();
    }
  }, [isAISpeaking, isProcessing, isUserSpeaking, startUserSpeaking]);

  
  // Lógica del modal de selección de voz (no cambia)
  useEffect(() => {
    const hasSelectedVoice = localStorage.getItem("selectedVoice")
    if (!hasSelectedVoice) {
      setShowVoiceSelection(true)
    } else {
      setIsFirstTime(false)
    }
  }, [])

  const handleVoiceSelected = (voice: string) => {
    localStorage.setItem("selectedVoice", voice)
    setShowVoiceSelection(false)
    setIsFirstTime(false)
  }

  const handleEndCall = () => {
    window.location.href = "/"
  }

  // --- LÓGICA DEL BOTÓN DE "DETENER/ENVIAR" ---
  const handleStopAndProcess = () => {
    if (isUserSpeaking) {
      // TODO: Aquí tu compañero obtendrá el audioBlob real del MediaRecorder
      const mockAudioBlob = new Blob(["mock audio"], { type: "audio/webm" });
      stopUserSpeaking(mockAudioBlob);
      console.log("Recording stopped, processing...");
    }
  };

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-black to-blue-900/20" />

      {/* Botón de Ajustes */}
      <div className="absolute top-6 right-6 z-20">
        <Button variant="ghost" size="icon" onClick={() => setShowSettings(true)} className="text-gray-400 hover:text-white hover:bg-gray-800/50 rounded-full">
          <Settings className="w-5 h-5" />
        </Button>
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen gap-8">
        <VoiceChatOrb isAISpeaking={isAISpeaking} isUserSpeaking={isUserSpeaking} />
        
        {/* --- BOTÓN DE CONTROL ÚNICO Y CENTRAL --- */}
        <Button
          onClick={handleStopAndProcess}
          // Se deshabilita mientras se procesa Y mientras la IA habla
          disabled={isProcessing || isAISpeaking}
          className="w-24 h-24 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white flex items-center justify-center transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isProcessing ? (
            <LoaderCircle className="w-8 h-8 animate-spin" />
          ) : isAISpeaking ? (
            <Mic className="w-8 h-8 opacity-50"/> // El usuario no puede hablar mientras la IA habla
          ) : (
            <Square className="w-8 h-8" /> // Icono de 'Detener y Enviar'
          )}
        </Button>
        <p className="text-gray-400 h-6">
            {isProcessing ? "Procesando..." : isAISpeaking ? "Lumen está hablando..." : isUserSpeaking ? "Escuchando... haz clic para enviar." : ""}
        </p>
        {error && <p className="text-red-500 text-center mt-4">{error}</p>}
      </div>

      {/* Barra de Navegación Inferior */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-20">
        <div className="flex items-center gap-4 px-6 py-4 bg-gray-900/80 backdrop-blur-lg rounded-full border border-gray-700/50">
          
          <Button variant="ghost" size="icon" onClick={() => setIsVideoOn(!isVideoOn)} className={`rounded-full w-12 h-12 ${isVideoOn ? "text-white hover:bg-gray-700" : "text-gray-400 hover:bg-gray-700"}`}>
            {isVideoOn ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
          </Button>
          <Button variant="ghost" size="icon" className="rounded-full w-12 h-12 text-gray-400 hover:text-white hover:bg-gray-700">
            <MoreHorizontal className="w-5 h-5" />
          </Button>
          <Button variant="ghost" size="icon" onClick={handleEndCall} className="rounded-full w-12 h-12 text-red-400 hover:text-red-300 hover:bg-red-500/20">
            <X className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Modales */}
      <VoiceSelectionModal isOpen={showVoiceSelection} onClose={() => setShowVoiceSelection(false)} onVoiceSelected={handleVoiceSelected} isFirstTime={isFirstTime} />
      <Dialog open={showSettings} onOpenChange={setShowSettings}>
        <DialogContent className="bg-gray-900 border-gray-700 text-white">
          <DialogHeader><DialogTitle>Ajustes del Chat de Voz</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <Button variant="outline" onClick={() => { setShowSettings(false); setShowVoiceSelection(true); }} className="w-full border-gray-600 text-white hover:bg-gray-800">
              Cambiar Voz de IA
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}