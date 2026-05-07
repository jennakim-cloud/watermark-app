import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
from pathlib import Path

st.set_page_config(page_title="(해상도 이슈로 점검 중)무신사 워터마크 삽입기", page_icon="🖼️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .stApp { background-color: #F5F5F3; }
    .card-title { font-size:0.7rem; font-weight:700; color:#888; letter-spacing:0.12em;
        text-transform:uppercase; margin-bottom:18px; padding-bottom:10px; border-bottom:1px solid #EEEEEE; }
    .upload-zone { border:2px dashed #CCCCCC; border-radius:4px; padding:40px 20px;
        text-align:center; background:#FAFAFA; color:#999; font-size:0.85rem; }
    .stDownloadButton > button { background:#111111 !important; color:#ffffff !important;
        border:none !important; border-radius:3px !important; font-weight:600 !important;
        letter-spacing:0.06em !important; padding:12px 28px !important;
        font-size:0.82rem !important; width:100% !important; }
    .stDownloadButton > button:hover { background:#333333 !important; }
    hr { border-color:#EEEEEE; }
    .file-info { font-size:0.78rem; color:#666; margin-top:6px; }
    .badge { display:inline-block; background:#111; color:#fff; font-size:0.65rem;
        letter-spacing:0.1em; padding:3px 10px; border-radius:2px; font-weight:700; }
    .badge-ok { background:#2D7A3A; }
    .badge-warn { background:#B45309; }
</style>
""", unsafe_allow_html=True)

LOGO_DIR    = Path(__file__).parent / "logos"
TARGET_SIZE = (1056, 720)
MARGIN      = 45

# 브랜드별 설정: 4배 PNG + 최종 합성 크기(px) 명시
BRANDS = {
    "무신사 스탠다드": {
    "black": "musinsa_standard_black.png",
    "white": "musinsa_standard_white.png",
    "final_w": 127,   # 126.52 반올림
    "final_h": 55,    # 450x194.5 비율 기준
},
    "무신사 기업":    {"black": "musinsa_corporate_black.png", "white": "musinsa_corporate_white.png", "final_w": 193, "final_h": 32},
    "무신사 스토어":  {"black": "musinsa_store_black.png",     "white": "musinsa_store_white.png",     "final_w": 182, "final_h": 34},
    "무신사 뷰티":   {"black": "musinsa_beauty_black.png",     "white": "musinsa_beauty_white.png",     "final_w": 167, "final_h": 46},
    "29CM":          {"black": "cm29_black.png",               "white": "cm29_white.png",               "final_w": 136, "final_h": 34},
}

def resize_and_crop(img, target=(1056, 720)):
    tw, th = target
    iw, ih = img.size
    scale  = max(tw / iw, th / ih)
    img    = img.resize((round(iw * scale), round(ih * scale)), Image.LANCZOS)
    iw, ih = img.size
    return img.crop(((iw-tw)//2, (ih-th)//2, (iw-tw)//2+tw, (ih-th)//2+th))

def load_logo(brand, color):
    info = BRANDS.get(brand)
    if not info:
        return None
    path = LOGO_DIR / info[color]
    if not path.exists():
        return None
    logo = Image.open(path).convert("RGBA")
    return logo.resize((info["final_w"], info["final_h"]), Image.LANCZOS)

def apply_watermark(base_img, position, color, brand):
    base = base_img.convert("RGBA")
    bw, bh = base.size
    logo = load_logo(brand, color)
    if logo is None:
        return base_img.convert("RGB")
    lw, lh = logo.size
    positions = {
        "우상단": (bw - lw - MARGIN, MARGIN),
        "우하단": (bw - lw - MARGIN, bh - lh - MARGIN),
        "좌상단": (MARGIN, MARGIN),
        "좌하단": (MARGIN, bh - lh - MARGIN),
    }
    x, y = positions.get(position, (MARGIN, MARGIN))
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    overlay.paste(logo, (x, y), logo)
    return Image.alpha_composite(base, overlay).convert("RGB")

def image_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="card-title">⚙ 워터마크 설정</div>', unsafe_allow_html=True)
    st.markdown("**브랜드**")
    brand = st.selectbox("브랜드", list(BRANDS.keys()), label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**로고 삽입 위치**")
    position = st.radio("위치", ["좌상단", "우상단", "좌하단", "우하단"],
        horizontal=False, label_visibility="collapsed",
        captions=["↖ 좌상단", "↗ 우상단", "↙ 좌하단", "↘ 우하단"])
    st.markdown("---")
    st.markdown("**로고 색상**")
    color = st.radio("색상", ["black", "white"], horizontal=True,
        label_visibility="collapsed",
        format_func=lambda x: "⬛ 블랙" if x == "black" else "⬜ 화이트")
    st.markdown("---")
    st.markdown('<div style="font-size:0.72rem;color:#999;line-height:1.7;">• 출력 규격: <b>1056 × 720 px</b><br>• 출력 포맷: <b>JPG (품질 95)</b><br>• 비율이 다른 이미지는 중앙 기준 크롭</div>', unsafe_allow_html=True)

# ── 메인 ─────────────────────────────────────────────────────────────────────
col_upload, col_preview = st.columns([1, 1.2], gap="large")

with col_upload:
    st.markdown('<div class="card-title">① 이미지 업로드</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("이미지 업로드",
        type=["jpg","jpeg","png","webp","bmp","tiff"],
        accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        st.markdown(f'<span class="badge badge-ok">✓ {len(uploaded_files)}개 업로드됨</span>', unsafe_allow_html=True)
        for f in uploaded_files:
            ow, oh = Image.open(f).size
            ok = (ow, oh) == TARGET_SIZE
            st.markdown(f'<div class="file-info">📄 {f.name} &nbsp;<span class="badge {"badge-ok" if ok else "badge-warn"}">{"규격 일치" if ok else f"리사이즈 필요 ({ow}×{oh})"}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="upload-zone">🖼️ JPG, PNG, WEBP 등 지원<br><small>복수 파일 동시 업로드 가능</small></div>', unsafe_allow_html=True)

with col_preview:
    st.markdown('<div class="card-title">② 미리보기 & 다운로드</div>', unsafe_allow_html=True)
    if not uploaded_files:
        st.markdown('<div class="upload-zone" style="height:300px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:8px;"><span style="font-size:2rem;">🖼️</span><span>업로드한 이미지가 여기에 표시됩니다</span></div>', unsafe_allow_html=True)
    else:
        tabs = st.tabs([f.name[:20] for f in uploaded_files]) if len(uploaded_files) > 1 else None

        def render_file(ufile, i, container):
            ufile.seek(0)
            result_img = apply_watermark(resize_and_crop(Image.open(ufile), TARGET_SIZE), position, color, brand)
            container.image(result_img, use_container_width=True)
            container.markdown(f'<div class="file-info" style="margin-top:4px;">📐 {result_img.size[0]}×{result_img.size[1]}px &nbsp;·&nbsp; 🏷️ {position} &nbsp;·&nbsp; 🎨 {"블랙" if color=="black" else "화이트"}</div>', unsafe_allow_html=True)
            out_name = f"{Path(ufile.name).stem}_watermark_{position}.jpg"
            container.download_button(label=f"⬇  다운로드  {out_name}", data=image_to_bytes(result_img), file_name=out_name, mime="image/jpeg", key=f"dl_{i}")

        if tabs:
            for i, ufile in enumerate(uploaded_files):
                with tabs[i]:
                    render_file(ufile, i, st)
        else:
            render_file(uploaded_files[0], 0, st)

if uploaded_files and len(uploaded_files) > 1:
    st.markdown("---")
    st.markdown('<div class="card-title">③ 전체 일괄 다운로드</div>', unsafe_allow_html=True)
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for ufile in uploaded_files:
            ufile.seek(0)
            result_img = apply_watermark(resize_and_crop(Image.open(ufile), TARGET_SIZE), position, color, brand)
            zf.writestr(f"{Path(ufile.name).stem}_watermark_{position}.jpg", image_to_bytes(result_img))
    zip_buf.seek(0)
    st.download_button(label=f"⬇  전체 {len(uploaded_files)}개 ZIP으로 다운로드", data=zip_buf.read(), file_name=f"musinsa_watermark_{position}.zip", mime="application/zip")

st.markdown("---")
st.markdown('<p style="text-align:center;font-size:0.72rem;color:#BBBBBB;letter-spacing:0.08em;">MUSINSA · PRESS IMAGE WATERMARK SYSTEM</p>', unsafe_allow_html=True)
