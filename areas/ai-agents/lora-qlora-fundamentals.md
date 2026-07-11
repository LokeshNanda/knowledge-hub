---
title: "LoRA / QLoRA fundamentals"
area: ai-agents
tags: [lora, qlora, peft, 4-bit-quantization, fine-tuning]
source: "Unsloth Qwen 2.5 finetuning Colab notebook (github.com/unslothai/unsloth)"
created: 2026-07-11
updated: 2026-07-11
status: growing
---

# LoRA / QLoRA fundamentals

## TL;DR
LoRA freezes the base model and injects small trainable low-rank matrices
into chosen linear layers, so you train <1% of the parameters while getting
most of the quality of full fine-tuning. QLoRA goes further: the frozen base
is stored in 4-bit precision while the adapters train in higher precision,
cutting memory ~4x versus fp16 and making 7B-class models trainable on a
single free-tier GPU.

## How it works
**The intuition: a trainable detour around a frozen weight.** Picture one
weight matrix `W` inside the model — say 4096×4096, about 16.7M numbers, all
frozen. LoRA bolts two tiny matrices beside it, and the input flows through
both paths and gets summed:

```
              ┌── W (frozen, 16.7M params) ──┐
input ────────┤                              ├──(+)──> output
              └── A (4096×16) → B (16×4096) ─┘
                   trainable, ~131K params
```

Because the detour's output is *added* to W's output, training just A and B
is enough to steer the layer's behavior — at ~0.8% of the parameter count.

Formally, a linear layer computes `y = Wx` where `W` is `d×k` and frozen,
and LoRA adds a parallel low-rank update:

```
y = Wx + (alpha/r) · B·A·x        A: r×k,  B: d×r,  r ≪ d,k
```

Only `A` and `B` are trained. With `r=16` on a 7B model (adapters on all
attention projections q/k/v/o plus the MLP gate/up/down projections), that
came to ~40M trainable parameters — under 1% of the model — in the Qwen 2.5
run in [the workflow note](unsloth-qlora-finetuning-workflow.md).

- **`r` (rank)** is the width of the detour — the "16" dimension in A and B.
  Higher r = more trainable capacity, more memory, more overfitting risk on
  small datasets. Rules of thumb: r=16 is a solid default; r=32-64 for
  harder tasks (e.g. SQL generation); r=128+ is rarely worth it.
- **`lora_alpha`** scales the update's magnitude; the effective scale is
  `alpha/r`. Setting `alpha = r` (both 16 in the notebook) gives scale 1.0 —
  the common default; `alpha = 2×r` for a stronger effect. Not worth
  agonizing over early on.
- **Target modules** decide *where* adaptation happens. The seven names in
  the notebook are the seven matrix types inside every transformer layer
  (q/k/v/o are attention; gate/up/down are the feed-forward network).
  Targeting all seven is the modern default; embeddings and the LM head are
  usually left alone.
- **`lora_dropout`** randomly disables parts of the adapter during training
  to fight overfitting. Fine at 0 for short runs; try 0.05-0.1 if the model
  memorizes instead of generalizing.

**QLoRA's addition:** the frozen `W` is quantized to 4-bit (the notebook
loads a pre-quantized checkpoint via `load_in_4bit=True`). Gradients never
update `W`, so its low precision mostly doesn't hurt; the trainable `A`/`B`
stay in fp16/bf16. Memory for the base drops ~4x versus fp16.

## Why it's designed this way
- Full fine-tuning needs memory for weights + gradients + Adam optimizer
  state — roughly 4x the weights' own size in bookkeeping, so training all
  7B parameters would need on the order of 100 GB. LoRA sidesteps this:
  gradients and optimizer state exist only for the tiny adapters.
- The 4-bit half attacks the *other* memory cost: a 7B model just sitting in
  memory at 16-bit needs ~14 GB — nearly all of a free T4's 16 GB before
  training starts. 4-bit shrinks that residency to ~4 GB. It's purely a
  memory trick; what you're training doesn't change.
- The low-rank form is motivated by the observation that fine-tuning weight
  *deltas* have low intrinsic rank — a small `B·A` captures most of the
  useful change.
- Adapters are composable and cheap to store (tens of MB): you can keep one
  base model and many task-specific adapters, swapping at load time — see
  [export formats](finetuned-llm-export-formats.md).

## Gotchas & edge cases
- `alpha/r` scaling matters: doubling `r` without touching `alpha` *halves*
  the update scale, which silently changes effective learning rate.
- 4-bit quantization degrades the base slightly; for quality-critical evals,
  compare against an fp16 baseline.
- LoRA underperforms full fine-tuning when the task requires large behavioral
  shifts (new language, heavy domain drift) — it's an adaptation technique,
  not a retraining technique.
- Variants seen but not yet understood: rsLoRA (rank-stabilized scaling,
  `alpha/sqrt(r)`) and LoftQ (quantization-aware adapter init).

## Where it shows up
- The default technique behind nearly every "fine-tune an open LLM on one
  GPU" tutorial (Unsloth, Axolotl, HF PEFT).
- Interview question staple: "how would you fine-tune a large model with
  limited compute?" — LoRA/QLoRA is the expected answer, with the memory
  arithmetic above as supporting detail.

## Related notes
- [Fine-tuning an LLM with Unsloth (Qwen 2.5 + LoRA walkthrough)](unsloth-qlora-finetuning-workflow.md)
  — a concrete end-to-end run using this technique.
- [Exporting fine-tuned LLMs: adapters vs merged vs GGUF](finetuned-llm-export-formats.md)
  — what an "adapter" is as a deployment artifact.
- [Chat templates & training-data formatting](chat-templates-and-training-data-formatting.md)
  — the data side of the same fine-tune.

## Open questions
- Precisely why does QLoRA's 4-bit NF4 quantization preserve quality so well?
  (The notebook asserts it; the QLoRA paper explains it — read it.)
- When is it worth adding embeddings/LM-head to `target_modules`?
- rsLoRA and LoftQ: what problems do they solve and when to switch them on?
