"""This module manages the GUI settings menu that appears when the program is first run."""

# C:\Users\alda_ik\Documents\04_PROGRAMMING\02_FINAL_PROJECT\gui.py

from tkinter import ttk
import tkinter as tk


def update_entry(variable: tk.StringVar, entry: tk.ttk.Entry) -> None:
    """Checks for the parsed state of a variable to enable
    or disable its text box.

    Args:
        variable (tk.StringVar): Container of the variable to check.
        entry (tk.ttk.Entry): Container of the value and its state.
    """
    if variable.get() == "Auto" or variable.get() == "Full":
        # If exposure is automatic, the button will be greyed-out
        entry.config(state="disabled")
    else:
        entry.config(state="normal")


def create_menu() -> (
    tuple[
        tk.StringVar,
        tk.StringVar,
        tk.StringVar,
        tk.StringVar,
        tk.StringVar,
        tk.StringVar,
        tk.StringVar,
        tk.StringVar,
        tk.StringVar,
        tk.StringVar,
        tk.Tk,
        tk.ttk.Entry,
        tk.ttk.Entry,
    ]
):
    """Creates the GUI menu to configure the initial settings:

    1. Creates the variables windows with an specific size and position.

    2. Creates varibales to store the inputs.

    3. Creates dropdown menus with default values.

    4. Defines a lambda function to parse the exposure and elevation varibales to update_time_entry().

    Returns:
        tuple: gain_var (tk.StringVar): Container of the gain mode (0 [0 dB] or 1 [18 dB]).

        check_var (tk.StringVar): Container of the streaming mode (Stream or Record).

        light_var (tk.StringVar): Container of the time of the day (Daytime or Nighttime).

        payload_var (tk.StringVar): Container of the payload used (None, KIODO, OsirisV1, Osiris4CubeSat,
        NORSAT-TD).

        zenith_var (tk.StringVar): Container of the zenith attenuation (Bad 1550nm [0.891], Good 1550nm [0.986],
        Bad 850nm [0.705], Good 850nm [0.950])

        elevation_var (tk.StringVar): Container of the elevation mode (Individual or Full).

        elevation_angle_var (tk.StringVar): Container of the elevation angle (if manual).

        exposure_var (tk.StringVar): Container of the exposure mode (Auto or Manual).

        exposure_time_var (tk.StringVar): Container of the exposure value (if manual).

        iso_var (tk.StringVar): Container of the main camera mode (Normal, Hot-pixel substraction, Subtraction,
        Camera's BC).

        root (tk.Tk): Main window of the GUI menu.

        exposure_time_entry (tk.ttk.Entry): Value of the exposure.

        elevation_angle_entry (tk.ttk.Entry): Value of the elevation.
    """
    root = tk.Tk()
    root.title("IR Camera for Satellite Tracking")
    # Dimensions and position of the settings menu (WidthxHeight+X+Y).
    root.geometry("370x320+900+5")

    # Variables
    gain_var = tk.StringVar(value="1")
    check_var = tk.StringVar(value="S")
    light_var = tk.StringVar(value="D")
    payload_var = tk.StringVar(value="")
    zenith_var = tk.StringVar(value="B_1")
    elevation_var = tk.StringVar(value="F")
    elevation_angle_var = tk.StringVar(value="")
    exposure_var = tk.StringVar(value="M")
    exposure_time_var = tk.StringVar(value="")
    iso_var = tk.StringVar(value="N")

    # Camera title
    ttk.Label(text="Camera settings", font=(14)).grid(
        row=0, column=0, pady=5, sticky=""
    )
    # LB title
    ttk.Label(text="LB Settings", font=(14)).grid(
        row=0, column=1, columnspan=1, pady=5
    )

    # Dropdown menus
    ttk.Label(text="Gain:").grid(row=1, column=0, sticky="")
    gain_combo = ttk.Combobox(
        textvariable=gain_var, values=["0 [0 dB]", "1 [18 dB]"]
    )
    gain_combo.grid(row=2, column=0)
    gain_combo.set("1 [18 dB]")

    ttk.Label(text="Payload:").grid(row=1, column=1, sticky="")
    payload_combo = ttk.Combobox(
        textvariable=payload_var,
        values=[
            "None",
            "KIODO",
            "OsirisV1",
            "Osiris4CubeSat",
            "NORSAT-TD",
        ],
    )
    payload_combo.grid(row=2, column=1)
    payload_combo.set("None")

    ttk.Label(text="Capture Mode:").grid(row=3, column=0, sticky="")
    check_combo = ttk.Combobox(
        textvariable=check_var, values=["Stream", "Record"]
    )
    check_combo.grid(row=4, column=0)
    check_combo.set("Stream")

    ttk.Label(text="Zenith-attenuation:").grid(row=3, column=1, sticky="")
    zenith_combo = ttk.Combobox(
        textvariable=zenith_var,
        values=[
            "Bad 1550nm [0.891]",
            "Good 1550nm [0.986]",
            "Bad 850nm [0.705]",
            "Good 850nm [0.950]",
        ],
    )
    zenith_combo.grid(row=4, column=1)
    zenith_combo.set("Bad 1550nm [0.891]")

    ttk.Label(text="Time of the day:").grid(row=5, column=0, sticky="")
    light_combo = ttk.Combobox(
        textvariable=light_var, values=["Daytime", "Nighttime"]
    )
    light_combo.grid(row=6, column=0)
    light_combo.set("Daytime")

    ttk.Label(text="Elevation:").grid(row=5, column=1, sticky="")
    elevation_combo = ttk.Combobox(
        textvariable=elevation_var, values=["Full", "Individual"]
    )
    elevation_combo.grid(row=6, column=1)
    elevation_combo.set("Full")

    ttk.Label(text="Elevation Angle (°):").grid(row=7, column=1, sticky="")
    elevation_angle_entry = ttk.Entry(textvariable=elevation_angle_var)
    elevation_angle_entry.grid(row=8, column=1)

    ttk.Label(text="Exposure:").grid(row=7, column=0, sticky="")
    exposure_combo = ttk.Combobox(
        textvariable=exposure_var, values=["Auto", "Manual"]
    )
    exposure_combo.grid(row=8, column=0)
    exposure_combo.set("Manual")

    ttk.Label(text="Exposure Time (µs):").grid(row=9, column=0, sticky="")
    exposure_time_entry = ttk.Entry(textvariable=exposure_time_var)
    exposure_time_entry.grid(row=10, column=0)

    ttk.Label(text="Tecnique Used:").grid(row=11, column=0, sticky="")
    iso_combo = ttk.Combobox(
        textvariable=iso_var,
        values=[
            "Normal",
            "Hot-pixel substraction",
            "Subtraction",
            "Camera's BC",
        ],
    )
    iso_combo.grid(row=12, column=0)
    iso_combo.set("Normal")

    # lambda to parse exposure and elevation states
    exposure_var.trace_add(
        "write",
        lambda *args: update_entry(exposure_var, exposure_time_entry),
    )

    elevation_var.trace_add(
        "write",
        lambda *args: update_entry(elevation_var, elevation_angle_entry),
    )

    return (
        gain_var,
        check_var,
        light_var,
        payload_var,
        zenith_var,
        elevation_var,
        elevation_angle_var,
        exposure_var,
        exposure_time_var,
        iso_var,
        root,
        exposure_time_entry,
        elevation_angle_entry,
    )
