import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
from src.WebDriverUtils import LOGGER

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TV Channel Scraper")
        self.root.geometry("400x500")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Mode selection
        ttk.Label(main_frame, text="WebDriver Mode:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mode_var = tk.StringVar(value="headless")
        ttk.Radiobutton(main_frame, text="Headless", variable=self.mode_var, value="headless").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="GUI", variable=self.mode_var, value="gui").grid(row=0, column=2, sticky=tk.W)
        
        # Output format selection
        ttk.Label(main_frame, text="Output Format:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar(value="excel")
        ttk.Radiobutton(main_frame, text="Excel", variable=self.output_var, value="excel").grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="CSV", variable=self.output_var, value="csv").grid(row=1, column=2, sticky=tk.W)
        
        # Provider selection
        ttk.Label(main_frame, text="Select Providers:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Create a frame for checkboxes
        checkbox_frame = ttk.Frame(main_frame)
        checkbox_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Provider checkboxes
        self.provider_vars = {}
        providers = [
            "DirecTV", "DirecTV Stream", "DishTV", 
            "FuboTV", "SlingTV", "HuluTV", "YouTubeTV"
        ]
        for i, provider in enumerate(providers):
            var = tk.BooleanVar(value=True)
            self.provider_vars[provider.lower().replace(" ", "")] = var
            ttk.Checkbutton(checkbox_frame, text=provider, variable=var).grid(
                row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2
            )
        
        # Select All button
        ttk.Button(main_frame, text="Select All", command=self.select_all).grid(row=4, column=0, pady=10)
        ttk.Button(main_frame, text="Deselect All", command=self.deselect_all).grid(row=4, column=1, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, length=300, mode='indeterminate', variable=self.progress_var)
        self.progress.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status = ttk.Label(main_frame, textvariable=self.status_var)
        self.status.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Run button
        self.run_button = ttk.Button(main_frame, text="Run Scraper", command=self.run_scraper)
        self.run_button.grid(row=7, column=0, columnspan=3, pady=10)
        
    def select_all(self):
        for var in self.provider_vars.values():
            var.set(True)
            
    def deselect_all(self):
        for var in self.provider_vars.values():
            var.set(False)
            
    def run_scraper(self):
        # Get selected providers
        selected_providers = [
            provider for provider, var in self.provider_vars.items()
            if var.get()
        ]
        
        if not selected_providers:
            messagebox.showwarning("Warning", "Please select at least one provider")
            return
            
        # Disable run button and show progress
        self.run_button.state(['disabled'])
        self.progress.start()
        self.status_var.set("Running...")
        
        # Run scraper in a separate thread
        thread = threading.Thread(target=self._run_scraper_thread, args=(selected_providers,))
        thread.daemon = True
        thread.start()
        
    def _run_scraper_thread(self, providers):
        try:
            # Build command
            cmd = ['python', 'TV_Webscraping.py', 
                  '--mode', self.mode_var.get(),
                  '--output', self.output_var.get()]
            
            if providers:
                cmd.extend(['--providers'] + providers)
                
            # Run scraper
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            # Check result
            if process.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Scraping completed successfully!"))
            else:
                error_msg = process.stderr or "Unknown error occurred"
                self.root.after(0, lambda: messagebox.showerror("Error", f"Scraping failed:\n{error_msg}"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error running scraper:\n{str(e)}"))
            
        finally:
            # Reset UI
            self.root.after(0, self._reset_ui)
            
    def _reset_ui(self):
        self.progress.stop()
        self.status_var.set("Ready")
        self.run_button.state(['!disabled'])

def main():
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 