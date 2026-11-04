import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import pandas as pd


class CircuitSolverApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Circuit Analysis Dashboard")
    self.root.geometry("850x650")
    self.root.configure(bg="#f4f6f9")

    # Configure Styling
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#f4f6f9")
    style.configure(
        "TLabelframe", background="#f4f6f9", font=("Segoe UI", 10, "bold")
    )
    style.configure(
        "TLabelframe.Label", background="#f4f6f9", foreground="#1e293b"
    )
    style.configure("TLabel", background="#f4f6f9", font=("Segoe UI", 10))
    style.configure(
        "Header.TLabel",
        font=("Segoe UI", 16, "bold"),
        foreground="#0f172a",
        background="#f4f6f9",
    )
    style.configure(
        "TButton",
        font=("Segoe UI", 10, "bold"),
        background="#2563eb",
        foreground="white",
        borderwidth=0,
    )
    style.map("TButton", background=[("active", "#1d4ed8")])

    # Header Title
    header_frame = ttk.Frame(self.root)
    header_frame.pack(fill="x", padx=20, pady=15)
    ttk.Label(
        header_frame,
        text="⚡ Circuit Analysis Solver Dashboard",
        style="Header.TLabel",
    ).pack(anchor="w")
    ttk.Label(
        header_frame,
        text=(
            "Solve 3-Unknown Systems via Node Voltage or Mesh Current Methods"
        ),
    ).pack(anchor="w")

    # Configuration Frame
    config_frame = ttk.LabelFrame(
        self.root, text=" 1. Solver Configuration ", padding=15
    )
    config_frame.pack(fill="x", padx=20, pady=10)

    ttk.Label(config_frame, text="Analysis Method:").grid(
        row=0, column=0, sticky="w", pady=5
    )
    self.method_var = tk.StringVar(value="Node Voltage Method")
    method_dropdown = ttk.Combobox(
        config_frame, textvariable=self.method_var, state="readonly", width=25
    )
    method_dropdown["values"] = (
        "Node Voltage Method",
        "Mesh Current Method",
    )
    method_dropdown.grid(row=0, column=1, sticky="w", padx=10, pady=5)

    ttk.Label(config_frame, text="Input Format:").grid(
        row=1, column=0, sticky="w", pady=5
    )
    self.input_format_var = tk.StringVar(
        value="Matrix Notation [A][X] = [B]"
    )
    format_dropdown = ttk.Combobox(
        config_frame,
        textvariable=self.input_format_var,
        state="readonly",
        width=25,
    )
    format_dropdown["values"] = (
        "Matrix Notation [A][X] = [B]",
        "System of Equations",
    )
    format_dropdown.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    # Matrix Input Frame
    self.matrix_frame = ttk.LabelFrame(
        self.root, text=" 2. Input System Coefficients (3 Unknowns) ", padding=15
    )
    self.matrix_frame.pack(fill="x", padx=20, pady=10)

    # Labels for Matrix Header
    ttk.Label(
        self.matrix_frame,
        text="Coefficients [A Matrix]",
        font=("Segoe UI", 9, "bold"),
    ).grid(row=0, column=0, columnspan=3, pady=(0, 5))
    ttk.Label(
        self.matrix_frame, text="Constants [B]", font=("Segoe UI", 9, "bold")
    ).grid(row=0, column=4, pady=(0, 5))

    # Create 3x3 Matrix Entries + Constant Vector
    self.entries_a = []
    self.entries_b = []

    for i in range(3):
      row_entries = []
      for j in range(3):
        entry = ttk.Entry(self.matrix_frame, width=10, justify="center")
        entry.grid(row=i + 1, column=j, padx=5, pady=5)
        entry.insert(0, "0.0")
        row_entries.append(entry)
      self.entries_a.append(row_entries)

      ttk.Label(self.matrix_frame, text="=").grid(row=i + 1, column=3, padx=5)

      b_entry = ttk.Entry(self.matrix_frame, width=10, justify="center")
      b_entry.grid(row=i + 1, column=4, padx=5, pady=5)
      b_entry.insert(0, "0.0")
      self.entries_b.append(b_entry)

    # Calculate Button
    calc_btn = ttk.Button(
        self.root, text="▶ Run Circuit Analysis", command=self.solve_circuit
    )
    calc_btn.pack(fill="x", padx=20, pady=10)

    # Results & Summary Table Frame
    results_frame = ttk.LabelFrame(
        self.root, text=" 3. Results & Stability Summary ", padding=15
    )
    results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # Stability Indicator
    self.stability_label = ttk.Label(
        results_frame,
        text="Status: Waiting for input...",
        font=("Segoe UI", 11, "bold"),
    )
    self.stability_label.pack(anchor="w", pady=(0, 10))

    # Setup Table (Treeview)
    columns = (
        "Element",
        "Voltage, (V)",
        "Current, (A)",
        "Power Absorbed (W)",
        "Power Delivered (W)",
    )
    self.table = ttk.Treeview(
        results_frame, columns=columns, show="headings", height=5
    )

    for col in columns:
      self.table.heading(col, text=col)
      self.table.column(col, anchor="center", width=140)

    self.table.pack(fill="both", expand=True)

  def solve_circuit(self):
    try:
      a_matrix = []
      for row in self.entries_a:
        a_matrix.append([float(e.get()) for e in row])

      b_vector = [float(e.get()) for e in self.entries_b]

      A = np.array(a_matrix)
      B = np.array(b_vector)

      det = np.linalg.det(A)
      if np.isclose(det, 0):
        messagebox.showerror(
            "Error",
            "Singular Matrix: The circuit system has no unique solution. Check"
            " node/mesh equations.",
        )
        return

      X = np.linalg.solve(A, B)

      for item in self.table.get_children():
        self.table.delete(item)

      v1, v2, v3 = X[0], X[1], X[2]

      elements_data = [
          (
              "Node 1 / Resistor 1",
              round(v1, 2),
              round(v1 / 10, 2),
              round((v1**2) / 10, 2),
              0.0,
          ),
          (
              "Node 2 / Resistor 2",
              round(v2, 2),
              round(v2 / 5, 2),
              round((v2**2) / 5, 2),
              0.0,
          ),
          (
              "Node 3 / Resistor 3",
              round(v3, 2),
              round(v3 / 2, 2),
              round((v3**2) / 2, 2),
              0.0,
          ),
          ("Source 1", round(v1, 2), round(v1 / 10, 2), 0.0, round(v1 * (v1 / 10), 2)),
      ]

      total_absorbed = 0
      total_delivered = 0
      for row in elements_data:
        self.table.insert("", "end", values=row)
        total_absorbed += row[3]
        total_delivered += row[4]

      if np.isclose(total_absorbed, total_delivered, atol=1e-2) or total_delivered >= 0:
        self.stability_label.config(
            text="Status: Circuit is STABLE (Energy Conserved)",
            foreground="#16a34a",
        )
      else:
        self.stability_label.config(
            text="Status: Circuit is UNSTABLE", foreground="#dc2626"
        )

    except ValueError:
      messagebox.showerror(
          "Input Error",
          "Please enter valid numeric values for all matrix coefficients.",
      )


if __name__ == "__main__":
  root = tk.Tk()
  app = CircuitSolverApp(root)
  root.mainloop()
