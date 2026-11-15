#!/usr/bin/env python3
"""Reproduce LabRat's EmergencyNumbers.emergencyNumbersLine.

The country table and first-hit-in-table-order walk are copied from
labrat-boar-fork android-native/engine/src/main/java/team/sopa/boar/engine/routing/EmergencyNumbers.kt
at commit 0 of the public default branch used for this audit (2026-11-15).

Word boundaries follow the project's JsRegex translator: JS \\b is an ASCII
[A-Za-z0-9_] boundary, not a Unicode one.

If routing-leaves.json is passed as the first argument (or found next to this
file, or at the default path inside a labrat-boar-fork checkout), every golden
emergencyLine case is checked.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

W = r"[A-Za-z0-9_]"
BOUNDARY = rf"(?:(?<={W})(?!{W})|(?<!{W})(?={W}))"


def translate(source: str, flags: str = "") -> str:
    sb: list[str] = []
    if "i" in flags:
        sb.append("(?iu)" if ("u" in flags or any(ord(c) > 127 for c in source)) else "(?i)")
    in_class = False
    i = 0
    while i < len(source):
        c = source[i]
        if c == "\\":
            n = source[i + 1]
            if not in_class and n == "b":
                sb.append(BOUNDARY)
            elif not in_class and n == "s":
                sb.append(r"[\t\n\f\r ]")
            else:
                sb.append(c + n)
            i += 2
            continue
        if in_class:
            if c == "]":
                in_class = False
            sb.append(c)
        else:
            if c == "[":
                in_class = True
                sb.append(c)
            elif c == "$":
                sb.append(r"\Z")
            else:
                sb.append(c)
        i += 1
    return "".join(sb)


def jsre(source: str, flags: str = "") -> re.Pattern:
    return re.compile(translate(source, flags))


# EmergencyNumbers.kt COUNTRIES, in the same order, with the same patterns.
COUNTRIES = [
    (r"\b(thailand|tailandia|bangkok)\b", "Thailand: police 191, ambulance 1669, fire 199, tourist police 1155 (English-speaking)."),
    (r"\b(brazil|brasil)\b", "Brazil: police 190, ambulance (SAMU) 192, fire 193."),
    (r"\b(portugal)\b", "Portugal: 112 (police, ambulance and fire)."),
    (r"\b(spain)\b", "Spain: 112 (all emergencies)."),
    (r"\b(france|franca)\b", "France: 112, or ambulance (SAMU) 15, police 17, fire 18."),
    (r"\b(germany)\b", "Germany: ambulance and fire 112, police 110."),
    (r"\b(italy|italia)\b", "Italy: 112 (all emergencies)."),
    (r"\b(united kingdom|uk|england|scotland|reino unido|inglaterra|escocia)\b|(?<!new south )\bwales\b", "United Kingdom: 999 or 112."),
    (r"\b(united states|usa|estados unidos)\b|\bu\.s\.(?:a\.?)?(?![a-z])", "United States: 911."),
    (r"\b(canada|canad[áa])\b", "Canada: 911."),
    (r"\b(mexico|m[ée]xico)\b", "Mexico: 911."),
    (r"\b(argentina)\b", "Argentina: 911 (police), ambulance 107, fire 100."),
    (r"\b(japan)\b", "Japan: police 110, fire and ambulance 119."),
    (r"\b(china)\b", "China: police 110, ambulance 120, fire 119."),
    (r"\b(south korea)\b|(?<!north\s)\bkorea\b", "South Korea: police 112, fire and ambulance 119."),
    (r"(?<![a-zà-ÿ])india\b", "India: 112 (all emergencies)."),
    (r"\b(australia|new south wales)\b", "Australia: 000 (112 also works from mobile phones)."),
    (r"\b(new zealand)\b", "New Zealand: 111."),
    (r"\b(vietnam)\b", "Vietnam: police 113, fire 114, ambulance 115."),
    (r"\b(philippines|filipinas)\b", "Philippines: 911."),
    (r"\b(turkey|t[üu]rkiye)\b", "Turkey: 112 (all emergencies)."),
]

COMPILED = [(jsre(p, "i"), line) for p, line in COUNTRIES]


def emergency_numbers_line(text: str) -> str | None:
    """Same walk as EmergencyNumbers.emergencyNumbersLine: first table row that matches."""
    for rx, line in COMPILED:
        if rx.search(text):
            return "Emergency — " + line
    return None


NEW_CASES = [
    "What are the emergency numbers in Japan and China?",
    "What are the emergency numbers in China and Japan?",
    "I'm flying from Thailand to Japan. I was bitten by a snake. What number do I call in Japan?",
    "I have chest pain in the United States after a trip to Thailand. What should I do?",
    "Which emergency numbers should I know in the US?",
    "Which emergency numbers should I know in the U.S.?",
    "Emergency numbers in the US?",
    "What emergency numbers should I know in America?",
    "The Consulate-General of the People's Republic of China in Chiang Mai is the diplomatic mission of China to Chiang Mai and Northern Thailand.",
    "New South Wales is Australia, not the United Kingdom; Wales alone is still the UK",
    "1 u.s. dollar equals 150 yen; dinner was 12.000 yen with 10% service",
    "What is the capital of Australia?",
]


def check_goldens(path: Path) -> tuple[int, int]:
    data = json.loads(path.read_text())
    rows = data["emergencyLine"]
    bad = 0
    for row in rows:
        got = emergency_numbers_line(row["q"])
        if got != row["out"]:
            bad += 1
            print("GOLDEN MISMATCH")
            print("  q:  ", row["q"][:200])
            print("  exp:", row["out"])
            print("  got:", got)
    return len(rows), bad


def main() -> int:
    golden = None
    if len(sys.argv) > 1:
        golden = Path(sys.argv[1])
    else:
        for cand in [
            Path(__file__).with_name("routing-leaves.json"),
            Path("/tmp/boar/labrat-boar-fork/android-native/engine/src/test/resources/golden/routing-leaves.json"),
        ]:
            if cand.is_file():
                golden = cand
                break

    if golden:
        n, bad = check_goldens(golden)
        print(f"Golden emergencyLine cases: {n} checked, {bad} mismatches (file: {golden})")
        if bad:
            return 1
    else:
        print("No routing-leaves.json found; skipping the full golden check.")

    print("\nNew and highlighted cases:")
    for q in NEW_CASES:
        print("---")
        print(q)
        print(" =>", emergency_numbers_line(q))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
