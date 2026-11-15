# LabRat's emergency-number table returns the first listed country, not the one you asked about

**poidh bounty [#1520](https://poidh.xyz/base/bounty/1520)** (on-chain id 534) · audit of RatLab / LabRat, research record 1.1.2  
**Date:** 15 November 2026 (Asia/Calcutta)  
**Scope:** one finding, in the shipped health-gate path  
**Sources:** [labrat-boar-fork](https://github.com/r4topunk/labrat-boar-fork) `@606923a`, plus the project's own golden file `routing-leaves.json`

This is a new finding. It is not a rediscovery of the already-claimed HealthGate issues (eval-runner `local-` pack ids, provenance licensing, spelled-out units, the 39.5 °C conversion, the 42 °C cap, or self-harm). Those live in other parts of the gate. This one is `EmergencyNumbers.kt`.

## The finding

When LabRat refuses to give health advice from memory, it is supposed to attach the emergency numbers for the country the question names. The author added that table because a no-source health answer had already given the *wrong* country's numbers (`EmergencyNumbers.kt` lines 3–7).

The implementation walks a hard-coded list in a fixed order and returns the **first row whose regex matches anywhere in the question**:

```kotlin
val hit = COUNTRIES.firstOrNull { it.names.containsMatchIn(text) } ?: return null
return "Emergency — ${hit.en}"
```

Thailand is first in the table. Japan is before China. The United Kingdom is before Australia. Sentence order does not matter. The country the user is asking about does not matter. A second country in the same question is dropped.

`HealthGate.fixedText` is the only production caller (`HealthGate.kt:42`). It fires when the turn is classified as a health question and no health-pack passage was kept. Questions that contain the word "emergency" are health questions (`QueryContext.kt`, `HEALTH` includes `emergency`). The author's own comment says a question like "What emergency numbers do I need in Thailand?" found nothing in the library, which is why the table exists. So this is exactly the path those questions take.

## Evidence

A Python port of the same patterns and the same first-hit walk reproduces **all 853** `emergencyLine` goldens in `routing-leaves.json` with zero mismatches. The project's own goldens already pin several of the failures. New contrast questions, run on the same function, make the table-order rule obvious.

| Question | What the function returns | What it should return |
|---|---|---|
| "What are the emergency numbers in Japan and China?" | **Japan** (110 / 119). China is omitted. *Pinned in the golden file.* | Both countries, or at least a combined answer |
| "What are the emergency numbers in China and Japan?" | **Japan again.** Reversing the sentence does not change the result. | Both, or China first if sentence order were used |
| "I'm flying from Thailand to Japan. I was bitten by a snake. What number do I call in Japan?" | **Thailand** (191 / 1669 / 199 / 1155) | Japan (110 / 119) |
| "I have chest pain in the United States after a trip to Thailand. What should I do?" | **Thailand**, not 911 | United States (911) |
| "The Consulate-General of the People's Republic of China in Chiang Mai is the diplomatic mission of China to Chiang Mai and Northern Thailand." | **Thailand.** *Pinned in the golden file.* The subject of the sentence is China. | China, or no line if this is not an emergency question |
| "New South Wales is Australia, not the United Kingdom; Wales alone is still the UK" | **United Kingdom.** *Pinned in the golden file.* | Australia, or both, given the contrast |
| "Which emergency numbers should I know in the US?" | **None.** The generic fallback then says "911 in the US, 112 in Europe" and never adds the dedicated US line. | United States (911), as "the U.S." already does |
| "Which emergency numbers should I know in the U.S.?" | United States: 911 | Correct (control) |

The "in the US" miss is a separate hole in the United States regex:

```text
\b(united states|usa|estados unidos)\b|\bu\.s\.(?:a\.?)?(?![a-z])
```

It accepts "USA", "U.S.", "U.S.A." and "United States", but not the usual unpunctuated form "the US". "America" is also absent. A bare `\bus\b` would be the wrong fix — it would match the pronoun in "tell us" — but `\bthe us\b` / `\bin the us\b` would cover the common phrasing without that collision.

Related, and weaker: the same United States regex fires on "1 u.s. dollar equals 150 yen; …" and returns "Emergency — United States: 911." That case is also pinned in the golden file. It only reaches a user if the health gate also fires on that turn, so it is a property of the matcher, not a demonstrated product path.

The function also returns a country line for any text that merely *mentions* a listed name, including "What is the capital of Australia?" and "Is tipping expected in restaurants in Portugal?" (both pinned). Those two are not health questions, so `fixedText` does not use the result. They still show that the matcher has no notion of "this question is asking about this country."

## Why it matters

This is the safety fallback: the app has already decided it will not answer from memory, and the one factual line it adds is the emergency number. Attaching the *wrong* country's numbers is worse than attaching none. The generic `NO_SOURCE` text already says "911 in the US, 112 in Europe." A Thailand line on a question about a snake bite *in Japan*, or on chest pain *in the United States*, can send someone to a number that does not exist where they are.

The feature was written specifically to stop the model giving the wrong country's numbers. The table-order walk reintroduces that failure for any question that names more than one listed country, and the golden tests have frozen several of those answers in place.

## A practical fix

1. Collect every country the text actually names, not the first row in the file.
2. Prefer a locative ("in Japan", "in the United States", "for Japan") over a mere mention ("after a trip to Thailand", "not the United Kingdom").
3. If more than one country still remains, list all of them. Do not pick a winner by file order.
4. Add `\bthe us\b` / `\bin the us\b` so "the US" matches the same way "the U.S." does. Do not add a bare `\bus\b`.
5. Keep currency phrases such as "u.s. dollar" from counting as a country hit.
6. Update the goldens that currently pin Japan-only for "Japan and China", Thailand for the China-in-Chiang-Mai sentence, and the UK for the "NSW is Australia, not the United Kingdom" contrast.

## Limits

- I did not run the 3 GB APK on a phone. `EmergencyNumbers.emergencyNumbersLine` is a pure function; the 853 golden cases and the contrast questions above are a reproduction of that function, which is what `HealthGate.fixedText` concatenates onto the refusal text.
- I am not claiming a new HealthGate classification bug. "What are the emergency numbers in Japan and China?" is a health question because it contains "emergency", which is by design.
- I have not measured how often multi-country questions appear in DEVICE-FINAL. The intended use of this table *is* "what emergency numbers do I need in X?", and the Japan/China golden is already such a question.

## How to reproduce

```bash
python3 repro/repro.py repro/routing-leaves.json
```

The script must report `853 checked, 0 mismatches`, then print the contrast cases in the table above.

## Licence

The write-up is CC BY 4.0. `repro.py` is MIT. LabRat itself is MIT; `routing-leaves.json` is copied from labrat-boar-fork for the golden check.
