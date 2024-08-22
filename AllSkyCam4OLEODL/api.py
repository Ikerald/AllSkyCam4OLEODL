"""This module contains the API of the Allied Vision Goldeye Camera.

It has been modified in order to allow both streaming and recording. It allows processing of the
frames without the need of writting them first.
"""

# C:\Users\alda_ik\Documents\04_PROGRAMMING\02_FINAL_PROJECT\api.py

from vmbpy import *  # noqa: F403

from typing import Optional
from datetime import datetime, timedelta
from tkinter import ttk
from matplotlib import dates as mdates
from matplotlib.dates import DateFormatter, HourLocator
import sys
import os
import threading
import cv2
import math
import pytz
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from . import image_processing as im
from . import constants as const
from . import printer as pri

# All frames will either be recorded in this format, or transformed to it before being displayed
opencv_display_format = PixelFormat.Bgr8  # noqa: F405


def feature_changed_handler(feature) -> None:
    """API propietary printing fuction to indicate a changed of value of a feature.

    Args:
        feature (_type_): Feature to be changed.
    """
    msg = "Feature '{}' changed value to '{}'"
    print(msg.format(str(feature.get_name()), str(feature.get())), flush=True)


def abort(reason: str, return_code: int = 1, usage: bool = False) -> None:
    """API propietary exiting fuction and indicate an error.

    Args:
        reason (str): Reason to abort operation.
        return_code (int, optional): Error code raised. Defaults to 1.
        usage (bool, optional): Bool to check if an argument has been parsed. Defaults to False.
    """
    print(reason + "\n")

    if usage:
        pri.print_usage()

    sys.exit(return_code)


def parse_args() -> Optional[str]:
    """API propietary fuction to parse an argument.

    Returns:
        Optional[str]: Parsed argument.
    """
    args = sys.argv[1:]
    argc = len(args)

    for arg in args:
        if arg in ("/h", "-h"):
            pri.print_usage()
            sys.exit(0)

    if argc > 1:
        abort(
            reason="Invalid number of arguments. Abort.",
            return_code=2,
            usage=True,
        )

    return None if argc == 0 else args[0]


def get_camera(camera_id: Optional[str]) -> Camera:  # noqa: F405
    """API propietary fuction to obtain the camera.

    Args:
        camera_id (Optional[str]): Specific camera we want to connect to.

    Returns:
        Camera: Camera we have connected to.
    """
    with VmbSystem.get_instance() as vmb:  # noqa: F405
        # ip = vmb.GevDeviceForceIPAddress.get()
        if camera_id:
            try:
                return vmb.get_camera_by_id(camera_id)

            except VmbCameraError:  # noqa: F405
                abort("Failed to access Camera '{}'. Abort.".format(camera_id))

        else:
            cams = vmb.get_all_cameras()
            if not cams:
                abort("No Cameras accessible. Abort.")

            return cams[0]


def setup_camera(
    cam: Camera,  # noqa: F405
    gain: tk.StringVar,
    exposure: tk.StringVar,
    exposure_time_value: int,
    iso: tk.StringVar,
) -> None:
    """Configures the camera based on user inputs:

    1. Checks camera mode, if the own camera's background is chosen, it needs be enabled.

    2. Sets the gain mode, either 0dB or 18dB.

    3. Selects the exposure mode, Auto or Manual. If Manual, sets the exposure value.

    4. Enables white balancing if camera supports it.

    5. Adjusts GeV packet size (just for PoE camera).

    Args:
        cam (Camera): Camera object from the VMBPY API module.
        gain (tk.StringVar): Container of the gain mode (0 [0 dB] or 1 [18 dB]).
        exposure (tk.StringVar): Container of the exposure mode (Manual or Auto).
        exposure_time_value (int): Specified exposure value for Manual mode.
        iso (tk.StringVar): Container of the camera mode: Normal, Hot-pixel substraction, Subtraction or Camera's BC.
    """
    with cam:
        # print(cam.LUTEnable)
        # lut = cam.LUTEnable.get()
        # print(cam.LUTEnable.get())
        # # lut = True
        # lut = True
        # print(cam.LUTEnable)
        # print(lut)
        # cam.LUTEnable.set(lut)
        # print(cam.LUTEnable)
        # print(cam.LUTEnable)
        # cam.LUTEnable.value(True)
        # print(cam.LUTEnable)

        # Default settings
        cam.BCMode.set("Off")
        cam.IntegrationMode.set("IntegrateWhileRead")
        # cam.IntegrationMode.set("IntegrateThenRead")
        print(cam.IntegrationMode)

        # Background Correction settings
        if iso.get() == "Camera's BC":
            cam.BCMode.set("On")
            cam.BCIntegrationStart.run()
        print(cam.BCMode)

        # lut_enable = cam.LUTEnable
        # print(lut_enable)
        # lut_enable.set(True)
        # print(lut_enable)

        # Gain settings
        if gain.get() == "1 [18 dB]":
            try:
                cam.SensorGain.set("Gain1")
            except (AttributeError, VmbFeatureError):  # noqa: F405
                pass
        else:
            try:
                cam.SensorGain.set("Gain0")
            except (AttributeError, VmbFeatureError):  # noqa: F405
                pass
        print(cam.SensorGain)

        # Exposure settings
        if exposure.get() == "Manual":
            try:
                cam.ExposureAuto.set("Off")
                exposure_time = cam.ExposureTime
                exposure_time.set(exposure_time_value)
            except (AttributeError, VmbFeatureError):  # noqa: F405
                pass
        else:
            try:
                cam.ExposureAuto.set("Continuous")
            except (AttributeError, VmbFeatureError):  # noqa: F405
                pass

        # White balancing settings
        try:
            cam.BalanceWhiteAuto.set("Continuous")
        except (AttributeError, VmbFeatureError):  # noqa: F405
            pass

        # GeV packet size settings (only available for GigE Cameras)
        try:
            stream = cam.get_streams()[0]
            stream.GVSPAdjustPacketSize.run()
            while not stream.GVSPAdjustPacketSize.is_done():
                pass
        except (AttributeError, VmbFeatureError):  # noqa: F405
            pass


def setup_pixel_format(cam: Camera) -> None:  # noqa: F405
    """Configures the camera's pixel format:

    1. Retrieves all the camera's compatible color pixel formats.

    2. Filters out formats not compatible with OpenCV.

    3. Retrieves all the camera's compatible monochrome pixel formats.

    4. Filters out formats not compatible with OpenCV.

    5. Selects the OpenCV-compatible color pixel format. If none exist, attempts
    to convert an incompatible format to be compatible. If conversion is not possible,
    selects an OpenCV-compatible monochrome pixel format.

    Args:
        cam (Camera): Camera object from the VMBPY API module.
    """
    # Available color pixel formats. Prefer color formats over monochrome formats
    cam_formats = cam.get_pixel_formats()
    cam_color_formats = intersect_pixel_formats(  # noqa: F405
        cam_formats,
        COLOR_PIXEL_FORMATS,  # noqa: F405
    )
    convertible_color_formats = tuple(
        f
        for f in cam_color_formats
        if opencv_display_format in f.get_convertible_formats()
    )

    cam_mono_formats = intersect_pixel_formats(cam_formats, MONO_PIXEL_FORMATS)  # noqa: F405
    convertible_mono_formats = tuple(
        f
        for f in cam_mono_formats
        if opencv_display_format in f.get_convertible_formats()
    )

    # Use OpenCV color format
    if opencv_display_format in cam_formats:
        cam.set_pixel_format(opencv_display_format)

    # Else convert color to OpenCV format
    elif convertible_color_formats:
        cam.set_pixel_format(convertible_color_formats[0])

    # Else use OpenCV monochrome format
    elif convertible_mono_formats:
        cam.set_pixel_format(convertible_mono_formats[0])

    else:
        abort("Camera does not support an OpenCV compatible format. Abort.")


def upload_lut(
    cam: Camera,  # noqa: F405
    lut_dataset_selector_index: int,
    gain: tk.StringVar,
) -> None:  # noqa: F405
    """Uploads and enables the LUT:

    1. Checks the gain to select the correct LUT path.

    2. Opens the LUT file, loads it into the camera and runs it.

    3. Prints the directory and selected LUT.

    Args:
        cam (Camera): Camera object from the VMBPY API module.
        lut_dataset_selector_index (int): Index of the selected LUT.
        gain (tk.StringVar): Container of the gain mode for choosing the LUT (0 [0 dB] or 1 [18 dB]).
    """
    # Set directory
    if gain.get() == "1 [18 dB]":
        dir = const.LUT_DIR1
    else:
        dir = const.LUT_DIR0

    # Read LUT, upload to camera
    with cam:
        with open(dir, mode="rb") as file:
            fileContent = file.read()

            cam.LUTDatasetSelector.set(lut_dataset_selector_index)
            cam.LUTValueAll.set(fileContent)

            cam.LUTDatasetSave.run()

    print(
        f"LUT from file {dir} loaded into LUT Nr.{lut_dataset_selector_index}."
    )


def grab_frame(cam: Camera) -> None:  # noqa: F405
    """Captures a frame to be used as a temporal frame:

    1. Grabs a frame from the camera.

    2. Saves the frame in the specified directory.

    Args:
        cam (Camera): Camera object from the VMBPY API module.
    """
    frame = cam.get_frame()
    cv2.imwrite(const.BACKGROUND_FRAME_DIR, frame.as_opencv_image())


class Handler:
    """Handles the mayority of the camera operation.

    Methods:

        __init__:                       Initializes the Handler class.

        update:                         Updates the live graph of the GUI.

        save_plot:                      Saves the plot stored in the instance.

        create_camera_control_slider:   Creates an slider, saves it in the instance.

        set_exposure:                   Updates the exposure value.

        set_min_max_value:              Updates the minimum or maximum spot size value.

        __call__:                       Between each frame, sends the frame for processing,
        prepares for the next one, and checks if the program has stopped.
    """

    def __init__(
        self,
        cam: Camera,  # noqa: F405
        exposure_time_value: int,
        check: tk.StringVar,
        light: tk.StringVar,
        gain: tk.StringVar,
        iso: tk.StringVar,
        payload: tk.StringVar,
        elevation_in: tk.StringVar,
        fig: plt.figure,
        ax: plt.axes,
        line: plt.hlines,
        xdata: list,
        ydata: list,
    ):
        """Initializes the Handler class with the specified camera and plotting parameters,
        and creates a directory for storing the frames:

        1. Sets up all necessary instances based on the chosen settings.

        2. Creates the directory for saving frames according to the specified settings
        (will be saves in the data directory on the root folder of the project, inside a folder
        called tracking_images).

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            cam (Camera): Camera object from the VMBPY API module.
            exposure_time_value (int): Specified exposure value for Manual mode.
            check (tk.StringVar): Container of the streaming mode.
            light (tk.StringVar): Container of the time of day.
            gain (tk.StringVar): Container of the gain mode (0 [0 dB] or 1 [18 dB]).
            iso (tk.StringVar): Container of the camera mode: Normal, Hot-pixel substraction, Subtraction or Camera's BC.
            payload (tk.StringVar): Container of the payload.
            elevation_in (tk.StringVar): Container of the elevation mode.
            fig (plt.figure): Figure for the GUI plot.
            ax (plt.axes): Axes for the GUI plot.
            line (plt.hlines): Lines for the GUI plot
            xdata (list): Data for the x-axis for the GUI plot
            ydata (list): Data for the y-axis for the GUI plot

        :no-index:
        """
        # Setting up instances
        self.shutdown_event = threading.Event()
        self.cam = cam
        self.exposure_slider = None
        self.min_value = 1
        self.max_value = const.H_SENSOR_SIZE * const.V_SENSOR_SIZE
        self.root = None

        # Input instances
        self.gain = 1
        self.counter = 0
        self.background = 0
        self.mode = 0
        self.cond = 0

        # Graph instances
        self.fig = fig
        self.ax = ax
        self.line = line
        self.xdata = xdata
        self.ydata = ydata

        # Graph's update
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update_graph,
            interval=100,
            blit=False,
            cache_frame_data=False,
        )

        # Directory where the tracking frames get saved: directory of script.
        d = r".\data"

        self.payload = payload.get()
        # self.elevation_mode = elevation_in.get()
        if gain.get() == "1 [18 dB]":
            self.gain = 1
        else:
            self.gain = 0

        if iso.get() == "Normal":
            self.background = 0
        elif iso.get() == "Subtraction":
            self.background = 1
        elif iso.get() == "Camera's BC":
            self.background = 2
        else:
            self.background = 3

        if light.get() == "Daytime":
            self.cond = 0
        else:
            self.cond = 1

        if check.get() == "Record":
            # Directory creation
            self.mode = 1
            now = datetime.now()
            if exposure_time_value == 1:
                foldername_NP = (
                    f"tc_{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_"
                    f"{now.strftime('%H')}{now.strftime('%m')}{now.strftime('%S')}_"
                    f"exp_AUTO_GAIN{self.gain}_NP"
                )
                if self.background == 0:
                    foldername = (
                        f"tc_{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_"
                        f"{now.strftime('%H')}{now.strftime('%m')}{now.strftime('%S')}"
                        f"_exp_AUTO_GAIN{self.gain}"
                    )
                elif self.background == 1:
                    foldername = (
                        f"tc_{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_"
                        f"{now.strftime('%H')}{now.strftime('%m')}{now.strftime('%S')}_"
                        f"exp_AUTO_GAIN{self.gain}_IS"
                    )
                elif self.background == 2:
                    foldername = (
                        f"tc_{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_"
                        f"{now.strftime('%H')}{now.strftime('%m')}{now.strftime('%S')}_"
                        f"exp_AUTO_GAIN{self.gain}_CAMERA_BC"
                    )
                else:
                    foldername = (
                        f"tc_{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_"
                        f"{now.strftime('%H')}{now.strftime('%m')}{now.strftime('%S')}_"
                        f"exp_AUTO_GAIN{self.gain}_HP"
                    )
            else:
                foldername_NP = (
                    f"tc_{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_"
                    f"{now.strftime('%H')}{now.strftime('%m')}{now.strftime('%S')}_"
                    f"exp_{exposure_time_value}us_GAIN{self.gain}_NP"
                )
                if self.background == 0:
                    foldername = (
                        f"tc_{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_"
                        f"{now.strftime('%H')}{now.strftime('%m')}{now.strftime('%S')}_"
                        f"exp_{exposure_time_value}us_GAIN{self.gain}"
                    )
                if self.background == 1:
                    foldername = (
                        f"tc_{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_"
                        f"{now.strftime('%H')}{now.strftime('%m')}{now.strftime('%S')}_"
                        f"exp_{exposure_time_value}us_GAIN{self.gain}_IS"
                    )
                if self.background == 2:
                    foldername = (
                        f"tc_{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_"
                        f"{now.strftime('%H')}{now.strftime('%m')}{now.strftime('%S')}_"
                        f"exp_{exposure_time_value}us_GAIN{self.gain}_CAMERA_BC"
                    )
                else:
                    foldername = (
                        f"tc_{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_"
                        f"{now.strftime('%H')}{now.strftime('%m')}{now.strftime('%S')}_"
                        f"exp_{exposure_time_value}us_GAIN{self.gain}_HP"
                    )

            if elevation_in.get() == "Full" and self.payload != "None":
                foldername = foldername + "_" + self.payload
                foldername_NP = foldername_NP + "_" + self.payload

            self.pnp = os.path.join(d, "tracking_images", foldername_NP)
            self.p = os.path.join(d, "tracking_images", foldername)

            os.makedirs(self.p)
            os.makedirs(self.pnp)

    def update_graph(self, frame: Frame) -> plt.hlines:  # noqa: F405
        """Updates the live graph of the GUI with new data stored in the current instance (self):

        1. If data is available, plots it on the graph.

        2. Adjusts the graph's horizontal and vertical limits, extends the x-axis by 60 seconds,
        and increase the y-axis limit by 10% of the maximum value.

        3. Updates the graph's format as needed.

        4. Plots the new data on the graph.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            frame (Frame): Frame object from the VMBPY API module.

        Returns:
            plt.hlines: Updated graph instance.

        :no-index:
        """
        if not self.xdata:  # If no data, just return
            return (self.line,)

        # Ensure xdata is in UTC
        self.xdata = [x.astimezone(pytz.UTC) for x in self.xdata]

        self.line.set_data(self.xdata, self.ydata)
        ax = self.ax

        # Update axis limits
        ax.set_xlim(
            self.xdata[0],
            max(self.xdata[-1], self.xdata[0] + timedelta(seconds=60)),
        )

        if self.ydata:
            ax.set_ylim(0, max(255, max(self.ydata) * 1.1))

        # Update the formatter to show appropriate range
        locator = mdates.AutoDateLocator()
        # formatter = mdates.AutoDateFormatter(locator)
        formatter = mdates.DateFormatter("%H:%M:%S", tz=mdates.UTC)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        self.fig.canvas.draw()
        return (self.line,)

    def save_plot(self) -> None:
        """Saves the plot stored in the current instance (self):

        1. If recording mode is selected, sets the plot size, data, title, and labels.

        2. Adjust the format of the time as H:M:S.

        3. If a payload is chosen, its name will be added to the plot's title.

        4. Saves the plot in the same directory as the recorded frames (stored in the instance).

        Args:
            self (Instance): Current instance, provides access to attributes and methods.

        :no-index:
        """
        if self.mode != 0:  # Only save if in recording mode
            plt.figure(figsize=(20, 8))
            plt.plot(self.xdata, self.ydata)

            # Enable the grid
            plt.grid(True)

            # Format the x-axis ticks
            time_format = mdates.DateFormatter("%H:%M:%S")
            plt.gca().xaxis.set_major_formatter(time_format)

            plt.xlabel("Time [UTC]")
            plt.ylabel("Brightness")
            plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
            # Adjust layout manually for a tighter fit, but not as tight as plt.tightlayout()
            plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.1)
            # plt.tight_layout()
            if self.payload != "None":
                plt.title(
                    f"{self.payload} downlink on {datetime.now().strftime('%Y-%m-%d')}"
                )
                plt.savefig(
                    f"{self.p}/{datetime.now().strftime('%Y-%m-%d')}_{self.payload}_DL_plot.png"
                )
            else:
                plt.title(f"Downlink on {datetime.now().strftime('%Y-%m-%d')}")
                plt.savefig(
                    f"{self.p}/{datetime.now().strftime('%Y-%m-%d')}_DL_plot.png"
                )
            plt.close()

    def create_camera_control_slider(self, root: tk.Tk) -> None:
        """Creates an slider, saves it in the current instance (self) and sets its initial values:

        1. Creates a slider within the current instance using the CameraControlSlider class.

        2. Sets the initial values of the minimum and maximum spot size and the exposure with set_initial_values().

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            root (tk.Tk): Main window of the GUI menu.

        :no-index:
        """
        self.camera_control_slider = CameraControlSlider(root, self)
        current_exposure = self.cam.ExposureTime.get()
        self.camera_control_slider.set_initial_values(
            current_exposure, self.min_value, self.max_value
        )

    def set_exposure(self, exposure_time: int) -> None:
        """Updates the exposure value stored in the current instance (self).

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            exposure_time (int): Exposure time value.
        :no-index:
        """
        try:  # Tries to update the exposure time
            self.cam.ExposureTime.set(exposure_time)
        except (AttributeError, VmbFeatureError):  # noqa: F405
            print("Failed to set exposure time")

    def set_min_max_value(self, value: int, siz: int) -> None:
        """Updates the minimum or maximum spot size value stored in the current instance (self).

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            value (int): Final minimum or maximum spot size value.
            siz (int): Integer to differenciate if we want to change the minimum or the maximum spot size value,
            1 for the maximum, 0 for minimum.

        :no-index:
        """
        if siz == 1:  # Max value
            self.max_value = value
            print(f"Max value set to: {value}")
        else:
            self.min_value = value
            print(f"Min value set to: {value}")

    def __call__(self, cam: Camera, stream: Stream, frame: Frame) -> None:  # noqa: F405
        """Between each frame, sends the current frame for processing, prepares for the next
        one, and checks if the program has stopped:

        1. If program shutdown is activated, exits the fuction.

        2. If a frame has been grabbed, increments the counter and starts image processing.

        3. Prepares for the next frame and checks if program is stopped (by pressing q / Q)

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            cam (Camera): Camera object from the VMBPY API module.
            stream (Stream): Stream object from the VMBPY API module.
            frame (Frame): Frame object from the VMBPY API module.

        :no-index:
        """
        if self.shutdown_event.is_set():
            return

        if frame.get_status() == FrameStatus.Complete:  # noqa: F405
            self.counter += 1
            # Image Processing fuction
            im.frame_processing(self, cam, frame)

        cam.queue_frame(frame)

        # Check for 'q' key press to stop recording
        if cv2.waitKey(1) & 0xFF == ord("q") or cv2.waitKey(1) & 0xFF == ord(
            "Q"
        ):
            self.shutdown_event.set()
            if self.root:
                self.root.quit()


class CameraControlSlider(tk.Toplevel):
    """Handles the sliders of the GUI menu.

    Methods:

        __init__: Initializes the CameraControlSlider class.

        setup_exposure_slider: Creates the exposure slider.

        setup_min_value_slider: Creates the minimum spot size value slider.

        setup_max_value_slider: Creates the maximum spot size value slider

        update_exposure: Updates the exposure value.

        update_min_value: Updates the minimum spot size value.

        update_max_value: Updates the maximum spot size value.

        update_from_exposure_entry: Updates the exposure value parsed through the button.

        update_from_min_entry: Updates the minimum spot size value parsed through the button.

        update_from_max_entry: Updates the maximum spot size value parsed through the button.

        set_initial_values: Sets the intial values for all the varibales of the sliders.

    Args:
        tk (tk.Toplevel): Window where the slider should be created.
    """

    def __init__(self, master: tk.Tk, camera_control: Handler):
        """Initializes the CameraControlSlider class with the specified
        GUI parameters, and creates the sliders:

        1. Sets up all necessary instances for the slider elements in the menu.

        2. Configures exposure, minimum, and maximum spot size using the appropriate functions.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            master (tk.Tk): Tinker GUI window.
            camera_control (Handler): Parsed through handler.
        """
        # Allows the child class to invoke the constructor of its parent class.
        super().__init__(master)
        self.camera_control = camera_control
        self.title("Camera Control Sliders")
        # Dimensions adn position of the control sliders (WidthxHeight+X+Y).
        self.geometry("370x285+900+360")

        # Creates a frame to hold min and max sliders side by side
        self.min_max_frame = ttk.Frame(self)
        self.min_max_frame.pack(fill="x", expand=True, pady=10)

        # Slider setup
        # Exposure slider
        self.setup_exposure_slider()
        # Min value slider
        self.setup_min_value_slider()
        # Max value slider
        self.setup_max_value_slider()

    def setup_exposure_slider(self) -> None:
        """Creates the exposure slider:

        1. Initializes all slider elements and converts the exposure to a logarithmic scale.

        2. Sets up the displayed exposure value and its slider.

        3. Configures the button to manually change the exposure value.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
        """
        # Initial values are converted to a logarithmic scale
        self.min_exposure = 10
        self.max_exposure = 3000000  # 1 second
        self.log_min_exposure = math.log10(self.min_exposure)
        self.log_max_exposure = math.log10(self.max_exposure)

        self.current_exposure = tk.DoubleVar(value=self.log_min_exposure)
        ttk.Label(self, text="Exposure Control").pack(pady=(10, 0))

        self.exposure_label = ttk.Label(
            self, text=f"Exposure: {self.min_exposure:.2f} µs"
        )
        self.exposure_label.pack(pady=(0, 5))

        # Exposure slider settings
        self.exposure_slider = ttk.Scale(
            self,
            from_=0,
            to=1000,
            orient="horizontal",
            length=600,
            command=self.update_exposure,  # Calls the fuction on each value change
            variable=self.current_exposure,
        )
        self.exposure_slider.pack(pady=5, padx=20, fill="x")

        self.exposure_entry = ttk.Entry(self, width=10)
        self.exposure_entry.pack(pady=5)
        self.exposure_entry.bind("<Return>", self.update_from_exposure_entry)

        self.exposure_set_button = ttk.Button(
            self, text="Set Exposure", command=self.update_from_exposure_entry
        )
        self.exposure_set_button.pack(pady=5)

    def setup_min_value_slider(self) -> None:
        """Creates the minimum spot size value slider:

        1. Initializes all slider elements and converts the minimum spot size value to a logarithmic scale.

        2. Sets up the displayed minimum value and its slider.

        3. Configures the button to manually change the minimum spot size value.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
        """
        self.min_value = 1
        self.max_value = const.H_SENSOR_SIZE * const.V_SENSOR_SIZE
        self.log_min_value = math.log10(self.min_value)
        self.log_max_value = math.log10(self.max_value)

        self.current_min = tk.DoubleVar(value=self.log_min_value)

        min_frame = ttk.Frame(self.min_max_frame)
        min_frame.pack(side="left", expand=True, fill="x", padx=10)

        ttk.Label(min_frame, text="Minimum Value Control").pack()
        self.min_label = ttk.Label(
            min_frame, text=f"Min. Beam Spot Size: {self.min_value:.0f}"
        )
        self.min_label.pack()

        self.min_slider = ttk.Scale(
            min_frame,
            from_=0,
            to=1000,
            orient="horizontal",
            command=self.update_min_value,
            variable=self.current_min,
        )
        self.min_slider.pack(fill="x")

        self.min_entry = ttk.Entry(min_frame, width=10)
        self.min_entry.pack()
        self.min_entry.bind("<Return>", self.update_from_min_entry)

        self.min_set_button = ttk.Button(
            min_frame, text="Set Min", command=self.update_from_min_entry
        )
        self.min_set_button.pack()

    def setup_max_value_slider(self) -> None:
        """Creates the maximum spot size value slider:

        1. Initializes all slider elements and converts the maximum spot size value to a logarithmic scale.

        2. Sets up the displayed maximum value and its slider.

        3. Configures the button to manually change the maximum spot size value.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
        """
        self.current_max = tk.DoubleVar(value=self.log_max_value)

        max_frame = ttk.Frame(self.min_max_frame)
        max_frame.pack(side="right", expand=True, fill="x", padx=10)

        ttk.Label(max_frame, text="Maximum Value Control").pack()
        self.max_label = ttk.Label(
            max_frame, text=f"Max Beam Spot Size: {self.max_value:.0f}"
        )
        self.max_label.pack()

        self.max_slider = ttk.Scale(
            max_frame,
            from_=0,
            to=1000,
            orient="horizontal",
            command=self.update_max_value,
            variable=self.current_max,
        )
        self.max_slider.pack(fill="x")

        self.max_entry = ttk.Entry(max_frame, width=10)
        self.max_entry.pack()
        self.max_entry.bind("<Return>", self.update_from_max_entry)

        self.max_set_button = ttk.Button(
            max_frame, text="Set Max", command=self.update_from_max_entry
        )
        self.max_set_button.pack()

    def update_exposure(self, event=None) -> None:
        """Updates the exposure value parsed through the slider:

        1. Gets the exposure from the slider and converts it to a logarithmic scale.

        2. Sends the updated exposure value to the camera.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            event (_type_, optional): Nothing, just compatibility purposes. Defaults to None.
        """
        log_value = (
            self.exposure_slider.get()
            / 1000
            * (self.log_max_exposure - self.log_min_exposure)
            + self.log_min_exposure
        )
        print(f"the log_value in update_exposure is {log_value}")
        print(
            f"the self.exposure_slider.get() in update_exposure is {self.exposure_slider.get()}"
        )
        print(
            f"the self.log_max_exposure in update_exposure is {self.log_max_exposure}"
        )
        print(
            f"the self.log_min_exposure in update_exposure is {self.log_min_exposure}"
        )
        exposure = round(10**log_value)
        self.exposure_label.config(text=f"Exposure: {exposure:.2f} µs")
        self.camera_control.set_exposure(exposure)
        self.exposure_entry.delete(0, tk.END)
        self.exposure_entry.insert(0, str(exposure))

    def update_min_value(self, event=None) -> None:
        """Updates the minimum spot size value parsed through the slider:

        1. Gets the minimum spot size value from the slider and converts it to a logarithmic scale.

        2. If the miniumum sleected spot size value is bigger than the maximum spot size value,
        the maximum spot size value is selected as the minimum spot size value. If a negative
        value is selected, it will be converted to 0.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            event (_type_, optional): Nothing, just compatibility purposes. Defaults to None.
        """
        log_value = (
            self.min_slider.get()
            / 1000
            * (self.log_max_value - self.log_min_value)
            + self.log_min_value
        )
        min_value = round(10**log_value)
        self.min_value = max(0, min(self.max_value - 1, min_value))
        self.min_label.config(text=f"Min Value: {self.min_value:.2f}")
        # Updates min value
        self.camera_control.set_min_max_value(self.min_value, 0)
        self.min_entry.delete(0, tk.END)
        self.min_entry.insert(0, str(self.min_value))

    def update_max_value(self, event=None) -> None:
        """Updates the maximum spot size value parsed through the slider:

        1. Gets the maximum spot size value from the slider and converts it to a logarithmic scale.

        2. The maximum selected spot size value will be the maximum value between the minimum spot size
        value and the smaller value between the maximum spot size value selected from the slider and whole
        dimensions of the image.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            event (_type_, optional): Nothing, just compatibility purposes. Defaults to None.
        """
        log_value = (
            self.max_slider.get()
            / 1000
            * (self.log_max_value - self.log_min_value)
            + self.log_min_value
        )
        max_value = round(10**log_value)
        self.max_value = max(
            self.min_value,
            min((const.H_SENSOR_SIZE * const.V_SENSOR_SIZE), max_value),
        )
        self.max_label.config(text=f"Max Value: {self.max_value:.2f}")
        self.camera_control.set_min_max_value(self.max_value, 1)
        self.max_entry.delete(0, tk.END)
        self.max_entry.insert(0, str(self.max_value))

    def update_from_exposure_entry(self, event=None) -> None:
        """Updates the exposure value parsed through the button:

        1. Gets the exposure value and converts it to a logarithmic scale if it is in the correct range.
        If not, it raises an error.

        2. Updates the exposure value calling the update_exposure() function.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            event (_type_, optional): Nothing, just compatibility purposes. Defaults to None.

        Raises:
            ValueError: Exposure time inputed in the text-box is either bigger than the maximum exposure time
            or smaller than the smallest exposure time.
        """
        try:
            exposure = float(self.exposure_entry.get())
            if self.min_exposure <= exposure <= self.max_exposure:
                log_value = (
                    (math.log10(exposure) - self.log_min_exposure)
                    / (self.log_max_exposure - self.log_min_exposure)
                    * 1000
                )
                self.exposure_slider.set(log_value)
                # Updates the exposure value
                self.update_exposure(None)
            else:
                raise ValueError
        except ValueError:
            self.exposure_entry.delete(0, tk.END)
            self.exposure_entry.insert(
                0, str(round(10 ** self.current_exposure.get()))
            )

    def update_from_min_entry(self, event=None) -> None:
        """Updates the minimum spot size value parsed through the button:

        1. Gets the minimum spot size value and converts it to a logarithmic scale if it is bigger than
        zero but smaller than the maximum value.

        2. Updates the minimum spot size value calling the update_min_value() function.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            event (_type_, optional): Nothing, just compatibility purposes. Defaults to None.

        Raises:
            ValueError: Minimum spot size value is either smaller than zero or bigger than the maximum spot
            size value.
        """
        try:
            min_value = int(self.min_entry.get())
            if 0 <= min_value < self.max_value:
                self.min_value = min_value
                log_value = (
                    (math.log10(max(1, min_value)) - self.log_min_value)
                    / (self.log_max_value - self.log_min_value)
                    * 1000
                )
                self.min_slider.set(log_value)
                # Updates the min spot value
                self.update_min_value(None)
            else:
                raise ValueError
        except ValueError:
            self.min_entry.delete(0, tk.END)
            self.min_entry.insert(0, str(self.min_value))

    def update_from_max_entry(self, event=None) -> None:
        """Updates the maximum spot size value parsed through the button:

        1. Gets the maximum spot size value and converts it to a logarithmic scale if it is bigger or
        equal to the minimum spot size values and smaller or equal than the full image.

        2. Updates the maximum spot size value calling the update_max_value() function.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            event (_type_, optional): Nothing, just compatibility purposes. Defaults to None.

        Raises:
            ValueError: Maximum spot size value is either bigger than the dimensions of the whole frame or
            smaller than the minimum spot size value.
        """
        try:
            max_value = int(self.max_entry.get())
            if max_value >= self.min_value and max_value <= (
                const.H_SENSOR_SIZE * const.V_SENSOR_SIZE
            ):
                self.max_value = max_value
                log_value = (
                    (math.log10(max_value) - self.log_min_value)
                    / (self.log_max_value - self.log_min_value)
                    * 1000
                )
                self.max_slider.set(log_value)
                # Updates the max spot value
                self.update_max_value(None)
            else:
                raise ValueError
        except ValueError:
            self.max_entry.delete(0, tk.END)
            self.max_entry.insert(0, str(self.max_value))

    def set_initial_values(
        self, exposure: float, min_value: int, max_value: int
    ) -> None:
        """Sets the intial values for all the varibales of the sliders.

        1. Gets the maximum and minimum spot size and exposure values and converts them to a logarithmic scale.

        2. Sets initial values of the sliders.

        3. Calls the update fuctions to set an inicial value for the variables.

        Args:
            self (Instance): Current instance, provides access to attributes and methods.
            exposure (float): Initial exposure time.
            min_value (int): Initial minimum spot size value.
            max_value (int): Initial maximum spot size value.
        """
        log_exposure = (
            (
                math.log10(
                    max(self.min_exposure, min(self.max_exposure, exposure))
                )
                - self.log_min_exposure
            )
            / (self.log_max_exposure - self.log_min_exposure)
            * 1000
        )
        self.min_value = min_value
        self.max_value = max_value
        log_min_value = (
            (math.log10(max(1, self.min_value)) - self.log_min_value)
            / (self.log_max_value - self.log_min_value)
            * 1000
        )
        log_max_value = (
            (math.log10(self.max_value) - self.log_min_value)
            / (self.log_max_value - self.log_min_value)
            * 1000
        )
        # Sets inital values of the sliders
        self.exposure_slider.set(log_exposure)
        self.min_slider.set(log_min_value)
        self.max_slider.set(log_max_value)
        # Sets inital values
        self.update_exposure(None)
        self.update_min_value(None)
        self.update_max_value(None)
