"""Reusable themed UI components for CustomTkinter."""

import customtkinter as ctk
from utils.colors import COLORS
from utils.scale import sv
from utils.constants import FONT_FAMILY


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
