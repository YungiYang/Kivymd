"""Emoji font helper — патч для коректного відображення emoji в Kivy SDL2.

Kivy SDL2 не підтримує кольорові emoji-шрифти (COLR/CBDT/SVG).
Але підтримує monochrome гліфи через [font=...] markup.
Цей модуль:
  1. Реєструє Segoe UI Emoji як «EmojiFont»
  2. Надає функцію emoji_markup() для обгортання emoji символів
  3. Патчить MDLabel і MDButtonText так, щоб emoji автоматично рендерились
"""

import os
import re

# ── Emoji Unicode ranges ──────────────────────────────────────────────────────
# Broad set of emoji/symbol codepoint ranges that need the emoji font
_EMOJI_RANGES = [
    (0x0023, 0x0023),   # #
    (0x002A, 0x002A),   # *
    (0x0030, 0x0039),   # 0-9 (as emoji)
    (0x00A9, 0x00A9),   # ©
    (0x00AE, 0x00AE),   # ®
    (0x203C, 0x2BFF),   # Misc symbols & arrows block
    (0x1F000, 0x1FFFF), # All emoji block (faces, objects, etc.)
    (0x2600, 0x27FF),   # Misc symbols
    (0xFE00, 0xFE0F),   # Variation selectors
    (0x1F300, 0x1FAFF), # Extended emoji
]

_EMOJI_FONT_PATH: str = ""

# Supported emoji font candidates (Windows)
_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\seguiemj.ttf",   # Segoe UI Emoji — best
    r"C:\Windows\Fonts\seguisym.ttf",   # Segoe UI Symbol — fallback
]


def _find_emoji_font() -> str:
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return ""


def setup_emoji_font() -> bool:
    """Registers the emoji font with Kivy's LabelBase. Returns True on success."""
    global _EMOJI_FONT_PATH
    _EMOJI_FONT_PATH = _find_emoji_font()
    if not _EMOJI_FONT_PATH:
        return False
    try:
        from kivy.core.text import LabelBase
        LabelBase.register(name="SegoeEmoji", fn_regular=_EMOJI_FONT_PATH)
        return True
    except Exception:
        return False


def _is_emoji_char(cp: int) -> bool:
    """Returns True if the codepoint is likely an emoji/symbol."""
    for lo, hi in _EMOJI_RANGES:
        if lo <= cp <= hi:
            return True
    return False


def emoji_markup(text: str) -> str:
    """Wraps emoji characters in [font=EmojiFont]...[/font] markup tags.
    
    Call this on any string before setting it as a label text when
    markup=True is enabled on that label.
    """
    if not _EMOJI_FONT_PATH or not text:
        return text

    font_path = _EMOJI_FONT_PATH.replace("\\", "/")
    result = []
    in_emoji = False

    for ch in text:
        cp = ord(ch)
        is_em = _is_emoji_char(cp)
        if is_em and not in_emoji:
            result.append(f"[font={font_path}]")
            in_emoji = True
        elif not is_em and in_emoji:
            result.append("[/font]")
            in_emoji = False
        result.append(ch)

    if in_emoji:
        result.append("[/font]")

    return "".join(result)


# ── Auto-patch MDLabel and MDButtonText ───────────────────────────────────────

def patch_kivymd_emoji():
    """Monkey-patches KivyMD widgets to auto-apply emoji_markup on text set.
    
    Must be called AFTER Kivy/KivyMD is imported but BEFORE widgets are created.
    """
    if not _EMOJI_FONT_PATH:
        return  # No emoji font available, skip

    try:
        from kivymd.uix.label.label import MDLabel
        from kivymd.uix.button.button import MDButtonText

        _orig_mdlabel_init = MDLabel.__init__
        _orig_mdbtntext_init = MDButtonText.__init__

        def _patched_mdlabel_init(self, **kwargs):
            # Enable markup so [font=...] tags work
            kwargs.setdefault("markup", True)
            if "text" in kwargs and kwargs["text"]:
                kwargs["text"] = emoji_markup(kwargs["text"])
            _orig_mdlabel_init(self, **kwargs)
            # Also patch the text property setter
            _install_text_observer(self)

        def _patched_mdbtntext_init(self, **kwargs):
            kwargs.setdefault("markup", True)
            if "text" in kwargs and kwargs["text"]:
                kwargs["text"] = emoji_markup(kwargs["text"])
            _orig_mdbtntext_init(self, **kwargs)
            _install_text_observer(self)

        MDLabel.__init__ = _patched_mdlabel_init
        MDButtonText.__init__ = _patched_mdbtntext_init

    except Exception as e:
        pass  # Silently skip if KivyMD structure changed


def _install_text_observer(widget):
    """Installs an observer so that whenever .text is set, emoji_markup is applied."""
    try:
        orig_setter = widget.__class__.text.fset if hasattr(widget.__class__.text, 'fset') else None

        def on_text(instance, value):
            # Prevent recursion: only process if value doesn't already have our markup
            if value and "[font=" not in value:
                marked = emoji_markup(value)
                if marked != value:
                    # Temporarily disconnect to avoid infinite loop
                    instance.unbind(text=on_text)
                    instance.text = marked
                    instance.bind(text=on_text)

        widget.bind(text=on_text)
    except Exception:
        pass
