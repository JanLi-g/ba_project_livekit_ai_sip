import { NextResponse } from 'next/server';
import { RoomServiceClient } from 'livekit-server-sdk';

/**
 * SIP Status API
 *
 * Zeigt alle aktiven SIP-Calls und deren Status
 */
export async function GET() {
  try {
    const rawLivekitUrl = process.env.LIVEKIT_URL || process.env.NEXT_PUBLIC_LIVEKIT_URL || 'http://localhost:7880';
    const livekitUrl = rawLivekitUrl.startsWith('ws://')
      ? `http://${rawLivekitUrl.slice(5)}`
      : rawLivekitUrl.startsWith('wss://')
        ? `https://${rawLivekitUrl.slice(6)}`
        : rawLivekitUrl;
    const livekitApiKey = process.env.LIVEKIT_API_KEY;
    const livekitApiSecret = process.env.LIVEKIT_API_SECRET;

    if (!livekitApiKey || !livekitApiSecret) {
      return NextResponse.json(
        {
          error: 'LiveKit-Konfiguration fehlt',
          details: 'LIVEKIT_API_KEY und LIVEKIT_API_SECRET müssen gesetzt sein.'
        },
        { status: 500 }
      );
    }

    const client = new RoomServiceClient(
      livekitUrl,
      livekitApiKey,
      livekitApiSecret
    );

    const rooms = await client.listRooms();

    // Filtere SIP-Calls (Room-Namen beginnen mit "sip-call-")
    const sipCalls = rooms.filter(room => room.name.startsWith('sip-call-'));
    const webCalls = rooms.filter(room => !room.name.startsWith('sip-call-'));

    return NextResponse.json({
      timestamp: new Date().toISOString(),
      summary: {
        totalRooms: rooms.length,
        sipCalls: sipCalls.length,
        webCalls: webCalls.length,
      },
      sipCalls: sipCalls.map(room => ({
        roomName: room.name,
        callId: room.name.replace('sip-call-', ''),
        participants: room.numParticipants,
        createdAt: new Date(Number(room.creationTime) * 1000).toISOString(),
        durationSeconds: Math.floor(Date.now() / 1000 - Number(room.creationTime)),
      })),
      webCalls: webCalls.map(room => ({
        roomName: room.name,
        participants: room.numParticipants,
        createdAt: new Date(Number(room.creationTime) * 1000).toISOString(),
      })),
    });
  } catch (error) {
    console.error('❌ Status-Abruf Fehler:', error);
    return NextResponse.json(
      {
        error: 'Status nicht verfügbar',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

