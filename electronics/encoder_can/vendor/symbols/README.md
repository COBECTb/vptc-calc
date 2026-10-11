# Pinned schematic symbol subset

The six official-library files in this directory are a minimal subset of the
[KiCad symbol libraries, release 9.0.6](https://gitlab.com/kicad/libraries/kicad-symbols/-/tree/9.0.6).
Copyright belongs to the KiCad library contributors. Their license, including
the electronic-design exception, is preserved in `LICENSE-KiCad.md`.

Only symbols used by this board are retained. Inherited symbols have been
expanded with their parent graphics and pins so that the project remains
self-contained and the KiCad library comparison is deterministic. Pin names,
pin numbers, electrical types, and symbol graphics retain the upstream data.
The schematic generator overrides each placed component's value, footprint,
manufacturer, and MPN from the checked electrical specification.

| File | Upstream symbols retained |
|---|---|
| MCU_ST_STM32G4.kicad_sym | STM32G431KBUx, expanded parent |
| Interface_CAN_LIN.kicad_sym | TCAN332G, expanded parent |
| Device.kicad_sym | R, C, Crystal_GND24 |
| Connector_Generic.kicad_sym | Conn_01x04, Conn_01x05 |
| Connector.kicad_sym | TestPoint |
| power.kicad_sym | PWR_FLAG |

`Encoder_CAN.kicad_sym` contains three project-specific symbols with pin
numbering checked against manufacturer datasheets: TMAG5273A2DBVR,
TPS7A2033PDBVR, and PESD5V0S2BT. These parts are not represented by guessed
generic six-/five-/three-pin devices. A copy also lives at the project root for
convenient library editing.

KiCad 10.0.6 is the validation runtime. The official symbols are deliberately
pinned to 9.0.6 rather than being silently replaced when a machine's global
KiCad libraries change. `sym-lib-table` points to these files.
