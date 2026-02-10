import os
import sys
import json
import time
import hmac
import hashlib
import datetime
import requests
import subprocess
from urllib.parse import quote

# --- CONFIGURATION ---
# Keys must be set via environment variables for security!
# openclaw config set skills.entries.bad-boy-ai.env.VOLC_AK "your_ak"
AK = os.environ.get("VOLC_AK")
SK = os.environ.get("VOLC_SK")

if not AK or not SK:
    print("[ERROR] Volcengine keys not found. Please set VOLC_AK and VOLC_SK env vars.")
    print("Run: openclaw config set skills.entries.bad-boy-ai.env.VOLC_AK 'YOUR_AK'")
    sys.exit(1)

REGION = "cn-north-1"
SERVICE = "cv"
HOST = "visual.volcengineapi.com"
VERSION = "2022-08-31" 

# --- BAD BOY PROMPT (BASE) ---
BASE_PROMPT = "handsome asian man, 25 years old, bad boy style, sharp jawline, messy hair, silver earring, smirk with dimple, masculine, cinematic lighting, 8k, photorealistic, best quality"

def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def get_signature_key(key, dateStamp, regionName, serviceName):
    kDate = sign(key.encode("utf-8"), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, "request")
    return kSigning

def do_request(action, body):
    method = "POST"
    endpoint = f"https://{HOST}/"
    content_type = "application/json"
    
    query_params = f"Action={action}&Version={VERSION}"
    payload = json.dumps(body)
    
    t = datetime.datetime.utcnow()
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")
    
    canonical_uri = "/"
    canonical_querystring = query_params
    canonical_headers = f"content-type:{content_type}\nhost:{HOST}\nx-date:{amz_date}\n"
    signed_headers = "content-type;host;x-date"
    payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    
    canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    
    algorithm = "HMAC-SHA256"
    credential_scope = f"{date_stamp}/{REGION}/{SERVICE}/request"
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    
    signing_key = get_signature_key(SK, date_stamp, REGION, SERVICE)
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    
    authorization_header = f"{algorithm} Credential={AK}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    headers = {
        "Content-Type": content_type,
        "X-Date": amz_date,
        "Authorization": authorization_header,
        "Host": HOST
    }
    
    url = f"{endpoint}?{query_params}"
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] API Request ({action}) failed: {e}")
        # Print response body if available for debugging
        if 'response' in locals():
            print(f"[DEBUG] Response: {response.text}")
        return None

def submit_task(prompt):
    body = {
        "req_key": "jimeng_t2i_v30",
        "prompt": prompt,
        "width": 1328, # 1:1
        "height": 1328,
        "seed": -1,
        "use_pre_llm": True
    }
    print(f"[INFO] Submitting task to Jimeng V3.0...")
    return do_request("CVSync2AsyncSubmitTask", body)

def get_result(task_id):
    body = {
        "req_key": "jimeng_t2i_v30",
        "task_id": task_id,
        "req_json": json.dumps({"return_url": True}) # Request URL return
    }
    return do_request("CVSync2AsyncGetResult", body)

def send_via_openclaw(channel, image_url, caption):
    print(f"[INFO] Sending to OpenClaw channel: {channel}")
    try:
        subprocess.run([
            "openclaw", "message", "send",
            "--target", channel,
            "--message", caption,
            "--media", image_url
        ], check=True)
        print("[INFO] Sent via CLI.")
    except Exception as e:
        print(f"[ERROR] CLI failed, trying HTTP fallback... ({e})")
        try:
            requests.post("http://localhost:18789/message", json={
                "action": "send",
                "channel": channel,
                "message": caption,
                "media": image_url
            })
            print("[INFO] Sent via HTTP API.")
        except Exception as e2:
            print(f"[ERROR] Failed to send message: {e2}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 clawra-selfie.py <prompt> <channel> [mode] [caption]")
        sys.exit(1)
        
    user_prompt = sys.argv[1]
    channel = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "auto"
    caption = sys.argv[4] if len(sys.argv) > 4 else "Sent via Jimeng V3.0"
    
    # Construct Prompt
    context = ""
    if mode == "direct" or "close-up" in user_prompt:
        context = "close-up selfie, looking at camera, holding phone, intimate angle"
    else:
        context = "mirror selfie, full body shot, holding phone in mirror"
        
    full_prompt = f"{BASE_PROMPT}, {context}, {user_prompt}"
    print(f"[INFO] Prompt: {full_prompt}")
    
    # 1. Submit Task
    submit_resp = submit_task(full_prompt)
    if not submit_resp or submit_resp.get("code") != 10000:
        print(f"[ERROR] Submission failed: {submit_resp}")
        sys.exit(1)
        
    task_id = submit_resp["data"]["task_id"]
    print(f"[INFO] Task ID: {task_id}. Polling for result...")
    
    # 2. Poll for Result
    max_retries = 30 # 30 * 2s = 60s timeout
    image_url = ""
    
    for i in range(max_retries):
        time.sleep(2)
        res = get_result(task_id)
        
        if not res:
            continue
            
        status = res.get("data", {}).get("status")
        print(f"[INFO] Status: {status}")
        
        if status == "done":
            # Success!
            urls = res["data"].get("image_urls", [])
            if urls:
                image_url = urls[0]
            break
        elif status in ["not_found", "expired"]:
            print(f"[ERROR] Task failed/expired: {status}")
            sys.exit(1)
        # else: 'in_queue' or 'generating', continue polling
        
    if image_url:
        print(f"[INFO] Image Ready: {image_url}")
        send_via_openclaw(channel, image_url, caption)
    else:
        print("[ERROR] Timeout or no URL returned.")
        sys.exit(1)

if __name__ == "__main__":
    main()
