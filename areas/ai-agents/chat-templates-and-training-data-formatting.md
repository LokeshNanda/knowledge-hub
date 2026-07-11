---
title: "Chat templates & training-data formatting for fine-tuning"
area: ai-agents
tags: [fine-tuning, chat-templates, tokenization, data-prep, sft]
source: "Claude lesson explaining the Unsloth Qwen 2.5 notebook (inbox drop, 2026-07-11)"
created: 2026-07-11
updated: 2026-07-11
status: seed
---

# Chat templates & training-data formatting for fine-tuning

## TL;DR
A model never trains on `{"instruction": ..., "output": ...}` dictionaries —
every example is flattened into one string of tokens first. Instruct models
expect that string to use the exact special-token markup they were trained
with (their *chat template*), and a mismatch between training format and the
model's expected format — or between training format and inference format —
silently produces an erratic model. This, plus forgetting the EOS token, is
the most common way beginner fine-tunes fail without any error message.

## How it works
Three layers between your dataset and what the model actually sees:

1. **Tokenization.** The tokenizer converts text to integer IDs — the model
   only ever sees IDs. Consequence: all lengths (including
   `max_seq_length`) are measured in tokens, not characters, and examples
   longer than `max_seq_length` are **truncated silently**.
2. **Flattening.** A formatting function maps each structured example to a
   single `"text"` string. Two common shapes:
   - *Plain instruction template* (e.g. Alpaca's `### Instruction / ###
     Input / ### Response`) — used when fine-tuning a **base** model, which
     has no built-in dialogue format. This is what the
     [Unsloth Qwen 2.5 walkthrough](unsloth-qlora-finetuning-workflow.md) uses.
   - *Chat template* — used with **instruct** models. Each model family has
     its own speaker markers (Qwen: `<|im_start|>user ... <|im_end|>`;
     Llama uses different tokens). `tokenizer.apply_chat_template(messages,
     tokenize=False)` emits the correct markup for whatever model is loaded,
     which is why notebooks use it instead of hand-building strings.
3. **End-of-sequence token.** Each training example must end with the EOS
   token (some templates add it; the Alpaca-style notebook appends
   `tokenizer.eos_token` manually). Without it the model never learns to
   stop and generates forever.

**Loss masking (`train_on_responses_only`).** By default the model is graded
on *every* token in the flattened string — including the prompt, so it's
partly learning to generate questions. Ideally loss is computed only on the
answer tokens; Unsloth ships a `train_on_responses_only` helper (TRL has the
equivalent "completions-only" collator) and it noticeably improves results.

## Why it's designed this way
- Chat templates exist because instruct models were *trained* with those
  exact markers delimiting speakers; the markup is how the model knows where
  the user stopped and it should respond. The format is part of the model's
  learned behavior, not decoration.
- `apply_chat_template` puts the format under the tokenizer's control so the
  same training code works across model families.
- The train/inference formats must match for the same reason: the model
  completes patterns it has seen. Fine-tune with one format, prompt with
  another, and you're out of distribution.

## Gotchas & edge cases
- **Mismatched chat templates are the #1 silent killer of beginner
  fine-tunes** — no error, just an erratic model. Always generate the
  training strings and the inference prompts through the same code path.
- **Silent truncation:** examples longer than `max_seq_length` lose their
  tails with no warning. For prompts that embed large context (e.g. schema
  DDL for text-to-SQL), 2048 is often too small — budget 4096+ and check
  tokenized lengths before training.
- Forgetting EOS → infinite generations (see the
  [workflow note](unsloth-qlora-finetuning-workflow.md) for the observed fix
  working: the tuned model emitted `<|endoftext|>` cleanly).
- Base vs instruct checkpoint changes everything about this step: base
  models need you to invent/adopt a template; instruct models require you to
  *match* theirs.

## Where it shows up
- Every SFT pipeline (Unsloth, TRL, Axolotl) has exactly this data-prep
  stage; debugging a "weird" fine-tuned model almost always starts here.
- Also the practical reason model-swapping isn't free: moving from Qwen to
  Llama means the training strings change even if the dataset doesn't.

## Related notes
- [Fine-tuning an LLM with Unsloth (Qwen 2.5 + LoRA walkthrough)](unsloth-qlora-finetuning-workflow.md)
  — the pipeline this data-prep stage feeds.
- [LoRA / QLoRA fundamentals](lora-qlora-fundamentals.md) — the other half
  of what makes the fine-tune work.

## Open questions
- How exactly does `train_on_responses_only` locate the response boundary in
  an arbitrary chat template (marker matching? offsets?), and what happens
  with multi-turn examples?
- What does a good pre-training data audit look like — distribution of
  tokenized lengths, truncation rate, template correctness checks?
