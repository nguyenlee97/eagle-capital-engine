# Eagle Capital Engine

Sub-project of **Project Eagle GTA** ? integrating WSR (Wall Street Raider) + CapLab (Capitalism Lab) as native financial simulation modules.

## Architecture

**Two-Stage Native Merger:**
- **Stage A1 (Done):** DB extraction ? 54 countries, 70 industries, 1590 corps ? `eagle_wsr_caplab_db.json` (2MB)
- **Stage A2 (In Progress):** Native Bridge ? Python IPC reads WSR/CapLab process memory, exposes financial data to Eagle Phone OS

## WSR RE Summary
- PowerBASIC 32-bit, no ASLR (`ImageBase 0x00400000`)
- Headless patch: `VA 0x0041DC16: 74 26 ? EB 26`
- Time offsets: `YEAR@ 0x006B6CC8`, `QTR@ 0x006B6BE8`, `SUBTICK@ 0x006B6AA8`
- Money: `CASH##(1)` = 10-byte EXT at entity array ($ Millions)

## CapLab RE Summary
- MSVC C++ 32-bit, SDL2 RGB565
- 56 DBF tables (1STD.SET, SERVICE_COMPANIES, FBUILDSTD, ...)
- `Info::next_day()` identified, `PersonInfo+0x50` = double (net worth)

## Files
| File | Description |
|------|-------------|
| `extract_wsr_caplab_db.py` | DB extraction script (32KB) |
| `data/eagle_wsr_caplab_db.json` | Extracted dataset (2MB) |
| `EAGLE_CAPITAL_ENGINE_SPEC.md` | Architecture spec |
| `AGENTS.md` | Agent workflow |
| `docs/supplementary_math_formulas_re.md` | RE math reference |

## Jira Tickets
- SCRUM-212: Research WSR + CapLab (Done)
- SCRUM-213: Stage A1 DB Extraction (Done)
- SCRUM-214: Architecture Blueprint (Done)
- SCRUM-215: Stage A2 Native Bridge Implementation (In Progress)

## Related Projects
- [eagle-literature-studio](https://github.com/nguyenlee97/eagle-literature-studio)
- [eagle-story-quest](https://github.com/nguyenlee97/eagle-story-quest)
