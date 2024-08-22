"""This module contains all the constants needed to allow the project to work correctly."""

# C:\Users\alda_ik\Documents\04_PROGRAMMING\02_FINAL_PROJECT\constants.py

import numpy as np

# Directories
HOT_PIXEL0_DIR: str = r".\data\references\gain0\hot_500000.tiff"
HOT_PIXEL1_DIR: str = r".\data\references\gain1\hot_50000.tiff"
BACKGROUND_FRAME_DIR: str = r".\temp_.tiff"
TEMP_FRAME_DIR: str = r".\temp.tiff"

LUT_DIR0: str = r".\data\lut\Goldeye-G-CL-008_LinLUT_Gain0.bin"
LUT_DIR1: str = r".\data\lut\Goldeye-G-CL-008_LinLUT_Gain1.bin"

HOT_PIXEL0_THRES_VAL: int = 45
LUT_INDEX: int = 4

# Calibration factors
# CALIBRATION_THOR: float = 0.139602768 / 166
# CALIBRATION_THOR_GRID: float = 0.139602768 / 1426
# CALIBRATION_EDMU: float = 0.139602768 / 166
# MIN_BEAM_SIZE = 1
# MAX_BEAM_SIZE = 10

GRID_RADIUS: int = 2

# Lens parameters
LENS_FOCAL_LENGTH: float = 3.5  # mm
V_SENSOR_SIZE: int = 256  # Pixels
H_SENSOR_SIZE: int = 320  # Pixels
PIXEL_SIZE: float = 0.03  # mm (30um)

FISH_CENTER = [161, 131]

K = np.array(
    [
        [123.48774151225143, 0.0, 160.36138044001243],
        [0.0, 123.21716405041697, 130.60363126947752],
        [0.0, 0.0, 1.0],
    ]
)
D = np.array(
    [
        [-0.04444806603723004],
        [0.0036746704759666278],
        [0.0030634545076764002],
        [-0.0019588697364114325],
    ]
)


######################  LINK BUDGET  ######################
# Fixed constants
C = 3e8  # m/s - speed of light
H = 6.626e-34  # m²-kg/s - Planck's constant
R_E = 6370e3  # m - Earth's radius

# Environment constants
PSI = 0.3
# PSI = 0  # a change according to el is not yet regarded
# PSI = 0.1
# PSI = 1E-8
P_THR = 0.1  # loss_fraction for ScintiLoss

# Satellite constants
# el = 15  # ° - Elevation of the satellite
# P_tx = 30  # dBm - Transmited power
# 1W mean was used in FLP-OSIRISv1 experiments with OCAM
# 100mW or 50mW mean we expect in KIODO, since the 20dBm mentioned in the book might be peak-power
