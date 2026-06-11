# FableBreaker Product Strategy

## Positioning

FableBreaker is a reproducible counter-benchmark service for AI-generated performance claims.
It is not anti-AI. It is anti-fake-proof.

Core message:

> Speed without semantic proof is marketing. FableBreaker makes evaluator optimization claims pass
> correctness, hidden seeds, adversarial cases, and reproducible audit before speed counts.

## What To Give Away

Give away the public trust layer:

- open benchmark language,
- public dataset generator,
- public scorer,
- public baseline candidate,
- public audit manifesto,
- simple local service,
- example public score reports.

This makes the work credible and helps builders. It also makes it harder for hype merchants to
control the benchmark narrative.

Every public release should be a full production ZIP, with `dataset/`, `candidates/`, `tools/`,
all `.py` files, manifests, score outputs, and readable proof docs included.

## What To Keep As Paid / Deeper Tech

Keep the certification layer deeper:

- rotating hidden seed corpora,
- larger private stress suites,
- per-family diagnostic reports,
- memory and allocation profiling,
- CI-hosted candidate evaluation,
- signed evidence packs,
- private benchmark design for companies,
- custom adversarial suites for compiler/runtime teams,
- longitudinal score history and regression monitoring.

## Offer Ladder

1. **Free Open Suite**
   Public repo, local runner, public dataset, public service.

2. **Hosted Public Leaderboard**
   Free submissions with delayed or limited hidden scoring.

3. **Certification Report**
   Paid one-time review for a model, agent, compiler, evaluator, runtime, or optimization claim.

4. **Private Red-Team Benchmark**
   Paid custom suite for teams that need to know whether their agent actually improved code or only
   optimized a demo path.

5. **Continuous Benchmark Monitoring**
   Subscription service that runs hidden/regression suites against new model or agent releases.

6. **Enterprise Benchmark Foundry**
   Custom benchmark design, audit packet generation, CI integration, evidence-pack signing, and
   internal leaderboard infrastructure.

## Buyer Types

- AI labs that need credible agent-evaluation proof.
- Compiler/runtime teams that want adversarial evaluator benchmarks.
- Devtool companies building code agents.
- Investors and technical diligence teams checking vendor claims.
- Open-source communities tired of hype benchmarks.
- Independent builders who want a fair proving ground.

## Public Narrative

Do not sell this as "we beat Fable" only. That is useful attention, but too small.

Sell it as:

- proof-before-speed infrastructure,
- anti-hype benchmark certification,
- hidden-seed adversarial evaluation,
- reproducibility layer for AI coding claims,
- public-good benchmark with paid trust services.

## First Launch Move

Publish the open repo with:

- a short README,
- the source note,
- the public dataset,
- the service runner,
- one example certified score,
- a call for agents/models to submit optimized candidates.

Then announce:

> I made a benchmark where speedup claims do not count unless correctness survives hidden generated
> cases. Public suite is free. Hidden certification is coming.

## Monitor Next

Next product artifact: a lightweight hosted leaderboard spec with submission format, hidden-seed
policy, and certification badge schema.
