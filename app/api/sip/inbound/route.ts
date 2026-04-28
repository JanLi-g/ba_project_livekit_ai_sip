import { NextRequest, NextResponse } from 'next/server';
import { AccessToken } from 'livekit-server-sdk';

/**
 * SIP Inbound Handler
 *
 * Wird von LiveKit SIP Bridge aufgerufen, wenn ein SIP-Call eingeht.
 * Erstellt einen LiveKit Room und gibt Token zurück.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { from, to, callId } = body;
    const livekitApiKey = process.env.LIVEKIT_API_KEY;
    const livekitApiSecret = process.env.LIVEKIT_API_SECRET;
    const rawLivekitUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL || process.env.LIVEKIT_URL || 'ws://localhost:7880';
    const livekitUrl = rawLivekitUrl.startsWith('http://')
      ? `ws://${rawLivekitUrl.slice(7)}`
      : rawLivekitUrl.startsWith('https://')
        ? `wss://${rawLivekitUrl.slice(8)}`
        : rawLivekitUrl;

    if (!livekitApiKey || !livekitApiSecret) {
      return NextResponse.json(
        {
          error: 'LiveKit-Konfiguration fehlt',
          details: 'LIVEKIT_API_KEY und LIVEKIT_API_SECRET müssen gesetzt sein.'
        },
        { status: 500 }
      );
    }

    console.log('📞 Eingehender SIP-Call:', {
      from,
      to,
      callId,
      timestamp: new Date().toISOString()
    });

    // Erstelle eindeutigen Room-Namen für SIP-Call
    const roomName = `sip-call-${callId || Date.now()}`;
    const participantName = `caller-${from}`;

    // Erstelle LiveKit Token für SIP-Bridge
    const token = new AccessToken(
      livekitApiKey,
      livekitApiSecret,
      {
        identity: participantName,
        name: `SIP Caller ${from}`,
      }
    );

    token.addGrant({
      roomJoin: true,
      room: roomName,
      canPublish: true,
      canSubscribe: true,
      canPublishData: true,
    });

    const jwt = token.toJwt();

    console.log('✅ LiveKit Room erstellt:', {
      roomName,
      participantName,
      wsUrl: livekitUrl
    });

    // Rückgabe an LiveKit SIP Bridge
    return NextResponse.json({
      roomName,
      token: jwt,
      participantName,
      wsUrl: livekitUrl,
    });
  } catch (error) {
    console.error('❌ SIP-Inbound-Fehler:', error);
    return NextResponse.json(
      {
        error: 'SIP-Call konnte nicht verarbeitet werden',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

/**
 * GET-Endpunkt für Status-Check
 */
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    service: 'SIP Inbound Handler',
    timestamp: new Date().toISOString()
  });
}

