import os
import json
import customtkinter as ctk
import tkinter.messagebox as mb
from tkinter import filedialog
from PIL import Image
from utils.colors import COLORS
from utils.scale import sv
from utils.constants import ICONS, BASE_PADDING, FONT_FAMILY
from utils.ui_components import Avatar, Card, font, TitleLabel, BodyLabel, MutedLabel
from utils.theme_manager import theme_manager
from utils.localization import tr

MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
PROFILES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'profiles')


class ProfileDialog:
    def __init__(self, master, advisor, user_id, on_save=None):
        self.advisor = advisor
        self.user_id = user_id
        self.on_save = on_save
        self._photo = None
        self._current_image_path = None
        self._build_ui(master)

    def _build_ui(self, master):
        self.root = ctk.CTkToplevel(master)
        self.root.title(tr('profile'))
        self.root.geometry(f"{sv(420)}x{sv(520)}")
        self.root.resizable(False, False)
        self.root.configure(fg_color=COLORS.get('light_bg'))
        try:
            self.root.transient(master)
            self.root.grab_set()
        except Exception:
            pass

        pad = sv(BASE_PADDING)

        # ── Profile header ──
        header = ctk.CTkFrame(self.root, fg_color='transparent')
        header.pack(fill='x', padx=pad, pady=(sv(20), sv(8)))

        ctk.CTkLabel(
            header, text=ICONS['user'],
            font=font(20), text_color=COLORS.get('primary'),
        ).pack(side='left', padx=(0, sv(10)))

        ctk.CTkLabel(
            header, text=tr('profile'),
            font=font(20, 'bold'), text_color=COLORS.get('text'),
        ).pack(side='left')

        ctk.CTkButton(
            header, text=ICONS['close'],
            command=self.root.destroy,
            fg_color='transparent', hover_color=COLORS.get('divider'),
            text_color=COLORS.get('muted_text'),
            corner_radius=sv(20), width=sv(32), height=sv(32),
            font=font(14),
        ).pack(side='right')

        # ── Scrollable body ──
        scroll = ctk.CTkScrollableFrame(
            self.root, fg_color='transparent',
            scrollbar_button_color=COLORS.get('primary'),
            scrollbar_button_hover_color=COLORS.get('accent'),
        )
        scroll.pack(fill='both', expand=True, padx=pad, pady=(0, pad))

        # ── Avatar section ──
        avatar_card = Card(master=scroll, radius=sv(14))
        avatar_card.pack(fill='x', pady=(0, sv(12)))
        avatar_inner = ctk.CTkFrame(avatar_card, fg_color='transparent')
        avatar_inner.pack(fill='x', padx=sv(20), pady=sv(16))

        profile = self.advisor.get_user_profile(self.user_id)
        display_name = profile.get('display_name', '')
        pic_path = profile.get('profile_pic')
        if pic_path and os.path.exists(pic_path):
            self._current_image_path = pic_path
        else:
            self._current_image_path = None

        self._avatar = Avatar(
            avatar_inner, size=64, name=display_name,
            image_path=self._current_image_path,
        )
        self._avatar.pack(side='left', padx=(0, sv(14)))

        info_frame = ctk.CTkFrame(avatar_inner, fg_color='transparent')
        info_frame.pack(side='left', fill='x', expand=True)

        BodyLabel(
            info_frame, text=display_name or '—',
            size=14, text_color=COLORS.get('text'),
        ).pack(anchor='w')

        MutedLabel(
            info_frame, text=tr('personal_account'), size=11,
        ).pack(anchor='w', pady=(sv(2), 0))

        # ── Photo upload row ──
        photo_row = ctk.CTkFrame(avatar_card, fg_color='transparent')
        photo_row.pack(fill='x', padx=sv(20), pady=(0, sv(16)))

        ctk.CTkButton(
            photo_row, text=f"{ICONS['upload']}  {tr('upload_photo')}",
            command=self._pick_image,
            fg_color=COLORS.get('elevated_bg'),
            hover_color=COLORS.get('divider'),
            text_color=COLORS.get('text'),
            corner_radius=sv(8), height=sv(34),
            font=font(12),
        ).pack(side='left', padx=(0, sv(8)))

        if self._current_image_path:
            ctk.CTkButton(
                photo_row, text=f"{ICONS['remove']}  {tr('remove_photo')}",
                command=self._remove_image,
                fg_color=COLORS.get('elevated_bg'),
                hover_color=COLORS.get('danger'),
                text_color=COLORS.get('danger'),
                corner_radius=sv(8), height=sv(34),
                font=font(12),
            ).pack(side='left')

        # ── Display name ──
        name_card = Card(master=scroll, radius=sv(14))
        name_card.pack(fill='x', pady=(0, sv(12)))
        name_inner = ctk.CTkFrame(name_card, fg_color='transparent')
        name_inner.pack(fill='x', padx=sv(20), pady=sv(14))

        ctk.CTkLabel(
            name_inner, text=tr('display_name'),
            font=font(13, 'bold'), text_color=COLORS.get('text'),
        ).pack(anchor='w', pady=(0, sv(6)))

        self.name_entry = ctk.CTkEntry(
            name_inner, placeholder_text=display_name or 'Enter display name',
            height=sv(38), font=font(13),
            border_width=1, border_color=COLORS.get('divider'),
        )
        self.name_entry.insert(0, display_name or '')
        self.name_entry.pack(fill='x')

        # ── Preview ──
        preview_card = Card(master=scroll, radius=sv(14))
        preview_card.pack(fill='x', pady=(0, sv(12)))
        preview_inner = ctk.CTkFrame(preview_card, fg_color='transparent')
        preview_inner.pack(fill='x', padx=sv(20), pady=sv(14))

        ctk.CTkLabel(
            preview_inner, text=tr('preview'),
            font=font(13, 'bold'), text_color=COLORS.get('text'),
        ).pack(anchor='w', pady=(0, sv(8)))

        self._preview_frame = ctk.CTkFrame(
            preview_inner, fg_color=COLORS.get('input_bg'),
            corner_radius=sv(10),
        )
        self._preview_frame.pack(fill='x', pady=sv(4))

        self._preview_avatar = Avatar(
            self._preview_frame, size=80, name=display_name,
            image_path=self._current_image_path,
        )
        self._preview_avatar.pack(pady=sv(12))

        # ── Save button ──
        save_btn = ctk.CTkButton(
            self.root, text=f"{ICONS['save']}  {tr('save_profile')}",
            command=self._save,
            fg_color=COLORS.get('primary'),
            hover_color=COLORS.get('primary_hover'),
            corner_radius=sv(10), height=sv(42),
            font=font(13, 'bold'),
        )
        save_btn.pack(fill='x', padx=pad, pady=(sv(4), sv(16)))

    def _pick_image(self):
        filepath = filedialog.askopenfilename(
            title=tr('choose_file'),
            filetypes=[
                ('Image files', '*.png *.jpg *.jpeg *.gif *.webp'),
                ('All files', '*.*'),
            ],
        )
        if not filepath:
            return

        ext = os.path.splitext(filepath)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            mb.showwarning(tr('warning'), tr('image_error'))
            return

        size = os.path.getsize(filepath)
        if size > MAX_IMAGE_SIZE:
            mb.showwarning(tr('warning'), tr('image_too_large'))
            return

        try:
            img = Image.open(filepath)
            img.thumbnail((200, 200), Image.LANCZOS)
            os.makedirs(PROFILES_DIR, exist_ok=True)
            safe_name = f'profile_{self.user_id}{ext}'
            dest = os.path.join(PROFILES_DIR, safe_name)
            img.save(dest)
            self._current_image_path = dest
            self._avatar.set_image(dest)
            self._preview_avatar.set_image(dest)
        except Exception:
            mb.showerror(tr('error'), tr('image_error'))

    def _remove_image(self):
        if self._current_image_path and os.path.exists(self._current_image_path):
            try:
                os.remove(self._current_image_path)
            except Exception:
                pass
        self._current_image_path = None
        self._avatar.set_image(None)
        self._preview_avatar.set_image(None)

    def _save(self):
        name = self.name_entry.get().strip()
        if not name:
            mb.showwarning(tr('warning'), tr('display_name') + " " + tr('required'))
            return

        success = self.advisor.update_display_name(self.user_id, name)
        if not success:
            mb.showerror(tr('error'), tr('profile_save_failed'))
            return

        if self._current_image_path is not None:
            self.advisor.update_profile_pic(self.user_id, self._current_image_path)
        else:
            try:
                profile = self.advisor.get_user_profile(self.user_id)
                old_pic = profile.get('profile_pic')
                if old_pic and os.path.exists(old_pic):
                    os.remove(old_pic)
                self.advisor.update_profile_pic(self.user_id, None)
            except Exception:
                pass

        mb.showinfo(tr('success'), tr('profile_saved'))
        if callable(self.on_save):
            self.on_save()
        self.root.destroy()

    def pack(self, *args, **kwargs):
        return self.root.pack(*args, **kwargs)