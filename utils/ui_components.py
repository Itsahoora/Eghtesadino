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
        super().__init__(master=master, text=text, font=font(size, 'bold'),
                         **kwargs)


class BodyLabel(ctk.CTkLabel):
    def __init__(self, master=None, text='', size=13, **kwargs):
        super().__init__(master=master, text=text, font=font(size), **kwargs)


class MutedLabel(ctk.CTkLabel):
    def __init__(self, master=None, text='', size=11, **kwargs):
        kwargs.setdefault('text_color', COLORS.get('muted_text'))
        super().__init__(master=master, text=text, font=font(size), **kwargs)