# app_ctk.py
import json
import os
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

# ------------ إعداد CustomTkinter ------------
ctk.set_appearance_mode("Light")  # "Dark" ممكن لاحقاً للتبديل
ctk.set_default_color_theme("blue")  # يؤثر في الأزرار والألوان الافتراضية

NOTES_FILE = "notes.json"

PALETTE = {
    "bg": "#F6F7FB",
    "card": "#FFFFFF",
    "accent": "#7ED6DF",    # تيفاني pastel
    "accent2": "#C39BD3",   # بنفسجي فاتح
    "muted": "#8E9AAF",
}

# ------------ JSON helpers مع معالجة الأخطاء ------------
def init_notes_file():
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def load_notes():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=4)

# ------------ نافذة التفاصيل المنبثقة ------------
def open_note_modal(master, note, refresh_callback=None):
    top = ctk.CTkToplevel(master)
    top.title(note.get("title", "ملاحظة"))
    top.geometry("420x320")
    top.configure(fg_color=PALETTE["bg"])

    title_lbl = ctk.CTkLabel(top, text=note["title"], font=ctk.CTkFont(size=16, weight="bold"),
                             anchor="e", justify="right")
    title_lbl.pack(fill="x", pady=(12,6), padx=12)

    date_lbl = ctk.CTkLabel(top, text=note["date"], font=ctk.CTkFont(size=11), fg_color=None, anchor="e")
    date_lbl.pack(fill="x", padx=12)

    body_txt = ctk.CTkTextbox(top, wrap="word", height=12)
    body_txt.insert("0.0", note["body"])
    body_txt.configure(state="disabled", fg_color=PALETTE["card"], corner_radius=8)
    body_txt.pack(fill="both", expand=True, padx=12, pady=12)

# ------------ تطبيق الواجهة الرئيسية ------------
class NotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("تطبيق الملاحظات — Pastel")
        self.geometry("760x560")
        self.minsize(600, 450)
        self.configure(fg_color=PALETTE["bg"])

        init_notes_file()
        self.notes = load_notes()

        self._build_ui()
        self.refresh_notes_display()

    def _build_ui(self):
        # رأس التطبيق
        header = ctk.CTkFrame(self, fg_color=PALETTE["bg"], corner_radius=0)
        header.pack(fill="x", padx=16, pady=(12,8))

        title = ctk.CTkLabel(header, text="تطبيق الملاحظات", font=ctk.CTkFont(size=20, weight="bold"),
                             anchor="e")
        title.pack(side="right")

        subtitle = ctk.CTkLabel(header, text="واجهة Pastel بتأثير Hover وCards", font=ctk.CTkFont(size=11),
                                fg_color=None, text_color=PALETTE["muted"], anchor="e")
        subtitle.pack(side="right", padx=(0,12))

        # المنطقة الرئيسية: قسم الإدخال + قسم العرض
        main_frame = ctk.CTkFrame(self, fg_color=PALETTE["bg"], corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=16, pady=8)

        # ----- جهة اليمين: إدخال ملاحظة -----
        right_panel = ctk.CTkFrame(main_frame, fg_color=PALETTE["bg"], corner_radius=0)
        right_panel.pack(side="right", fill="y", padx=(0,12), pady=8)

        lbl_title = ctk.CTkLabel(right_panel, text="عنوان الملاحظة:", anchor="e")
        lbl_title.pack(anchor="e", pady=(6,2), padx=4)
        self.entry_title = ctk.CTkEntry(right_panel, width=320, placeholder_text="ضع عنوانًا مختصرًا")
        self.entry_title.pack(padx=4, pady=(0,8))

        lbl_body = ctk.CTkLabel(right_panel, text="نص الملاحظة:", anchor="e")
        lbl_body.pack(anchor="e", pady=(6,2), padx=4)
        self.text_body = ctk.CTkTextbox(right_panel, width=320, height=10)
        self.text_body.pack(padx=4, pady=(0,8))

        # زر الإضافة مع تأثير hover بسيط (تغيير اللون وحجم الخط)
        self.add_btn = ctk.CTkButton(right_panel, text="إضافة الملاحظة", command=self.on_add_click,
                                     width=200, height=40, corner_radius=12,
                                     fg_color=PALETTE["accent"], text_color="white")
        self.add_btn.pack(pady=8)

        # ربط hover (تكبير طفيف وتغيير لون)
        self.add_btn.bind("<Enter>", self._on_add_hover)
        self.add_btn.bind("<Leave>", self._on_add_leave)

        # زر تبديل الLight/Dark (اختياري)
        self.mode_switch = ctk.CTkSwitch(right_panel, text="Dark Mode", command=self.toggle_mode)
        self.mode_switch.pack(pady=(10,0))

        # ----- جهة اليسار: عرض الملاحظات (Scrollable cards) -----
        left_panel = ctk.CTkFrame(main_frame, fg_color=PALETTE["bg"], corner_radius=0)
        left_panel.pack(side="left", fill="both", expand=True, padx=(12,0), pady=8)

        notes_label = ctk.CTkLabel(left_panel, text="جميع الملاحظات", font=ctk.CTkFont(size=14, weight="bold"),
                                   anchor="w")
        notes_label.pack(fill="x", padx=6, pady=(2,6))

        # شريط تمرير مع إطار قابل للتمرير
        self.scroll_frame = ctk.CTkScrollableFrame(left_panel, width=420, corner_radius=8)
        self.scroll_frame.pack(fill="both", expand=True, padx=6, pady=(0,6))
        self.scroll_frame.pack_propagate(False)

        # مكان لبطاقات الملاحظات
        self.cards_container = ctk.CTkFrame(self.scroll_frame, fg_color=PALETTE["bg"])
        self.cards_container.pack(fill="both", expand=True, padx=6, pady=6)

    # ---------- فعّاليات الواجهة ----------
    def _on_add_hover(self, event):
        # تغيير لون وحجم الخط كأنيمشن بسيط
        event.widget.configure(fg_color=PALETTE["accent2"])
        event.widget.configure(font=ctk.CTkFont(size=12, weight="bold"))

    def _on_add_leave(self, event):
        event.widget.configure(fg_color=PALETTE["accent"])
        event.widget.configure(font=ctk.CTkFont(size=11))

    def toggle_mode(self):
        # تبديل أوتوماتيكي بين Light و Dark
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Dark" if current == "Light" else "Light")

    def on_add_click(self):
        title = self.entry_title.get().strip()
        body = self.text_body.get("0.0", "end").strip()

        if not title or not body:
            messagebox.showwarning("خطأ", "الرجاء إدخال عنوان ونص الملاحظة.")
            return

        note = {
            "title": title,
            "body": body,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.notes.append(note)
        save_notes(self.notes)

        # مؤثر بسيط: مسح الحقول ثم عرض رسالة صغيرة ثم تحديث العرض
        self.entry_title.delete(0, "end")
        self.text_body.delete("0.0", "end")

        # تأكيد بصري صغير
        self.add_btn.configure(text="تمت الإضافة ✓")
        self.after(900, lambda: self.add_btn.configure(text="إضافة الملاحظة"))

        self.refresh_notes_display()

    def refresh_notes_display(self):
        # تنظيف الحاوية
        for child in self.cards_container.winfo_children():
            child.destroy()

        # عرض الملاحظات كـ Cards
        if not self.notes:
            empty = ctk.CTkLabel(self.cards_container, text="لا توجد ملاحظات حتى الآن.", text_color=PALETTE["muted"])
            empty.pack(pady=12)
            return

        # أعلى الملاحظة أحدث أولاً
        for i, note in enumerate(reversed(self.notes)):
            self._create_card(self.cards_container, note, index=len(self.notes)-1 - i)

    def _create_card(self, parent, note, index):
        card = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=10, height=80)
        card.pack(fill="x", pady=8, padx=6)

        # عنوان ووقت
        title_lbl = ctk.CTkLabel(card, text=note["title"], font=ctk.CTkFont(size=13, weight="bold"),
                                 anchor="e")
        title_lbl.place(relx=0.99, rely=0.18, anchor="ne")

        date_lbl = ctk.CTkLabel(card, text=note["date"], font=ctk.CTkFont(size=10), text_color=PALETTE["muted"],
                                anchor="e")
        date_lbl.place(relx=0.99, rely=0.42, anchor="ne")

        # نص مختصر
        snippet = note["body"]
        if len(snippet) > 90:
            snippet = snippet[:90] + "..."

        body_lbl = ctk.CTkLabel(card, text=snippet, anchor="w", width=360, wraplength=420, justify="right")
        body_lbl.place(relx=0.01, rely=0.5, anchor="w")

        # زر فتح التفاصيل
        view_btn = ctk.CTkButton(card, text="عرض", width=70, fg_color=PALETTE["accent"], corner_radius=8,
                                 command=lambda n=note: open_note_modal(self, n))
        view_btn.place(relx=0.01, rely=0.18, anchor="w")

        # Hover effect على البطاقة: ظل خفيف (محاكاة بتغيير اللون الخلفي)
        def on_enter(e):
            card.configure(fg_color="#FBFBFF")
        def on_leave(e):
            card.configure(fg_color=PALETTE["card"])

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

# ------------ تشغيل التطبيق ------------
if __name__ == "__main__":
    app = NotesApp()
    app.mainloop()
