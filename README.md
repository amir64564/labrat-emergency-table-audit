# LabRat attaches the wrong emergency number

Audit finding for [poidh #1520](https://poidh.xyz/base/bounty/1520) (on-chain bounty id 534).

LabRat's `EmergencyNumbers` table walks countries in a fixed file order and returns the first regex hit, so "Japan and China" and "China and Japan" both get Japan, a snake bite on the way from Thailand to Japan gets Thailand's numbers, and "the US" does not match at all. Several of these answers are already pinned in the project's own golden tests.

- Live write-up: https://amir64564.github.io/labrat-emergency-table-audit/
- Markdown: [REPORT.md](REPORT.md)
- Proof figure: [proof/emergency-table.png](proof/emergency-table.png)
- Reproduction: `python3 repro/repro.py repro/routing-leaves.json` (853 / 853 goldens, then the contrast cases)

Source under audit: [labrat-boar-fork @606923a](https://github.com/r4topunk/labrat-boar-fork/tree/606923a7064c8f176b45123f716c7d82ad234144).
