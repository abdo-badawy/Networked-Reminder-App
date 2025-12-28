import tkinter as tk
from tkinter import messagebox
import threading
import socket
import time

class Reminder:
    def __init__(self, task, time_):
        self.task = task
        self.time = time_
        self.done = False

class NetworkClient:
    @staticmethod
    def sync(task, time_, port):
        def _send():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect(('127.0.0.1', port))
                s.send(f"{task}|{time_}".encode())
                s.close()
            except:
                print("[NETWORK] Server is offline, but reminder saved locally.")
        threading.Thread(target=_send, daemon=True).start()

class ReminderManager:
    def __init__(self, root):
        self.root = root
        self.reminders = []
        self.observers = []

    def add_reminder(self, r): self.reminders.append(r)
    def attach(self, callback): self.observers.append(callback)

    def notify(self, reminder):
        for cb in self.observers:
            self.root.after(0, lambda r=reminder, c=cb: c(r))

    def start_checking(self):
        def _loop():
            while True:
                now = time.strftime("%H:%M")
                for r in self.reminders:
                    if r.time == now and not r.done:
                        r.done = True
                        self.notify(r)
                time.sleep(15)
        threading.Thread(target=_loop, daemon=True).start()

class ReminderApp:
    def __init__(self, root, port):
        self.root = root
        self.port = port 
        self.root.title(f"Reminder App (Port: {port})")
        
        self.manager = ReminderManager(root)
        self.manager.attach(self.show_alert)
        self.manager.start_checking()

    
        tk.Label(root, text="Task:").pack(pady=2)
        self.task_entry = tk.Entry(root)
        self.task_entry.pack(pady=2)
        tk.Label(root, text="Time (HH:MM):").pack(pady=2)
        self.time_entry = tk.Entry(root)
        self.time_entry.pack(pady=2)
        tk.Button(root, text="Add & Sync", command=self.add_item, bg="green", fg="white").pack(pady=10)
        self.listbox = tk.Listbox(root, width=40)
        self.listbox.pack(pady=5)

    def show_alert(self, r):
        messagebox.showinfo("Reminder", f"Time for: {r.task}")

    def add_item(self):
        task, t_str = self.task_entry.get(), self.time_entry.get()
        try:
            time.strptime(t_str, "%H:%M")
            r = Reminder(task, t_str)
            self.manager.add_reminder(r)
            self.listbox.insert(tk.END, f"[{t_str}] {task}")
            
            
            NetworkClient.sync(task, t_str, self.port)
            
            self.task_entry.delete(0, tk.END)
            self.time_entry.delete(0, tk.END)
        except:
            messagebox.showerror("Error", "Format: HH:MM")

if __name__ == "__main__":
    
    CURRENT_PORT = 14253
    
    root = tk.Tk()
    app = ReminderApp(root, CURRENT_PORT)
    root.mainloop()