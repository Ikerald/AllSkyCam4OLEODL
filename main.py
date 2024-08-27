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
import time
import matplotlib.pyplot as plt
import os

import AllSkyCam4OLEODL


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
                    el_lb, int_lb = AllSkyCam4OLEODL.link_budget(
                        elevation_in, elevation_angle, payload_in, zenith, h_ogs
                    )
                else:
                    el_lb = 0
                    int_lb = 0

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
                fig, ax, line, xdata, ydata = AllSkyCam4OLEODL.create_graph(
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
                    el_lb,
                    int_lb,
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
