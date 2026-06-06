"""
webcam_scanner.py — A reusable live webcam scanning dialog for Tkinter/CustomTkinter.
Detects and decodes QR codes and barcodes, then triggers a callback on success.
"""

import cv2
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
try:
    import winsound
except ImportError:
    winsound = None
from config import COLORS, FONTS
from ui_utils import place_popup
from lang import t


class WebcamScanner(ctk.CTkToplevel):
    def __init__(self, parent, app, title_key="Webcam Scanner", callback=None):
        super().__init__(parent)
        self.app = app
        self.callback = callback
        self.lang = app.current_lang if app else "English"
        
        self.title(t(title_key, self.lang))
        place_popup(self, 640, 520, parent)
        self.resizable(False, False)
        self.grab_set()
        self.attributes("-topmost", True)
        
        # UI Setup
        # Video feed label
        self.video_label = ctk.CTkLabel(
            self, 
            text=t("Initializing Camera...", self.lang), 
            fg_color="black", 
            width=620, 
            height=420,
            font=FONTS.get("body", ("Segoe UI", 15))
        )
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bottom controls
        self.control_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            self.control_frame, 
            text=t("Align QR/Barcode within camera frame", self.lang), 
            font=FONTS.get("body", ("Segoe UI", 13)),
            text_color=COLORS.get("text_dark", "#1A1A2E")
        )
        self.status_label.pack(side="left", padx=10)
        
        self.cancel_button = ctk.CTkButton(
            self.control_frame, 
            text=t("Cancel", self.lang), 
            font=FONTS.get("button", ("Segoe UI", 13, "bold")),
            fg_color=COLORS.get("btn_danger", "#F43F5E"), 
            hover_color="#E11D48", 
            command=self.close_scanner,
            height=36,
            corner_radius=10
        )
        self.cancel_button.pack(side="right", padx=10)
        
        # Detectors
        self.qr_detector = cv2.QRCodeDetector()
        self.barcode_detector = cv2.barcode.BarcodeDetector()
        
        # Camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.video_label.configure(
                text=t("Error: Could not open camera.\nPlease check your webcam connection.", self.lang)
            )
            self.status_label.configure(
                text=t("Camera Error", self.lang), 
                text_color=COLORS.get("btn_danger", "#EF4444")
            )
            return
            
        self.active = True
        self.update_frame()
        self.bind("<Destroy>", self.on_destroy)
        
    def update_frame(self):
        if not self.active or not self.cap.isOpened():
            return
            
        ret, frame = self.cap.read()
        if not ret:
            self.after(30, self.update_frame)
            return
            
        # Try QR Code detection on original un-flipped frame
        qr_data, bbox, _ = self.qr_detector.detectAndDecode(frame)
        if qr_data:
            self.on_code_scanned(qr_data)
            return
            
        # Try Barcode detection on original un-flipped frame
        barcode_data, _, _ = self.barcode_detector.detectAndDecode(frame)
        if barcode_data:
            if isinstance(barcode_data, (tuple, list)):
                if barcode_data and barcode_data[0]:
                    self.on_code_scanned(barcode_data[0])
                    return
            elif isinstance(barcode_data, str) and barcode_data:
                self.on_code_scanned(barcode_data)
                return
                
        # Now flip for human display!
        display_frame = cv2.flip(frame, 1)
        
        # Draw guide rectangle in the center of the flipped frame
        h, w, _ = display_frame.shape
        start_pt = (int(w * 0.25), int(h * 0.25))
        end_pt = (int(w * 0.75), int(h * 0.75))
        cv2.rectangle(display_frame, start_pt, end_pt, (0, 255, 0), 2)
        
        # Convert to RGB and PIL/PhotoImage
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        img_tk = ImageTk.PhotoImage(image=img)
        
        self.video_label.configure(image=img_tk, text="")
        self.video_label.image = img_tk
        
        self.after(30, self.update_frame)
        
    def on_code_scanned(self, code):
        self.active = False
        if winsound:
            try:
                winsound.Beep(2000, 150)
            except Exception:
                pass
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()
        if self.callback:
            self.callback(code)
            
    def close_scanner(self):
        self.destroy()
        
    def on_destroy(self, event):
        if event.widget == self:
            self.active = False
            if self.cap.isOpened():
                self.cap.release()
