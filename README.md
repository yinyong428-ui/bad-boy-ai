# Bad Boy AI (AI Boyfriend) 😈

> **"Be genuinely helpful, but with attitude."**

Your personal AI boyfriend skill for OpenClaw. He's charming, a bit dangerous, and sends you badass selfies on demand using xAI Grok Imagine (via fal.ai) or Volcengine (Jimeng).

![Bad Boy](https://raw.githubusercontent.com/yinyong428/bad-boy-ai/main/skill/assets/clawra.jpg)

## Features

- **📸 Selfie Generation**: Ask "send a pic" or "what are you doing?" and get a photorealistic selfie.
- **😈 Bad Boy Persona**: Defines a "Core Truth" in your agent's soul to act cool, flirty, and slightly teasing.
- **🖼️ High Quality**: Supports **Volcengine (Jimeng V3.0)** for cinema-grade Asian male portraits.
- **💬 Multi-Platform**: Works on Telegram, Discord, WhatsApp, etc.

## Quick Start

### 1. Install

```bash
npx clawhub@latest install yinyong428/bad-boy-ai
```

### 2. Configure Keys

You need a **Volcengine (火山引擎)** account for high-quality image generation.

Get your AK/SK from [Volcengine Console](https://console.volcengine.com/iam/keymanage/).

```bash
# Edit the script manually to set your AK/SK (for now)
# Path: skills/bad-boy-ai/skill/scripts/clawra-selfie.py
```

*(Note: Future versions will support env var configuration for Volcengine)*

### 3. Usage

Just talk to your agent!

- "Send me a selfie"
- "What are you doing?"
- "Show me you at the gym"
- "I want to see you in a suit"

## Persona (Soul)

This skill injects a specific persona into your agent:

- **Vibe**: Bad boy, confident, charming, loyal.
- **Tone**: Cool, concise, flirty. No robotic "How can I help you".
- **Visuals**: Handsome Asian male, 25yo, messy hair, silver earring, smirk.

## Customization

You can change his look by editing the `BASE_PROMPT` in `skill/scripts/clawra-selfie.py`.

```python
BASE_PROMPT = "handsome asian man, 25 years old, bad boy style..."
```

## License

MIT
