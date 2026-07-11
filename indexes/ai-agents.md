# AI & Agents — map of content

_Last regenerated: 2026-07-11_

## Fine-tuning

- [Fine-tuning an LLM with Unsloth (Qwen 2.5 + LoRA walkthrough)](../areas/ai-agents/unsloth-qlora-finetuning-workflow.md) — end-to-end QLoRA SFT run on a free T4: 4-bit Qwen2.5-7B, LoRA r=16, SFTTrainer, hyperparameter intuitions, loss-curve reading. `growing`
- [LoRA / QLoRA fundamentals](../areas/ai-agents/lora-qlora-fundamentals.md) — the adapter math (r, alpha, target modules, dropout) with a worked 4096×4096 example, and the memory arithmetic behind 4-bit + adapters. `growing`
- [Chat templates & training-data formatting](../areas/ai-agents/chat-templates-and-training-data-formatting.md) — how examples become token strings, chat-template matching, EOS, loss masking; where beginner fine-tunes silently fail. `seed`
- [Exporting fine-tuned LLMs: adapters vs merged vs GGUF](../areas/ai-agents/finetuned-llm-export-formats.md) — the three deployment artifacts after a LoRA fine-tune and when to pick each. `growing`
