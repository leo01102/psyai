// components/voice-chat-orb.tsx

"use client"

import { useEffect, useState } from "react"
import PulsingBorderShader from "@/components/shared/pulsing-border-shader"

interface VoiceChatOrbProps {
  isAISpeaking: boolean
  isUserSpeaking: boolean
}

export default function VoiceChatOrb({ isAISpeaking, isUserSpeaking }: VoiceChatOrbProps) {
  const [pulseIntensity, setPulseIntensity] = useState(1)

  useEffect(() => {
    if (isAISpeaking) {
      setPulseIntensity(1.5)
    } else {
      setPulseIntensity(1)
    }
  }, [isAISpeaking])

  return (
    <div className="relative">
      {/* Enhanced glow effect when AI is speaking */}
      <div
        className={`absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 blur-3xl scale-110 transition-all duration-500 ${
          isAISpeaking ? "scale-125 opacity-100" : "scale-110 opacity-70"
        }`}
      />

      {/* Main orb with enhanced animation */}
      <div className="relative">
        <div className={`transition-transform duration-300 ${isAISpeaking ? "scale-105" : "scale-100"}`}>
          <PulsingBorderShader
            intensity={pulseIntensity}
            pulse={isAISpeaking ? 0.4 : 0.2}
            speed={isAISpeaking ? 2 : 1.5}
          />
        </div>

        {/* User speaking indicator - soundwave animation in center */}
        {isUserSpeaking && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="w-1 bg-white rounded-full animate-pulse"
                  style={{
                    height: `${Math.random() * 20 + 10}px`,
                    animationDelay: `${i * 0.1}s`,
                    animationDuration: "0.5s",
                  }}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Enhanced floating elements with more dynamic animation */}
      <div
        className={`absolute -top-4 -right-4 w-3 h-3 bg-purple-400 rounded-full transition-all duration-300 ${
          isAISpeaking ? "animate-bounce scale-125" : "animate-bounce"
        }`}
        style={{ animationDelay: "0s" }}
      />
      <div
        className={`absolute top-1/3 -left-6 w-2 h-2 bg-blue-400 rounded-full transition-all duration-300 ${
          isAISpeaking ? "animate-bounce scale-125" : "animate-bounce"
        }`}
        style={{ animationDelay: "1s" }}
      />
      <div
        className={`absolute bottom-1/4 -right-8 w-4 h-4 bg-pink-400 rounded-full transition-all duration-300 ${
          isAISpeaking ? "animate-bounce scale-125" : "animate-bounce"
        }`}
        style={{ animationDelay: "2s" }}
      />
    </div>
  )
}
