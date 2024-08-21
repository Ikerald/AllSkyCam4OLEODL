"""This modules manages the checking and validation of the user inputs."""

# C:\Users\alda_ik\Documents\04_PROGRAMMING\02_FINAL_PROJECT\input_checks.py


def checks(
    elevation_in,
    elevation_angle_in,
    exposure_in,
    exposure_time_in,
    zenith,
) -> tuple[int, int, float]:
    """Based on the selected values in the GUI it preapres the exposure, elevation and
    zenith attenuation we will finally use.

    1. If manual exposure mode is selected, retrieves the exposure time, ensuring that the
    value is non-negative.

    2. If individual elevation mode is selected, retrieves the elevation angle, ensuring that the selected
    value is between 0 and 90 degrees of elevation.

    3. Selects the value of the atmospheric zenith attenuation.

    Args:
        elevation_in (tk.StringVar): Container of the chosen elevation mode.
        elevation_angle_in (tk.StringVar): Container of the chosen elevation angle (if manual).
        exposure_in (tk.StringVar): Container of the chosen exposure mode.
        exposure_time_in (tk.StringVar): Container of the chosen exposure value (if manual).
        zenith (tk.StringVar): Container of the atmospheric zenith attenuation.

    Raises:
        ValueError: Exposure time value is a lower than zero.
        ValueError: Elevation angle is lower than 0 or bigger than 90.

    Returns:
        tuple[int, int, float]: elevation_angle (int): Final selected elevation angle (if individual).

        exposure_time_value (int): Final selected exposure value (if manual).

        zenith (float): Final selected zenith attenuation value
    """
    # Validate exposure time
    if exposure_in.get() == "Manual":
        try:
            exposure_time_value = int(exposure_time_in.get())
            if exposure_time_value <= 0:
                raise ValueError
        # Error validation
        except ValueError:
            print("[ERROR] Invalid exposure time. Must be a positive integer.")
            return
    else:
        exposure_time_value = 1  # Default value for Auto mode

    # Validate elevation
    if elevation_in.get() == "Individual":
        try:
            elevation_angle = int(elevation_angle_in.get())
            print(elevation_angle)
            if elevation_angle <= 0 or elevation_angle >= 90:
                raise ValueError
        # Error validation
        except ValueError:
            print(
                "[ERROR] Invalid elevation angle. Must be a whole angle between 1 and 89 degrees."
            )
            return
    else:
        elevation_angle = 15  # Default value for Auto mode

    if zenith.get() == "Bad 1550nm [0.891]":
        zenith = 0.891
    elif zenith.get() == "Good 1550nm [0.986]":
        zenith = 0.986
    elif zenith.get() == "Bad 800nm [0.705]":
        zenith = 0.705
    else:
        zenith = 0.950

    return (
        elevation_angle,
        exposure_time_value,
        zenith,
    )
