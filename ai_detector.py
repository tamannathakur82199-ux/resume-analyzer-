"""Heuristic check: does the resume text look AI-written?

IMPORTANT: this is an *indicator*, not proof. No tool can tell for certain whether a person or a
chatbot wrote a piece of text. The check looks for patterns that chatbot-written resumes often show:

  1. leftovers copied from a chatbot (e.g. "As an AI language model", "[Your Name]", markdown symbols)
  2. clichéd buzzwords (spearheaded, leveraged, results-driven, seamless, robust ...)
  3. bullets that are all almost the same length
  4. most bullets ending in a "resulting in / leading to / ensuring ..." result clause
  5. a metric (%) in nearly every bullet, mostly round numbers (40 %, 25 %, 30 %)
  6. heavy use of em dashes (weak signal)
  7. generic "template" wording ("strong foundation in", "seeking an entry-level role", "contribute to growth")
  8. result clauses glued on with "-ing" words (", enhancing ...", ", ensuring ...", "to ensure ...")
  9. vague claims with no numbers ("efficiently", "smooth performance", "intuitive interface")
 10. generic soft-skill lists and every bullet opening with a different strong verb (weak signals)
 11. very long, wordy bullets; stacked "polish" adjectives (clean, modern, responsive, intuitive ...);
     third-person phrasing ("Possesses hands-on knowledge ..."); abbreviations spelled out in brackets

Heavily edited AI text can pass, and formal / template-based or non-native writing can be flagged.
Use the result to decide *who to question in the interview*, never as the only reason to reject.
Pure Python - no extra packages needed.
"""
from __future__ import annotations

import re
import statistics

from resume_parser import BULLET_RE, DATE_RANGE_RE
from skills_db import ACTION_VERBS

MIN_WORDS = 80
# sensitivity -> (score for "Likely", score for "Possible")
LEVEL_SETS = {"strict": (60, 35), "balanced": (50, 25), "sensitive": (38, 15)}
SENSITIVITIES = tuple(LEVEL_SETS)


def level_for(score: int, sensitivity: str = "balanced") -> str:
    likely, possible = LEVEL_SETS.get(sensitivity, LEVEL_SETS["balanced"])
    return "Likely" if score >= likely else "Possible" if score >= possible else "Unlikely"


NOTE = ("Indicator only - not proof. Formal or template-based resumes can be flagged and edited AI text can "
        "pass. Verify with an interview or a practical task.")

# (label, regex, weight)
BUZZWORDS = [
    ("spearheaded", r"\bspearhead\w*", 2), ("leveraged", r"\bleverag\w*", 2),
    ("orchestrated", r"\borchestrat\w*", 2), ("harnessing", r"\bharness\w*", 2),
    ("seamless", r"\bseamless\w*", 2), ("robust", r"\brobust\b", 2),
    ("cutting-edge", r"\bcutting[- ]edge\b|\bstate[- ]of[- ]the[- ]art\b", 2),
    ("results-driven", r"\bresults?[- ]driven\b", 2),
    ("proven track record", r"\bproven (?:track record|ability|expertise)\b|\btrack record of\b", 2),
    ("detail-oriented", r"\bdetail[- ]oriented\b", 2),
    ("passionate about", r"\bpassionate (?:about|for)\b|\bpassion for\b", 2),
    ("fast-paced", r"\bfast[- ]paced\b", 2), ("pivotal", r"\bpivotal\b", 2),
    ("foster", r"\bfoster\w*", 2), ("synergy", r"\bsynerg\w*", 2),
    ("high-impact", r"\bhigh[- ]impact\b", 2), ("thereby", r"\bthereby\b", 2),
    ("championed", r"\bchampion(?:ed|ing)\b", 2),
    ("ever-evolving", r"\bever[- ](?:evolving|changing)\b", 2),
    ("testament", r"\btestament\b", 2), ("delve", r"\bdelv\w*", 2), ("tapestry", r"\btapestry\b", 2),
    ("driving innovation", r"\bdriv\w+ innovation\b|\bdrive innovation\b", 2),
    # weaker: common in human resumes too
    ("dynamic", r"\bdynamic\b", 1), ("innovative", r"\binnovative\b", 1),
    ("comprehensive", r"\bcomprehensive\b", 1), ("streamlined", r"\bstreamlin\w*", 1),
    ("holistic", r"\bholistic\b", 1), ("impactful", r"\bimpactful\b", 1),
    ("cross-functional", r"\bcross[- ]functional\b", 1), ("stakeholders", r"\bstakeholders?\b", 1),
    ("continuous improvement", r"\bcontinuous improvement\b", 1),
    ("best practices", r"\bbest practices\b", 1), ("data-driven", r"\bdata[- ]driven\b", 1),
    ("eager to", r"\beager to\b", 1), ("adept", r"\badept (?:at|in|with)\b", 1),
    ("well-versed", r"\bwell[- ]versed\b", 1), ("highly motivated", r"\bhighly motivated\b|\bself[- ]motivated\b", 1),
    ("team player", r"\bteam player\b", 1), ("scalable", r"\bscalable\b", 1),
    ("utilized", r"\butili[sz](?:e|ed|es|ing)\b", 1), ("facilitated", r"\bfacilitat\w+", 1),
    ("intuitive", r"\bintuitive\b", 1), ("showcasing", r"\bshowcas\w+", 1),
    ("demonstrated", r"\bdemonstrat(?:ed|ing|es)\b", 1), ("results-oriented", r"\bresults?[- ]oriented\b", 2),
    ("actionable insights", r"\bactionable insights?\b|\binformed decision[- ]making\b", 2),
    ("user experience", r"\b(?:enhanc\w+|improv\w+) (?:the )?user experience\b", 1),
]
_BUZZ = [(label, re.compile(rx, re.I), w) for label, rx, w in BUZZWORDS]

CHATBOT_PHRASES = re.compile(
    r"\bas an ai\b|\blanguage model\b|\bi hope this (?:helps|resume)\b|"
    r"\bfeel free to (?:customi[sz]e|modify|adjust|tailor)\b|"
    r"\bhere(?:'s| is) (?:your|a|the) (?:updated |tailored |sample |professional |revised )?(?:resume|cv)\b|"
    r"\bcertainly[!,]|\bplease (?:replace|insert)\b|\binsert (?:your|company|job)\b", re.I)
PLACEHOLDER = re.compile(
    r"\[(?:your|company|job title|insert|add|city|state|date|university|college|name|email|phone|degree)"
    r"[^\]\n]{0,40}\]", re.I)
MARKDOWN = re.compile(r"\*\*[^*\n]+\*\*|^\s*#{1,4}\s+\S|^\s*-{3,}\s*$", re.M)
RESULT_CLAUSE = re.compile(
    r"\b(?:resulting in|resulted in|leading to|led to|thereby|ensuring|enabling|contributing to|"
    r"which (?:led|resulted|improved|reduced|enhanced)|driving)\b", re.I)
PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")
# result clauses glued on with "-ing" words or "to ensure ..."
TAIL_CLAUSE = re.compile(
    r",\s*(?:thereby\s+|while\s+)?(?:enhancing|improving|ensuring|enabling|facilitating|supporting|boosting|"
    r"reducing|increasing|streamlining|optimi[sz]ing|demonstrating|showcasing|providing|allowing|promoting|"
    r"fostering|delivering|maximi[sz]ing|minimi[sz]ing|strengthening|contributing|driving|making|helping)\b|"
    r"\bto (?:ensure|enhance|improve|streamline|facilitate)\b", re.I)
GENERIC_PHRASES = [
    ("strong foundation in", r"\bstrong (?:foundation|background|understanding|knowledge) (?:in|of)\b"),
    ("solid understanding", r"\bsolid (?:understanding|foundation|grasp)\b"),
    ("seeking a role / opportunity", r"\bseeking (?:an? )?[\w\- ]{0,25}(?:role|position|opportunity)\b|"
                                    r"\bopportunity to (?:apply|utili[sz]e|contribute|grow|leverage)\b"),
    ("contribute to growth / success", r"\bcontribut\w+ to (?:the )?(?:growth|success|goals|organi[sz]ation|"
                                      r"impactful|innovative)\b"),
    ("dynamic organization", r"\bdynamic (?:organi[sz]ation|environment|team|company)\b"),
    ("apply my skills", r"\b(?:apply|utili[sz]e|leverage) (?:my |the |technical )?(?:technical )?"
                        r"(?:skills|knowledge|expertise)\b"),
    ("hands-on experience", r"\bhands[- ]on (?:experience|knowledge|exposure)\b"),
    ("aspiring", r"\baspiring\b"),
    ("motivated / dedicated and ...", r"\b(?:motivated|dedicated|hard[- ]?working|enthusiastic|proactive) "
                                      r"(?:and|professional|individual)\b"),
    ("real-world problems", r"\breal[- ]world (?:problems|applications|projects|challenges)\b"),
]
_GENERIC = [(label, re.compile(rx, re.I)) for label, rx in GENERIC_PHRASES]
VAGUE = re.compile(
    r"\b(?:efficient(?:ly)?|effective(?:ly)?|seamless(?:ly)?|smooth(?:ly)?|intuitive|user[- ]friendly|"
    r"high[- ]quality|reliable|secure|robust|scalable|meaningful|strong|significant(?:ly)?|various|multiple|"
    r"optimal|improved?|enhanc\w+|performance|usability|user experience)\b", re.I)
POLISH = re.compile(
    r"\b(?:clean|modern|responsive|intuitive|scalable|robust|efficient|reliable|secure|seamless|dynamic|"
    r"innovative|interactive|user[- ]friendly|engaging|comprehensive|structured|intelligent|streamlined|"
    r"high[- ]performance|visually appealing|sleek)\b", re.I)
THIRD_PERSON = re.compile(r"\b(?:possesses|exhibits|demonstrates|brings|combines|boasts)\b", re.I)
SPELLED_OUT = re.compile(r"\b[A-Z][a-z]+(?: (?:[A-Za-z&]+)){1,5} \(([A-Z][A-Za-z+#.]*(?: [A-Za-z]+)?)\)")
SOFT_SKILLS = re.compile(
    r"\b(?:problem[- ]solving|communication|teamwork|time management|adaptability|leadership|critical thinking|"
    r"collaboration|creativity|attention to detail)\b", re.I)
NUMBER = re.compile(r"\d+\s*%|(?<![\d/])(?!(?:19|20)\d\d\b)\d{2,}[\d,]*\+?")


def _logical_lines(lines):
    """Join wrapped lines (PDF / pasted text) back into whole bullets / sentences."""
    out = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        is_bullet = bool(BULLET_RE.match(line))
        text = BULLET_RE.sub("", line).strip()
        if out and not is_bullet and "|" not in text and not DATE_RANGE_RE.search(text):
            prev = out[-1]
            ends = re.search(r"[.!?]$", prev["text"])
            if (prev["bullet"] and not ends) or text[:1].islower():
                prev["text"] += " " + text
                continue
        out.append({"bullet": is_bullet, "text": text})
    return out


def _statements(parsed: dict) -> list[str]:
    """Bullet points of the experience / projects sections (long lines if there are no bullets)."""
    sec = parsed["sections"]
    items = _logical_lines(sec.get("experience", []) + sec.get("projects", []))
    bullets = [i["text"] for i in items if i["bullet"]]
    if len(bullets) >= 3:
        return bullets
    return [i["text"] for i in items
            if len(i["text"].split()) >= 7 and " | " not in i["text"] and not DATE_RANGE_RE.search(i["text"])]


def detect_ai_written(parsed: dict, sensitivity: str = "balanced") -> dict:
    text = parsed["raw_text"]
    words = len(text.split())
    short = words < MIN_WORDS   # too little text for style statistics; chatbot leftovers are still checked

    signals = []

    def add(name, detail, points):
        if points > 0:
            signals.append({"name": name, "detail": detail, "points": int(round(points))})

    # 1) leftovers from a chatbot
    chat = sorted({m.group().strip().lower() for m in CHATBOT_PHRASES.finditer(text)})
    if chat:
        add("Chatbot text left in the resume", "Found: " + "; ".join(chat[:4]), 40)
    holders = sorted({m.group() for m in PLACEHOLDER.finditer(text)})
    if holders:
        add("Unfilled template placeholders", "Found: " + ", ".join(holders[:4]), 15)
    if MARKDOWN.search(text):
        add("Markdown symbols (** or ###)", "Typical of text copied from a chatbot window", 10)
    if short:
        if not signals:
            return {"score": 0, "level": "Not enough text", "signals": [], "words": words, "note": NOTE}
        score = min(100, sum(s["points"] for s in signals))
        return {"score": score, "level": level_for(score, sensitivity), "signals": signals,
                "words": words, "note": NOTE}

    # 2) buzzword density
    found, weight = [], 0
    for label, rx, w in _BUZZ:
        if rx.search(text):
            found.append(label)
            weight += w
    if weight >= 2:
        add("Clichéd buzzwords", f"{len(found)} found: " + ", ".join(found[:10]), min(30, 4 * weight))

    # 3-5) bullet style
    stmts = _statements(parsed)
    if len(stmts) >= 4:
        lengths = [len(s.split()) for s in stmts]
        mean = statistics.mean(lengths)
        cv = statistics.pstdev(lengths) / mean if mean else 1
        if mean >= 12 and cv < 0.18:
            add("Bullets are almost the same length", f"average {mean:.0f} words, variation {cv:.2f}", 20)
        elif mean >= 12 and cv < 0.25:
            add("Bullets are very evenly sized", f"average {mean:.0f} words, variation {cv:.2f}", 12)
        elif mean >= 12 and cv < 0.32:
            add("Bullets are fairly evenly sized", f"average {mean:.0f} words, variation {cv:.2f}", 5)

        clause = sum(bool(RESULT_CLAUSE.search(s) or TAIL_CLAUSE.search(s)) for s in stmts) / len(stmts)
        if clause >= 0.5:
            add("Formulaic 'resulting in / enhancing / ensuring ...' endings", f"{clause:.0%} of bullets", 15)
        elif clause >= 0.35:
            add("Often ends bullets with 'resulting in / enhancing / ensuring ...'", f"{clause:.0%} of bullets", 8)

        if len(stmts) >= 5:
            no_digit = sum(not re.search(r"\d", s) for s in stmts) / len(stmts)
            vague = sum(len(set(m.lower() for m in VAGUE.findall(s))) >= 2 for s in stmts) / len(stmts)
            if no_digit >= 0.7 and vague >= 0.5:
                add("Vague claims with no numbers", f"{vague:.0%} of bullets use words like 'efficiently', "
                    "'performance', 'user experience' but give no figures", 10)
            elif no_digit >= 0.7 and vague >= 0.3:
                add("Mostly vague, unmeasured claims", f"{no_digit:.0%} of bullets have no numbers", 5)
            firsts = [re.sub(r"[^a-z]", "", s.split()[0].lower()) for s in stmts if s.split()]
            if (len(set(firsts)) == len(firsts) and
                    sum(f in ACTION_VERBS for f in firsts) / len(firsts) >= 0.8):
                add("Every bullet opens with a different strong verb (weak signal)",
                    ", ".join(f.title() for f in firsts[:6]), 4)

        metric = sum(bool(NUMBER.search(s)) for s in stmts) / len(stmts)
        percents = [float(p) for s in stmts for p in PERCENT.findall(s)]
        pts = 0
        detail = []
        if metric >= 0.8:
            pts += 8
            detail.append(f"{metric:.0%} of bullets contain a metric")
        if len(percents) >= 3 and sum(p % 5 == 0 for p in percents) / len(percents) >= 0.8:
            pts += 7
            detail.append("percentages are mostly round numbers (" + ", ".join(f"{p:g}%" for p in percents[:5]) + ")")
        add("Metric in nearly every bullet", "; ".join(detail), pts)

    # few-but-wordy bullets and polished prose (also works when there are only 3 bullets)
    summary_text = " ".join(parsed["sections"].get("summary", []))
    prose = " ".join(stmts + [summary_text])
    if len(stmts) >= 3:
        mean_words = statistics.mean(len(x.split()) for x in stmts)
        if mean_words >= 20:
            add("Long, wordy bullets", f"average {mean_words:.0f} words per bullet (resume bullets are usually 10-18)", 8)
        elif mean_words >= 17:
            add("Rather long bullets", f"average {mean_words:.0f} words per bullet", 4)
        if len(stmts) < 5 and not any(re.search(r"\d", x) for x in stmts):
            add("No figures or concrete results in any bullet", f"{len(stmts)} bullets, none with a number", 4)
    polish = sorted({m.lower() for m in POLISH.findall(prose)})
    if len(polish) >= 5:
        add("Stacked 'polish' adjectives", f"{len(polish)} found: " + ", ".join(polish[:8]), 10)
    elif len(polish) >= 3:
        add("Stacked 'polish' adjectives", f"{len(polish)} found: " + ", ".join(polish), 6)
    if THIRD_PERSON.search(summary_text):
        add("Third-person phrasing in the summary (weak signal)",
            "e.g. '" + THIRD_PERSON.search(summary_text).group().title() + " ...'", 4)
    body_text = "\n".join(l for k, v in parsed["sections"].items() if k not in ("education", "header") for l in v)
    spelled = {m.group(1) for m in SPELLED_OUT.finditer(body_text)}
    if len(spelled) >= 3:
        add("Spells out abbreviations in brackets (weak signal)", ", ".join(sorted(spelled)[:5]), 3)

    # generic template wording
    generic = [label for label, rx in _GENERIC if rx.search(text)]
    if len(generic) >= 5:
        add("Generic template wording", f"{len(generic)} found: " + ", ".join(generic[:6]), 16)
    elif len(generic) >= 3:
        add("Generic template wording", f"{len(generic)} found: " + ", ".join(generic), 10)
    elif len(generic) == 2:
        add("Generic template wording", ", ".join(generic), 5)
    soft = {m.lower() for m in SOFT_SKILLS.findall(text)}
    if len(soft) >= 3:
        add("Generic soft-skills list (weak signal)", ", ".join(sorted(soft)[:5]), 3)

    # 6) em dashes (weak)
    dashes = DATE_RANGE_RE.sub(" ", text).count("—")
    if dashes >= 3 and dashes / words * 100 >= 0.8:
        add("Many em dashes (weak signal)", f"{dashes} found", 5)

    score = min(100, sum(s["points"] for s in signals))
    return {"score": score, "level": level_for(score, sensitivity), "signals": signals,
            "words": words, "note": NOTE}


def advice_for_candidate(check: dict) -> str | None:
    if check["level"] in ("Unlikely", "Not enough text", "Not checked"):
        return None
    return ("[AI-WRITTEN] Parts of this resume read like AI-generated text (" +
            ", ".join(s["name"].lower() for s in check["signals"][:3]) +
            "). Rewrite them in your own words with real details: actual project names, tools you used and "
            "true numbers. You should be able to explain every line in an interview.")


# --------------------------------------------------------------------------- standalone check helpers
VERDICTS = {
    "Likely": "Likely AI-written",
    "Possible": "Possibly AI-assisted (some parts look AI-written)",
    "Unlikely": "Probably written by a person",
    "Not enough text": "Not enough text to judge",
    "Not checked": "Not checked",
}


def verdict_text(check: dict) -> str:
    return VERDICTS.get(check["level"], check["level"])


def suspicious_lines(parsed: dict, limit: int = 5) -> list[dict]:
    """The bullet points / sentences that look most AI-written, with the reason for each."""
    scored = []
    stmts = _statements(parsed)
    summary = " ".join(parsed["sections"].get("summary", []))
    stmts = stmts + [s.strip() for s in re.split(r"(?<=[.!?])\s+", summary) if len(s.split()) >= 7]
    for line in stmts:
        reasons, pts = [], 0
        words = sorted({label for label, rx, w in _BUZZ if w == 2 and rx.search(line)})
        if words:
            reasons.append("buzzwords: " + ", ".join(words[:4]))
            pts += 2 * len(words)
        weak = sorted({label for label, rx, w in _BUZZ if w == 1 and rx.search(line)})
        if weak:
            reasons.append("common filler: " + ", ".join(weak[:3]))
            pts += len(weak)
        generic = [label for label, rx in _GENERIC if rx.search(line)]
        if generic:
            reasons.append("template wording: " + ", ".join(generic[:3]))
            pts += 2 * len(generic)
        polish = sorted({m.lower() for m in POLISH.findall(line)})
        if len(polish) >= 2:
            reasons.append("stacked adjectives: " + ", ".join(polish[:4]))
            pts += len(polish)
        if THIRD_PERSON.search(line):
            reasons.append("third-person phrasing")
            pts += 1
        if len(line.split()) >= 22:
            reasons.append("very long sentence")
            pts += 1
        if RESULT_CLAUSE.search(line) or TAIL_CLAUSE.search(line):
            reasons.append("result clause at the end ('..., enhancing / ensuring ...')")
            pts += 2
        pcts = [float(p) for p in PERCENT.findall(line)]
        if pcts and all(p % 5 == 0 for p in pcts):
            reasons.append("round-number metric (" + ", ".join(f"{p:g}%" for p in pcts[:3]) + ")")
            pts += 1
        if not re.search(r"\d", line) and len({m.lower() for m in VAGUE.findall(line)}) >= 2:
            reasons.append("vague claim, no figures")
            pts += 1
        if pts >= 2:
            scored.append({"line": line, "reasons": reasons, "points": pts})
    scored.sort(key=lambda d: -d["points"])
    return scored[:limit]


def check_text(text: str, meta: dict | None = None, sensitivity: str = "balanced") -> dict:
    """AI-written check straight from resume text (no job description needed)."""
    from resume_parser import parse_resume   # local import: parser is only needed here
    parsed = parse_resume(text, meta)
    result = detect_ai_written(parsed, sensitivity)
    result["name"] = parsed["name"]
    result["suspicious_lines"] = suspicious_lines(parsed)
    return result
