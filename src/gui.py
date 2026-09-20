import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess

class InvoiceBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("בוט ריכוז חשבוניות - D-Dialog")
        self.root.geometry("520x550")
        self.root.resizable(True, True)
        
        # Configure Font
        self.root.option_add('*font', ('Segoe UI', 10))
        
        # Theme styling
        style = ttk.Style()
        style.theme_use('vista') # Standard Windows look
        
        # Frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(
            main_frame, 
            text="בוט ניהול וריכוז חשבוניות D-Dialog", 
            font=('Segoe UI', 14, 'bold'),
            foreground="#1a73e8"
        )
        header_label.pack(pady=(0, 20))
        
        # Mode Selection Frame
        mode_frame = ttk.LabelFrame(main_frame, text=" בחר אפשרות הרצה ", padding="12")
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.run_mode = tk.IntVar(value=1)
        
        self.r1 = ttk.Radiobutton(mode_frame, text="הרץ עבור חודש קודם (אוטומטי)", variable=self.run_mode, value=1, command=self.toggle_inputs)
        self.r1.pack(anchor=tk.W, pady=3)
        
        self.r2 = ttk.Radiobutton(mode_frame, text="הרץ עבור החודש הנוכחי", variable=self.run_mode, value=2, command=self.toggle_inputs)
        self.r2.pack(anchor=tk.W, pady=3)
        
        self.r3 = ttk.Radiobutton(mode_frame, text="הזן חודש ושנה באופן ידני", variable=self.run_mode, value=3, command=self.toggle_inputs)
        self.r3.pack(anchor=tk.W, pady=3)
        
        # Manual Inputs Frame
        self.inputs_frame = ttk.Frame(mode_frame)
        self.inputs_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(self.inputs_frame, text="חודש (1-12):").grid(row=0, column=0, padx=5, pady=2)
        self.month_entry = ttk.Entry(self.inputs_frame, width=6)
        self.month_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(self.inputs_frame, text="שנה (לדוגמה 2026):").grid(row=0, column=2, padx=5, pady=2)
        self.year_entry = ttk.Entry(self.inputs_frame, width=10)
        self.year_entry.grid(row=0, column=3, padx=5, pady=2)
        
        self.toggle_inputs()
        
        # Progress Log Frame
        log_frame = ttk.LabelFrame(main_frame, text=" סטטוס והתקדמות ", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, font=('Consolas', 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text['yscrollcommand'] = scrollbar.set
        
        # Configure RTL text justification
        self.log_text.tag_configure('rtl', justify='right')
        
        # Buttons Frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Run Invoices Button
        self.run_btn = ttk.Button(btn_frame, text="📁 בוט חשבוניות", command=self.start_bot_thread)
        self.run_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        
        # Run Summarizer Button
        self.summarize_btn = ttk.Button(btn_frame, text="🎙️ סכם הקלטה מקומית", command=self.start_summarizer_thread)
        self.summarize_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
        
        # Sync Drive Button
        self.sync_drive_btn = ttk.Button(btn_frame, text="☁️ סנכרן מ-Drive", command=self.start_drive_sync_thread)
        self.sync_drive_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))
        
    def toggle_inputs(self):
        if self.run_mode.get() == 3:
            for child in self.inputs_frame.winfo_children():
                child.configure(state='normal')
        else:
            for child in self.inputs_frame.winfo_children():
                child.configure(state='disabled')
                
    def write_log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        
    def start_bot_thread(self):
        self.run_btn.configure(state='disabled')
        self.log_text.delete("1.0", tk.END)
        self.write_log("מתחיל ריצת בוט...")
        
        threading.Thread(target=self.run_bot, daemon=True).start()
        
    def run_bot(self):
        mode = self.run_mode.get()
        cmd = [sys.executable, "main.py"]
        
        if mode == 2:
            import datetime
            now = datetime.datetime.now()
            cmd += ["--month", str(now.month), "--year", str(now.year)]
        elif mode == 3:
            m = self.month_entry.get().strip()
            y = self.year_entry.get().strip()
            if not m or not y:
                messagebox.showerror("שגיאה", "אנא הזן חודש ושנה תקינים.")
                self.root.after(0, lambda: self.run_btn.configure(state='normal'))
                return
            cmd += ["--month", m, "--year", y]
            
        try:
            # Set python to output in UTF-8 to prevent replacement characters in GUI log
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            # Run main.py headlessly and capture standard output
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW # Keeps cmd terminal hidden
            )
            
            for line in iter(process.stdout.readline, ''):
                self.root.after(0, self.write_log, line.strip())
                
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                self.root.after(0, lambda: messagebox.showinfo("הצלחה", "סריקת החשבוניות הושלמה בהצלחה!"))
            else:
                self.root.after(0, lambda: messagebox.showerror("שגיאה", "הריצה נכשלה. בדוק את הפירוט בחלון הסטטוס."))
                
        except Exception as e:
            self.root.after(0, self.write_log, f"שגיאה בהפעלת הבוט: {e}")
            
        self.root.after(0, lambda: self.run_btn.configure(state='normal'))
        self.root.after(0, lambda: self.summarize_btn.configure(state='normal'))

    def start_summarizer_thread(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="בחר קובץ הקלטה לסיכום פגישה",
            filetypes=[
                ("קובצי שמע ווידאו", "*.m4a;*.mp3;*.wav;*.aac;*.ogg;*.flac;*.mp4;*.webm;*.mov"),
                ("קובצי שמע (m4a, mp3, wav)", "*.m4a;*.mp3;*.wav;*.aac;*.ogg"),
                ("כל הקבצים", "*.*")
            ]
        )
        if not file_path:
            return
            
        self.run_btn.configure(state='disabled')
        self.summarize_btn.configure(state='disabled')
        self.log_text.delete("1.0", tk.END)
        self.write_log(f"מתחיל תהליך סיכום עבור הקובץ: {os.path.basename(file_path)}...")
        
        threading.Thread(target=self.run_summarizer, args=(file_path,), daemon=True).start()

    def run_summarizer(self, file_path):
        try:
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            cmd = [sys.executable, "meeting_summarizer.py", file_path]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            for line in iter(process.stdout.readline, ''):
                self.root.after(0, self.write_log, line.strip())
                
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                self.root.after(0, lambda: messagebox.showinfo("הצלחה", "סיכום הפגישה הופק ונפתח בדפדפן!"))
            else:
                self.root.after(0, lambda: messagebox.showerror("שגיאה", "הסיכום נכשל. בדוק את הפירוט ביומן."))
        except Exception as e:
            self.root.after(0, self.write_log, f"שגיאה בסיכום הפגישה: {e}")
            
        self.root.after(0, lambda: self.run_btn.configure(state='normal'))
        self.root.after(0, lambda: self.summarize_btn.configure(state='normal'))
        self.root.after(0, lambda: self.sync_drive_btn.configure(state='normal'))

    def start_drive_sync_thread(self):
        self.run_btn.configure(state='disabled')
        self.summarize_btn.configure(state='disabled')
        self.sync_drive_btn.configure(state='disabled')
        self.log_text.delete("1.0", tk.END)
        self.write_log("בודק הקלטות חדשות ב-Google Drive ומסנכרן...")
        
        threading.Thread(target=self.run_drive_sync, daemon=True).start()

    def run_drive_sync(self):
        try:
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            cmd = [sys.executable, "drive_meeting_sync.py"]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            for line in iter(process.stdout.readline, ''):
                self.root.after(0, self.write_log, line.strip())
                
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                self.root.after(0, lambda: messagebox.showinfo("הצלחה", "סנכרון ההקלטות מ-Drive הושלם!"))
            else:
                self.root.after(0, lambda: messagebox.showerror("שגיאה", "הסנכרון נכשל. בדוק את הפירוט ביומן."))
        except Exception as e:
            self.root.after(0, self.write_log, f"שגיאה בסנכרון Drive: {e}")
            
        self.root.after(0, lambda: self.run_btn.configure(state='normal'))
        self.root.after(0, lambda: self.summarize_btn.configure(state='normal'))
        self.root.after(0, lambda: self.sync_drive_btn.configure(state='normal'))

if __name__ == "__main__":
    # Ensure working directory is set to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    root = tk.Tk()
    app = InvoiceBotGUI(root)
    root.mainloop()
