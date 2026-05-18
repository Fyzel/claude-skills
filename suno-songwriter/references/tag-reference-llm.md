# Suno Meta-Tags Reference (Distilled)

Version: 2025-12-02 (distilled from tag-reference_20251120-02.md)
Target: LLM consumption for audio generation prompts

---

## Restrictions

Avoid in "Style of Music" field:
- "kraftwerk" → use "krautrock" / "old school EDM"
- "Orbis Mundi"
- "skank" → use "ska stroke" for guitar technique

---

## Notation

**Pipe notation** for local overrides:
`[SectionName | param1: value, param2: value]`

Example: `[chorus | style: phonk hook, vocals: autotune-light, instruments: 808 bass]`

---

## Control Meta-Tags

### [track]
- Group: control
- Purpose: Top-level container for global track properties.
- Usage: `[track: genre: phonk drift, style: lo-fi hip-hop, mood: gritty night drive, length: 180]`
- Parameters: `genre`, `style`, `mood`, `length`, `instruments`, `loop-friendly`, `persona`
- Notes: Place at top; sections may override these values.

### [control]
- Group: control
- Purpose: High-level directives for generation behavior.
- Usage: `[control: cinematic, emotional, slow-build]`
- Parameters: `hallucinatory`, `no-repeat`, `dynamic transitions`, `instrumental`, `experimental`
- Notes: v5.0 expanded support; combine multiple directives.

### [sequence]
- Group: control
- Purpose: Define section order and repetition pattern.
- Usage: `[sequence: intro, verse, chorus, verse, chorus, bridge, outro]`
- Parameters: `linear`, `cyclical`, `reversed`, `mirrored`
- Notes: Helps structure long compositions.

### [length]
- Group: control
- Purpose: Target track duration in seconds.
- Usage: `[length: 210]`
- Notes: 180 typical for v3.5/v4.0; 360 for v4.5+ ambient/instrumental.

### [compression]
- Group: control
- Purpose: Dynamic range control hint.
- Usage: `[compression: light]`
- Parameters: `light`, `moderate`, `heavy`
- Notes: Affects overall mix dynamics.

---

## Structure Meta-Tags

### [intro]
- Group: structure
- Purpose: Opening section establishing mood/instrumentation.
- Usage: 
  - Basic: `[intro]` followed by description or silence.
  - Styled: `[intro | soft, atmospheric, synth-driven]`
- Parameters: `soft`, `dramatic`, `percussive`, `atmospheric`, `synth-driven`
- Notes: Text after tag describes the intro character.

### [verse]
- Group: structure
- Purpose: Main narrative/lyrical section.
- Usage:
  - Basic: `[verse]` followed by lyrics.
  - Styled: `[verse | intimate, acoustic, sparse]`
- Notes: Multiple verses: `[verse 1]`, `[verse 2]`, etc.

### [pre-chorus]
- Group: structure
- Purpose: Build-up section before chorus.
- Usage: `[pre-chorus]` followed by lyrics.
- Notes: Creates anticipation; often increases energy.

### [chorus]
- Group: structure
- Purpose: Main hook/refrain section.
- Usage:
  - Basic: `[chorus]` followed by lyrics.
  - Styled: `[chorus | anthemic, layered harmonies, full arrangement]`
- Notes: Typically repeated; highest energy section.

### [bridge]
- Group: structure
- Purpose: Contrasting section providing variety.
- Usage:
  - Basic: `[bridge]` followed by lyrics.
  - Styled: `[bridge | stripped-down, key change, reflective]`
- Notes: Often precedes final chorus; provides contrast.

### [interlude]
- Group: structure
- Purpose: Short instrumental break between sections.
- Usage: `[interlude: ambient pad swells before chorus]`
- Parameters: `instrumental`, `melodic`, `rhythmic`, `ambient`, `minimal`
- Notes: No lyrics inside; transition function.

### [intermezzo]
- Group: structure
- Purpose: Self-contained contrasting passage.
- Usage: `[intermezzo: dramatic orchestral swell]`
- Parameters: `contrasting`, `reflective`, `dramatic`, `ornamental`
- Notes: More substantial than interlude; may be unrelated to main theme.

### [break]
- Group: structure
- Purpose: Sudden reduction or pause in arrangement.
- Usage: `[break: drums only, 4 bars]`
- Parameters: `minimal`, `percussive`, `ambient`, `dramatic`
- Notes: Creates tension before return.

### [drop]
- Group: structure
- Purpose: High-energy moment after build-up (EDM-style).
- Usage: `[drop: heavy bass, full percussion]`
- Notes: Typically follows a build or break.

### [build]
- Group: structure
- Purpose: Rising energy section leading to climax/drop.
- Usage: `[build: synth riser, percussion intensifying]`
- Parameters: `gradual`, `intense`, `filtered`, `layered`
- Notes: v4.5+ confirmed; improved polyphonic builds in v5.0.

### [hook]
- Group: structure
- Purpose: Catchy, memorable phrase or motif.
- Usage: `[hook] Short memorable line here`
- Notes: Keep text very short, rhythmically clear; v4.5+ confirmed.

### [solo]
- Group: structure
- Purpose: Featured instrumental lead passage.
- Usage: `[solo: melodic guitar improvisation]`
- Parameters: `guitar`, `saxophone`, `synth`, `piano`, `drum`
- Notes: Instrument-specific variants: `[guitar solo]`, `[sax solo]`, etc.

### [outro]
- Group: structure
- Purpose: Closing section of track.
- Usage:
  - Basic: `[outro]` followed by description.
  - Styled: `[outro | fading, minimal, reverb tail]`
- Parameters: `fade-out`, `abrupt`, `reprise`, `ambient`
- Notes: Place before `[end]`.

### [end]
- Group: structure
- Purpose: Signal track conclusion.
- Usage: `[end]`
- Notes: Unreliable alone; combine with outro description. May not stop instrumentals.

### [coda]
- Group: structure
- Purpose: Concluding passage after main structure.
- Usage: `[coda: final thematic statement, resolution]`
- Notes: Classical term; provides closure.

---

## Style/Genre Meta-Tags

### [genre]
- Group: style
- Purpose: Primary musical genre classification.
- Usage: `[genre: midwest emo + neosoul]`
- Notes: v4.5+ handles hybrid genres (X + Y) reliably. 1,200+ genres supported.

### [style]
- Group: style
- Purpose: Aesthetic/textural descriptors.
- Usage: `[style: gritty, lo-fi, nocturnal]`
- Notes: Freeform; supports compound styles like `horror-synth`, `glitch-jazz`.

### [mood]
- Group: style
- Purpose: Emotional character of track.
- Usage: `[mood: melancholic, introspective, bittersweet]`
- Parameters: `dark`, `uplifting`, `dreamy`, `aggressive`, `serene`, `tense`
- Notes: Affects overall emotional arc.

### [era]
- Group: style
- Purpose: Historical/stylistic period reference.
- Usage: `[era: 1980s synthwave]`
- Notes: User-tested; guides production aesthetics.

### [ambient]
- Group: style
- Purpose: Atmospheric, textural, non-rhythmic character.
- Usage: `[ambient: dark, textural drones]`
- Parameters: `textural`, `minimal`, `dark`, `bright`, `dissonant`
- Notes: Can be used as style modifier or section type.

---

## Tempo/Rhythm Meta-Tags

### [tempo]
- Group: tempo
- Purpose: Speed/feel of track.
- Usage: `[tempo: mid-tempo 90s hip-hop swing]`
- Notes: No exact BPM; use descriptive phrases. v4.5+ parses complex tempo descriptions.

### [bpm]
- Group: tempo
- Purpose: Approximate tempo indicator.
- Usage: `[bpm: 120]`
- Notes: Suggestive, not precise; combine with feel descriptors.

### [rhythm]
- Group: tempo
- Purpose: Rhythmic pattern/feel characteristics.
- Usage: `[rhythm: syncopated, swing feel, broken beat]`
- Parameters: `steady`, `syncopated`, `polyrhythmic`, `shuffle`, `straight`
- Notes: Affects groove character.

### [accelerando]
- Group: tempo
- Purpose: Gradual tempo increase.
- Usage: `[accelerando: gradual into climax]`
- Parameters: `gradual`, `sudden`, `layered`, `intensified`, `syncopated`
- Notes: Creates urgency/excitement.

### [ritardando]
- Group: tempo
- Purpose: Gradual tempo decrease.
- Usage: `[ritardando: slowing into outro]`
- Parameters: `gradual`, `dramatic`, `subtle`
- Notes: Creates resolution/finality.

### [pulse]
- Group: tempo
- Purpose: Underlying rhythmic foundation.
- Usage: `[pulse: steady 4/4, driving]`
- Notes: Defines basic rhythmic grid.

### [sincopation]
- Group: tempo
- Purpose: Off-beat rhythmic accents.
- Usage: `[sincopation: jazzy groove, off-beat snare]`
- Parameters: `light`, `complex`, `jazzy`, `heavily-accented`
- Notes: Also spelled "syncopation".

---

## Vocal Meta-Tags

### [vocals]
- Group: vocal
- Purpose: Vocal characteristics and style.
- Usage: `[vocals: warm, intimate, close-mic, female]`
- Parameters: gender, tone descriptors, processing hints
- Notes: v4.5+ responds to nuanced descriptors.

### [vocal-style]
- Group: vocal
- Purpose: Specific vocal delivery technique.
- Usage: `[vocal-style: whispered, airy, breathy]`
- Notes: Replaced deprecated `[sing-style]` from v3.

### [vocalist]
- Group: vocal
- Purpose: Voice character/persona lock.
- Usage: `[vocalist: deep baritone, raspy]`
- Notes: v5.0 improved consistency across sections.

### [male vocal] / [female vocal]
- Group: vocal
- Purpose: Gender specification for vocals.
- Usage: `[male vocal]` or `[female vocal]`
- Notes: v4.5+ confirmed; use at section start.

### [duet]
- Group: vocal
- Purpose: Two distinct vocal parts.
- Usage: `[duet: male and female trading lines]`
- Notes: User-tested; alternating vocal deliveries.

### [choir]
- Group: vocal
- Purpose: Choral vocal arrangement.
- Usage: `[choir: angelic, layered, gospel-style]`
- Parameters: `angelic`, `powerful`, `layered`, `gospel`, `dissonant`
- Notes: v4.5+ produces richer choir harmonies.

### [background-vocals]
- Group: vocal
- Purpose: Supporting/harmony vocals.
- Usage: `[background-vocals: layered harmonies in chorus]`
- Parameters: `harmonic`, `call-response`, `layered`, `ethereal`, `chant`
- Notes: Thickens arrangement.

### [harmonies]
- Group: vocal
- Purpose: Vocal harmony layers.
- Usage: `[harmonies: tight thirds, gospel-style]`
- Notes: User-tested; adds vocal depth.

### [whisper]
- Group: vocal
- Purpose: Whispered vocal delivery.
- Usage: `[whisper] the secrets only night can hear`
- Notes: v4.5+ improved detection; for lead vocal.

### [whispering]
- Group: vocal
- Purpose: Background whisper texture/layer.
- Usage: `[whispering: eerie murmurs underneath]`
- Notes: More textural than `[whisper]`; atmospheric.

### [spoken word]
- Group: vocal
- Purpose: Non-sung speech delivery.
- Usage: `[spoken word] Poetry-style narration here`
- Notes: Poetic cadence; less strict than rap flow.

### [rap]
- Group: vocal
- Purpose: Rhythmic spoken delivery with flow.
- Usage: `[rap | aggressive, fast flow]`
- Notes: Stricter rhythm than spoken word.

### [rapped verse]
- Group: vocal
- Purpose: Verse section with rap delivery.
- Usage: `[rapped verse]` followed by lyrics.
- Notes: v4.5+ confirmed.

### [shout]
- Group: vocal
- Purpose: Forceful/shouted vocal element.
- Usage: `[shout: group chant over chorus]`
- Parameters: `single`, `group`, `layered`, `distorted`
- Notes: For intensity/emphasis.

### [ad-lib]
- Group: vocal
- Purpose: Improvised vocal/instrumental phrase.
- Usage: `[ad-lib: vocal runs in final chorus]`
- Parameters: `vocal`, `instrumental`, `rhythmic`, `melodic`
- Notes: Embellishments and fills.

### [announcer]
- Group: vocal
- Purpose: Spoken host/presenter voice.
- Usage: `[announcer: retro radio DJ, warm tone]`
- Notes: v4.5+ confirmed; radio/podcast framing.

### [vulnerable vocals]
- Group: vocal
- Purpose: Emotionally exposed, intimate delivery.
- Usage: `[vulnerable vocals: fragile, close-mic, minimal reverb]`
- Notes: User-tested; raw emotional quality.

### [distorted vocals]
- Group: vocal
- Purpose: Processed/degraded vocal sound.
- Usage: `[distorted vocals: lo-fi, bitcrushed]`
- Notes: v4.5+ confirmed.

---

## Instrument Meta-Tags

### [instruments]
- Group: instrument
- Purpose: List instruments for track palette.
- Usage: `[instruments: acoustic guitar, soft synth pads, subtle piano]`
- Notes: Place before structure tags; establishes timbre.

### [instrument]
- Group: instrument
- Purpose: Highlight single prominent instrument.
- Usage: `[instrument: violin (lead)]`
- Parameters: `piano`, `guitar`, `violin`, `synth`, `brass`
- Notes: Makes specified instrument prominent.

### [instrumental]
- Group: instrument
- Purpose: Generate track with no vocals.
- Usage: `[instrumental]` or `[instrumental: cinematic orchestral]`
- Notes: Place at start of lyrics field; v4.5+ stricter adherence.

### [bass]
- Group: instrument
- Purpose: Bassline characteristics.
- Usage: `[bass: deep sub-bass, pulsing]`
- Parameters: `deep`, `sub-bass`, `pulsing`, `saturated`, `modulated`, `syncopated`
- Notes: Defines low-end character.

### [bass-slide]
- Group: instrument
- Purpose: Sliding bass note effect.
- Usage: `[bass-slide: downward glissando before drop]`
- Parameters: `upward`, `downward`, `glissando`, `percussive`, `synth`
- Notes: Groove/tension element.

### [arpeggio]
- Group: instrument
- Purpose: Broken chord sequence pattern.
- Usage: `[arpeggio: syncopated synth arpeggios]`
- Parameters: `rising`, `falling`, `circular`, `syncopated`, `randomized`
- Notes: Creates movement/texture.

---

## Dynamic Meta-Tags

### [dynamics]
- Group: dynamic
- Purpose: Volume/intensity variations.
- Usage: `[dynamics: gradual build from pp to ff]`
- Parameters: `pp`, `p`, `mp`, `mf`, `f`, `ff`, `crescendo`, `decrescendo`
- Notes: Shapes emotional arc.

### [intensity]
- Group: dynamic
- Purpose: Emotional/musical tension control.
- Usage: `[intensity: low → medium → explosive → collapse]`
- Parameters: `low`, `medium`, `high`, `rising`, `falling`, `fluctuating`, `plateau`, `explosive`
- Notes: Effective with `[control]`; defines energy arc.

### [crescendo]
- Group: dynamic
- Purpose: Gradual increase in volume/intensity.
- Usage: `[crescendo: strings swell into climax]`
- Notes: Classical dynamic marking.

### [decrescendo]
- Group: dynamic
- Purpose: Gradual decrease in volume/intensity.
- Usage: `[decrescendo: fading into silence]`
- Notes: Also "diminuendo".

### [sforzando]
- Group: dynamic
- Purpose: Sudden strong accent.
- Usage: `[sforzando: brass stabs into chorus]`
- Parameters: `single-hit`, `repeated`, `orchestral`, `percussive`
- Notes: Dramatic impact moments.

### [attack]
- Group: dynamic
- Purpose: Note onset character.
- Usage: `[attack: soft on pads, sharp on percussion]`
- Parameters: `sharp`, `soft`, `gradual`, `percussive`
- Notes: Shapes sound envelope.

### [silence]
- Group: dynamic
- Purpose: Intentional pause/absence of sound.
- Usage: `[silence: dramatic pause before chorus]`
- Parameters: `short`, `sudden`, `gradual`, `echoed`
- Notes: For contrast/tension.

---

## Harmony/Melody Meta-Tags

### [key]
- Group: harmony
- Purpose: Musical key specification.
- Usage: `[key: E minor]`
- Notes: Affects overall tonality.

### [harmony]
- Group: harmony
- Purpose: Harmonic characteristics.
- Usage: `[harmony: rich, jazz voicings, extended chords]`
- Parameters: `consonant`, `dissonant`, `modal`, `chromatic`, `diatonic`
- Notes: Shapes harmonic complexity.

### [melody]
- Group: harmony
- Purpose: Melodic characteristics.
- Usage: `[melody: lyrical, ascending phrases]`
- Parameters: `lyrical`, `angular`, `stepwise`, `leaping`, `ornamental`
- Notes: Defines melodic character.

### [chord]
- Group: harmony
- Purpose: Chord progression hints.
- Usage: `[chord: minor progression, descending]`
- Notes: Suggestive; not precise notation.

### [modulation]
- Group: harmony
- Purpose: Key change within track.
- Usage: `[modulation: shift up half-step for final chorus]`
- Parameters: `gradual`, `sudden`, `pivot`, `direct`
- Notes: Creates lift/interest.

### [polyphony]
- Group: harmony
- Purpose: Multiple independent melodic lines.
- Usage: `[polyphony: two-voice counterpoint]`
- Notes: v4.5+ confirmed; richer in v5.0.

---

## Thematic Meta-Tags

### [theme]
- Group: thematic
- Purpose: Main melodic/motivic idea.
- Usage: `[theme A: strings introduce main melody]`
- Notes: Use labeled variants: `[Theme A]`, `[Theme B]`.

### [motif]
- Group: thematic
- Purpose: Short recurring musical idea.
- Usage: `[motif: 4-note descending figure]`
- Notes: Building block for development.

### [subject]
- Group: thematic
- Purpose: Primary theme marking (fugal).
- Usage: `[subject: main fugue theme on piano]`
- Notes: v5.0 confirmed; classical technique.

### [inversion]
- Group: thematic
- Purpose: Theme played upside-down melodically.
- Usage: `[inversion: subject inverted on strings]`
- Parameters: `strict`, `free`, `stretched`
- Notes: v5.0 confirmed; fugal technique.

### [lament]
- Group: thematic
- Purpose: Sorrowful, descending motif.
- Usage: `[lament: descending strings in minor]`
- Parameters: `descending`, `vocal`, `instrumental`, `choral`
- Notes: v5.0 confirmed; sorrowful character.

### [aria-rise]
- Group: thematic
- Purpose: Operatic, rising vocal phrase.
- Usage: `[aria-rise: soprano rises into climax, strings swell]`
- Parameters: `solo`, `choral`, `orchestral`
- Notes: v5.0 enhanced operatic implementation.

### [chant-loop]
- Group: thematic
- Purpose: Repeating ritualistic vocal pattern.
- Usage: `[chant-loop: hypnotic mantra, layered voices]`
- Notes: v5.0 expanded ritualistic parameters.

---

## Effects Meta-Tags

### [sfx]
- Group: effects
- Purpose: Non-musical sound effects.
- Usage: `[sfx: distant whispering, mechanical hum]`
- Parameters: `wind`, `whispering`, `industrial`, `nature`, `glitch`
- Notes: Atmospheric/narrative elements.

### [effects]
- Group: effects
- Purpose: Audio processing characteristics.
- Usage: `[effects: heavy reverb, tape saturation]`
- Notes: General effects container.

### [signal-processing]
- Group: effects
- Purpose: Specific audio processing.
- Usage: `[signal-processing: bitcrush on drums, phaser on synths]`
- Parameters: `reverb`, `delay`, `compression`, `saturation`, `bitcrush`, `phaser`, `flanger`, `chorus`, `distortion`
- Notes: Technical processing hints.

### [siren]
- Group: effects
- Purpose: Alarm/siren sound effect.
- Usage: `[siren: style: industrial, length: medium]`
- Parameters: `air-raid`, `police`, `industrial`; `short`, `medium`
- Notes: Urgency/sci-fi element.

---

## Arrangement Meta-Tags

### [arrangement]
- Group: arrangement
- Purpose: Overall organization of elements.
- Usage: `[arrangement: layered, building toward climax]`
- Parameters: `dense`, `minimal`, `layered`, `dynamic`, `orchestral`
- Notes: Structural density control.

### [articulation]
- Group: arrangement
- Purpose: Note attack/connection style.
- Usage: `[articulation: staccato strings, legato woodwinds]`
- Parameters: `staccato`, `legato`, `marcato`, `tenuto`, `accented`, `spiccato`, `sustained`
- Notes: Performance technique.

### [sonority]
- Group: arrangement
- Purpose: Tonal quality/richness.
- Usage: `[sonority: warm, rich brass]`
- Parameters: `bright`, `dark`, `warm`, `rich`, `thin`, `harsh`
- Notes: Overall timbral character.

### [improvisation]
- Group: arrangement
- Purpose: Free melodic/harmonic variations.
- Usage: `[improvisation: jazzy trumpet solo]`
- Parameters: `freeform`, `jazzy`, `ornamental`, `structured`, `call-and-response`
- Notes: Spontaneous elements.

---

## Language/Localization

### [language]
- Group: control
- Purpose: Lyrics language specification.
- Usage: `[language: Japanese]`
- Parameters: `English`, `Spanish`, `French`, `Japanese`, `Italian`, `Multilingual`
- Notes: Affects vocal phonetics.

---

## Deprecated/Obsolete Tags

| Tag | Status | Alternative |
|-----|--------|-------------|
| `[sing-style]` | Deprecated v4 | Use `[vocal-style]` |
| `[song-type]` | Inert v4+ | Use structure tags |
| `[theme]` (unlabeled) | Ignored | Use `[Theme A]`, `[Theme B]` |
| `[section]` | Redundant | Use explicit structure tags |
| `[loop]` | Removed | Manually copy structures |
| `[autotune]` | Deprecated | Describe in style text |
| `[mix]`, `[master]`, `[filter]`, `[panning]`, `[volume]` | Ineffective | N/A |

---

## Version Notes

**v4.5 improvements:**
- Style of Music field: 1000 chars (was 200)
- Genre mashups work reliably
- Tempo descriptors parsed more naturally
- Vocal texture tags more responsive
- `[instrumental]` strictly honored
- Longer structures (8+ min) supported
- Tags can be embedded in natural sentences

**v5.0 (November 2025) additions:**
- `[aria-rise]` enhanced operatic
- `[build]` improved polyphonic builds
- `[chant-loop]` expanded ritualistic
- `[inversion]` fugal technique
- `[lament]` sorrowful motif
- `[polyphony]` richer vocal polyphony
- `[scat break]` jazz improvisation
- `[subject]` primary theme marking
- `[technique]` compositional method

---

## Quick Reference: Common Patterns

**Instrumental ambient track:**
```
[instrumental]
[control: atmospheric, slow-build]
[genre: dark ambient]
[mood: mysterious, vast]
[tempo: very slow, drifting]
[instruments: synth pads, deep drones, distant bells]
[length: 360]
[intro | minimal, emerging from silence]
[verse | layers building slowly]
[chorus | full texture, shimmering]
[outro | fading into void]
[end]
```

**Vocal song with structure:**
```
[control: dynamic transitions]
[genre: indie pop]
[mood: bittersweet, nostalgic]
[tempo: mid-tempo]
[vocals: warm female, intimate]
[instruments: acoustic guitar, soft drums, piano]
[length: 210]
[intro | guitar fingerpicking]
[verse 1]
Lyrics here...
[pre-chorus]
Building lyrics...
[chorus | full arrangement, harmonies]
Hook lyrics...
[verse 2]
More lyrics...
[bridge | stripped down, key change]
Bridge lyrics...
[chorus]
[outro | fading reprise]
[end]
```
