'use client';

import { useState, useEffect } from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useConnectionState,
  useTracks,
} from '@livekit/components-react';
import { Track, ConnectionState } from 'livekit-client';

interface VoiceAgentProps {
  roomName?: string;
  participantName?: string;
}

function VoiceAgentContent() {
  const [transcription] = useState<string>('');
  const connectionState = useConnectionState();
  const tracks = useTracks();

  // Prüfe ob Agent spricht basierend auf aktuellen Tracks
  const isAgentSpeaking = tracks.some(
    (track) =>
      track.source === Track.Source.Microphone &&
      track.participant.identity !== 'user' &&
      !track.publication.isMuted
  );

  return (
    <div className="flex flex-col gap-4 p-6 bg-white dark:bg-zinc-900 rounded-lg shadow-lg">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
          Voice Agent
        </h3>
        <div className="flex items-center gap-2">
          <div
            className={`h-3 w-3 rounded-full ${
              connectionState === ConnectionState.Connected
                ? 'bg-green-500'
                : connectionState === ConnectionState.Connecting
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-zinc-600 dark:text-zinc-400">
            {connectionState === ConnectionState.Connected
              ? 'Verbunden'
              : connectionState === ConnectionState.Connecting
              ? 'Verbindet...'
              : 'Getrennt'}
          </span>
        </div>
      </div>

      {isAgentSpeaking && (
        <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
          <div className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />
          <span className="text-sm font-medium">Agent spricht...</span>
        </div>
      )}

      <div className="min-h-[200px] p-4 bg-zinc-50 dark:bg-zinc-800 rounded-md border border-zinc-200 dark:border-zinc-700">
        <p className="text-sm text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">
          {transcription || 'Warten auf Transkription...'}
        </p>
      </div>

      <div className="text-xs text-zinc-500 dark:text-zinc-400">
        Aktive Tracks: {tracks.length}
      </div>

      {/* RoomAudioRenderer spielt automatisch alle Audio-Tracks ab */}
      <RoomAudioRenderer />
    </div>
  );
}

export default function VoiceAgent({
  roomName = 'voice-agent-room',
  participantName = 'user',
}: VoiceAgentProps) {
  const [token, setToken] = useState<string>('');
  const [wsUrl, setWsUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [userStarted, setUserStarted] = useState(false);

  useEffect(() => {
    async function getToken() {
      try {
        setIsLoading(true);
        setError('');

        const response = await fetch('/api/livekit/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            roomName,
            participantName,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Token-Abruf fehlgeschlagen');
        }

        const data = await response.json();
        setToken(data.token);
        setWsUrl(data.url);
      } catch (err) {
        console.error('Fehler beim Abrufen des Tokens:', err);
        setError(err instanceof Error ? err.message : 'Unbekannter Fehler');
      } finally {
        setIsLoading(false);
      }
    }

    getToken();
  }, [roomName, participantName]);

  const handleStartAgent = () => {
    setUserStarted(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="h-8 w-8 border-4 border-zinc-300 border-t-zinc-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-zinc-600 dark:text-zinc-400">Verbindung wird hergestellt...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
        <h3 className="text-lg font-semibold text-red-900 dark:text-red-200 mb-2">
          Fehler
        </h3>
        <p className="text-red-700 dark:text-red-300">{error}</p>
      </div>
    );
  }

  if (!token || !wsUrl) {
    return (
      <div className="p-6 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
        <p className="text-yellow-700 dark:text-yellow-300">
          Token oder URL nicht verfügbar
        </p>
      </div>
    );
  }

  // Zeige Start-Button für User-Geste (AudioContext-Anforderung)
  if (!userStarted) {
    return (
      <div className="flex flex-col gap-4 p-8 bg-white dark:bg-zinc-900 rounded-lg shadow-lg border border-zinc-200 dark:border-zinc-800">
        <div className="text-center">
          <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 mb-2">
            Voice Agent bereit
          </h3>
          <p className="text-zinc-600 dark:text-zinc-400 mb-6">
            Klicken Sie auf Start, um die Verbindung herzustellen und das Mikrofon zu aktivieren.
          </p>
          <button
            onClick={handleStartAgent}
            className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-colors duration-200 text-lg"
          >
            🎤 Voice Agent starten
          </button>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-4">
            Sie werden nach Mikrofon-Zugriff gefragt
          </p>
        </div>
      </div>
    );
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={wsUrl}
      connect={userStarted}
      audio={true}
      video={false}
      className="w-full"
      options={{
        // KRITISCH: Warte länger auf den Agent, bevor Reconnect versucht wird
        disconnectOnPageLeave: false,
        // Erhöhe die Anzahl der Reconnect-Versuche und Wartezeiten
        reconnectPolicy: {
          nextRetryDelayInMs: (context) => {
            // Erste 3 Versuche: Warte länger (Agent braucht Zeit zum Starten)
            if (context.retryCount < 3) {
              return 5000 * (context.retryCount + 1); // 5s, 10s, 15s
            }
            return null; // Danach: Keine weiteren Versuche
          },
        },
      }}
    >
      <VoiceAgentContent />
    </LiveKitRoom>
  );
}

