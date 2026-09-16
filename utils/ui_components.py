import os
import tkinter as tk
import customtkinter as ctk
from utils.colors import COLORS
from utils.scale import sv
from utils.constants import FONT_FAMILY
from utils.theme_manager import theme_manager

# Set EGHTESADINO_REDUCE_MOTION=1 to disable smooth transitions
_REDUCE_MOTION = os.environ.get("EGHTESADINO_REDUCE_MOTION", "0") == "1"


def _motion_ok():
    return not _REDUCE_MOTION


def font(size_token=14, weight="normal"):
    return (FONT_FAMILY, sv(size_token), weight)


class BaseScreen:
    """Shared screen lifecycle. Subclasses build ``self.root`` in ``_build_ui``."""

    def _mark_built(self):
        """Record the theme mode this screen was built under so show_screen
        can detect a stale build (theme toggled while screen was hidden)."""
        self._built_mode = theme_manager.mode

    def is_stale(self):
        return getattr(self, "_built_mode", None) != theme_manager.mode

    def pack(self, *args, **kwargs):
        return self.root.pack(*args, **kwargs)

    def pack_forget(self, *args, **kwargs):
        return self.root.pack_forget(*args, **kwargs)

    def rebuild(self):
        self.root.destroy()
        self._build_ui()
        if getattr(self, "user_id", None) is not None:
            try:
                self.refresh_ui()
            except Exception:
                pass
        self.root.pack(fill="both", expand=True)

    def _nav(self, target):
        if callable(self.on_navigate):
            self.on_navigate(target)


class Card(ctk.CTkFrame):
    """Clean elevated surface for a professional financial dashboard.

    A solid card with a subtle hairline border. Pass ``hover=True`` to opt
    interactive cards into a primary-border highlight on mouse enter.
    """

    def __init__(self, radius=14, bg_color="card_bg", hover=False, **kwargs):
        self._rest_border = COLORS.get("divider")
        self._hover_border = COLORS.get("primary")
        self._hover_enabled = hover
        color = COLORS.get(bg_color, "#ffffff")
        super().__init__(**kwargs)
        try:
            self.configure(
                fg_color=color,
                corner_radius=sv(radius),
                border_width=1,
                border_color=self._rest_border,
            )
        except Exception:
            self.configure(fg_color=color)

        if hover:
            self.bind("<Enter>", self._on_enter, add="+")
            self.bind("<Leave>", self._on_leave, add="+")

    def _on_enter(self, _event=None):
        if not self._hover_enabled:
            return
        try:
            self.configure(border_color=self._hover_border)
        except Exception:
            pass

    def _on_leave(self, _event=None):
        if not self._hover_enabled:
            return
        try:
            self.configure(border_color=self._rest_border)
        except Exception:
            pass


class TitleLabel(ctk.CTkLabel):
    def __init__(self, master=None, text="", size=20, **kwargs):
        super().__init__(master=master, text=text, font=font(size, "bold"), **kwargs)


class BodyLabel(ctk.CTkLabel):
    def __init__(self, master=None, text="", size=13, **kwargs):
        super().__init__(master=master, text=text, font=font(size), **kwargs)


class MutedLabel(ctk.CTkLabel):
    def __init__(self, master=None, text="", size=11, **kwargs):
        kwargs.setdefault("text_color", COLORS.get("muted_text"))
        super().__init__(master=master, text=text, font=font(size), **kwargs)


class SectionTitle(ctk.CTkFrame):
    """Consistent section heading across screens: icon + bold title on one row."""

    def __init__(self, master, icon, text, icon_color=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        ctk.CTkLabel(
            self,
            text=icon,
            font=font(16),
            text_color=icon_color or COLORS.get("primary"),
        ).pack(side="left", padx=(0, sv(8)))
        ctk.CTkLabel(
            self,
            text=text,
            font=font(16, "bold"),
            text_color=COLORS.get("text"),
        ).pack(side="left")


class ProgressBar(ctk.CTkFrame):
    """Rounded progress bar. Animated to target unless motion is disabled"""

    def __init__(
        self,
        master,
        height=8,
        fg_color="divider",
        progress_color="accent",
        duration_ms=260,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._height = height
        self._fg_color = COLORS.get(fg_color, "#334155")
        self._progress_color = COLORS.get(progress_color, "#34D399")
        self._progress = 0.0
        self._duration = duration_ms
        self._after_id = None

        radius = sv(max(height // 2, 4))
        self._bg = ctk.CTkFrame(self, fg_color=self._fg_color, corner_radius=radius)
        self._bg.pack(fill="both", expand=True)

        self._fill = ctk.CTkFrame(
            self._bg, fg_color=self._progress_color, corner_radius=radius, width=0
        )
        self._fill.place(relx=0, rely=0, relheight=1.0)

    def _cleanup(self):
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def set(self, value):
        target = max(0.0, min(1.0, value))
        if not _motion_ok() or self._duration <= 0:
            self._progress = target
            self._fill.place_configure(relwidth=target)
            return
        if target == self._progress:
            return
        self._cleanup()
        start = self._progress
        steps = max(6, int(self._duration / 16))
        self._animate_to(start, target, steps, 0)

    def _animate_to(self, start, target, steps, step):
        if not self.winfo_exists():
            return
        t = (step + 1) / steps
        eased = 1 - (1 - t) ** 3  # ease-out cubic
        current = start + (target - start) * eased
        self._progress = current
        try:
            self._fill.place_configure(relwidth=current)
        except Exception:
            return
        if step < steps - 1:
            try:
                self._after_id = self.after(
                    16, lambda: self._animate_to(start, target, steps, step + 1)
                )
            except Exception:
                self._progress = target
                self._fill.place_configure(relwidth=target)

    def configure_progress_color(self, color):
        self._fill.configure(fg_color=color)


class Donut(ctk.CTkFrame):
    def __init__(
        self,
        master,
        size=72,
        progress_color="accent",
        track_color="divider",
        thickness=7,
        **kwargs
    ):
        # Do not pass size/color kwargs up to CTkFrame; they're donut-specific.
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        self._size = sv(size)
        self._thickness = sv(thickness)
        self._frac = 0.0
        self._last_mode = None
        # Keep the original tokens so colors can be re-resolved on theme change
        self._progress_token = progress_color
        self._track_token = track_color

        self._canvas = tk.Canvas(
            self,
            width=self._size,
            height=self._size,
            bg=COLORS.get("card_bg"),
            highlightthickness=0,
            bd=0,
        )
        self._canvas.pack()

        self._redraw()

    def _ensure_theme(self):
        """Re-resolve theme-dependent colors + canvas bg if the mode changed."""
        mode = getattr(theme_manager, "mode", "dark")
        if mode == self._last_mode and hasattr(self, "_color"):
            return
        self._last_mode = mode
        self._color = COLORS.get(self._progress_token, "#34D399")
        self._track = COLORS.get(self._track_token, "#334155")
        try:
            self._canvas.configure(bg=COLORS.get("card_bg"))
        except Exception:
            pass

    def _redraw(self):
        if not self._canvas.winfo_exists():
            return
        self._ensure_theme()
        pad = self._thickness // 2 + 1
        bbox = (pad, pad, self._size - pad, self._size - pad)
        self._canvas.delete("all")
        self._canvas.create_arc(
            *bbox,
            start=90,
            extent=359.999,
            style="arc",
            outline=self._track,
            width=self._thickness
        )
        extent = -360.0 * self._frac
        if extent <= -0.01:
            self._canvas.create_arc(
                *bbox,
                start=90,
                extent=extent,
                style="arc",
                outline=self._color,
                width=self._thickness
            )

    def set_color(self, color_token):
        """Switch the ring accent to a theme token (e.g. 'warning' for deficit)."""
        self._progress_token = color_token
        self._color = COLORS.get(color_token, "#34D399")
        self._redraw()

    def set(self, value, animate=True):
        """Animate the ring fraction to ``value`` (0.0 to 1.0)."""
        target = max(0.0, min(1.0, float(value)))
        if not animate or not _motion_ok():
            self._frac = target
            self._redraw()
            return
        start = self._frac
        steps = max(6, int(240 / 16))
        self._animate_to(start, target, steps, 0)

    def _animate_to(self, start, target, steps, step):
        if not self.winfo_exists():
            return
        t = (step + 1) / steps
        eased = 1 - (1 - t) ** 3
        self._frac = start + (target - start) * eased
        self._redraw()
        if step < steps - 1:
            try:
                self.after(16, lambda: self._animate_to(start, target, steps, step + 1))
            except Exception:
                self._frac = target
                self._redraw()


class ScreenHeader(ctk.CTkFrame):
    """Reusable screen header with back button and title"""

    def __init__(self, master, icon, title, on_back=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left")

        if on_back:
            ctk.CTkButton(
                left,
                text="←  Back",
                command=on_back,
                fg_color=COLORS.get("elevated_bg"),
                hover_color=COLORS.get("divider"),
                text_color=COLORS.get("text"),
                corner_radius=sv(8),
                height=sv(34),
                font=font(12),
            ).pack(side="left", padx=(0, sv(12)))

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right")

        ctk.CTkLabel(
            right,
            text=icon,
            font=font(18),
            text_color=COLORS.get("primary"),
        ).pack(side="left", padx=(0, sv(6)))

        ctk.CTkLabel(
            right,
            text=title,
            font=font(20, "bold"),
            text_color=COLORS.get("text"),
        ).pack(side="left")
