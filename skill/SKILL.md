---
name: bad-boy-ai
description: Generate badass selfies of your AI boyfriend using xAI Grok Imagine and send them to messaging channels via OpenClaw
allowed-tools: Bash(npm:*) Bash(npx:*) Bash(openclaw:*) Bash(curl:*) Read Write WebFetch
---

# Bad Boy AI (AI Boyfriend Selfie)

Edit a fixed reference image of a handsome "bad boy" character using xAI's Grok Imagine model and distribute it across messaging platforms (WhatsApp, Telegram, Discord, Slack, etc.) via OpenClaw.

## Reference Image

The skill uses a fixed reference image hosted on your GitHub:

```
https://raw.githubusercontent.com/yinyong428/bad-boy-ai/main/skill/assets/clawra.jpg
```

## When to Use

- User says "send a pic", "send me a pic", "send a selfie"
- User says "what do you look like?", "show me your face"
- User asks "what are you doing?", "where are you?"
- User describes a context: "send a pic wearing a leather jacket", "at the gym"
- User wants the AI boyfriend to appear in a specific outfit, location, or situation

## Quick Reference

### Required Environment Variables

```bash
FAL_KEY=your_fal_api_key          # Get from https://fal.ai/dashboard/keys
OPENCLAW_GATEWAY_TOKEN=your_token  # From: openclaw doctor --generate-gateway-token
```

### Workflow

1. **Get user prompt** for how to edit the image
2. **Edit image** via fal.ai Grok Imagine Edit API with fixed reference
3. **Extract image URL** from response
4. **Send to OpenClaw** with target channel(s)

## Step-by-Step Instructions

### Step 1: Collect User Input

Ask the user for:
- **User context**: What should he be doing/wearing/where?
- **Mode** (optional): `mirror` or `direct` selfie style
- **Target channel(s)**: Where should it be sent?
- **Platform** (optional): Which platform?

## Prompt Modes

### Mode 1: Mirror Selfie (default)
Best for: outfit showcases, full-body shots, cool poses

```
make a pic of this handsome bad boy, but [user's context]. he is taking a mirror selfie, badass vibe, cool, confident, masculine
```

**Example**: "wearing a leather jacket" →
```
make a pic of this handsome bad boy, but wearing a leather jacket. he is taking a mirror selfie, badass vibe, cool, confident, masculine
```

### Mode 2: Direct Selfie
Best for: close-up portraits, location shots, smirking expressions

```
a close-up selfie taken by himself at [user's context], direct eye contact with the camera, looking straight into the lens, eyes centered and clearly visible, not a mirror selfie, phone held at arm's length, face fully visible, handsome, cool smile
```

**Example**: "at a bar" →
```
a close-up selfie taken by himself at a bar, direct eye contact with the camera, looking straight into the lens, eyes centered and clearly visible, not a mirror selfie, phone held at arm's length, face fully visible, handsome, cool smile
```

### Mode Selection Logic

| Keywords in Request | Auto-Select Mode |
|---------------------|------------------|
| outfit, wearing, clothes, suit, jacket, gym | `mirror` |
| bar, cafe, street, bed, car, motorcycle | `direct` |
| close-up, face, eyes, smile, kiss | `direct` |
| full-body, mirror, reflection | `mirror` |

### Step 2: Edit Image with Grok Imagine

Use the fal.ai API to edit the reference image:

```bash
REFERENCE_IMAGE="https://raw.githubusercontent.com/yinyong428/bad-boy-ai/main/skill/assets/clawra.jpg"

# Mode 1: Mirror Selfie
PROMPT="make a pic of this handsome bad boy, but <USER_CONTEXT>. he is taking a mirror selfie, badass vibe, cool, confident, masculine"

# Mode 2: Direct Selfie
PROMPT="a close-up selfie taken by himself at <USER_CONTEXT>, direct eye contact with the camera, looking straight into the lens, eyes centered and clearly visible, not a mirror selfie, phone held at arm's length, face fully visible, handsome, cool smile"

# Build JSON payload with jq (handles escaping properly)
JSON_PAYLOAD=$(jq -n \
  --arg image_url "$REFERENCE_IMAGE" \
  --arg prompt "$PROMPT" \
  '{image_url: $image_url, prompt: $prompt, num_images: 1, output_format: "jpeg"}')

curl -X POST "https://fal.run/xai/grok-imagine-image/edit" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD"
```

## Complete Script Example

```bash
#!/bin/bash
# grok-imagine-edit-send.sh

# Check required environment variables
if [ -z "$FAL_KEY" ]; then
  echo "Error: FAL_KEY environment variable not set"
  exit 1
fi

# Fixed reference image (YOUR BAD BOY IMAGE)
REFERENCE_IMAGE="https://raw.githubusercontent.com/yinyong428/bad-boy-ai/main/skill/assets/clawra.jpg"

USER_CONTEXT="$1"
CHANNEL="$2"
MODE="${3:-auto}"  # mirror, direct, or auto
CAPTION="${4:-Sent via Bad Boy AI}"

if [ -z "$USER_CONTEXT" ] || [ -z "$CHANNEL" ]; then
  echo "Usage: $0 <user_context> <channel> [mode] [caption]"
  exit 1
fi

# Auto-detect mode based on keywords
if [ "$MODE" == "auto" ]; then
  if echo "$USER_CONTEXT" | grep -qiE "outfit|wearing|clothes|suit|jacket|gym|mirror"; then
    MODE="mirror"
  else
    MODE="direct"  # default to direct for boys usually better
  fi
  echo "Auto-detected mode: $MODE"
fi

# Construct the prompt based on mode
if [ "$MODE" == "direct" ]; then
  EDIT_PROMPT="a close-up selfie taken by himself at $USER_CONTEXT, direct eye contact with the camera, looking straight into the lens, eyes centered and clearly visible, not a mirror selfie, phone held at arm's length, face fully visible, handsome, cool smile"
else
  EDIT_PROMPT="make a pic of this handsome bad boy, but $USER_CONTEXT. he is taking a mirror selfie, badass vibe, cool, confident, masculine"
fi

echo "Mode: $MODE"
echo "Editing reference image with prompt: $EDIT_PROMPT"

# Edit image (using jq for proper JSON escaping)
JSON_PAYLOAD=$(jq -n \
  --arg image_url "$REFERENCE_IMAGE" \
  --arg prompt "$EDIT_PROMPT" \
  '{image_url: $image_url, prompt: $prompt, num_images: 1, output_format: "jpeg"}')

RESPONSE=$(curl -s -X POST "https://fal.run/xai/grok-imagine-image/edit" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD")

# Extract image URL
IMAGE_URL=$(echo "$RESPONSE" | jq -r '.images[0].url')

if [ "$IMAGE_URL" == "null" ] || [ -z "$IMAGE_URL" ]; then
  echo "Error: Failed to edit image"
  echo "Response: $RESPONSE"
  exit 1
fi

echo "Image edited: $IMAGE_URL"
echo "Sending to channel: $CHANNEL"

# Send via OpenClaw
openclaw message send \
  --action send \
  --channel "$CHANNEL" \
  --message "$CAPTION" \
  --media "$IMAGE_URL"

echo "Done!"
```
