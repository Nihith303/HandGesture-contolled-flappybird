import tkinter as tk
from tkinter import ttk, messagebox
from db_operations import db

class PatientForm:
    def __init__(self, on_submit):
        self.root = tk.Tk()
        self.root.title("Patient Information")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.on_submit = on_submit
        
        # Center the window
        window_width = 400
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_label = ttk.Label(
            self.root, 
            text="Patient Login", 
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=10)
        
        # Frame for radio buttons
        radio_frame = ttk.LabelFrame(self.root, text="Select Patient Type")
        radio_frame.pack(pady=10, padx=20, fill='x')
        
        # Radio buttons for patient type
        self.patient_type = tk.StringVar(value='existing')
        ttk.Radiobutton(
            radio_frame, 
            text="Existing Patient", 
            variable=self.patient_type, 
            value='existing',
            command=self.toggle_fields
        ).pack(anchor='w', pady=5, padx=10)
        
        ttk.Radiobutton(
            radio_frame, 
            text="New Patient", 
            variable=self.patient_type, 
            value='new',
            command=self.toggle_fields
        ).pack(anchor='w', pady=5, padx=10)
        
        # Frame for form
        self.form_frame = ttk.LabelFrame(self.root, text="Patient Information")
        self.form_frame.pack(pady=10, padx=20, fill='x')
        
        # Patient Name (initially hidden)
        self.name_label = ttk.Label(self.form_frame, text="Patient Name:")
        self.name_label.grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.form_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        
        # Patient ID
        ttk.Label(self.form_frame, text="Patient ID:").grid(row=1, column=0, sticky='w', pady=5)
        self.id_var = tk.StringVar()
        self.id_entry = ttk.Entry(self.form_frame, textvariable=self.id_var, width=30)
        self.id_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        self.id_entry.focus()
        
        # Error message
        self.error_var = tk.StringVar()
        error_label = ttk.Label(
            self.root, 
            textvariable=self.error_var, 
            foreground='red',
            wraplength=350
        )
        error_label.pack(pady=5)
        
        # Submit button
        submit_btn = ttk.Button(
            self.root, 
            text="Start Game", 
            command=self.submit,
            style='Accent.TButton'
        )
        submit_btn.pack(pady=10)
        
        # Configure style
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 10))
        
        # Bind Enter key to submit
        self.root.bind('<Return>', lambda e: self.submit())
        
        # Initialize fields based on default selection
        self.toggle_fields()
    
    def show(self):
        self.root.mainloop()
    
    def toggle_fields(self):
        """Show/hide name field based on patient type"""
        if self.patient_type.get() == 'new':
            self.name_label.grid()
            self.name_entry.grid()
            self.form_frame['text'] = "New Patient Information"
        else:
            self.name_label.grid_remove()
            self.name_entry.grid_remove()
            self.form_frame['text'] = "Existing Patient Information"
    
    def validate_patient_exists(self, patient_id):
        """Check if patient exists in the database"""
        try:
            stats = db.get_patient_stats(patient_id)
            return stats is not None
        except Exception as e:
            print(f"Error checking patient: {e}")
            return False
    
    def submit(self):
        patient_type = self.patient_type.get()
        patient_id = self.id_var.get().strip()
        
        if not patient_id:
            self.error_var.set("Please enter a Patient ID")
            return
            
        if patient_type == 'new':
            name = self.name_var.get().strip()
            if not name:
                self.error_var.set("Please enter a name for the new patient")
                return
                
            # Check if patient ID already exists
            if self.validate_patient_exists(patient_id):
                self.error_var.set(f"Patient ID {patient_id} already exists. Please use a different ID or select 'Existing Patient'.")
                return
                
            # Add new patient to database
            if not db.add_patient(name, patient_id):
                self.error_var.set("Error creating new patient. Please try again.")
                return
                
        else:  # Existing patient
            if not self.validate_patient_exists(patient_id):
                self.error_var.set(f"No patient found with ID: {patient_id}")
                return
            
            # Get patient name from database
            stats = db.get_patient_stats(patient_id)
            name = stats.get('name', 'Player')
        
        # Start a new session
        if db.start_session(patient_id):
            self.root.destroy()
            self.on_submit(name, patient_id)
        else:
            self.error_var.set("Error starting game session. Please try again.")

def get_patient_info(on_submit):
    form = PatientForm(on_submit)
    form.show()

if __name__ == "__main__":
    def test_callback(name, patient_id):
        print(f"Starting game for {name} (ID: {patient_id})")
    
    get_patient_info(test_callback)
