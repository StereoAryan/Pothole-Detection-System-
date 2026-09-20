import cv2
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO


MODEL_PATH = 'best.pt'
class_labels = ['Pothole']


class PotholeDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🕳️ Pothole Detection System")
        self.root.geometry("1920x1080")
        self.root.state('zoomed')
        self.root.configure(bg="#0a0e27")

        # Load model
        try:
            self.model = YOLO(MODEL_PATH)
            self.model_loaded = True
        except:
            self.model_loaded = False
            messagebox.showerror("Error", f"Could not load model from {MODEL_PATH}")


        # State variables
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.fps = 0
        self.detection_count = 0
        self.total_detections = 0
        self.confidence_threshold = 0.25

        # Create GUI - New Layout
        self.create_compact_header()
        self.create_large_video_display()
        self.create_bottom_controls()

        # Start with camera 0
        self.open_source(0)
        self.update_frame()

    def create_compact_header(self):
        """Create minimal header"""
        header = tk.Frame(self.root, bg="#1a1f3a", height=50)
        header.pack(fill=tk.X, padx=5, pady=5)
        header.pack_propagate(False)

        # Title
        title = tk.Label(header, text="🕳️ AI Pothole Detection System",
                         font=("Helvetica", 20, "bold"),
                         bg="#1a1f3a", fg="#00d4ff")
        title.pack(side=tk.LEFT, padx=15, pady=10)

        # Status
        self.status_label = tk.Label(header, text="● READY",
                                     font=("Helvetica", 13, "bold"),
                                     bg="#1a1f3a", fg="#00ff88")
        self.status_label.pack(side=tk.RIGHT, padx=15)

    def create_large_video_display(self):
        """Create large video display area that takes most space"""
        # Main video container
        video_container = tk.Frame(self.root, bg="#0a0e27")
        video_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Video frame with minimal decoration
        video_frame = tk.Frame(video_container, bg="#000000", relief=tk.SOLID, bd=2)
        video_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for video - takes all available space
        self.canvas = tk.Canvas(video_frame, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_bottom_controls(self):
        """Create all controls at the bottom"""
        # Bottom container
        bottom_panel = tk.Frame(self.root, bg="#1a1f3a", relief=tk.RAISED, bd=2)
        bottom_panel.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        # First row: Statistics
        stats_row = tk.Frame(bottom_panel, bg="#1a1f3a")
        stats_row.pack(fill=tk.X, pady=5)

        tk.Label(stats_row, text="📊 LIVE STATISTICS",
                 font=("Helvetica", 11, "bold"),
                 bg="#1a1f3a", fg="#00d4ff").pack(side=tk.LEFT, padx=15)

        # Stats containers
        stats_container = tk.Frame(stats_row, bg="#1a1f3a")
        stats_container.pack(side=tk.LEFT, expand=True)

        # FPS
        fps_frame = tk.Frame(stats_container, bg="#2d3561", relief=tk.FLAT, bd=1)
        fps_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(fps_frame, text="FPS", font=("Helvetica", 9),
                 bg="#2d3561", fg="#888888").pack(padx=15, pady=(5, 0))
        self.fps_label = tk.Label(fps_frame, text="0",
                                  font=("Helvetica", 22, "bold"),
                                  bg="#2d3561", fg="#00ff88")
        self.fps_label.pack(padx=15, pady=(0, 5))

        # Current detections
        det_frame = tk.Frame(stats_container, bg="#2d3561", relief=tk.FLAT, bd=1)
        det_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(det_frame, text="CURRENT", font=("Helvetica", 9),
                 bg="#2d3561", fg="#888888").pack(padx=15, pady=(5, 0))
        self.det_label = tk.Label(det_frame, text="0",
                                  font=("Helvetica", 22, "bold"),
                                  bg="#2d3561", fg="#ff6b6b")
        self.det_label.pack(padx=15, pady=(0, 5))

        # Total detections
        total_frame = tk.Frame(stats_container, bg="#2d3561", relief=tk.FLAT, bd=1)
        total_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(total_frame, text="TOTAL", font=("Helvetica", 9),
                 bg="#2d3561", fg="#888888").pack(padx=15, pady=(5, 0))
        self.total_label = tk.Label(total_frame, text="0",
                                    font=("Helvetica", 22, "bold"),
                                    bg="#2d3561", fg="#ffd93d")
        self.total_label.pack(padx=15, pady=(0, 5))

        # Separator
        tk.Frame(bottom_panel, bg="#00d4ff", height=2).pack(fill=tk.X, pady=5)

        # Second row: All controls
        controls_row = tk.Frame(bottom_panel, bg="#1a1f3a")
        controls_row.pack(fill=tk.X, pady=5, padx=10)

        # Video Source Section
        source_section = tk.LabelFrame(controls_row, text="📹 Video Source",
                                       font=("Helvetica", 10, "bold"),
                                       bg="#1a1f3a", fg="#00d4ff", bd=2)
        source_section.pack(side=tk.LEFT, padx=5)

        source_btns = tk.Frame(source_section, bg="#1a1f3a")
        source_btns.pack(padx=10, pady=8)

        cameras = [
            ("📷 Camera 0", lambda: self.open_source(0)),
            ("📷 Camera 1", lambda: self.open_source(1)),
            ("📁 Video File", self.open_video_file),
            ("🌐 Stream URL", self.open_stream)
        ]

        for text, cmd in cameras:
            btn = tk.Button(source_btns, text=text, command=cmd,
                            bg="#2d3561", fg="#ffffff",
                            font=("Helvetica", 9, "bold"),
                            relief=tk.FLAT, padx=12, pady=6,
                            activebackground="#00d4ff",
                            activeforeground="#000000",
                            cursor="hand2")
            btn.pack(side=tk.LEFT, padx=3)

        # Playback Control Section
        playback_section = tk.LabelFrame(controls_row, text="⏯️ Playback",
                                         font=("Helvetica", 10, "bold"),
                                         bg="#1a1f3a", fg="#00d4ff", bd=2)
        playback_section.pack(side=tk.LEFT, padx=5)

        self.play_btn = tk.Button(playback_section, text="⏸️  PAUSE",
                                  command=self.toggle_playback,
                                  bg="#2d3561", fg="#ffffff",
                                  font=("Helvetica", 10, "bold"),
                                  relief=tk.FLAT, padx=25, pady=8,
                                  activebackground="#ff6b6b",
                                  cursor="hand2")
        self.play_btn.pack(padx=10, pady=8)

        # Settings Section
        settings_section = tk.LabelFrame(controls_row, text="⚙️ Settings",
                                         font=("Helvetica", 10, "bold"),
                                         bg="#1a1f3a", fg="#00d4ff", bd=2)
        settings_section.pack(side=tk.LEFT, padx=5)

        settings_content = tk.Frame(settings_section, bg="#1a1f3a")
        settings_content.pack(padx=10, pady=8)

        # Confidence slider
        conf_frame = tk.Frame(settings_content, bg="#1a1f3a")
        conf_frame.pack(side=tk.LEFT, padx=5)

        tk.Label(conf_frame, text="Confidence Threshold:",
                 bg="#1a1f3a", fg="#ffffff",
                 font=("Helvetica", 9)).pack()

        self.conf_scale = tk.Scale(conf_frame, from_=0.1, to=0.9,
                                   resolution=0.05, orient=tk.HORIZONTAL,
                                   bg="#2d3561", fg="#ffffff",
                                   highlightthickness=0, troughcolor="#0a0e27",
                                   activebackground="#00d4ff",
                                   length=180, width=15)
        self.conf_scale.set(self.confidence_threshold)
        self.conf_scale.pack()

        # Reset button
        reset_frame = tk.Frame(settings_content, bg="#1a1f3a")
        reset_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(reset_frame, text="🔄 Reset Stats",
                  command=self.reset_stats,
                  bg="#2d3561", fg="#ffffff",
                  font=("Helvetica", 9, "bold"),
                  relief=tk.FLAT, padx=15, pady=8,
                  activebackground="#ffd93d",
                  cursor="hand2").pack()

        # Exit button
        exit_frame = tk.Frame(settings_content, bg="#1a1f3a")
        exit_frame.pack(side=tk.LEFT, padx=5)

        tk.Button(exit_frame, text="❌ Exit",
                  command=self.on_closing,
                  bg="#ff4757", fg="#ffffff",
                  font=("Helvetica", 9, "bold"),
                  relief=tk.FLAT, padx=20, pady=8,
                  activebackground="#ff6b6b",
                  cursor="hand2").pack()

    def open_source(self, src):
        """Open video source"""
        if self.cap:
            self.cap.release()

        try:
            self.cap = cv2.VideoCapture(src)
            if not self.cap.isOpened():
                raise Exception("Cannot open source")
            self.is_running = True
            self.update_status(f"● ACTIVE - Source: {src}", "#00ff88")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open source: {src}")
            self.cap = None

    def open_video_file(self):
        """Open video file dialog"""
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        if filename:
            self.open_source(filename)

    def open_stream(self):
        """Open stream URL dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Stream URL")
        dialog.geometry("450x180")
        dialog.configure(bg="#1a1f3a")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Enter RTSP/HTTP Stream URL:",
                 bg="#1a1f3a", fg="#ffffff",
                 font=("Helvetica", 12, "bold")).pack(pady=20)

        url_entry = tk.Entry(dialog, width=50, font=("Helvetica", 11),
                             bg="#2d3561", fg="#ffffff", insertbackground="#ffffff")
        url_entry.pack(pady=10, ipady=5)

        def submit():
            url = url_entry.get().strip()
            if url:
                self.open_source(url)
                dialog.destroy()

        btn_frame = tk.Frame(dialog, bg="#1a1f3a")
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Connect", command=submit,
                  bg="#00d4ff", fg="#000000",
                  font=("Helvetica", 11, "bold"),
                  padx=30, pady=8, cursor="hand2",
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                  bg="#ff4757", fg="#ffffff",
                  font=("Helvetica", 11, "bold"),
                  padx=30, pady=8, cursor="hand2",
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

    def toggle_playback(self):
        """Toggle pause/play"""
        self.is_running = not self.is_running
        if self.is_running:
            self.play_btn.config(text="⏸️  PAUSE")
            self.update_status("● ACTIVE", "#00ff88")
        else:
            self.play_btn.config(text="▶️  PLAY")
            self.update_status("⏸️ PAUSED", "#ffd93d")

    def reset_stats(self):
        """Reset statistics"""
        self.total_detections = 0
        self.total_label.config(text="0")
        messagebox.showinfo("Reset", "Statistics have been reset!")

    def update_status(self, text, color):
        """Update status label"""
        self.status_label.config(text=text, fg=color)

    def update_frame(self):
        """Update video frame"""
        if self.cap and self.is_running:
            ret, frame = self.cap.read()

            if ret and self.model_loaded:
                self.current_frame = frame.copy()
                start_time = time.time()

                # Run detection
                self.confidence_threshold = self.conf_scale.get()
                results = self.model(frame, conf=self.confidence_threshold)

                self.detection_count = 0
                for r in results:
                    if hasattr(r, 'boxes'):
                        for box in r.boxes:
                            self.detection_count += 1
                            self.total_detections += 1

                            # Draw detection
                            xyxy = box.xyxy[0].cpu().numpy()
                            x1, y1, x2, y2 = map(int, xyxy)
                            conf = float(box.conf[0])

                            # Draw rectangle with thicker lines
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 4)

                            # Draw corner accents
                            corner_len = 30
                            cv2.line(frame, (x1, y1), (x1 + corner_len, y1), (0, 255, 0), 6)
                            cv2.line(frame, (x1, y1), (x1, y1 + corner_len), (0, 255, 0), 6)
                            cv2.line(frame, (x2, y1), (x2 - corner_len, y1), (0, 255, 0), 6)
                            cv2.line(frame, (x2, y1), (x2, y1 + corner_len), (0, 255, 0), 6)
                            cv2.line(frame, (x1, y2), (x1 + corner_len, y2), (0, 255, 0), 6)
                            cv2.line(frame, (x1, y2), (x1, y2 - corner_len), (0, 255, 0), 6)
                            cv2.line(frame, (x2, y2), (x2 - corner_len, y2), (0, 255, 0), 6)
                            cv2.line(frame, (x2, y2), (x2, y2 - corner_len), (0, 255, 0), 6)

                            # Draw label with better visibility
                            label = f"POTHOLE {conf:.2f}"
                            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                            cv2.rectangle(frame, (x1, y1 - 35), (x1 + w + 10, y1), (0, 255, 255), -1)
                            cv2.putText(frame, label, (x1 + 5, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

                # Calculate FPS
                self.fps = int(1 / (time.time() - start_time))

                # Update stats
                self.fps_label.config(text=str(self.fps))
                self.det_label.config(text=str(self.detection_count))
                self.total_label.config(text=str(self.total_detections))

                # Display frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)

                # Resize to fit canvas
                canvas_w = self.canvas.winfo_width()
                canvas_h = self.canvas.winfo_height()
                if canvas_w > 1 and canvas_h > 1:
                    img.thumbnail((canvas_w, canvas_h), Image.Resampling.LANCZOS)

                self.photo = ImageTk.PhotoImage(image=img)
                self.canvas.delete("all")
                self.canvas.create_image(canvas_w // 2, canvas_h // 2,
                                         image=self.photo, anchor=tk.CENTER)

        self.root.after(10, self.update_frame)

    def on_closing(self):
        """Cleanup on close"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PotholeDetectorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()