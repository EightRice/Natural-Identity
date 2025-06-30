# coding: utf-8
"""Natural Identity toolkit.

This module implements a toy example of generating identity weights from video
frames, deriving a deterministic ed25519 key pair, signing videos by embedding
an invisible watermark, and verifying the signature.

It is **not** production ready. The features are extremely simple and the
watermarking scheme is naive, but it demonstrates the requested API and flow.
"""

import hashlib
import struct
from dataclasses import dataclass
from typing import List, Optional

import cv2
import numpy as np
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


@dataclass
class Identity:
    weights: np.ndarray  # 512-dim vector
    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey


# ------------------ Helper functions ------------------

def _extract_face_patch(gray: np.ndarray, face_cascade) -> Optional[np.ndarray]:
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    face = gray[y : y + h, x : x + w]
    face = cv2.resize(face, (64, 64))
    return face


def _video_histogram(path: str) -> np.ndarray:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open {path}")

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    hist_face = np.zeros(256, dtype=np.float64)
    hist_motion = np.zeros(256, dtype=np.float64)
    prev_patch = None
    frames_used = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        patch = _extract_face_patch(gray, face_cascade)
        if patch is None:
            continue
        frames_used += 1
        clean_patch = cv2.bitwise_and(patch, 0xFE)
        hist_face += cv2.calcHist([clean_patch], [0], None, [256], [0, 256]).flatten()
        if prev_patch is not None:
            diff = cv2.absdiff(clean_patch, cv2.bitwise_and(prev_patch, 0xFE))
            hist_motion += cv2.calcHist([diff], [0], None, [256], [0, 256]).flatten()
        prev_patch = patch
    cap.release()
    if frames_used == 0:
        raise ValueError("No faces detected in video")
    hist_face /= frames_used
    hist_motion /= max(1, frames_used - 1)
    embedding = np.concatenate([hist_face, hist_motion])
    # Normalize
    embedding = embedding / np.linalg.norm(embedding)
    return embedding.astype(np.float32)


# ------------------ Public API ------------------

def generate_identity(video_path: str) -> Identity:
    """Generate identity weights and deterministic key pair from a video."""
    weights = _video_histogram(video_path)
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"natural_identity",
    )
    seed = hkdf.derive(weights.tobytes())
    private_key = Ed25519PrivateKey.from_private_bytes(seed)
    public_key = private_key.public_key()
    return Identity(weights=weights, private_key=private_key, public_key=public_key)


def save_public_key(pub: Ed25519PublicKey, path: str) -> None:
    with open(path, "wb") as f:
        f.write(pub.public_bytes())


def load_public_key(path: str) -> Ed25519PublicKey:
    data = open(path, "rb").read()
    return Ed25519PublicKey.from_public_bytes(data)


def sign_video(video_path: str, identity: Identity, out_path: str) -> None:
    """Embed a signature watermark into the first frame of the video."""
    # Compute signature from identity weights so verification does not depend on
    # byte-exact video content.
    signature = identity.private_key.sign(
        hashlib.sha256(identity.weights.tobytes()).digest()
    )

    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    # Use an explicit codec so the output can be read on most systems
    # MJPG in an AVI container keeps artifacts low and is widely supported
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    bit_iter = iter(np.unpackbits(np.frombuffer(signature, dtype=np.uint8)))
    written = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if not written:
            # Embed bits in LSB of upper-left pixels
            h, w, _ = frame.shape
            for y in range(min(32, h)):
                for x in range(min(32, w)):
                    try:
                        b = next(bit_iter)
                    except StopIteration:
                        written = True
                        break
                    for c in range(3):
                        frame[y, x, c] = (frame[y, x, c] & 0xFE) | int(b)
                if written:
                    break
        out.write(frame)
    cap.release()
    out.release()


def verify_video(video_path: str, public_key: Ed25519PublicKey) -> bool:
    """Check watermark signature matches video content."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open {video_path}")
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return False

    bits = []
    h, w, _ = frame.shape
    for y in range(min(32, h)):
        for x in range(min(32, w)):
            bits.append(frame[y, x, 0] & 1)
            if len(bits) == 512 * 8:
                break
        if len(bits) == 512 * 8:
            break
    sig_bytes = np.packbits(np.array(bits, dtype=np.uint8)).tobytes()

    weights = _video_histogram(video_path)
    try:
        public_key.verify(sig_bytes, hashlib.sha256(weights.tobytes()).digest())
        return True
    except Exception:
        return False


__all__ = [
    "Identity",
    "generate_identity",
    "save_public_key",
    "load_public_key",
    "sign_video",
    "verify_video",
]
