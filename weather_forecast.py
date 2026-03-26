import tkinter as tk
import customtkinter as ctk
import requests
import threading
from datetime import datetime
import io
from PIL import Image, ImageTk

# --- CONFIG ---
API_KEY = "f0f000840adb70adc492dfb961d62c5c" 
ICON_BASE_URL = "http://openweathermap.org/img/wn/"

class SkyCastVivid(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SkyCast Vivid")
        self.geometry("500x950")
        
        # Theme Management
        self.is_dark = False
        ctk.set_appearance_mode("light")

        # Color Palette (Standard Hex only to avoid TclError)
        self.primary_blue = "#38BDF8"
        self.accent_gold = "#FBBF24"
        self.card_color = ("#FFFFFF", "#1E293B") 
        self.text_main = ("#0F172A", "#F8FAFC")
        self.text_muted = "#64748B"

        self.icon_cache = {}

        # 1. --- BACKGROUND IMAGE ---
        try:
            # Ensure 'bg.png' exists in your script folder
            img = Image.open("bg.png").resize((500, 950), Image.Resampling.LANCZOS)
            self.bg_image_tk = ImageTk.PhotoImage(img)
            self.bg_label = tk.Label(self, image=self.bg_image_tk)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            self.configure(fg_color=("#F1F5F9", "#0F172A"))

        # 2. --- TOP NAV & TOGGLE ---
        self.nav = ctk.CTkFrame(self, fg_color="transparent")
        self.nav.pack(pady=(40, 10), padx=25, fill="x")

        self.logo = ctk.CTkLabel(self.nav, text="SKYCAST", font=("Verdana", 26, "bold"), text_color=self.primary_blue)
        self.logo.pack(side="left")

        self.theme_btn = ctk.CTkButton(self.nav, text="🌙 Dark", width=80, height=32, corner_radius=16,
                                        fg_color=self.card_color, text_color=self.text_main,
                                        command=self.toggle_theme)
        self.theme_btn.pack(side="right")

        # 3. --- SEARCH ---
        self.search_frame = ctk.CTkFrame(self, fg_color=self.card_color, corner_radius=25, height=52)
        self.search_frame.pack(pady=10, padx=25, fill="x")
        self.search_frame.pack_propagate(False)

        self.city_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search city...", 
                                       fg_color="transparent", border_width=0, font=("Inter", 14))
        self.city_entry.pack(side="left", padx=20, fill="x", expand=True)

        self.search_btn = ctk.CTkButton(self.search_frame, text="⚡", width=45, corner_radius=20, 
                                        fg_color=self.primary_blue, command=self.run_search)
        self.search_btn.pack(side="right", padx=10)

        # 4. --- SCROLLABLE CONTENT ---
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=10)

        # Hero
        self.city_lbl = ctk.CTkLabel(self.container, text="SkyCast", font=("Inter", 32, "bold"), text_color=self.text_main)
        self.city_lbl.pack(pady=(10, 0))

        self.icon_lbl = ctk.CTkLabel(self.container, text="")
        self.icon_lbl.pack()

        self.temp_lbl = ctk.CTkLabel(self.container, text="--°", font=("Inter", 90, "bold"), text_color=self.accent_gold)
        self.temp_lbl.pack()

        self.desc_lbl = ctk.CTkLabel(self.container, text="ENTER A CITY", font=("Inter", 12, "bold"), text_color=self.text_muted)
        self.desc_lbl.pack()

        # Hourly Card
        self.h_card = ctk.CTkFrame(self.container, fg_color=self.card_color, corner_radius=25)
        self.h_card.pack(pady=25, padx=15, fill="x")
        ctk.CTkLabel(self.h_card, text="24-HOUR FORECAST", font=("Inter", 10, "bold"), text_color=self.primary_blue).pack(pady=(15, 5), padx=20, anchor="w")
        self.h_scroll = ctk.CTkScrollableFrame(self.h_card, orientation="horizontal", fg_color="transparent", height=130)
        self.h_scroll.pack(fill="x", padx=10, pady=(0, 10))

        # Daily Card (Restored)
        self.d_card = ctk.CTkFrame(self.container, fg_color=self.card_color, corner_radius=25)
        self.d_card.pack(pady=10, padx=15, fill="x")
        ctk.CTkLabel(self.d_card, text="5-DAY PREDICTION", font=("Inter", 10, "bold"), text_color=self.primary_blue).pack(pady=(15, 10), padx=20, anchor="w")
        self.d_list = ctk.CTkFrame(self.d_card, fg_color="transparent")
        self.d_list.pack(fill="x", padx=15, pady=(0, 15))

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        ctk.set_appearance_mode("dark" if self.is_dark else "light")
        self.theme_btn.configure(text="☀️ Light" if self.is_dark else "🌙 Dark")

    def get_vivid_icon(self, code, size=(60, 60)):
        try:
            url = f"{ICON_BASE_URL}{code}@2x.png"
            resp = requests.get(url)
            img = Image.open(io.BytesIO(resp.content)).resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except: return None

    def run_search(self):
        city = self.city_entry.get().strip()
        if city: threading.Thread(target=self.fetch_all, args=(city,), daemon=True).start()

    def fetch_all(self, city):
        try:
            c = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric").json()
            f = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric").json()
            if c.get("cod") == 200:
                self.update_ui(c, f)
        except: pass

    def update_ui(self, c, f):
        # Main Hero
        self.city_lbl.configure(text=c['name'].upper())
        self.temp_lbl.configure(text=f"{round(c['main']['temp'])}°")
        self.desc_lbl.configure(text=c['weather'][0]['description'].upper())
        
        main_img = self.get_vivid_icon(c['weather'][0]['icon'], (160, 160))
        self.icon_lbl.configure(image=main_img)
        self.icon_lbl.image = main_img

        # Hourly
        for w in self.h_scroll.winfo_children(): w.destroy()
        for i in range(8):
            item = f['list'][i]
            box = ctk.CTkFrame(self.h_scroll, fg_color="transparent", width=80)
            box.pack(side="left", padx=8)
            ctk.CTkLabel(box, text=datetime.fromtimestamp(item['dt']).strftime("%H:%M"), font=("Inter", 11)).pack()
            img = self.get_vivid_icon(item['weather'][0]['icon'])
            lbl = ctk.CTkLabel(box, image=img, text=""); lbl.image = img; lbl.pack()
            ctk.CTkLabel(box, text=f"{round(item['main']['temp'])}°", font=("Inter", 13, "bold"), text_color=self.primary_blue).pack()

        # Daily (Restored)
        for w in self.d_list.winfo_children(): w.destroy()
        seen = []
        for item in f['list']:
            date = datetime.fromtimestamp(item['dt']).strftime("%A")
            if date not in seen and "12:00:00" in item['dt_txt']:
                seen.append(date)
                row = ctk.CTkFrame(self.d_list, fg_color="transparent")
                row.pack(fill="x", pady=8)
                ctk.CTkLabel(row, text=date, font=("Inter", 14, "bold"), width=120, anchor="w").pack(side="left")
                img = self.get_vivid_icon(item['weather'][0]['icon'], (40, 40))
                lbl = ctk.CTkLabel(row, image=img, text=""); lbl.image = img; lbl.pack(side="left", expand=True)
                ctk.CTkLabel(row, text=f"{round(item['main']['temp'])}°", font=("Inter", 15, "bold"), text_color=self.primary_blue).pack(side="right")

if __name__ == "__main__":
    app = SkyCastVivid()
    app.mainloop()