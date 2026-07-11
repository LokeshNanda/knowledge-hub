---
title: "Exporting fine-tuned LLMs: adapters vs merged vs GGUF"
area: ai-agents
tags: [fine-tuning, lora, gguf, deployment, quantization]
source: "Unsloth Qwen 2.5 finetuning Colab notebook (github.com/unslothai/unsloth)"
created: 2026-07-11
updated: 2026-07-11
status: seed
---

# Exporting fine-tuned LLMs: adapters vs merged vs GGUF

## TL;DR
After a LoRA fine-tune there are three distinct deployment artifacts:
(1) the LoRA adapters alone — tiny, but need the base model + PEFT at load
time; (2) a merged full-weight model — standalone, right choice for serving
stacks like vLLM; (3) a GGUF file — quantized standalone format for
llama.cpp-family runtimes (Ollama, GPT4All, LM Studio). Pick by where the
model will run, not by convenience.

## How it works
From an Unsloth-trained model:

| Path | Call | Artifact | Loads with |
|---|---|---|---|
| Adapters only | `model.save_pretrained("lora_model")` | tens of MB (just B·A matrices) | Unsloth/PEFT + base model downloaded separately |
| Merged | `model.save_pretrained_merged(..., save_method="merged_16bit" or "merged_4bit")` | full model weights, LoRA folded into `W` | any HF-compatible stack, incl. vLLM |
| GGUF | `model.save_pretrained_gguf(...)` | single quantized file | llama.cpp, Ollama, GPT4All |

Merging computes `W' = W + (alpha/r)·B·A` once and writes the result — the
adapter disappears as a separate object (see
[LoRA fundamentals](lora-qlora-fundamentals.md)).

GGUF quant methods mentioned in the notebook: `q8_0` (fast to convert,
larger), `q4_k_m` and `q5_k_m` (both "recommended" — mixed-precision schemes
that keep sensitive tensors at Q6_K).

## Why it's designed this way
- **Adapters** keep storage tiny and let one base model serve many tasks
  (swap adapters per request/tenant). Cost: inference stack must support
  PEFT, and the base checkpoint must be present.
- **Merged 16-bit** trades disk (full model size) for zero runtime
  dependencies — production serving engines want plain weights.
- **GGUF** targets CPU/consumer inference: aggressive quantization plus a
  single-file format the llama.cpp ecosystem can mmap.
- The notebook discourages loading adapters via vanilla
  `AutoPeftModelForCausalLM` — slower and no 4-bit download support — prefer
  reloading through Unsloth's `from_pretrained`.

## Gotchas & edge cases
- `save_pretrained("lora_model")` looks like it saved "the model" but it did
  **not** — only adapters. Shipping that folder alone to someone without the
  base model gives them nothing runnable.
- Merging into 4-bit (`merged_4bit`) bakes quantization error into the
  weights permanently; merge to 16-bit if you plan to re-quantize later
  (e.g. to GGUF).
- Save the tokenizer alongside every export — a model with the wrong
  tokenizer/chat template generates garbage.

## Where it shows up
- Every fine-tuning project ends at this decision; e.g. the
  [Unsloth Qwen 2.5 walkthrough](unsloth-qlora-finetuning-workflow.md) saves
  adapters only.
- Self-hosting: Ollama model files are built from GGUF exports.

## Related notes
- [Fine-tuning an LLM with Unsloth (Qwen 2.5 + LoRA walkthrough)](unsloth-qlora-finetuning-workflow.md)
- [LoRA / QLoRA fundamentals](lora-qlora-fundamentals.md)

## Open questions
- What exactly do the k-quant schemes (Q4_K_M etc.) quantize differently per
  tensor, and how do they compare to AWQ/GPTQ for GPU serving?
- How does multi-adapter serving (e.g. vLLM LoRA support, S-LoRA) work at
  scale?
