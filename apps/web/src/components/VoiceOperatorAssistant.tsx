import React, { useState } from "react";
import { Mic, MicOff, Volume2, Radio, AlertCircle } from "lucide-react";

export const VoiceOperatorAssistant: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [radioChannel, setRadioChannel] = useState("UHF-CH4 (462.625 MHz)");
  const [lastTranscript, setLastTranscript] = useState(
    "[AUDIO CUE: SIREN_3X] BREAK BREAK BREAK. EDGESHIELD CONTROL. REPLAY ATTACK ON VALVE-GAMMA-01. RECOMMENDED SOP: TRIP SOLENOID FAILSAFE. OVER."
  );

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Radio className="w-6 h-6 text-emerald-400" />
          <h2 className="text-xl font-bold text-white">Rural Operator Voice Dispatch & Radio Copilot</h2>
        </div>
        <span className="px-3 py-1 bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 rounded-full text-xs font-mono">
          {radioChannel}
        </span>
      </div>

      <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
          <span className="flex items-center gap-1.5"><Volume2 className="w-4 h-4 text-cyan-400" /> LAST PHONETIC RADIO BROADCAST</span>
          <span className="text-emerald-400">STATUS: TRANSMITTED</span>
        </div>
        <p className="text-sm font-mono text-cyan-300 bg-slate-900 p-3 rounded border border-cyan-900/40 leading-relaxed">
          {lastTranscript}
        </p>
      </div>

      <div className="flex items-center justify-between pt-2">
        <button
          onClick={toggleRecording}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition ${
            isRecording
              ? "bg-rose-600 hover:bg-rose-500 text-white animate-pulse"
              : "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700"
          }`}
        >
          {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4 text-rose-400" />}
          {isRecording ? "Transmitting Voice SOP..." : "Push-To-Talk Radio Dispatch"}
        </button>

        <span className="text-xs text-slate-500 font-mono">
          Simplex PTT Protocol (STANAG 4285 / DMR Tier II)
        </span>
      </div>
    </div>
  );
};
