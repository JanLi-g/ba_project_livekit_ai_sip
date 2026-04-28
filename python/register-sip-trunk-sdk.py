#!/usr/bin/env python3
"""
Registriert einen SIP-Trunk bei LiveKit über die SDK
(Aktualisiert für neue LiveKit API)
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from livekit import api
from livekit.protocol import sip as sip_proto


load_dotenv(".env.local")


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"❌ Fehlende Umgebungsvariable: {name}")
        sys.exit(1)
    return value


# LiveKit Credentials
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "http://localhost:7880")
LIVEKIT_API_KEY = require_env("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = require_env("LIVEKIT_API_SECRET")
SIP_DID_NUMBER = require_env("SIP_DID_NUMBER")
SIP_PROVIDER_USERNAME = require_env("SIP_PROVIDER_USERNAME")
SIP_PROVIDER_PASSWORD = require_env("SIP_PROVIDER_PASSWORD")
SIP_PROVIDER_DOMAIN = os.getenv("SIP_PROVIDER_DOMAIN", "sip.plusnet.de")


async def register_plusnet_trunk():
    """Registriert den Plusnet SIP-Trunk"""

    print("")
    print("=" * 60)
    print("LiveKit SIP Trunk Registration (Plusnet)")
    print("=" * 60)
    print("")

    # Erstelle LiveKit API Client
    print("🔐 Verbinde mit LiveKit API...")
    lk_api = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET
    )

    print("📞 Registriere Plusnet SIP-Trunk...")
    print(f"   URL: {LIVEKIT_URL}")
    print(f"   Domain: {SIP_PROVIDER_DOMAIN}")
    print(f"   Nummer: {SIP_DID_NUMBER}")
    print(f"   Provider: Asterisk (lokal)")
    print("")

    try:
        # Zuerst: Liste existierende Trunks
        print("📋 Prüfe existierende Trunks...")
        existing_trunks = await lk_api.sip.list_inbound_trunk(
            sip_proto.ListSIPInboundTrunkRequest()
        )

        trunk_id = None
        for t in existing_trunks.items:
            print(f"   Gefunden: {t.name} (ID: {t.sip_trunk_id})")
            if "Asterisk" in t.name or "Plusnet" in t.name:
                trunk_id = t.sip_trunk_id
                print(f"   -> Verwende existierenden Trunk: {trunk_id}")

        # Erstelle Inbound Trunk (für eingehende Anrufe von Asterisk)
        if not trunk_id:
            print("\n📥 Erstelle Inbound Trunk...")
            inbound_trunk = await lk_api.sip.create_inbound_trunk(
                sip_proto.CreateSIPInboundTrunkRequest(
                    trunk=sip_proto.SIPInboundTrunkInfo(
                        name="Asterisk-Plusnet Inbound",
                        # Leere numbers = akzeptiere alle eingehenden Nummern
                        numbers=[SIP_DID_NUMBER],
                        # Erlaubte Adressen: Asterisk Container + alle (für Tests)
                        allowed_addresses=["172.20.0.0/16", "0.0.0.0/0"],
                        # Keine Auth nötig von Asterisk (lokales Netz)
                        auth_username=SIP_PROVIDER_USERNAME,
                        auth_password=SIP_PROVIDER_PASSWORD,
                        metadata='{"provider":"plusnet","via":"asterisk"}'
                    )
                )
            )
            trunk_id = inbound_trunk.sip_trunk_id
            print(f"✅ Inbound Trunk erstellt!")
            print(f"   Trunk ID: {trunk_id}")
            print(f"   Name: {inbound_trunk.name}")

        # Prüfe existierende Dispatch Rules
        print("\n📋 Prüfe existierende Dispatch Rules...")
        existing_rules = await lk_api.sip.list_dispatch_rule(
            sip_proto.ListSIPDispatchRuleRequest()
        )

        rule_exists = False
        for r in existing_rules.items:
            print(f"   Gefunden: {r.name} (ID: {r.sip_dispatch_rule_id})")
            if trunk_id and trunk_id in r.trunk_ids:
                rule_exists = True
                print(f"   -> Dispatch Rule existiert bereits")

        # Erstelle Dispatch Rule (leitet Anrufe an einen Room)
        if not rule_exists:
            print("\n📌 Erstelle Dispatch Rule...")
            dispatch_rule = await lk_api.sip.create_dispatch_rule(
                sip_proto.CreateSIPDispatchRuleRequest(
                    trunk_ids=[trunk_id],
                    rule=sip_proto.SIPDispatchRule(
                        dispatch_rule_direct=sip_proto.SIPDispatchRuleDirect(
                            room_name="sip-call",  # Fester Room-Name
                            pin=""  # Kein PIN erforderlich
                        )
                    ),
                    name="Plusnet to Agent Room",
                    metadata='{"source":"sip","provider":"plusnet"}'
                )
            )
            print(f"✅ Dispatch Rule erstellt!")
            print(f"   Rule ID: {dispatch_rule.sip_dispatch_rule_id}")

        # Zeige finale Konfiguration
        print("\n" + "=" * 60)
        print("📋 Finale SIP-Konfiguration:")
        print("=" * 60)

        print("\n🔹 Inbound Trunks:")
        trunks = await lk_api.sip.list_inbound_trunk(
            sip_proto.ListSIPInboundTrunkRequest()
        )
        for t in trunks.items:
            print(f"   - {t.name}")
            print(f"     ID: {t.sip_trunk_id}")
            print(f"     Nummern: {t.numbers}")
            print(f"     Erlaubte Adressen: {t.allowed_addresses}")

        print("\n🔹 Dispatch Rules:")
        rules = await lk_api.sip.list_dispatch_rule(
            sip_proto.ListSIPDispatchRuleRequest()
        )
        for r in rules.items:
            print(f"   - {r.name}")
            print(f"     ID: {r.sip_dispatch_rule_id}")
            print(f"     Trunk IDs: {r.trunk_ids}")

        print("")
        print("=" * 60)
        print(f"✅ Fertig! Anrufe an {SIP_DID_NUMBER} werden")
        print("   an den Room 'sip-call' weitergeleitet.")
        print("=" * 60)
        print("")

    except Exception as e:
        print(f"❌ Fehler: {e}")
        print("")
        import traceback
        traceback.print_exc()

    finally:
        await lk_api.aclose()


if __name__ == "__main__":
    asyncio.run(register_plusnet_trunk())
