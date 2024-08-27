"""This modules manages the creation and display of the link budget."""

# C:\Users\alda_ik\Documents\04_PROGRAMMING\03_SCRIPTS\05_LINK_BUDGET\link_budget.py

from typing import Union, Tuple
from scipy.special import erfinv

import numpy as np
import mplcursors
import matplotlib.pyplot as plt

import math

from . import constants as const


def printer_lb(
    el: Union[np.ndarray, int],
    elevation_mode,
    sat,
    a_tx: int,
    p_tx: int,
    ppb: int,
    teta_tx: float,
    a_rx: int,
    leng: Union[np.ndarray, float],
    g_tx: float,
    a_fsl: Union[np.ndarray, float],
    i_axial: Union[np.ndarray, float],
    area_rx: float,
    a_atm: Union[np.ndarray, float],
    a_bw: int,
    g_rx: float,
    p_rx: Union[np.ndarray, float],
    int_ogs_lin: Union[np.ndarray, float],
    int_ogs_lin_loss: Union[np.ndarray, float],
    p_ogs_mean: Union[np.ndarray, float],
    p_ogs_mean_loss: Union[np.ndarray, float],
    p_rx_lin: Union[np.ndarray, float],
    wl: float,
    p_rfe_lin: float,
    a_sci: int,
) -> Tuple[Union[np.ndarray, int], Union[np.ndarray, float]]:
    """Prints the graph or the results and summary of the link budget.

    1. If the elevation mode is "Full" it will just print the graph, if not
    it will print the result of the link budget.

    Args:
        el (np.ndarray | int): Elevation of the satellite
        elevation_mode (tk.StringVar): Container of the elevation mode.
        sat (tk.StringVar): Container of the payload used.
        a_tx (int): Transmitter optical loss.
        p_tx (int): Transmitter power.
        ppb (int): Photons/bit.
        teta_tx (float): Transmitter divergence.
        a_rx (int): Receiver optical loss onto RFE.
        leng (np.ndarray | float): Length of the link.
        g_tx (float): Transmitter antenna gain.
        a_fsl (np.ndarray | float): Free-space loss.
        i_axial (np.ndarray | float): Axial intensity at OGS-distance.
        area_rx (float): Receiver antenna area.
        a_atm (np.ndarray | float): Atmospheric attenuation loss.
        a_bw (int): Mean BeamWander loss.
        g_rx (float): Reveiver antenna gain.
        p_rx (np.ndarray | float): Received power.
        int_ogs_lin (np.ndarray | float): Intensity onto OGS-apertue exc. losses.
        int_ogs_lin_loss (np.ndarray | float): Intensity onto OGS-apertue inc. losses.
        p_ogs_mean (np.ndarray | float): Power into the OGS-apertue - no additional RX-losses.
        p_ogs_mean_loss (np.ndarray | float): Power into the OGS-apertue including RX-losses.
        p_rx_lin (np.ndarray | float): RxPower onto RFE-detector incl all losses.
        wl (float): Wavelength.
        p_rfe_lin (float): RFE-sensitivity for an specific Photons/bit.
        a_sci (int): Scintillation loss.
    """
    if elevation_mode.get() == "Full":
        print(int_ogs_lin_loss)
        el = np.arange(5, 90)
        print(el)
        plt.figure()

        plt.plot(el, int_ogs_lin_loss * 1e6, "-", color="r", linewidth=2)
        plt.ylabel("Intensity onto Camera-apertue  / µW/m²")
        plt.xlabel("Elevation / 1°")
        plt.subplots_adjust(left=0.17, right=0.95, top=0.92, bottom=0.13)
        plt.title(f"{sat.get()} intensity Link Budget")
        plt.grid(True)

        fig_manager = plt.get_current_fig_manager()

        # Dimensions and position of the link budget window (WidthxHeight+X+Y)
        fig_manager.window.wm_geometry("355x372+545+290")

        mplcursors.cursor()
        plt.show(block=False)
    else:
        print("///////////////////////////////////////////////////")
        print()
        print(f"Transmit-power = {p_tx} dBm")
        print(f"Divergence = {((teta_tx*1E6*10)/10)} µrad")
        print(f"Optical loss Tx = {a_tx} dB")

        print(
            f"Optical loss onto RFE (incl. splitting) = {a_rx} dB - We are not "
            f"taking into account optical loss as the receiver is a camera"
        )
        # if sat == "OsirisV1":
        #    print(
        #        f"Optical loss onto RFE (incl. splitting) = {a_rx} dB - in OSIRISv1 from FLP -7,5dB were measured in 30cm telescope towards PowerSensor"
        #    )
        # print(f"Optical loss Rx (incl. splitting) = {a_rx} dB - in KIODO only 4% of Rx-light was on RFE-APD")

        print()
        print(f"Link-distance  = {(leng/100)*.1} km")
        print(f"Tx-antenna gain = + {g_tx} dB")
        print(f"Freespace Loss  = {a_fsl} dB")
        print(
            f"   # axial Intensity a OGS-distance = {i_axial*1E6} µW/m^2, after "
            f"only distance and Tx-internal losses"
        )
        print(f"   # Area of Rx-antenna = {area_rx} m^2")
        print(
            f"   # power into Rx-aperture [no a_atmo nor a_pointing, only a_Tx, "
            f"a_fsl, g_Rx]  = {1E6*i_axial * area_rx} µW"
        )
        print()
        print(f"atmosph. atten. = {a_atm} dB")
        print(
            f"mean BeamWander loss = {a_bw} dB - Being the receiver a camera, we are "
            f"not taking into acount BeamWander losses"
        )

        print(
            f"scinti-loss     = {a_sci} dB - Once again we suppose Scintillation loss as cero"
        )

        print()
        print(f"Rx-antenna gain = + {g_rx} dB")
        print(f"optical loss Rx = {a_rx} dB, includes splitting for Tracking")
        print(f"RxPower on RFE with all losses  = {p_rx} dBm")
        print(
            f"   # intensity onto OGS-apertue incl atmosphere but excl. "
            f"Rx-losses = {int_ogs_lin *1E6} µW/m^2"
        )
        print(
            f"   # intensity onto OGS-apertue incl atmosphere including "
            f"Rx-losses = {int_ogs_lin_loss *1E6} µW/m^2"
        )
        print(
            f"   # power into the OGS-apertue - no additional RX-losses"
            f"= {(10**(p_ogs_mean/10)/1000)*1E6} µW"
        )
        print(
            f"   # power into the OGS-apertue including RX-losses = "
            f"{(10**(p_ogs_mean_loss/10)/1000)*1E6} µW"
        )
        print(
            f"RxPower onto RFE-detector incl all losses =  {p_rx_lin*1E9} nW, "
            f"sufficient for {(p_rx_lin/ppb/(const.H*const.C/wl))/1E9} Gbps at {ppb} Photons/bit"
        )
        print(
            f"RFE-sensitivity for {ppb} Ppb  =  {p_rfe_lin*1E9} nW or "
            f"{math.log10(p_rfe_lin*1000)*10} dBm"
        )
        print()
        print(f"Link Margin: {p_rx - math.log10(p_rfe_lin*1000)*10 } dBm")
        print()

        print("///////////////////// Summary /////////////////////")
        if elevation_mode.get() == "Individual":
            print(f"mean source power  +{p_tx} dBm")
            print(f"Tx-internal losses {a_tx} dBm")
            print(f"Tx-antenna gain    +{g_tx} dB")
            print(f"pointing loss      {a_bw} dB")
            print(f"Distance           {leng/1000} km")
            print(f"freespace loss     {a_fsl} dB")
            print(f"Atmospheric loss   {a_atm} dB")
            print(f"scintillation loss {a_sci} dB")
            print(f"Rx-antenna gain    +{g_rx} dB")
            print(f"Power into Rx-Aper {p_ogs_mean} dBm")
            print(f"Rx-internal losses {a_rx} dB")
            p_rx_ = (
                p_tx + a_tx + g_tx + a_bw + a_fsl + a_atm + a_sci + g_rx + a_rx
            )
            print(f"Power onto detectr {p_rx_} dBm")
            print(
                f"Sensitivity of RFE {10*math.log10(p_rfe_lin*1000)} dBm  /  {p_rfe_lin*1E9} nW"
            )
            print(
                f"Link Margin        {p_rx_ - 10*math.log10(p_rfe_lin*1000)} dB"
            )
            print()

            print("//////////////////// Intensity ////////////////////")
            print(
                f"Axial Intensity at OGS-distance = {i_axial*1E6} µW/m^2, after only "
                f"distance and Tx-internal losses"
            )
            print(
                f"Intensity onto OGS-apertue incl atmosphere but excl. Rx-losses = "
                f"{int_ogs_lin *1E6} µW/m^2"
            )
            print(
                f"Intensity onto OGS-apertue incl atmosphere including Rx-losses = "
                f"{int_ogs_lin_loss *1E6} µW/m^2"
            )
            print()

            print("////////////////////// Power //////////////////////")
            print(
                f"Power into Rx-aperture [no a_atmo nor a_pointing, only a_Tx, a_fsl, "
                f"g_Rx]  = {1E6*i_axial * area_rx} µW"
            )
            print(
                f"Power into the OGS-apertue - no additional RX-losses = "
                f"{(10**(p_ogs_mean/10)/1000)*1E6} µW"
            )
            print(
                f"Power into the OGS-apertue including RX-losses = "
                f"{(10**(p_ogs_mean_loss/10)/1000)*1E6} µW"
            )


def link_budget(
    elevation_mode, el: int, payload, zenith: float, h_ogs: int
) -> None:
    """Performs the link budget based on the parameters from the GUI:

    1. Selects specific parameters based on the payload chosen.

    2. Specifies the losses.

    3. Calculates antennas dimensions.

    4. If the elevation mode is "Full", the elevation angle will be converted to an array from 0 to 90 degrees.

    5. The rest of the parameters dependent on the elevation are calculated based on if
    the elevation is just a point or the full range.

    6. Computes the final received power at the receiver.

    7. Calculates the intensity onto the receiver using its area.

    Args:
        elevation_mode (tk.StringVar): Container of the elevation mode.
        el (int): Elevation angle.
        payload (tk.StringVar): Container of the payload used.
        zenith (float): Final selected zenith attenuation value.
        h_ogs (int): Final height of the selected OGS.

    Returns:
        tuple: el (np.ndarray | int): Elevation of the satellite.
        int_ogs_lin_loss (np.ndarray | float): Intensity onto OGS-apertue inc. losses.
    """
    if payload.get() == "OsirisV1":
        h_orbit = 595  # km - Satellite height
        wl = 1545e-9  # m - Wavelenght of the downlink
        p_tx = 30  # dBm - Transmited power
        teta_tx = 1e-3  # rad - OSIRISv1: 1.0E-3 oder 1.2E-3 mrad - die Dokumente sagen immer 1,2 aber CF meinte f�rs CNES-Paper 1,0
        a_tx = -1  # dB - Optical Transmissor losses (Tx)
        dr = 39e6  # bps - datarate in KIODO, 39Mbps in OSIRIS-FLP for OCAM and some tests to OP
        ppb = 250  # ppb - Photons per bit required bei RFE at BER=1E-3 at first OSIRIS with APD-RFE-100-OLD, 320Photons for RFE-300-NEW
    # diese Formel muss noch durch WL erg�nzt werden:   D_tx=0.2; teta_tx = 100E-6 * 0.01/D_tx; % estimate for near-optimum cut-gauss Tx
    elif payload.get() == "KIODO":
        h_orbit = 610  # km - Satellite height
        wl = 847e-9  # m - Wavelenght of the downlink
        p_tx = 20  # dBm - Transmited power
        # p_tx = 16.99
        teta_tx = 5.5e-6  # rad - OICETS-Kirari-LUCE FWHM beam divergence
        a_tx = -1  # dB - Optical Transmissor losses (Tx)
        dr = 39e6  # bps - datarate in KIODO, 39Mbps in OSIRIS-FLP for OCAM and some tests to OP
        ppb = 250  # ppb - Photons per bit required bei RFE at BER=1E-3 at first OSIRIS with APD-RFE-100-OLD, 320Photons for RFE-300-NEW
    elif payload.get() == "CubeCat":
        h_orbit = 455  # km - Satellite height
        wl = 1545e-9  # m - Wavelenght of the downlink
        p_tx = 24.7712  # dBm - Transmited power [300 mW]
        # p_tx = 16.99
        teta_tx = 104e-6  # rad - collimator F220FC-1550
        a_tx = 0  # dB - Optical Transmissor losses (Tx)
        dr = 39e6  # bps - datarate in KIODO, 39Mbps in OSIRIS-FLP for OCAM and some tests to OP
        ppb = 250  # ppb - Photons per bit required bei RFE at BER=1E-3 at first OSIRIS with APD-RFE-100-OLD, 320Photons for RFE-300-NEW
        # diese Formel muss noch durch WL ergnzt werden:   D_tx=0.2; teta_tx = 100E-6 * 0.01/D_tx; % estimate for near-optimum cut-gauss Tx
    else:
        h_orbit = 595  # km - Satellite height
        wl = 1545e-9  # m - Wavelenght of the downlink
        p_tx = 30  # dBm - Transmited power
        teta_tx = 1e-3  # mrad - OSIRISv1: 1.0E-3 oder 1.2E-3 mrad - die Dokumente sagen immer 1,2 aber CF meinte frs CNES-Paper 1,0
        a_tx = -1  # dB - Optical Transmissor losses (Tx)
        dr = 39e6  # bps - datarate in KIODO, 39Mbps in OSIRIS-FLP for OCAM and some tests to OP
        ppb = 250  # ppb - Photons per bit required bei RFE at BER=1E-3 at first OSIRIS with APD-RFE-100-OLD, 320Photons for RFE-300-NEW
        # diese Formel muss noch durch WL ergnzt werden:   D_tx=0.2; teta_tx = 100E-6 * 0.01/D_tx; % estimate for near-optimum cut-gauss Tx

    h_orbit_m = h_orbit * (10**3)  #  m - Satellite height
    # 1W mean was used in FLP-OSIRISv1 experiments with OCAM
    # 100mW or 50mW mean we expect in KIODO, since the 20dBm mentioned in the book might be peak-power

    sigma_jit = 0.85 * teta_tx / 2  # erzeugt dann -3dB BW-loss
    # sigma_jit = 1E-9 # 0.85*teta_tx/2 # erzeugt dann -3dB BW-loss
    # sigma_jit = teta_tx/4 # irrelevant when we set beta later below

    beta = teta_tx**2 / sigma_jit**2 / (8 * math.log(2))
    # beta = 8
    # beta = 2 # produces a pointing loss of -1.7dB
    # beta=1000 # no pointing loss for the plot in fig.10

    ############  RECEIVER SETTINGS  ############   -> Check standalone script for noncam values
    # LOSSES
    a_rx = 0  # dB - Optical Receiver losses (Tx)  -
    a_bw = 0  # dB - Beam Wander losses
    a_sci = 0  # dB - Scintillation losses

    ###########  ANTENA'S DIMENTIONS  ###########
    d_rx_o = 2.5e-3  # m - Diameter Rx-apertur in meter - Infra-FE4.41.0-17
    # d_rx_o = 5.6e-3  # m - Diameter Rx-apertur in meter - Infra-FE5.61.0-
    area_rx = math.pi * (d_rx_o / 2) ** 2
    # m^2 - Area of a fisheye lens based on its aperture

    # alpha = (180/math.pi) * math.asin( (const.R_E+h_ogs)/(const.R_E+h_orbit) * math.sin((90+el)*math.pi/180) )
    # gamma = 90 - el - alpha;
    # leng = math.sqrt( (const.R_E+h_ogs)**2 + (const.R_E+h_orbit_m)**2 - 2 * (const.R_E+h_ogs)*(const.R_E+h_orbit_m)*math.cos(gamma*math.pi/180) )
    if elevation_mode.get() == "Individual":
        a = math
        grad = el * math.pi / 180
    else:
        el = np.arange(5, 90)
        a = np
        grad = np.radians(el)

    leng = a.sqrt(
        (const.R_E + h_ogs) ** 2 * a.sin(grad) ** 2
        + 2 * (h_orbit_m - h_ogs) * (const.R_E + h_ogs)
        + (h_orbit_m - h_ogs) ** 2
    ) - (const.R_E + h_ogs) * a.sin(grad)

    a_fsl = 10 * a.log10((wl / (4 * math.pi * leng)) ** 2)
    # dB - Freespace losses

    a_atm = 10 * a.log10(zenith ** (1.0 / a.sin(math.pi * el / 180)))
    # dB - Athmosperic Attenuation
    # It is using degrees now

    g_tx = 10 * math.log10((3.33 / teta_tx) ** 2)
    # dB - Gain of thetransmissor antena

    # weitere Berechnung - sollte selbes rauskommen:  i_axial = (0.693/pi) * 10**( (a_tx+p_tx) /10)/1000  / (leng*teta_tx/2)**2 # W/m^2
    i_axial = 0.001 * 10 ** (
        (
            p_tx
            + a_tx
            + g_tx
            + a_fsl
            + 10 * math.log10(4 * math.pi * 1 / (wl**2))
        )
        / 10
    )  # W/m^2 - Axial Intensity

    g_rx = 10 * math.log10(4 * math.pi * area_rx / (wl**2))
    # dB - Gain of the receiver antena
    # g_rx = 0

    p_rx = (
        p_tx + a_tx + g_tx + a_fsl + a_bw + a_atm + a_sci + g_rx + a_rx
    )  # dBm - RxPower on RFE with all losses

    p_ogs_mean = p_rx - a_rx
    # dBm - power onto OGS-aperture - no Rx-internal losses
    p_ogs_mean_loss = p_rx
    # dBm - power onto OGS-aperture - WITH Rx-internal losses
    int_ogs_lin = (10 ** ((p_ogs_mean) / 10) / 1000) / area_rx
    int_ogs_lin_loss = (10 ** ((p_ogs_mean_loss) / 10) / 1000) / area_rx
    p_rx_lin = (10 ** (p_rx / 10)) / 1000  # W
    p_rfe_lin = ppb * const.H * const.C * dr / wl  # W

    printer_lb(
        el,
        elevation_mode,
        payload,
        a_tx,
        p_tx,
        ppb,
        teta_tx,
        a_rx,
        leng,
        g_tx,
        a_fsl,
        i_axial,
        area_rx,
        a_atm,
        a_bw,
        g_rx,
        p_rx,
        int_ogs_lin,
        int_ogs_lin_loss,
        p_ogs_mean,
        p_ogs_mean_loss,
        p_rx_lin,
        wl,
        p_rfe_lin,
        a_sci,
    )

    return (el, int_ogs_lin_loss)
