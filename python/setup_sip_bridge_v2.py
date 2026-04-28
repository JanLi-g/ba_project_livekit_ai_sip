#!/usr/bin/env python3
"""
LiveKit SIP Bridge Setup - Vollstaendige Integration
Registriert SIP-Trunk und erstellt Dispatch-Rules fuer Plusnet -> Voice Agent
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from livekit import api

# Lade .env.local
load_dotenv(".env.local")


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"[ERROR] Fehlende Umgebungsvariable: {name}")
        sys.exit(1)
    return value

# LiveKit Credentials
# WICHTIG: Für lokale Ausführung localhost verwenden, nicht den Docker-Namen "livekit"
LIVEKIT_URL_FROM_ENV = os.getenv("LIVEKIT_URL", "")
if LIVEKIT_URL_FROM_ENV.startswith("ws://"):
    LIVEKIT_URL = "http://" + LIVEKIT_URL_FROM_ENV.removeprefix("ws://")
elif LIVEKIT_URL_FROM_ENV.startswith("wss://"):
    LIVEKIT_URL = "https://" + LIVEKIT_URL_FROM_ENV.removeprefix("wss://")
else:
    LIVEKIT_URL = LIVEKIT_URL_FROM_ENV or "http://localhost:7880"

LIVEKIT_API_KEY = require_env("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = require_env("LIVEKIT_API_SECRET")

# Plusnet SIP Credentials (aus .env.local)
PLUSNET_DOMAIN = os.getenv("SIP_PROVIDER_DOMAIN", "sip.plusnet.de")
PLUSNET_USERNAME = require_env("SIP_PROVIDER_USERNAME")
PLUSNET_PASSWORD = require_env("SIP_PROVIDER_PASSWORD")
PLUSNET_NUMBER = require_env("SIP_DID_NUMBER")


async def cleanup_existing_config(lk_api):
    """Entfernt alte SIP-Konfigurationen"""
    print("\n[CLEANUP] Raeume alte Konfigurationen auf...")

    try:
        # Loesche alle Dispatch Rules
        rules = await lk_api.sip.list_dispatch_rule(
            api.ListSIPDispatchRuleRequest()
        )
        for rule in rules.items:
            print(f"   [DELETE] Dispatch Rule: {rule.sip_dispatch_rule_id}")
            await lk_api.sip.delete_dispatch_rule(
                api.DeleteSIPDispatchRuleRequest(
                    sip_dispatch_rule_id=rule.sip_dispatch_rule_id
                )
            )

        # Loesche alle Inbound Trunks
        inbound_trunks = await lk_api.sip.list_inbound_trunk(
            api.ListSIPInboundTrunkRequest()
        )
        for trunk in inbound_trunks.items:
            trunk_id = getattr(trunk, 'sip_inbound_trunk_id', None) or getattr(trunk, 'sip_trunk_id', None)
            print(f"   [DELETE] Inbound Trunk: {trunk_id}")
            # Workaround: Nutze delete_sip_trunk, da delete_inbound_trunk nicht existiert
            await lk_api.sip.delete_sip_trunk(
                api.DeleteSIPTrunkRequest(sip_trunk_id=trunk_id)
            )

        # Loesche alle Outbound Trunks
        outbound_trunks = await lk_api.sip.list_outbound_trunk(
            api.ListSIPOutboundTrunkRequest()
        )
        for trunk in outbound_trunks.items:
            print(f"   [DELETE] Outbound Trunk: {trunk.sip_outbound_trunk_id}")
            await lk_api.sip.delete_outbound_trunk(
                api.DeleteSIPOutboundTrunkRequest(sip_outbound_trunk_id=trunk.sip_outbound_trunk_id)
            )

        print("   [OK] Cleanup abgeschlossen")
    except Exception as e:
        print(f"   [WARNING] Cleanup Fehler (kann ignoriert werden): {e}")


async def setup_sip_inbound_trunk(lk_api):
    """Registriert den Plusnet Inbound SIP-Trunk (empfaengt Anrufe)"""
    print("\n[SIP-IN] Registriere Plusnet Inbound SIP-Trunk...")
    print(f"   Domain: {PLUSNET_DOMAIN}")
    print(f"   Nummer: {PLUSNET_NUMBER}")
    print(f"   Username: {PLUSNET_USERNAME}")

    try:
        inbound_trunk = await lk_api.sip.create_sip_inbound_trunk(
            api.CreateSIPInboundTrunkRequest(
                trunk=api.SIPInboundTrunkInfo(
                    name="Plusnet Inbound",
                    numbers=[PLUSNET_NUMBER],
                    allowed_addresses=[],  # Leer = von ueberall (spaeter Plusnet IPs)
                    allowed_numbers=[],     # Leer = alle Anrufer erlaubt
                    auth_username=PLUSNET_USERNAME,
                    auth_password=PLUSNET_PASSWORD,
                    metadata='{"provider":"plusnet","type":"inbound"}'
                )
            )
        )

        # Robust: Trunk-ID ausgeben, egal wie das Attribut heißt
        trunk_id = getattr(inbound_trunk, 'sip_inbound_trunk_id', None) or getattr(inbound_trunk, 'sip_trunk_id', None)
        print(f"   [OK] Inbound-Trunk registriert: {trunk_id}")
        return trunk_id

    except Exception as e:
        print(f"   [ERROR] Fehler beim Registrieren: {e}")
        raise


async def setup_sip_outbound_trunk(lk_api):
    """Registriert den Plusnet Outbound SIP-Trunk (fuer ausgehende Anrufe - optional)"""
    print("\n[SIP-OUT] Registriere Plusnet Outbound SIP-Trunk (optional)...")

    try:
        outbound_trunk = await lk_api.sip.create_sip_outbound_trunk(
            api.CreateSIPOutboundTrunkRequest(
                trunk=api.SIPOutboundTrunkInfo(
                    name="Plusnet Outbound",
                    address=PLUSNET_DOMAIN,
                    numbers=[PLUSNET_NUMBER],
                    auth_username=PLUSNET_USERNAME,
                    auth_password=PLUSNET_PASSWORD,
                    metadata='{"provider":"plusnet","type":"outbound"}'
                )
            )
        )

        print(f"   [OK] Outbound-Trunk registriert: {outbound_trunk.sip_outbound_trunk_id}")
        return outbound_trunk.sip_outbound_trunk_id

    except Exception as e:
        print(f"   [WARNING] Outbound-Trunk optional: {e}")
        return None


async def setup_dispatch_rule(lk_api, inbound_trunk_id):
    """Erstellt Dispatch-Rule: Eingehende Anrufe -> Voice Agent Room"""
    print("\n[DISPATCH] Erstelle Dispatch-Rule (Anruf -> Agent)...")

    try:
        rule = await lk_api.sip.create_sip_dispatch_rule(
            api.CreateSIPDispatchRuleRequest(
                rule=api.SIPDispatchRule(
                    dispatch_rule_direct=api.SIPDispatchRuleDirect(
                        room_name="sip-call-{callID}",
                        pin=""
                    )
                )
            )
        )

        print(f"   [OK] Dispatch-Rule erstellt: {rule.sip_dispatch_rule_id}")
        print(f"   [CONFIG] Konfiguration:")
        print(f"      * Eingehender Anruf -> Room: sip-call-{{callID}}")
        print(f"      * Room Preset: VOICE_AGENT")
        print(f"      * Caller Identity: caller-{{number}}")

        return rule.sip_dispatch_rule_id

    except Exception as e:
        print(f"   [ERROR] Fehler bei Dispatch-Rule: {e}")
        raise


async def verify_configuration(lk_api):
    """Ueberprueft die aktuelle Konfiguration"""
    print("\n[VERIFY] Verifiziere Konfiguration...")

    # Liste alle Inbound Trunks
    inbound = await lk_api.sip.list_inbound_trunk(
        api.ListSIPInboundTrunkRequest()
    )
    print(f"\n[INBOUND] Inbound-Trunks: {len(inbound.items)}")
    for trunk in inbound.items:
        print(f"   * {trunk.name} (ID: {trunk.sip_trunk_id})")
        print(f"     Nummern: {', '.join(trunk.numbers)}")

    # Liste alle Outbound Trunks
    outbound = await lk_api.sip.list_outbound_trunk(
        api.ListSIPOutboundTrunkRequest()
    )
    print(f"\n[OUTBOUND] Outbound-Trunks: {len(outbound.items)}")
    for trunk in outbound.items:
        print(f"   * {trunk.name} (ID: {trunk.sip_trunk_id})")
        print(f"     Adresse: {trunk.address}")

    # Liste alle Dispatch Rules
    rules = await lk_api.sip.list_dispatch_rule(
        api.ListSIPDispatchRuleRequest()
    )
    print(f"\n[DISPATCH] Dispatch-Rules: {len(rules.items)}")
    for rule in rules.items:
        # Zeige ID und ggf. weitere Infos an
        print(f"   * (ID: {getattr(rule, 'sip_dispatch_rule_id', '?')})")
        # Zeige Room-Name, falls möglich
        drd = getattr(rule, 'dispatch_rule_direct', None)
        if drd and hasattr(drd, 'room_name'):
            print(f"     -> Room: {drd.room_name}")


async def delete_all_inbound_trunks(lk_api):
    """Löscht alle vorhandenen Inbound SIP-Trunks (Workaround für API-Bugs)"""
    trunks = await lk_api.sip.list_inbound_trunk(api.ListSIPInboundTrunkRequest())
    for trunk in trunks.items:
        trunk_id = getattr(trunk, 'sip_inbound_trunk_id', None) or getattr(trunk, 'sip_trunk_id', None)
        print(f"[FORCE] Lösche Inbound-Trunk: {trunk_id}")
        try:
            await lk_api.sip.delete_sip_trunk(
                api.DeleteSIPTrunkRequest(sip_trunk_id=trunk_id)
            )
        except Exception as e:
            print(f"[WARN] Konnte Trunk nicht löschen: {e}")


async def main():
    """Hauptfunktion"""
    print("")
    print("=" * 70)
    print("  LiveKit SIP Bridge Setup - Plusnet -> Voice Agent")
    print("=" * 70)

    # Validiere Konfiguration
    if not PLUSNET_USERNAME or not PLUSNET_PASSWORD:
        print("\n[ERROR] Plusnet-Zugangsdaten fehlen in .env.local")
        print("   Benoetigt: PLUSNET_USERNAME, PLUSNET_PASSWORD, PLUSNET_NUMBER")
        sys.exit(1)

    print(f"\n[CONNECT] Verbinde mit LiveKit: {LIVEKIT_URL}")

    # Erstelle API Client
    lk_api = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET
    )

    try:
        # 0. Lösche alle Inbound-Trunks explizit (Workaround für API-Bugs)
        await delete_all_inbound_trunks(lk_api)

        # 1. Cleanup (optional - auskommentiert um bestehende Config zu behalten)
        await cleanup_existing_config(lk_api)

        # 2. Erstelle Inbound-Trunk (empfaengt Anrufe von Plusnet)
        inbound_trunk_id = await setup_sip_inbound_trunk(lk_api)

        # 3. Erstelle Outbound-Trunk (optional - fuer ausgehende Anrufe)
        outbound_trunk_id = await setup_sip_outbound_trunk(lk_api)

        # 4. Erstelle Dispatch-Rule (leitet eingehende Anrufe an Agent weiter)
        rule_id = await setup_dispatch_rule(lk_api, inbound_trunk_id)

        # 5. Verifiziere
        await verify_configuration(lk_api)

        print("\n" + "=" * 70)
        print("  [SUCCESS] SETUP ERFOLGREICH!")
        print("=" * 70)
        print(f"\n[PHONE] Die Telefonnummer {PLUSNET_NUMBER} ist jetzt live!")
        print("\n[NEXT] Naechste Schritte:")
        print("   1. Starte den Agent Worker:")
        print("      -> python python/agent_worker.py")
        print("")
        print("   2. Rufe an:")
        print(f"      -> {PLUSNET_NUMBER}")
        print("")
        print("   3. Der Agent antwortet automatisch!")
        print("")
        print("[LOGS] Logs ansehen:")
        print("   * LiveKit: docker logs livekit-sip -f")
        print("   * Agent: Konsolen-Ausgabe von agent_worker.py")
        print("")
        print("=" * 70)
        print("")

    except Exception as e:
        print(f"\n[ERROR] Setup fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        await lk_api.aclose()


if __name__ == "__main__":
    asyncio.run(main())

