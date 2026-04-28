# Systemarchitektur – Übersicht (PlantUML)

Die folgende PlantUML-Datei beschreibt die Systemarchitektur des Projekts und visualisiert die zentralen Komponenten und Datenflüsse:

```plantuml
@startuml
skinparam dpi 120
skinparam nodesep 40
skinparam ranksep 30
skinparam defaultFontSize 10
left to right direction

actor "Caller" as Caller
rectangle "SIP / Asterisk\n(Signaling)" as SIP
rectangle "Media Bridge\n(Transcode)" as Bridge
cloud "LLM / ASR / TTS\n(May be external)" as LLM
database "Audit / Storage\n(transcripts, metrics, CDRs)" as Store
rectangle "Orchestrator\n(ARI/AMI)" as Orchestrator

Caller <-> SIP
note left of SIP
  RTP (full-duplex)
end note

SIP <-> Bridge
note left of Bridge
  RTP
end note

Bridge <-> LLM
note left of LLM
  audio (PCM16 @16k) / TTS (bi-directional)
  (optional VAD)
end note

LLM -[#006400]-> Store : transcripts
Bridge -[#006400]-> Store : metrics
SIP -[#006400]-> Store : CDRs
Orchestrator -[#006400,dashed]-> Store : audit events

LLM -[#0000FF,dashed]-> Orchestrator
Orchestrator -[#0000FF,dashed]-> SIP

note right of LLM
  Trust boundary: treat external LLMs as third-party.
  Apply DPA, encryption in transit & at rest, minimal retention.
end note

note bottom
  Legend: arrows = data flows; dashed blue = control/API; green = stored data
  "full-duplex" = simultaneous bi-directional media streams (RTP both directions)
end note
@enduml
```

**Hinweis:**
- Die Datei `diagrams/llm_dataflow_overview.puml` im Repository enthält diese Architektur als PlantUML-Quelltext.
- Für eine grafische Darstellung kann die Datei mit einem PlantUML-Renderer (z.B. VSCode-Plugin, Online-Renderer) als Diagramm exportiert werden.
