"""Reusable themed UI components for CustomTkinter."""

import os
import json
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
from io import BytesIO
from utils.colors import COLORS
from utils.scale import sv
from utils.constants import FONT_FAMILY, ICONS


def font(size_token=14, weight='normal'):
    return (FONT_FAMILY, sv(size_token), weight)


class Card(ctk.CTkFrame):
    def __init__(self, radius=14, bg_color='card_bg', **kwargs):
        color = COLORS.get(bg_color, '#ffffff')
        super().__init__(**kwargs)
        try:
            self.configure(fg_color=color, corner_radius=sv(radius),
                           border_width=0)
        except Exception:
            self.configure(fg_color=color)


class TitleLabel(ctk.CTkLabel):
    def __init__(self, master=None, text='', size=20, **kwargs):
        super().__init__(master=master, text=text, font=font(size, 'bold'), **kwargs)


class BodyLabel(ctk.CTkLabel):
    def __init__(self, master=None, text='', size=13, **kwargs):
        super().__init__(master=master, text=text, font=font(size), **kwargs)


class MutedLabel(ctk.CTkLabel):
    def __init__(self, master=None, text='', size=11, **kwargs):
        kwargs.setdefault('text_color', COLORS.get('muted_text'))
        super().__init__(master=master, text=text, font=font(size), **kwargs)


def animate_pulse(widget, attr='fg_color', color1=None, color2=None,
                   loops=2, delay=80):
    if widget is None:
        return

    try:
        original = widget.cget(attr)
    except Exception:
        original = None

    if color1 is None:
        color1 = COLORS.get('primary', '#3B82F6')
    if color2 is None:
        color2 = COLORS.get('card_bg', '#1E293B')

    sequence = []
    for _ in range(loops):
        sequence.append(color1)
        sequence.append(color2)
    if original is not None:
        sequence.append(original)

    def step(index):
        if index >= len(sequence):
            return
        try:
            widget.configure(**{attr: sequence[index]})
        except Exception:
            pass
        if index + 1 < len(sequence):
            widget.after(delay, step, index + 1)

    step(0)


def animate_card_intro(card):
    animate_pulse(card, attr='fg_color', loops=1, delay=90)


class Avatar(ctk.CTkCanvas):
    def __init__(self, master=None, size=36, name='', image_path=None, **kwargs):
        self.size = sv(size)
        self.name = name
        self.image_path = image_path
        self._photo = None
        super().__init__(master, width=self.size, height=self.size,
                         highlightthickness=0, bg=COLORS.get('light_bg'))
        self._draw()

    def _draw(self):
        self.delete('all')
        r = self.size / 2
        bg = COLORS.get('primary')
        self.create_oval(2, 2, self.size - 2, self.size - 2, fill=bg, outline='')

        if self.image_path and os.path.exists(self.image_path):
            try:
                img = Image.open(self.image_path).convert('RGBA')
                img = img.resize((int(self.size), int(self.size)), Image.LANCZOS)
                mask = Image.new('L', (int(self.size), int(self.size)), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse([2, 2, self.size - 2, self.size - 2], fill=255)
                img.putalpha(mask)
                bio = BytesIO()
                img.save(bio, format='PNG')
                bio.seek(0)
                self._photo = ctk.PhotoImage(data=bio.read())
                self.create_image(r, r, image=self._photo, anchor='center')
                return
            except Exception:
                pass

        initials = self._get_initials()
        self.create_text(r, r, text=initials, fill='#FFFFFF',
                         font=font(int(self.size * 0.4), 'bold'), anchor='center')

    def _get_initials(self):
        if not self.name:
            return '?'
        parts = self.name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.name[:2].upper()

    def set_image(self, image_path):
        self.image_path = image_path
        self._draw()

    def set_name(self, name):
        self.name = name
        self._draw()


class DropdownMenu:
    def __init__(self, master, button_widget, menu_items, on_select,
                 dropdown_fg=None, dropdown_bg=None):
        self.master = master
        self.button_widget = button_widget
        self.menu_items = menu_items
        self.on_select = on_select
        self._window = None
        self._open = False
        self._dropdown_bg = dropdown_bg or COLORS.get('card_bg')
        self._dropdown_fg = dropdown_fg or COLORS.get('text')
        self._frame = None
        button_widget.configure(command=self._toggle)

    def _toggle(self):
        if self._open:
            self.close()
        else:
            self.open()

    def open(self):
        if self._open:
            return
        self._open = True
        self._window = ctk.Toplevel(self.master)
        self._window.wm_overrideredirect(True)
        self._window.wm_transient(self.master.winfo_toplevel())
        self._window.configure(
            bg=self._dropdown_bg,
            highlightbackground=COLORS.get('divider'),
            highlightthickness=1,
        )
        try:
            self._window.wm_attributes('-topmost', True)
        except Exception:
            pass

        self._frame = ctk.CTkFrame(
            self._window, fg_color=self._dropdown_bg,
            corner_radius=sv(12), border_width=0,
        )
        self._frame.pack(fill='both', expand=True)

        for item in self.menu_items:
            if isinstance(item, dict):
                text = item.get('text', '')
                icon = item.get('icon', '')
                command = item.get('command')
                divider = item.get('divider', False)
                danger = item.get('danger', False)
            elif isinstance(item, str):
                if item == '---':
                    self._add_divider()
                    continue
                text = item
                icon = ''
                command = None
                danger = False
            else:
                continue

            if divider:
                self._add_divider()
                continue

            btn = ctk.CTkButton(
                self._frame,
                text=f'{icon}  {text}' if icon else text,
                anchor='w',
                command=command if command else lambda t=text: self._select(t),
                fg_color='transparent',
                hover_color=COLORS.get('light_bg'),
                text_color=COLORS.get('danger') if danger else self._dropdown_fg,
                font=font(13),
                height=sv(36),
                corner_radius=sv(8),
                border_width=0,
            )
            btn.pack(fill='x', padx=sv(4), pady=sv(2))

        x = self.button_widget.winfo_rootx()
        y = self.button_widget.winfo_rooty() + self.button_widget.winfo_height()
        w = self.button_widget.winfo_width()
        self._window.geometry(f'+{x}+{y}')
        self._window.update_idletasks()
        mw = self._window.winfo_width()
        if x + mw > self.master.winfo_screenwidth():
            x = self.master.winfo_screenwidth() - mw - 8
        if x < 0:
            x = 8
        self._window.geometry(f'+{x}+{y}')

        self._window.bind('<Button-1>', self._on_click_outside)
        self.master.winfo_toplevel().bind('<Button-1>', self._on_click_outside)
        self.master.winfo_toplevel().bind('<Escape>', self._on_escape)

    def _add_divider(self):
        ctk.CTkFrame(
            self._frame, height=1, fg_color=COLORS.get('divider'),
        ).pack(fill='x', padx=sv(8), pady=sv(4))

    def _select(self, text):
        self.close()
        if callable(self.on_select):
            self.on_select(text)

    def close(self):
        if not self._open:
            return
        self._open = False
        try:
            if self._window:
                self._window.destroy()
        except Exception:
            pass
        self._window = None
        self._frame = None
        try:
            self.master.winfo_toplevel().unbind('<Button-1>', self._on_click_outside)
        except Exception:
            pass
        try:
            self.master.winfo_toplevel().unbind('<Escape>', self._on_escape)
        except Exception:
            pass

    def _on_click_outside(self, event):
        try:
            if self._window and not self._window.winfo_containing(
                    event.x_root, event.y_root).winfo_exists():
                self.close()
        except Exception:
            self.close()

    def _on_escape(self, event):
        self.close()

    def is_open(self):
        return self._open
