import { NextRequest, NextResponse } from 'next/server';
import { AccessToken } from 'livekit-server-sdk';

export async function POST(request: NextRequest) {
  try {
    const { roomName, participantName } = await request.json();

    if (!roomName || !participantName) {
      return NextResponse.json(
        { error: 'roomName und participantName sind erforderlich' },
        { status: 400 }
      );
    }

    const apiKey = process.env.LIVEKIT_API_KEY;
    const apiSecret = process.env.LIVEKIT_API_SECRET;

    if (!apiKey || !apiSecret) {
      return NextResponse.json(
        { error: 'LiveKit API-Credentials nicht konfiguriert' },
        { status: 500 }
      );
    }

    // AccessToken erstellen
    const at = new AccessToken(apiKey, apiSecret, {
      identity: participantName,
      // Token ist 10 Stunden gültig
      ttl: '10h',
    });

    // Berechtigungen für den Raum gewähren
    at.addGrant({
      roomJoin: true,
      room: roomName,
      canPublish: true,
      canSubscribe: true,
      canPublishData: true,
    });

    const token = await at.toJwt();

    return NextResponse.json({
      token,
      url: process.env.LIVEKIT_URL || 'ws://localhost:7880',
    });
  } catch (error) {
    console.error('Fehler beim Erstellen des LiveKit-Tokens:', error);
    return NextResponse.json(
      { error: 'Interner Serverfehler' },
      { status: 500 }
    );
  }
}

