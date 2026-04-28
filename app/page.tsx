import Image from "next/image";
import VoiceAgent from "./components/VoiceAgent";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black p-8">
      <main className="flex w-full max-w-4xl flex-col gap-8">
        <div className="flex items-center gap-4">
          <Image
            className="dark:invert"
            src="/next.svg"
            alt="Next.js logo"
            width={100}
            height={20}
            priority
          />
          <h1 className="text-3xl font-semibold text-black dark:text-zinc-50">
            LiveKit Voice Agent
          </h1>
        </div>

        <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
            Audio-Pipeline mit LLM-Integration
          </h2>
          <p className="text-zinc-600 dark:text-zinc-400 mb-6">
            Dieser Prototyp demonstriert eine Echtzeit-Audio-Pipeline für Voice-Agenten.
            Die KI kann Ihre Spracheingaben verarbeiten und darauf antworten.
          </p>

          <VoiceAgent
            roomName="voice-agent-room"
            participantName="user"
          />
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-6">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-2">
            📋 Nächste Schritte
          </h3>
          <ul className="list-disc list-inside text-blue-700 dark:text-blue-300 space-y-2">
            <li>LiveKit Server lokal starten oder Cloud-Instanz verwenden</li>
            <li>Agent-Worker implementieren (Python oder Node.js)</li>
            <li>OpenAI API-Key in .env.local konfigurieren</li>
            <li>SIP-Integration für Telefon-Calls einrichten (optional)</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
