# Natural Identity – Anti‑Deep‑Fake Signature & Verification Suite

Deep‑fake technology has torn down the cost of impersonation. Policies and takedown requests arrive only after the damage is done. **Natural Identity flips the timeline**: it lets every content creator embed a cryptographically verifiable, perception‑invisible signature directly into their videos and later prove ownership—or detect fraudulent clones—with a single CLI command.

### Why It Matters
*   **Creators’ Peace of Mind** – First‑party proof that “this is really me” shields reputation and accelerates DMCA claims.  
*   **Platform Trust** – Streaming platforms can add a real‑time “authentic” badge, cutting moderation overhead.  
*   **Legal Evidence** – The 256‑bit signature survives YouTube’s transcode pipeline and can be cited in court filings as machine‑verifiable evidence of provenance.  
*   **End‑User Empowerment** – Viewers run the verifier locally; no central authority gatekeeps the authenticity stamp.

### System Components
1. **Multimodal Encoder** – A lightweight transformer ingests synchronized face, voice, and micro‑gesture features to derive a 512‑D identity embedding.  
2. **Invisible Watermark** – A spread‑spectrum LSB modulator writes a signed hash of the embedding into spatial‑temporal noise below human detection thresholds (Δ SSIM < 0.002).  
3. **Verifier** – Given unknown footage and a public key, outputs match probability, tamper score, and watermark extraction result.

### Folder Map
TERMS.md contractual details and penalties
models/
├── encoder/ identity embedding training code
├── watermark/ encoder/decoder kernels (CUDA & CPU)
└── verifier/ end‑to‑end verification pipeline
cli/ Rust‑based CLI front‑end
docs/ white‑paper, threat model, benchmark reports
submissions/ final artefacts + evaluation logs

objectivec
Copy

### Build & Test
```bash
# train identity weights
python -m models.encoder.train --video myfootage.mp4 --out weights.pt

# embed signature
python -m models.watermark.encode --in original.mp4 --weights weights.pt --out signed.mp4

# verify new footage
cargo run --bin nid-verify signed.mp4 weights.pt
All commands fall back to pure‑CPU if no GPU is present, though with reduced throughput.

Definition of Done
Identity training converges within 30 epochs (<3 hours on a single RTX 4070) and yields verification F1 ≥ 0.90 on the open‑source DFDC subset.

Watermark insertion increases bitrate ≤3 % and remains visually indistinguishable (PSNR > 45 dB).

Extraction accuracy ≥95 % after round‑trip through YouTube (ipfs.io/ipfs/... sample link) and a 1 Mbit/s H.264 transcode.

End‑to‑end CLI pipeline documented, reproducible via make demo on Ubuntu 22.04.

Security review in docs/threat_model.md, covering bit‑flip, cropping, and GAN removal attacks.

Continuous‑integration suite (GitHub Actions) runs lint, unit tests, and the short DFDC benchmark on every push; all green.

docs/whitepaper.pdf (≥10 pages) explains watermark math, legal framing, and comparison to prior art.

Artefact bundle (weights.pt, signed.mp4, logs, and SHA‑256 manifest) committed to submissions/ and hash pinned on‑chain.

Governance & Licensing
Core library under Apache 2.0; trained identity weights belong to their respective users and are never uploaded by default. Project direction steered by an open governance forum in the Trustless Business DAO.

