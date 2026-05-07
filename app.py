import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import base64
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="무신사 스탠다드 워터마크 삽입기",
    page_icon="🖼️",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* 전체 배경 */
    .stApp {
        background-color: #F5F5F3;
    }

    /* 헤더 */
    .main-header {
        background: #111111;
        color: #ffffff;
        padding: 32px 40px;
        margin: -1rem -1rem 2rem -1rem;
        letter-spacing: 0.08em;
    }
    .main-header h1 {
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.1em;
    }
    .main-header p {
        font-size: 0.78rem;
        color: #aaaaaa;
        margin: 6px 0 0 0;
        letter-spacing: 0.05em;
    }

    /* 카드 */
    .card {
        background: #ffffff;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 28px;
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 0.7rem;
        font-weight: 700;
        color: #888;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 18px;
        padding-bottom: 10px;
        border-bottom: 1px solid #EEEEEE;
    }

    /* 위치 선택 버튼 */
    .position-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 8px;
    }
    .pos-btn {
        border: 1.5px solid #DDDDDD;
        background: #FAFAFA;
        border-radius: 3px;
        padding: 12px 8px;
        cursor: pointer;
        text-align: center;
        font-size: 0.82rem;
        font-weight: 500;
        color: #444;
        transition: all 0.15s ease;
    }
    .pos-btn.active {
        border-color: #111111;
        background: #111111;
        color: #ffffff;
    }

    /* 색상 선택 */
    .color-row {
        display: flex;
        gap: 10px;
        margin-top: 8px;
    }
    .color-chip {
        display: flex;
        align-items: center;
        gap: 8px;
        border: 1.5px solid #DDDDDD;
        border-radius: 3px;
        padding: 10px 16px;
        cursor: pointer;
        font-size: 0.82rem;
        font-weight: 500;
        transition: all 0.15s ease;
        flex: 1;
        justify-content: center;
    }
    .color-chip.active { border-color: #111; background: #F0F0F0; }

    /* 업로드 영역 */
    .upload-zone {
        border: 2px dashed #CCCCCC;
        border-radius: 4px;
        padding: 40px 20px;
        text-align: center;
        background: #FAFAFA;
        color: #999;
        font-size: 0.85rem;
    }

    /* 프리뷰 */
    .preview-container img {
        border: 1px solid #E0E0E0;
        border-radius: 2px;
        width: 100%;
    }

    /* 다운로드 버튼 */
    .stDownloadButton > button {
        background: #111111 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 3px !important;
        font-weight: 600 !important;
        letter-spacing: 0.06em !important;
        padding: 12px 28px !important;
        font-size: 0.82rem !important;
        width: 100% !important;
        transition: background 0.15s ease !important;
    }
    .stDownloadButton > button:hover {
        background: #333333 !important;
    }

    /* 구분선 스타일 hr */
    hr { border-color: #EEEEEE; }

    /* Streamlit 기본 요소 튜닝 */
    .stRadio > div { gap: 8px; }
    .stRadio label { font-size: 0.85rem !important; }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #CCCCCC;
        border-radius: 4px;
        padding: 10px;
    }
    .stSelectbox select { font-size: 0.85rem; }

    /* 상태 배지 */
    .badge {
        display: inline-block;
        background: #111;
        color: #fff;
        font-size: 0.65rem;
        letter-spacing: 0.1em;
        padding: 3px 10px;
        border-radius: 2px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-ok { background: #2D7A3A; }
    .badge-warn { background: #B45309; }

    /* 파일명 표시 */
    .file-info {
        font-size: 0.78rem;
        color: #666;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ── 로고 파일 경로 ─────────────────────────────────────────────────────────────
LOGO_DIR = Path(__file__).parent / "logos"

# 브랜드별 로고 파일 (black/white 각각 지정 크기로 저장됨)
LOGO_FILES = {
    "무신사 스탠다드": {
        "black": LOGO_DIR / "musinsa_standard_black.png",
        "white": LOGO_DIR / "musinsa_standard_white.png",
    },
    "무신사 기업": {
        "black": LOGO_DIR / "musinsa_corporate_black.png",
        "white": LOGO_DIR / "musinsa_corporate_white.png",
    },
    "무신사 스토어": {
        "black": LOGO_DIR / "musinsa_store_black.png",
        "white": LOGO_DIR / "musinsa_store_white.png",
    },
    "무신사 뷰티": {
        "black": LOGO_DIR / "musinsa_beauty_black.png",
        "white": LOGO_DIR / "musinsa_beauty_white.png",
    },
    "무신사 스포츠": {
        "black": LOGO_DIR / "musinsa_sports_black.png",
        "white": LOGO_DIR / "musinsa_sports_white.png",
    },
}

TARGET_SIZE = (1056, 720)
MARGIN      = 45    # 고정 여백 (px)

# ── 핵심 함수 ─────────────────────────────────────────────────────────────────

def resize_and_crop(img: Image.Image, target=(1056, 720)) -> Image.Image:
    """중앙 기준으로 크롭하여 정확한 규격으로 맞춤"""
    tw, th = target
    iw, ih = img.size

    scale = max(tw / iw, th / ih)
    new_w = round(iw * scale)
    new_h = round(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - tw) // 2
    top = (new_h - th) // 2
    img = img.crop((left, top, left + tw, top + th))
    return img


def load_logo(brand: str, color: str):
    """로고 이미지 로드."""
    path = LOGO_FILES.get(brand, {}).get(color)
    if path and path.exists():
        return Image.open(path).convert("RGBA")
    return make_text_logo(color)


def make_text_logo(color: str) -> Image.Image:
    """실제 로고 파일이 없을 때 텍스트 기반 임시 로고 반환"""
    fg = (255, 255, 255, 220) if color == "white" else (0, 0, 0, 200)
    img = Image.new("RGBA", (320, 60), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    except:
        font = ImageFont.load_default()
    draw.text((10, 15), "MUSINSA STANDARD", fill=fg, font=font)
    return img


def apply_watermark(
    base_img: Image.Image,
    position: str,
    color: str,
    brand: str,
) -> Image.Image:
    """베이스 이미지에 로고 워터마크를 합성"""
    base = base_img.convert("RGBA")
    bw, bh = base.size

    logo = load_logo(brand, color)
    if logo is None:
        return base_img.convert("RGB")

    # 로고는 이미 지정 크기로 저장되어 있음 — 그대로 사용
    lw, lh = logo.size

    # 위치 계산 (마진 45px 고정)
    if position == "우상단":
        x, y = bw - lw - MARGIN, MARGIN
    elif position == "우하단":
        x, y = bw - lw - MARGIN, bh - lh - MARGIN
    elif position == "좌상단":
        x, y = MARGIN, MARGIN
    elif position == "좌하단":
        x, y = MARGIN, bh - lh - MARGIN
    else:
        x, y = MARGIN, MARGIN

    # 합성
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    overlay.paste(logo, (x, y), logo)
    result = Image.alpha_composite(base, overlay)
    return result.convert("RGB")


def image_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


# ── UI 시작 ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>MUSINSA STANDARD — WATERMARK</h1>
    <p>보도자료 이미지 워터마크 자동 삽입 시스템 · 1056×720px · JPG</p>
</div>
""", unsafe_allow_html=True)

# ── 사이드바: 설정 패널 ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="card-title">⚙ 워터마크 설정</div>', unsafe_allow_html=True)

    # 브랜드 선택
    st.markdown("**브랜드**")
    brand = st.selectbox(
        "브랜드",
        list(LOGO_FILES.keys()),
        label_visibility="collapsed",
    )

    st.markdown("---")

    # 로고 위치
    st.markdown("**로고 삽입 위치**")
    position = st.radio(
        "위치",
        ["좌상단", "우상단", "좌하단", "우하단"],
        horizontal=False,
        label_visibility="collapsed",
        captions=["↖ 좌상단", "↗ 우상단", "↙ 좌하단", "↘ 우하단"],
    )

    st.markdown("---")

    # 로고 색상
    st.markdown("**로고 색상**")
    color = st.radio(
        "색상",
        ["black", "white"],
        horizontal=True,
        label_visibility="collapsed",
        format_func=lambda x: "⬛ 블랙" if x == "black" else "⬜ 화이트",
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem; color:#999; line-height:1.7;">
    • 출력 규격: <b>1056 × 720 px</b><br>
    • 출력 포맷: <b>JPG (품질 95)</b><br>
    • 비율이 다른 이미지는 중앙 기준 크롭
    </div>
    """, unsafe_allow_html=True)

# ── 메인: 업로드 + 프리뷰 ─────────────────────────────────────────────────────
col_upload, col_preview = st.columns([1, 1.2], gap="large")

with col_upload:
    st.markdown('<div class="card-title">① 이미지 업로드</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "이미지를 드래그하거나 클릭하여 업로드",
        type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        st.markdown(f'<span class="badge badge-ok">✓ {len(uploaded_files)}개 업로드됨</span>', unsafe_allow_html=True)
        for f in uploaded_files:
            img_tmp = Image.open(f)
            orig_w, orig_h = img_tmp.size
            needs_resize = (orig_w, orig_h) != TARGET_SIZE
            badge_cls = "badge-warn" if needs_resize else "badge-ok"
            badge_txt = f"리사이즈 필요 ({orig_w}×{orig_h})" if needs_resize else f"규격 일치 ({orig_w}×{orig_h})"
            st.markdown(
                f'<div class="file-info">📄 {f.name} &nbsp; <span class="badge {badge_cls}">{badge_txt}</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown("""
        <div class="upload-zone">
            🖼️ JPG, PNG, WEBP 등 지원<br>
            <small>복수 파일 동시 업로드 가능</small>
        </div>
        """, unsafe_allow_html=True)

with col_preview:
    st.markdown('<div class="card-title">② 미리보기 & 다운로드</div>', unsafe_allow_html=True)

    if not uploaded_files:
        st.markdown("""
        <div class="upload-zone" style="height:300px; display:flex; align-items:center; justify-content:center; flex-direction:column; gap:8px;">
            <span style="font-size:2rem;">🖼️</span>
            <span>업로드한 이미지가 여기에 표시됩니다</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 복수 파일이면 탭으로 구분, 1개면 그냥 표시
        if len(uploaded_files) > 1:
            tab_names = [f.name[:20] for f in uploaded_files]
            tabs = st.tabs(tab_names)
        else:
            tabs = None

        def render_file(ufile, i, container):
            ufile.seek(0)
            base_img = Image.open(ufile)
            resized = resize_and_crop(base_img, TARGET_SIZE)
            result_img = apply_watermark(resized, position, color, brand)

            container.image(result_img, use_container_width=True)
            container.markdown(
                f'<div class="file-info" style="margin-top:4px;">'
                f'📐 {result_img.size[0]}×{result_img.size[1]}px &nbsp;·&nbsp; '
                f'🏷️ {position} &nbsp;·&nbsp; '
                f'🎨 {"블랙" if color=="black" else "화이트"}'
                f'</div>',
                unsafe_allow_html=True,
            )
            img_bytes = image_to_bytes(result_img)
            stem = Path(ufile.name).stem
            out_name = f"{stem}_watermark_{position}.jpg"
            container.download_button(
                label=f"⬇  다운로드  {out_name}",
                data=img_bytes,
                file_name=out_name,
                mime="image/jpeg",
                key=f"dl_{i}",
            )

        if tabs is not None:
            for i, ufile in enumerate(uploaded_files):
                with tabs[i]:
                    render_file(ufile, i, st)
        else:
            render_file(uploaded_files[0], 0, st)

# ── 일괄 다운로드 (ZIP) ────────────────────────────────────────────────────────
if uploaded_files and len(uploaded_files) > 1:
    st.markdown("---")
    st.markdown('<div class="card-title">③ 전체 일괄 다운로드</div>', unsafe_allow_html=True)

    import zipfile

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for ufile in uploaded_files:
            ufile.seek(0)
            base_img = Image.open(ufile)
            resized = resize_and_crop(base_img, TARGET_SIZE)
            result_img = apply_watermark(resized, position, color, brand)
            img_bytes = image_to_bytes(result_img)
            stem = Path(ufile.name).stem
            zf.writestr(f"{stem}_watermark_{position}.jpg", img_bytes)

    zip_buf.seek(0)
    st.download_button(
        label=f"⬇  전체 {len(uploaded_files)}개 ZIP으로 다운로드",
        data=zip_buf.read(),
        file_name=f"musinsa_watermark_{position}.zip",
        mime="application/zip",
    )

# ── 푸터 ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; font-size:0.72rem; color:#BBBBBB; letter-spacing:0.08em;">'
    'MUSINSA STANDARD · PRESS IMAGE WATERMARK SYSTEM'
    '</p>',
    unsafe_allow_html=True,
)
