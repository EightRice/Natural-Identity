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

pgsql
Copy

---

### **dIRC / README.md**

```markdown
# dIRC – A Self‑Hosted, Consensus‑Backed Successor to IRC & Discord

IRC gave us openness; modern chat gave us rich UX. dIRC keeps both by letting every participant own their data while a lightweight BFT layer guarantees that everyone in a channel sees the same message order—even offline nodes can sync months later without trusting a corporation.

### Problem → Solution
* **Lock‑in & Censorship** – Central servers can silence communities; dIRC replaces them with a rotating leader‑election among peers.  
* **History Loss** – Traditional P2P chats lose messages when devices are offline; dIRC uses CRDTs plus stake‑weighted BFT consensus so gaps merge deterministically.  
* **Privacy vs. Searchability** – Messages are E2E‑encrypted but merklized indexes enable opt‑in full‑text search without revealing plaintext to peers.

### Technical Outline
1. **Node Core (Go)** – Handles p2p handshake (Noise‑XK), local RocksDB store, and CRDT operations.  
2. **Consensus** – HotStuff‑style BFT with ⅔ + δ stake threshold; selection rotates hourly, preventing long‑range forks.  
3. **Timeline Compression** – Vector‑clock pruner reduces history size to O(n log n) while preserving causality proofs.  
4. **Client UI (Electron + Svelte)** – Feels like Discord: servers, channels, emojis, voice (WebRTC mesh), and theme packs.

### Directory Tree
TERMS.md
protocol/
└── go-dirc/ reference daemon
ui/ Electron client
docs/ spec, UML diagrams, API docs
scripts/ test‑net spin‑up & benchmarks
submissions/

markdown
Copy

### Getting Started
* Build daemon: `go install ./protocol/go-dirc/cmd/dircd`  
* Start a local genesis cluster of three nodes: `./scripts/run_localnet.sh`  
* Launch client: `npm i && npm run dev` inside `ui/`

### Definition of Done
* Spec draft ratified in repo (`docs/spec_v1.md`) and signed in commit `spec-final`.  
* `dircd` reaches ≥1 000 msgs/s aggregate throughput on a 50‑node DigitalOcean test‑net (8 vCPU each), with consensus finality ≤3 seconds 95ᵗʰ percentile.  
* Two‑hour network partition test results in perfect automatic merge (no data loss, order preserved).  
* Electron client implements: login (ED25519 keys), DM, channel chat, emoji reactions, file upload ≤25 MB, theme switcher, and voice rooms (Opus 48 kHz).  
* CI pipeline spins up a five‑node docker‑compose network and runs 400 DMs + 2 k channel messages; all integration tests pass.  
* Full install docs and an operator guide live in `docs/`.  
* Artefacts (Docker images, test‑net logs, checksums) deposited in `submissions/` and hash matched on‑chain.

### Future Threads
Bridges for Matrix and Discord, mobile clients in Flutter, and group‑chat NFTs for channel governance are planned but out of scope for v1.

### License
Daemon under GPL‑3; UI under MPL‑2 to encourage embed reuse; message spec in public domain.