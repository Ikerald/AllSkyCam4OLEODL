"""Main fuction of the project where everything is called.

Python version:     3.12.2.
Numpy version:      2.0.0.
Scipy version:      1.14.0.
Matplotlib version: 3.9.1.
Mplcursors version: 0.5.3.
Tkinter version:    0.1.0.
Pytz version:       2024.1.
OpenCV version:     4.10.0.84.


Author:
    Iker Aldasoro - 19.04.2024
"""

# C:\Users\alda_ik\Documents\04_PROGRAMMING\02_FINAL_PROJECT\constants.py

from tkinter import ttk
from datetime import datetime
from typing import Tuple
import time
import matplotlib.pyplot as plt
import os

import AllSkyCam4OLEODL


def create_graph(
    elevation_in, payload
) -> Tuple[plt.figure, plt.axes, plt.hlines, list, list]:
    """Creates the live graph displayed in the GUI:

    1. Creates the plot with an specific size, position, title and labels.

    2. If a payload with full elevation range has been chosen, the graph will be smaller to acomodate the link
    budget graph.

    3. Initializes the data for the graph.

    Args:
        elevation_in (tk.StringVar): Container of the elevation mode (Individual or Full).
        payload (tk.StringVar): Container of the payload used (None, KIODO, OsirisV1, Osiris4CubeSat, CubeCat).

    Returns:
        tuple[plt.figure, plt.axes, plt.hlines, list, list]: fig (plt.figure): Figure of the created plot.

        ax (plt.axes): Axes of the created plot.

        line (plt.hlines): Lines of the created plot.

        xdata (list): X-axis data from the created plot.

        ydata (list): Y-axis data from the created plot.
    """
    # Create figure and axis objects
    fig, ax = plt.subplots()
    if elevation_in.get() == "Full" and payload.get() != "None":
        # Size and position of the intensity graph.
        fig.set_size_inches(5.38, 3.3)
        fig.canvas.manager.window.wm_geometry("+5+290")
        fig.subplots_adjust(left=0.11, right=0.95, top=0.92, bottom=0.13)
    else:
        fig.set_size_inches(8.9, 3.3)
        fig.canvas.manager.window.wm_geometry("+5+290")
        fig.subplots_adjust(left=0.08, right=0.97, top=0.92, bottom=0.13)

    (line,) = ax.plot([], [], lw=2)

    ax.set_ylim(0, 255)
    ax.grid()
    if payload.get() != "None":
        ax.set_title(
            f"{payload.get()} downlink on {datetime.now().strftime('%Y-%m-%d')}"
        )
    else:
        ax.set_title(f"Downlink on {datetime.now().strftime('%Y-%m-%d')}")
    ax.set_xlabel("Time [UTC]")
    ax.set_ylabel("Brightness")

    # Initialize empty data
    xdata, ydata = [], []

    return fig, ax, line, xdata, ydata


def main():
    AllSkyCam4OLEODL.print_preamble()
    cam_id = AllSkyCam4OLEODL.parse_args()

    with AllSkyCam4OLEODL.VmbSystem.get_instance():
        with AllSkyCam4OLEODL.get_camera(cam_id) as cam:
            AllSkyCam4OLEODL.print_preamble_settings()

            (
                gain_in,
                check_in,
                light_in,
                payload_in,
                h_ogs_in,
                zenith_in,
                elevation_in,
                elevation_angle_in,
                exposure_in,
                exposure_time_in,
                iso_in,
                root,
                exposure_time_entry,
                elevation_angle_entry,
            ) = AllSkyCam4OLEODL.create_menu()

            def start_streaming():
                # Validate inputs
                (
                    elevation_angle,
                    exposure_time_value,
                    zenith,
                    h_ogs,
                ) = AllSkyCam4OLEODL.checks(
                    elevation_in,
                    elevation_angle_in,
                    exposure_in,
                    exposure_time_in,
                    zenith_in,
                    h_ogs_in,
                )

                if payload_in.get() != "None":
                    AllSkyCam4OLEODL.link_budget(
                        elevation_in, elevation_angle, payload_in, zenith, h_ogs
                    )

                # Setup camera
                AllSkyCam4OLEODL.upload_lut(
                    cam, AllSkyCam4OLEODL.LUT_INDEX, gain_in
                )
                AllSkyCam4OLEODL.setup_camera(
                    cam, gain_in, exposure_in, exposure_time_value, iso_in
                )
                AllSkyCam4OLEODL.setup_pixel_format(cam)
                AllSkyCam4OLEODL.grab_frame(cam)
                AllSkyCam4OLEODL.print_start_stream()

                # Create graph
                fig, ax, line, xdata, ydata = create_graph(
                    elevation_in, payload_in
                )
                # plt.show(block=False)  # Show the plot window without blocking

                handler = AllSkyCam4OLEODL.Handler(
                    cam,
                    exposure_time_value,
                    check_in,
                    light_in,
                    gain_in,
                    iso_in,
                    payload_in,
                    elevation_in,
                    fig,
                    ax,
                    line,
                    xdata,
                    ydata,
                )
                handler.create_camera_control_slider(root)
                plt.ion()  # Turn on interactive mode
                plt.show()

                try:
                    cam.start_streaming(handler=handler, buffer_count=10)
                    while not handler.shutdown_event.is_set():
                        root.update()
                        time.sleep(
                            0.01
                        )  # Small delay to prevent high CPU usage
                finally:
                    cam.stop_streaming()
                    AllSkyCam4OLEODL.print_end_stream()
                    handler.save_plot()  # Save the plot when streaming stops
                    root.quit()
                    root.destroy()
                    if os.path.isfile(AllSkyCam4OLEODL.BACKGROUND_FRAME_DIR):
                        os.remove(AllSkyCam4OLEODL.BACKGROUND_FRAME_DIR)

            start_button = ttk.Button(
                root, text="Start Capture", command=start_streaming, width=60
            )
            # start_button.grid(row=13, column=0, columnspan=2, pady=10)
            start_button.grid(
                row=13, column=0, columnspan=2, pady=10, sticky=""
            )

            # Initial call to set the correct state of the exposure and elevation
            AllSkyCam4OLEODL.update_entry(exposure_in, exposure_time_entry)
            AllSkyCam4OLEODL.update_entry(elevation_in, elevation_angle_entry)

            root.mainloop()


if __name__ == "__main__":
    main()
