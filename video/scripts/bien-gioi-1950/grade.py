"""Chỉnh màu ảnh render cho khớp tông bản gốc: độ sáng p5/p50/p95 ≈ 57/113/159, tỉ lệ R:G:B ≈ 1.05:1:0.62."""
import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
def grade(a):
    a = a.astype(np.float32)
    lum = a.mean(-1); s = lum[::5, ::5]
    p = np.percentile(s, [1, 5, 50, 95, 99.5])
    tgt = np.interp(lum, p, [40, 66, 118, 160, 188])
    a *= (tgt / np.maximum(lum, 1))[..., None]
    m = a.reshape(-1, 3)[::97].mean(0); g = m[1]
    a *= np.array([1.05 * g / m[0], 1.0, 0.62 * g / m[2]])[None, None, :]
    gray = a.mean(-1, keepdims=True); a = gray + (a - gray) * 1.12
    return np.clip(a, 0, 255).astype(np.uint8)
if __name__ == "__main__":
    im = np.asarray(Image.open(sys.argv[1]).convert("RGB"))
    Image.fromarray(grade(im)).save(sys.argv[2])
