# VenueVibe: Architecture & System Design Specification

## 1. Unique Selling Proposition (USP)
VenueVibe is not a standard mapping application; it is a **B2B2C gamified crowd load-balancing engine**. While existing solutions passively show maps, VenueVibe actively manipulates crowd dynamics by financially incentivizing users (via "VibePoints") to route toward underutilized stadium vendors. This simultaneously increases stadium F&B revenue while eliminating user wait times.

## 2. Technical Stack & Feasibility
This architecture utilizes an elite-tier, serverless cloud infrastructure designed for high-concurrency environments (50,000+ simultaneous users per stadium).
* **Frontend:** Vanilla JS, CSS3 (Glassmorphism UI), HTML5. 100% Client-side rendering for a sub-1MB footprint.
* **Backend:** Python FastAPI deployed on **Google Cloud Run** for zero-downtime auto-scaling.
* **Mapping:** Google Maps JavaScript API with dynamic HTTP referrer restrictions.
* **Generative AI:** **Google Gemini 2.5 Flash** integrated via the official GenAI SDK.

## 3. Generative AI Implementation & In-Context Tuning
To meet rigorous latency requirements for real-time pedestrian routing, we bypassed traditional high-latency fine-tuning in favor of **In-Context Prompt Tuning**. 
By injecting a rigid system prompt detailing spatial constraints and crowd psychology parameters directly into the context window, the Gemini 2.5 Flash model behaves as a specialized, zero-shot spatial reasoning engine. This ensures highly predictable, formatted outputs without the architectural overhead of hosting custom LoRA weights.

## 4. Security Protocols
* **API Gateway:** Cloud Run environment variables isolate all LLM access keys.
* **Payload Protection:** Strict Pydantic models validate all incoming spatial coordinates to prevent prompt injection.
* **Cross-Origin:** Explicit CORS policies restrict backend access to the production frontend.
