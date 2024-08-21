"""This script manages all the printing functions needed to display the results correctly."""

# C:\Users\alda_ik\Documents\04_PROGRAMMING\02_FINAL_PROJECT\constants.py


def print_preamble() -> None:
    """Printing fuction - prints program preamble."""
    print("///////////////////////////////////////////////////")
    print("/// IR Camera System for Satellite Observation ///")
    print("///////////////////////////////////////////////////\n")


def print_preamble_settings() -> None:
    """Printing fuction - prints settings preamble."""
    print("//////////////////// Settings ////////////////////")


def print_start_stream() -> None:
    """Printing fuction - prints the start of the stream."""
    print()
    print("/// Stream started. Press <q> to stop stream ///")


def print_end_stream() -> None:
    """Printing fuction - prints the end of the stream."""
    print("/////////////////// Stream ended ///////////////////")
    print("///////////////////////////////////////////////////\n")


def print_usage() -> None:
    """Printing fuction - prints the usage."""
    print("Usage:")
    print("    python asynchronous_grab_opencv.py [camera_id]")
    print("    python asynchronous_grab_opencv.py [/h] [-h]")
    print()
    print("Parameters:")
    print(
        "    camera_id   ID of the camera to use (using first camera if not specified)"
    )
    print()
