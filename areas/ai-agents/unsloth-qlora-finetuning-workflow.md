---
title: "Fine-tuning an LLM with Unsloth (Qwen 2.5 + LoRA walkthrough)"
area: ai-agents
tags: [fine-tuning, unsloth, lora, qwen, sft-trainer, peft]
source: "Unsloth Qwen 2.5 finetuning Colab notebook (github.com/unslothai/unsloth)"
created: 2026-07-11
updated: 2026-07-11
status: seed
---

# Fine-tuning an LLM with Unsloth (Qwen 2.5 + LoRA walkthrough)

## TL;DR
A complete supervised fine-tuning (SFT) run of Qwen2.5-7B on a free Tesla T4
(14.7 GB): load the base model in 4-bit, attach LoRA adapters (~40M trainable
params, <1% of the model), train 60 demo steps on the Alpaca-cleaned
instruction dataset with TRL's `SFTTrainer`, then save the adapters. Unsloth
wraps HuggingFace + PEFT with custom kernels that roughly double training and
inference speed. Peak GPU memory during training was ~7.9 GB — a 7B model
fine-tuned comfortably on free-tier hardware.

## How it works
The pipeline, end to end:

```
FastLanguageModel.from_pretrained("unsloth/Qwen2.5-7B",
                                  max_seq_length=2048, load_in_4bit=True)
        │  base model frozen in 4-bit  (see [LoRA/QLoRA fundamentals])
        ▼
FastLanguageModel.get_peft_model(r=16, lora_alpha=16, lora_dropout=0,
    target_modules=[q,k,v,o proj + gate/up/down proj],
    use_gradient_checkpointing="unsloth")
        │  → 40,370,176 trainable params across all 28 layers
        ▼
Dataset: yahma/alpaca-cleaned (51,760 examples), formatted into the
Alpaca template (### Instruction / ### Input / ### Response)
+ EOS token appended manually to every example
        ▼
trl.SFTTrainer: batch 2 × grad-accum 4 (effective 8), lr 2e-4 linear,
warmup 5, optim adamw_8bit, weight_decay 0.01, fp16 (T4 has no bf16),
max_steps=60 (demo — a real run uses num_train_epochs=1)
        ▼
FastLanguageModel.for_inference(model)  → ~2x faster generation
        ▼
model.save_pretrained("lora_model")  → adapters only (see export note)
```

Observed numbers from the run: 60 steps took 462 s (~7.7 min); memory went
from 5.76 GB reserved (model load) to 7.89 GB peak, i.e. only ~2.1 GB of
overhead for the actual training. The fine-tuned model answered test prompts
correctly and emitted `<|endoftext|>` cleanly.

## Why it's designed this way
- **4-bit base + LoRA adapters** is the QLoRA recipe: it's what makes a 7B
  model trainable on 14.7 GB at all. Full fine-tuning of 7B params in fp16
  would need well over 80 GB with optimizer states.
- **`adamw_8bit`** quantizes optimizer state (normally 2× fp32 copies per
  param) — another large memory win with negligible quality loss.
- **`use_gradient_checkpointing="unsloth"`** is Unsloth's own variant,
  claimed ~30% less VRAM than standard checkpointing.
- **Unsloth's speedup** comes from hand-written Triton kernels and patched
  attention/MLP forward passes. The notebook asserts "2x faster" but never
  explains the mechanism — flagged in Open questions.
- **`packing=False`**: packing concatenates short examples into one sequence
  for up to ~5x throughput; left off here, worth knowing it exists.

## Gotchas & edge cases
- **Append the EOS token to every training example.** The notebook calls this
  out explicitly: without it the model never learns to stop and you get
  infinite generations. This is the single most common silent bug in DIY SFT.
- **This run trains on the full prompt+response.** Loss masking so the model
  is only trained on responses ("train on completions only") is linked to TRL
  docs but *not implemented* — the model is also being penalized for
  reconstructing the instruction text.
- **`max_steps=60` is a smoke test, not a fine-tune.** 60 steps × effective
  batch 8 = 480 of 51,760 examples seen (<1% of one epoch).
- **Base vs instruct checkpoint**: this uses the *base* Qwen2.5-7B, so the
  Alpaca template effectively teaches it instruction-following from scratch.
  Fine-tuning an instruct model instead requires matching its existing chat
  template.
- Must call `FastLanguageModel.for_inference(model)` before generating —
  easy to forget after training.

## Where it shows up
- The standard entry point for anyone fine-tuning open-weight LLMs on
  consumer/free hardware (Colab T4, single consumer GPU).
- Interview-relevant as the concrete instance of "how would you adapt an
  open-source model cheaply?" — the answer is this exact QLoRA recipe.

## Related notes
- [LoRA / QLoRA fundamentals](lora-qlora-fundamentals.md) — what the adapter
  math and 4-bit quantization are actually doing.
- [Exporting fine-tuned LLMs: adapters vs merged vs GGUF](finetuned-llm-export-formats.md)
  — what to do with the model after training.

## Open questions
- *How* does Unsloth achieve 2x speed — kernel fusion? avoiding double
  dequantization? Worth a `/deep-dive unsloth internals`.
- What do `use_rslora` (rank-stabilized LoRA) and `loftq_config` do? Both
  exposed in the config, both left at defaults, neither explained.
- How is train-on-responses-only masking implemented in TRL, and how much
  does it matter in practice?
- RoPE scaling ("kaiokendev's method") lets `max_seq_length` exceed native
  context — mechanism not understood yet.
