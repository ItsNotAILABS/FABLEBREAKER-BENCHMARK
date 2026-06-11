# FableBreaker Product Strategy

## Strategic Read

FableBreaker is correctness-first certification for AI/runtime/compiler speed claims.

FableBreaker should be positioned as the anti-benchmark-theater layer for builders making serious
performance claims. The market tension is already there: AI benchmarks are increasingly questioned
for contamination, gaming, cherry-picking, and weak auditability. Recent benchmarking criticism
centers on leakage, inflated scores, and systems optimizing for public tests instead of real
capability, while serious benchmark institutions like MLCommons pair performance with rules, review,
audit processes, and accuracy requirements.

The strongest market move is:

> **"Speed claims do not count until correctness survives adversarial generated cases."**

That line is the spine.

---

## Audience Map

### Primary Audience

AI systems builders, compiler/runtime engineers, evaluator optimization teams, benchmark authors,
and technical founders who need credible proof around performance improvements.

### Secondary Audience

AI researchers, open-source maintainers, infra teams, developer-tool companies, coding-agent teams,
and technical media watching claims like "17.7x faster" spread without deep verification.

### Economic Buyer (Later)

Companies shipping AI developer tools, runtimes, compilers, model-agent systems, or optimization
engines who need evidence packs before publishing claims, fundraising, selling enterprise contracts,
or entering public comparison fights.

### Influence Audience

X/Twitter technical circles, GitHub builders, Hacker News readers, AI safety/evals people,
benchmark researchers, and people skeptical of AI hype but hungry for rigorous tools.

---

## Core Pains

The buyer/user pain is not "I need a benchmark." It is:

- "My performance claim will get attacked unless the evidence is reproducible."
- "Public benchmarks can be gamed, memorized, or cherry-picked."
- "Speedups look impressive until semantic correctness breaks."
- "I need hidden adversarial cases without becoming a closed, untrusted gatekeeper."
- "I want to prove my optimizer works beyond the one demo case."
- "I need audit artifacts that other engineers can rerun."

For the public/open-source audience, the emotional pain is sharper:

> "We are drowning in benchmark screenshots, but starving for proof."

---

## Motivations

The practical motivation is credibility. The emotional motivation is liberation from hype.

### Builders Want

- proof before public claims
- reproducible audits
- adversarial validation
- hidden-seed certification
- a benchmark others can fork and improve
- a neutral way to say "this optimization is real"

### Companies Want

- public trust
- defensible claims
- sales enablement evidence
- private regression testing
- certification badges
- third-party validation

---

## Buying Triggers

FableBreaker becomes urgent when someone is about to:

- publish a major speedup claim
- launch a runtime/compiler/model-agent tool
- respond to criticism of a benchmark result
- compare against a rival system
- ship an optimization engine
- raise money using performance claims
- enter a public technical debate
- need CI-based regression checks for correctness and speed

The biggest trigger right now is the Fable/HVM-style public narrative: fast AI optimization creates
viral numbers, but viral numbers invite scrutiny. That makes FableBreaker timely.

---

## Market Context

The category is forming around trust infrastructure for AI claims.

### Existing Alternatives

- public benchmarks
- self-reported GitHub results
- ad hoc eval scripts
- academic benchmark suites
- MLPerf-style formal benchmark governance
- private internal test suites

### FableBreaker's Opening

FableBreaker is not trying to be MLPerf for everything. It is a counter-benchmark for semantic
correctness under adversarial generated cases, starting with interaction-net/evaluator optimization
claims.

That narrowness is good. It gives the product teeth.

---

## Positioning Options

### 1. The Claim Audit

> "Before you publish the speedup, prove it survives adversarial correctness."

Best for paid certification, evidence packs, enterprise use.

### 2. The Anti-Benchmark-Theater Benchmark

> "Speed screenshots are cheap. Reproducible semantic proof is not."

Best for X, GitHub launch, technical virality.

### 3. The Open Core Certification Layer

> "Open generator and scorer. Paid hidden-seed certification when the claim matters."

Best for sustainable business model.

### 4. The Runtime/Compiler Truth Harness

> "A generated adversarial test suite for evaluator optimization claims."

Best for technical users who care less about rhetoric and more about tooling.

### Recommended Strategic Angle

Lead with:

> **FableBreaker is the correctness firewall for AI speedup claims.**

Support it with:

> Speed without semantic proof is marketing.

This angle works because it does three things at once: it names the enemy, gives builders a tool,
and creates a paid certification path without hiding the public-good layer.

Do not position it as "anti-Fable" or "anti-HVM." That makes it look reactive. Position it as
pro-proof, pro-builder, and anti-unverified-claims.

---

## Offer Architecture

### Free Public Layer

- dataset generator
- scorer
- reference evaluator
- public adversarial families
- baseline candidate
- local audit runner
- manifest
- README
- proof docs
- public GitHub repo
- Zenodo DOI archive

### Paid Certification Layer

- rotating hidden seeds
- larger private suites
- hosted leaderboard
- signed evidence packs
- private custom corpora
- CI integration
- per-family diagnostics
- claim audit reports
- regression monitoring

### First Monetizable Product

**AI Claim Audit:** submit a speedup claim, get a public/private evidence pack showing correctness,
adversarial survival, and reproducible scoring.

---

## Campaign Handoff

### Campaign Theme

**Proof Before Speed**

### Launch Sequence

1. GitHub repo with clean README and one-command audit.
2. X announcement with the strongest tension line.
3. Technical X thread explaining why correctness must precede speed.
4. Zenodo DOI for citation and permanence.
5. Follow-up post showing the free vs certified layers.
6. Invite optimization attempts: "Beat the baseline, but your numbers only count if correctness
   survives."

### Calls to Action

- **Primary CTA:** Run the audit.
- **Secondary CTA:** Submit a claim for certification.
- **Community CTA:** Fork it, break it, improve it.

---

## Copy Handoff

### Core Headline

> Speed Claims Don't Count Until Correctness Survives.

### Subhead

FableBreaker is a reproducible counter-benchmark for AI/runtime/compiler optimization claims, built
around generated adversarial cases, semantic hashes, and correctness-first scoring.

### Short Launch Post

> I built FableBreaker: a correctness-first benchmark for AI speedup claims.
>
> Speed without semantic proof is marketing.
>
> • Generated adversarial cases
> • Public + hidden splits
> • Semantic hash verification
> • One-command audit
> • Free open-source public suite
>
> Run it before you believe the number.

### Sharper Variant

> A 17x speedup is meaningless if the evaluator quietly changes the answer.
>
> FableBreaker makes correctness the entry fee.
>
> First survive the adversarial cases.
> Then talk about speed.

### Certification Offer Copy

> Publishing a performance claim?
>
> FableBreaker Claim Audit tests whether the claim survives generated adversarial cases, hidden
> seeds, semantic hashing, and reproducible scoring.
>
> You get a signed evidence pack your audience can inspect, cite, and trust.

---

## Image Handoff

### Visual Direction

Use clean technical credibility, not sci-fi hype. Think "forensic lab for benchmark claims."

### Primary Image Concept

A split-screen technical audit board. Left side: flashy speedup chart with warning marks. Right
side: green verified semantic hashes, adversarial case families, hidden seed lock, and "correctness
passed" stamp.

### Prompt

> A precise editorial tech illustration for an open-source AI benchmark certification tool called
> FableBreaker. Visual metaphor: a performance speedometer being inspected by a rigorous audit
> system. Include abstract code panels, semantic hash checks, adversarial test-case tiles, hidden
> seed lock icons, and a clean verification stamp reading "Correctness First." Style: modern
> technical publication, crisp vector-like bitmap rendering, high contrast, white and graphite
> interface palette with restrained green verification accents, no fantasy elements, no exaggerated
> sci-fi glow, no fake logos, no unreadable tiny text.

### Secondary Image Concepts

- "Benchmark theater vs proof lab"
- "Speed chart blocked by correctness gate"
- "Generated adversarial cases as a test matrix"
- "Evidence pack as a technical certificate"

---

## Video Handoff

### Best Short-Form Video Concept: "The Speedup Trap"

Structure, 35–45 seconds:

**Beat 1:**
Show a big speedup number.
VO: "Everyone loves a 17x speedup."

**Beat 2:**
Cut to broken semantic outputs.
VO: "But speed means nothing if the answer changed."

**Beat 3:**
Show generated adversarial cases flowing into scorer.
VO: "FableBreaker makes correctness the entry fee."

**Beat 4:**
Show public suite, hidden seeds, semantic hashes.
VO: "Generated cases. Hidden splits. Reproducible audits. Semantic verification before speed."

**Beat 5:**
Show GitHub repo / terminal one-command run.
VO: "Run the public suite free. Certify serious claims when the number matters."

**End card:**
FableBreaker — Proof Before Speed
CTA: Run the audit.

---

## Best Strategic Next Move

Publish the repo as the public-good layer, but make the README point clearly toward the future
certification layer. The free release earns trust. The paid layer sells trust custody.

The cleanest market sentence is:

> **FableBreaker is open-source benchmark infrastructure for people who believe performance claims
> should survive correctness audits before they become marketing.**
