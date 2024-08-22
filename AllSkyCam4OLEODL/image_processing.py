"""This module manages the processing of the frames taken by the camera."""

# C:\Users\alda_ik\Documents\04_PROGRAMMING\02_FINAL_PROJECT\image_processing.py

from datetime import datetime
from typing import Tuple
import cv2
import os
import csv
import math
import numpy as np

from . import constants as const


def dark_frame_setup(frame: np.array) -> np.array:
    """Prepares a frame for processing:

    1. A threshold of 45 is applied to a previously recorded image of the camera's hot pixels.

    2. The resulting thresholded image is normalized, resulting in an image with values [0, 1].

    3. Finally the normalized image is scaled, obtaining an image with values [0, 255].

    Args:
        frame (np.array): Frame with the hot pixels present.

    Returns:
        np.array: Image after normalization, thresholding and scaling.
    """
    # Apply threshold to create a binary image
    _, thresh = cv2.threshold(
        frame, const.HOT_PIXEL0_THRES_VAL, 255, cv2.THRESH_BINARY
    )

    # Normalize the binary image
    normalized = cv2.normalize(
        thresh, None, 0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F
    )
    # Scale the image to [0, 255]
    normalized = normalized * 255
    normalized = normalized.astype(np.uint8)

    return normalized


def subtract_frames(frame: np.array, frame_substracted: np.array) -> np.array:
    """Subtracts one frame from another using OpenCV:

    1. Checks if both frames have the same dimensions and format.

    2. Substracts both of the frames.

    Args:
        frame (np.array): Original frame.
        frame_substracted (np.array): Frame to substract.

    Returns:
        np.array: Image obtained after frame subtraction.
    """
    # Ensure images are the same size and format
    assert (
        frame.shape == frame_substracted.shape
    ), "Both image frames must have the same dimensions"
    assert (
        frame.dtype == frame_substracted.dtype
    ), "Both image frames must have the same data type"

    # Subtract the dark frame using OpenCV
    subtracted_image = cv2.subtract(frame, frame_substracted)

    return subtracted_image


def write_csv(
    self,
    frame_mean_pixel_value: int,
    frame_number: str,
    time: str,
    exposure: float,
    r: float,
    elevation: float,
    azimuth: float,
    fov: float,
    location: Tuple,
    pvalue: float,
    pvalue_grid: np.uint32,
    intensity: float,
    intensity_grid: np.float64,
) -> None:
    """Writes a csv file with all the parameters needed to perform the analysis of the final satellite pass:

    1. Creates the dictionaries and fields.

    2. Writes the csv file.

    Args:
        self (Instance): Parsed instance from Handler in the api module, provides access to attributes and methods.
        frame_mean_pixel_value (int): Mean Pixel Value of the entire frame.
        frame_number (str): Frame number.
        time (str): Current time where the frame as been recorded.
        exposure (float): Exposure time used for that particular frame.
        r (float): Radial position of the brightest point.
        elevation (float): Elevation of the brightest point
        azimuth (float): Azimuth of the brightest point.
        fov (float): Field Of View of the camera, in degrees, at the brightest point
        location (tuple): Location of the brightest point: [0] = x-axis, [1] = y-axis.
        pvalue (float): Pixel Value of the brightest point [0-255].
        pvalue_grid (np.uint32): Pixel Value of the whole brightest contour.
        intensity (float): Intensity value of the brightest point.
        intensity_grid (np.float64): Intensity value of the whole brightest contour.
    """
    if self.gain == 1:
        gain = "Gain 1 [18dB]"
    else:
        gain = "Gain 0 [0dB]"
    exposure = exposure.get()
    mydict = [
        {
            "Frame": frame_number,
            "Gain Mode": gain,
            "Time [CEST]": time,
            "Exposure [us]": exposure,
            "Location [x, y]": location,
            "Elevation [°]": elevation,
            "Azimuth [°]": azimuth,
            "FOV": fov,
            "R": r,
            "Mean Pixel Value [DN]": frame_mean_pixel_value,
            "Brightest Pixel Value [DN]": pvalue,
            "Grid Brightest Pixel Value [DN]": pvalue_grid,
            "Intensity [uW/m^-2]": intensity,
            "Grid Intensity[uW/m^-2]": intensity_grid,
        }
    ]

    fields = [
        "Frame",
        "Gain Mode",
        "Time [CEST]",
        "Exposure [us]",
        "Location [x, y]",
        "Elevation [°]",
        "Azimuth [°]",
        "FOV",
        "R",
        "Mean Pixel Value [DN]",
        "Brightest Pixel Value [DN]",
        "Grid Brightest Pixel Value [DN]",
        "Intensity [uW/m^-2]",
        "Grid Intensity[uW/m^-2]",
    ]

    if self.payload != "None":
        filename = f"{self.p}/{datetime.now().strftime('%Y-%m-%d')}_{self.payload}_DL_csv.csv"
    else:
        filename = f"{self.p}/{datetime.now().strftime('%Y-%m-%d')}_DL_csv.csv"
    file_exists = os.path.isfile(filename)

    # Write csv
    with open(filename, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        writer.writerows(mydict)


def brightest_V2(
    self,
    frame: np.array,
    exposure: float,
) -> Tuple[Tuple, float, float, float, float, float]:
    """Calculates the brightest point of the frame based on an specified minimum and maximum spot size.

    1. Setups the calibration factor.

    2. Depending if the daylight or nighttime is selcted a different process will be applyed:

        In case of Daytime: Bilateral filter 3 200x200 -> OTSU Thresholding.

        In case of Nighttime: Gaussian blur 3x3 -> Threshold based on black values.

    3. Finds the contours of the figure (zones of the fram with similar pixel values).

    4. Bounds the contours and filters them based on the minimum and maximum spot sizes values.

    5. Select the contour with the highest mean pixel value.

    6. Obtains the brightest pixel and the sum of all the values from the brightest contour.

    7. Converts pixel value to intensity using the correction factor.

    Args:
        self (Instance): Current instance, provides access to attributes and methods.
        frame (np.array): Frame from where the brightest point will be obtained.
        exposure (float): Exposure time used for that particular frame.

    Returns:
        tuple[tuple, float, float, float, float, float]: max_loc (tuple):Location of the brightest point:
        [0] = x-axis, [1] = y-axis.

        max_val (float): Pixel value of the brightest point [0-255].

        intensity_brightest (float): Intensity value of the brightest point.

        max_mean_pixel_value (float): Mean pixel value of the whole brightest contour.

        sum_max_mean_pixel_value[0] (float): Summed pixel value of the whole brightest contour.

        intensity_brightest_grid (float): Summed intensity value of the whole brightest contour.
    """
    max_mean_pixel_value = 0
    max_val = 0
    max_loc = [0, 0]
    intensity_brightest = 0
    intensity_brightest_grid = 0
    sum_max_mean_pixel_value = [0, 0, 0]
    # sum_max_mean_pixel_value[0]

    exposure = exposure.get()  # Exposure in us

    # Calibration factors
    calibration_THOR = 0.139602768 / (0.0001 * exposure + 18.545)
    calibration_THOR_grid = 0.139602768 / (0.0008 * exposure + 443.22)
    if self.gain == 1:
        calibration_THOR_gain = 0.139602768 / (1.4788 * exposure - 82.62)
    else:
        calibration_THOR_gain = 0.139602768 / (0.2427 * exposure + 1.67)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if self.cond == 0:
        # Processing for Daytime - Bilateral filter and otsu thresholding
        # filter = cv2.bilateralFilter(gray, 3, 100, 100)
        filter = cv2.bilateralFilter(gray, 3, 200, 200)
        # filter = cv2.GaussianBlur(gray, (5, 5), 0)
        # filter = cv2.GaussianBlur(gray, (3, 3), 0)

        _, th = cv2.threshold(
            filter, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
    else:
        # Processing for Nighttime - Gaussian filter and thresholding based on dark pixels pixel value
        thresh_val = 0.0004 * exposure + 13.113

        filter = cv2.GaussianBlur(gray, (3, 3), 0)
        _, th = cv2.threshold(filter, thresh_val, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    min_size = self.min_value
    max_size = self.max_value

    for contour in contours:
        _, _, w, h = cv2.boundingRect(contour)
        # Filter contours based on min and max spot size
        if min_size <= w * h and max_size >= w * h:
            mask = np.zeros(gray.shape, np.uint8)
            cv2.drawContours(mask, [contour], 0, 255, -1)

            mean_pixel_value = cv2.mean(gray, mask=mask)[0]

            # Compares current contour with the brightest one
            if mean_pixel_value > max_mean_pixel_value:
                max_mean_pixel_value = mean_pixel_value

                # Obtain brightest point and full brightness of the contour
                masked_gray = cv2.bitwise_and(gray, gray, mask=mask)
                sum_max_mean_pixel_value = cv2.sumElems(masked_gray)
                _, max_val, _, max_loc = cv2.minMaxLoc(masked_gray)

        # Convert to intensity
        intensity_brightest = max_val * calibration_THOR
        intensity_brightest_grid = (
            sum_max_mean_pixel_value[0] * calibration_THOR_grid
        )

    return (
        max_loc,
        max_val,
        intensity_brightest,
        max_mean_pixel_value,
        sum_max_mean_pixel_value[0],
        intensity_brightest_grid,
    )


def calculate_el_azi(max_loc: Tuple) -> Tuple[float, float, float, float]:
    """Calculates the elevation and azimuth of the brightest point of the frame, making use of the
    fisheye projections. Equidistant, equisolid and stereographic can be selected.

    1. Calculates the distance from the center of the image to the brightest point.

    2. Applies the projection to obtain the fov of the lens in the brightest point.

    3. Obtains the elevation based on the fov.

    4. Calculates the azimuth based on the center of the lens.

    Args:
        max_loc (tuple): Location of the brightest point: [0] = x-axis, [1] = y-axis.

    Returns:
        tuple[float, float, float, float]: elevation (float): Elevation of the brightest point.

        fov (float): Field Of View of the camera, in degrees, at the brightest point.

        r (float): Radial position of the brightest point.

        azimuth (float): Azimuth of the brightest point.
    """
    # print(max_loc)
    # print(type(max_loc))
    # max_loc = np.array([[[max_loc[0], max_loc[1]]]], dtype=np.float32)
    # # Undistort the point
    # undist_max_loc = cv2.fisheye.undistortPoints(max_loc, const.K, const.D, P=const.K)
    # undist_max_loc = undist_max_loc[0][0]
    # max_loc = (int(round(undist_max_loc[0])), int(round(undist_max_loc[1])))
    # print(max_loc)

    F = const.LENS_FOCAL_LENGTH
    r = math.sqrt(
        (max_loc[0] - const.FISH_CENTER[0]) ** 2
        + (max_loc[1] - const.FISH_CENTER[1]) ** 2
    )

    # Lens Projections
    # EQUIDISTANT PROJECTION
    # fov_rad = (r * const.PIXEL_SIZE) / F  # rad - FOV in radians
    # EQUISOLID PROJECTION
    fov_rad = 2 * math.asin((r * const.PIXEL_SIZE) / (2 * F))
    # STEREOGRAPHIC PROJECTION
    # fov_rad = 2 * math.atan((r * const.PIXEL_SIZE) / (2 * F))
    # RECTILINEAR PROJECTION
    # fov_rad = math.atan((r * const.PIXEL_SIZE) / F)

    fov = (fov_rad * (180 / math.pi)) * 2  # ° - FOV in degrees
    elevation = (180 - fov) / 2

    # Azimuth at the exact center of the frame
    if max_loc[1] == const.FISH_CENTER[1]:
        azimuth = 0
    else:
        azimuth = (
            math.atan(
                (max_loc[0] - const.FISH_CENTER[0])
                / (max_loc[1] - const.FISH_CENTER[1])
            )
        ) * (180 / math.pi)

    # If point is in the upper part of the frame
    if max_loc[1] >= const.FISH_CENTER[1]:
        azimuth = 180 + azimuth
    else:
        # If point is the bottom-right part of the frame
        if max_loc[0] >= const.FISH_CENTER[0]:
            azimuth = 360 + azimuth

    return elevation, fov, r, azimuth


def frame_draw(
    frame: np.array,
    time: str,
    exposure: float,
    rad: int,
    max_bright_loc: Tuple,
    max_bright_val: float,
    int_bright_val: float,
    mean_bright_grid_val: np.uint32,
    max_bright_grid_val: np.uint32,
    int_bright_grid_val: np.float64,
    min_size: int,
    max_size: int,
    elevation: float,
    azimuth: float,
) -> None:
    """Draws the overlays on top of the frame:

    Args:
        frame (np.array): Frame where the overlays will be drawn.
        time (str): Actual time in that particular frame.
        exposure (float): Exposure time used for that particular frame.
        rad (int): Radius of the intensity grid.
        max_bright_loc (tuple): Location of the brightest point: [0] = x-axis, [1] = y-axis.
        max_bright_val (float): Pixel value of the brightest point [0-255].
        int_bright_val (float): Intensity value of the brightest point.
        mean_bright_grid_val (np.uint32): Mean pixel value of the whole brightest contour.
        max_bright_grid_val (np.uint32): Summed pixel value of the whole brightest contour.
        int_bright_grid_val (np.float64): Summed intensity value of the whole brightest contour.
        min_size (int): Minimum spot size value used.
        max_size (int): Maximum spot size value used.
        elevation (float): Elevation of the brightest point.
        azimuth (float): Azimuth of the brightest point.
    """
    # Draw the time, exposure, coordinates and crosshair on the frame
    cv2.putText(
        frame,
        time,
        (1, 7),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.3,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        f"Exposure: {exposure.get()} us",
        (1, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        f"Min Size: {min_size:.0f}",
        (1, 47),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        f"Max Size: {max_size:.0f}",
        (1, 56),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        f"El.: {elevation:.0f}",
        (1, 201),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        f"Az.: {azimuth:.0f}",
        (1, 210),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        f"Brightness at {max_bright_loc}: {int_bright_val:.3f} uw/m^2 -> {max_bright_val}",
        (1, 238),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    if max_bright_val == 255:
        cv2.putText(
            frame,
            "Saturated! Lower Exposure",
            (115, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.25,
            (255, 255, 255),
            1,
        )
    cv2.putText(
        frame,
        f"Brightness {rad*2+1}x{rad*2+1} grid: {int_bright_grid_val:.3f} uw/m^2 "
        f"-> {max_bright_grid_val} (mean: {mean_bright_grid_val:.1f})",
        (1, 245),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "N",
        (160, 7),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "S",
        (160, 254),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "E",
        (1, 128),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "W",
        (310, 128),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "SW",
        (290, 242),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "(225)",
        (280, 227),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "(248)",
        (295, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "NW",
        (290, 17),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "(338)",
        (225, 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "(315)",
        (280, 29),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "(293)",
        (295, 66),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "SE",
        (30, 242),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "(135)",
        (35, 227),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "(113)",
        (11, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "NE",
        (30, 17),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "(45)",
        (35, 29),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "(68)",
        (11, 66),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.25,
        (255, 255, 255),
        1,
    )

    # Circle for the brightest point
    cv2.circle(frame, max_bright_loc, 5, (255, 255, 255), 1)

    # Crosshair
    # cv2.line(frame, (159, 128), (161, 128), (255, 255, 255), 1)
    # cv2.line(frame, (160, 127), (160, 129), (255, 255, 255), 1)


def frame_processing(self, cam, frame) -> None:
    """Procceses the frame.

    1. Grabs a temporal frame.

    2. Depending on the selected mode by the user:

    - Hot-pixel removal.
        A frame with the hot pixels will threshold and normalized by the dark_frame_setup() fuction
        and then subtracted to the the taken frame with the subtract_frames() function.

    - Own background correction.
        Substracts the temporal frame to the next grabbed frame. The subtract_frames() fuction is
        applied for substracting the temporal frame, just grabbed, with the next frame.

    - Normal operation.
        The temporal frame will be used directly.

    - Camera's own background correction.
        The temporal frame will be used directly.

    3. Obtains the brightest point thanks to the brightest_V2() function.

    4. Obtains the elevation and azimuth of the brightest pixel with the calculate_el_azi() fuction.

    5. Draws all the desired values on top of the frame using the frame_draw() fuction.

    6. Just in case the Record mode is being used, both the processed and unprocessed frames,
    besides the csv file, will all be saved.

    7- Finally the frames will be display and the first temporal frame will be removed.

    Args:
        self (Instance): Current instance, provides access to attributes and methods.
        cam (Camera): Camera object from the VMBPY API module.
        frame (Frame): Frame object from the VMBPY API module.
    """
    # Get the current time with ms.
    now = datetime.now()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    exposure_time = cam.ExposureTime
    msg = "Stream from '{}'. Press <q> to stop stream."

    print("{} acquired {}".format(cam, frame), flush=True)

    # Create a temporal frame where the proccessing will be made.
    cv2.imwrite(const.TEMP_FRAME_DIR, frame.as_opencv_image())
    frame_temp = cv2.imread(const.TEMP_FRAME_DIR)

    # Hot-pixel removal
    if self.background == 3:
        # Setup of the hot pixels of the wanted exposure.
        hot = cv2.imread(const.HOT_PIXEL0_DIR)
        normalized = dark_frame_setup(hot)
        # Removal of the dark pixels from the taken frame.
        frame_subs = subtract_frames(frame_temp, normalized)
    # Background substraction.
    elif self.background == 1:
        normalized = cv2.imread(const.BACKGROUND_FRAME_DIR)
        # background = background.astype(np.uint8)
        frame_subs = subtract_frames(frame_temp, normalized)
        # frame_subs = subtract_frames(normalized, frame_temp)  #   Chroma effect
    # Normal operation or Background correction mode
    else:
        frame_subs = cv2.imread(const.TEMP_FRAME_DIR)

    # Calculate the brightest point, elevation and azimuth
    mean_val_grid = 0
    (
        max_loc,
        max_val,
        intensity_brightest,
        mean_val_grid,
        max_val_grid,
        intensity_brightest_grid,
    ) = brightest_V2(self, frame_subs, exposure_time)

    elevation, fov, r, azimuth = calculate_el_azi(max_loc)

    # Append data for update the live graph of the GUI
    self.xdata.append(now)
    self.ydata.append(max_val)

    # Draw on-top of the frame
    frame_draw(
        frame_subs,
        current_time,
        exposure_time,
        const.GRID_RADIUS,
        max_loc,
        max_val,
        intensity_brightest,
        mean_val_grid,
        max_val_grid,
        intensity_brightest_grid,
        self.min_value,
        self.max_value,
        elevation,
        azimuth,
    )

    # We only write the frame if the mode selected is Record.
    if self.mode != 0:
        cv2.imwrite(
            f"{self.p}/{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_{now.strftime('%H')}"
            f"{now.strftime('%M')}{now.strftime('%S')}_frame_{str(self.counter)}.tiff",
            frame_subs,
        )
        cv2.imwrite(
            f"{self.pnp}/{now.strftime('%Y')}{now.strftime('%m')}{now.strftime('%d')}_{now.strftime('%H')}"
            f"{now.strftime('%M')}{now.strftime('%S')}_frame_{str(self.counter)}.tiff",
            frame_temp,
        )

        # Calculate mean pixel value of the frame and generate csv
        frame_mpv = frame_subs.mean()
        frame_num = f"frame_{str(self.counter)}"
        write_csv(
            self,
            frame_mpv,
            frame_num,
            current_time,
            exposure_time,
            r,
            elevation,
            azimuth,
            fov,
            max_loc,
            max_val,
            max_val_grid,
            intensity_brightest,
            intensity_brightest_grid,
        )

    # Create the window for the frames
    window = np.concatenate((frame_subs, frame_temp), axis=1)
    winname = msg.format(cam.get_name())
    cv2.namedWindow(winname)
    cv2.moveWindow(winname, 70, 5)
    cv2.imshow(winname, window)  # Show the frame

    if os.path.isfile(const.TEMP_FRAME_DIR):
        os.remove(const.TEMP_FRAME_DIR)
