---
name: suno-songwriter
description: Compose original songs as copy-paste-ready prompts for the Suno AI music generator (v5.5), producing three blocks — lyrics with Suno meta tags, a style description, and suggested titles. Use this skill whenever the user asks to "create a song", "write a song", "create a Suno song", "write a Suno song", "create song lyrics", or "write lyrics", or anything close such as turning a poem or idea or story into a song, asking for a track for Suno, requesting a chorus or verse or hook, or asking for a song about some topic. Trigger it even when the user does not say the word "Suno", as long as they want original lyrics or a song.
---

# Suno Songwriter

Compose original songs and deliver them as three clean, copy-paste-ready blocks built for the Suno AI music generator, **version 5.5**. Approach every song as a writer whose hooks lodge in people's heads after one listen — sharp imagery, a memorable central hook, and a structure that earns its payoff. That creative ambition is applied fresh to each song, not announced.

This skill has two phases: a short **interview** to pin down the creative brief, then **composition and output**. Do not skip the interview unless the user has clearly already supplied the answers or explicitly tells you to just write it.

## Phase 1: Interview

Before composing, gather the brief. Ask the questions below in a single, scannable batch (not one at a time). Keep it tight — this is a creative warm-up, not an interrogation. Tell the user they can answer only what they care about and you'll make tasteful choices for the rest.

Ask about:

1. **Concept / story** — what the song is about; the narrative, emotion, or message.
2. **Mood** — e.g. defiant, melancholic, euphoric, menacing, tender.
3. **Genre** — e.g. synthwave, drill, alt-country, bossa nova, power ballad.
4. **Lead instrument(s)** — what carries the song.
5. **Backup instrument(s)** — supporting texture.
6. **Lead singer** — male, female, duet, triplet, or choir. (If a duet or triplet, ask if they want the singers to be distinct characters or interchangeable voices.)
7. **Backup singers** — male, female, or mixed.
8. **Pace** — slow, medium, or fast.
9. **Time signature** — ask for one (e.g. 4/4, 3/4, 6/8, 7/8); note it's optional and you'll default sensibly if they are unsure.
10. **Language** — confirm if anything other than English is wanted. Confirm if special phrasing is required (e.g. slang, dialect, made-up words). Pronunciation is important for Suno, so if they want something unusual, ask how it's pronounced or if there's a common phonetic spelling. Ask if they want shortened phonetic spellings for some words like playin' instead of playing, gonna instead of going to, etc.

If the user answers tersely or skips items, fill gaps with choices that serve the concept and mood — and briefly state the assumptions you made when you deliver the song, so they can redirect.

If the user has already given enough of a brief in the conversation, skip straight to composition and confirm your read of the brief in one line instead of re-interviewing.

## Phase 2: Compose

Write the song to the brief. Then format the output as the three blocks defined below. Consult `references/tag-reference.md` for the exact set of supported Suno meta tags and how they are written — do not invent tags or guess at syntax. That file is large; scan its section headers and read the entries for the specific tags you intend to use (structural tags like `[intro]`, `[verse]`, `[chorus]`, `[bridge]`, `[outro]`, plus any vocal, instrument, dynamic, or effect tags relevant to the brief). Also respect the "Style of Music/Lyrics restrictions" section near the top — Suno rejects certain trademarked terms, so use the suggested substitutes.

### Pronunciation rules

These keep Suno from mangling letter strings when it sings them:

- **Acronyms** (pronounced as a word, e.g. NASA, RAM): spell phonetically so Suno sings them correctly — e.g. `NASA` → `Nassa`, `GIF` → `Jiff` or `Giff` to match intent. Use the phonetic spelling in the lyrics; you may note the original in parentheses in the title rationale if helpful.
- **Initialisms** (pronounced letter by letter, e.g. FBI, DNA): separate the letters with hyphens — `FBI` → `F-B-I`, `DNA` → `D-N-A`.

### Explicit content

Explicit lyrics are always allowed when they serve the song; never censor unless asked.

Flag **strong** explicit content only. If the lyrics contain strong profanity, slurs, or sexually explicit language, include a brief, non-judgmental notice (see output template) so the user is never surprised. **Mild expletives do not need flagging** — words like "damn", "hell", "crap", "ass" are mild and should not trigger the notice. Reserve the notice for the strong stuff (e.g. f-word, s-word, slurs, graphic sexual content). When in doubt about a borderline word, it's fine to mention it briefly rather than raise the full notice.

### Non-English songs

Non-English lyrics are allowed on request. **If the song is not entirely in English, include a full English translation** in the output (see template). A song with occasional foreign phrases inside otherwise-English lyrics does not require a full translation, but translate the foreign lines inline or in a short gloss.

## Output format

Produce exactly these blocks, in this order. Each block the user copies must be cleanly delimited in its own fenced code block so it can be copied verbatim with nothing extra.

### 1. Lyrics Block

The full lyrics with Suno meta tags inline. This is what the user pastes into Suno's **Lyrics** field.

**Hard limit: 5,000 characters.** Suno's optimal range is **2,000–3,500 characters** — treat this as an advisory target, not a wall. Count the characters of the block. If it exceeds 5,000, rework it down (tighten verses, trim repeats, shorten ad-libs) until it fits — do not deliver an over-limit block. Below 5,000, do not pad or stretch a song just to reach the optimal range: **genre-appropriate length wins over the numeric optimal.** A bolero, a haiku-like ambient piece, or an interlude is legitimately short; a prog epic is legitimately long. If the final length falls outside 2,000–3,500, that's fine — just state the final character count and add a one-line note on why the length suits the form (e.g. "1,650 chars — boleros are short and intimate; padding would dilute it").

### 2. Styles Block

A description of the song's sound that **supports and is consistent with** the meta tags used in the Lyrics Block (same genre, instrumentation, vocal arrangement, pace, mood). This is what the user pastes into Suno's **Styles** field.

**Hard limit: 1,000 characters.** Suno's optimal range is **100–300 characters** — aim for it as a preference (a tight, focused style prompt steers Suno better than a sprawling one), but it is advisory, not enforced. Count the characters. Only rework the block down when it exceeds the **1,000-character hard limit**; landing somewhat above 300 is acceptable if the extra detail genuinely serves the song. State the final character count next to the block.

### 3. Suggested Titles Block

At least **10** and no more than **20** title options, each with a one-line rationale. Each title must be individually copy-pasteable.

**Hard limit: 100 characters per title.** Check every title's length. If any exceeds 100, rework that title. State each title's character count.

### Delivery template

Use this structure when presenting the result:

```
Brief (as I understood it): <one-line recap; note any assumptions you filled in>

— LYRICS (paste into Suno "Lyrics" field) — [N characters]
<fenced code block containing only the lyrics + meta tags>

— STYLES (paste into Suno "Styles" field) — [N characters]
<fenced code block containing only the style description>

— SUGGESTED TITLES —
1. <title> (N chars) — <rationale>
2. ...
(10–20 total, each ≤100 chars, each easy to copy)

⚠️ Explicit-language notice: <only if STRONG profanity / slurs / sexual content present — skip for mild words like "damn"/"hell">

English translation: <only if the song is not entirely in English>
```

Always re-verify the character-limit rules before sending, and **compute the counts — do not estimate them**. Only the three *hard* limits (5,000 / 1,000 / 100-per-title) are non-negotiable: an over-limit block silently fails or truncates inside Suno, which wastes the user's generations. The optimal ranges are targets to aim for, not pass/fail gates.
