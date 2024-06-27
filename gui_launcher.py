# gui_launcher.py
import subprocess
from tkinter import Tk, Button

def run_main_script():
    print("Launching main script...")  # Debug print
    result = subprocess.Popen(['python', 'main.py'])
    print("Main script launched.")  # Debug print
    result.wait()  # Wait for the process to complete
    print("Main script completed.")  # Debug print
    return result

def main():
    root = Tk()
    root.title("Book Inventory GUI Launcher")

    start_button = Button(root, text="Start Uploading", command=run_main_script)
    start_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
