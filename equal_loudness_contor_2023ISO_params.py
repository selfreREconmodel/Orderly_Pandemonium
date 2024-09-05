import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt


def iso226(phon, fq=None, sq=False, mirror=0):
    # Ensure phon is treated as an array
    phon = np.atleast_1d(phon)

    # Check input
    if np.any(phon > 80):
        print(
            "Warning: SPL values may not be accurate for loudness levels above 80 phon."
        )
    elif np.any((phon != 0) & (phon < 20)):
        print(
            "Warning: SPL values may not be accurate for loudness levels below 20 phon."
        )

    if fq is not None:
        if np.any((fq < 20) | (fq > 4000)) and np.any(phon > 90):
            print(
                "Warning: ISO 226:2003 is valid for 20-4000 Hz only up to 90 phon. SPL values may be inaccurate."
            )
        elif np.any((fq < 5000) | (fq > 12500)) and np.any(phon > 80):
            print(
                "Warning: ISO 226:2003 is valid for 5000-12500 Hz only up to 80 phon. SPL values may be inaccurate."
            )
        elif np.any(fq > 12500):
            print(
                "Warning: ISO 226:2003 defines loudness levels up to 12.5 kHz. SPL values for frequencies above 12.5 kHz may be inaccurate."
            )
        assert np.all(fq >= 0), "Frequencies must be greater than or equal to 0 Hz."

    # References iso2003
    # params = {
    #     "f": [
    #         20,
    #         25,
    #         31.5,
    #         40,
    #         50,
    #         63,
    #         80,
    #         100,
    #         125,
    #         160,
    #         200,
    #         250,
    #         315,
    #         400,
    #         500,
    #         630,
    #         800,
    #         1000,
    #         1250,
    #         1600,
    #         2000,
    #         2500,
    #         3150,
    #         4000,
    #         5000,
    #         6300,
    #         8000,
    #         10000,
    #         12500,
    #     ],
    #     "alpha_f": [
    #         0.532,
    #         0.506,
    #         0.480,
    #         0.455,
    #         0.432,
    #         0.409,
    #         0.387,
    #         0.367,
    #         0.349,
    #         0.330,
    #         0.315,
    #         0.301,
    #         0.288,
    #         0.276,
    #         0.267,
    #         0.259,
    #         0.253,
    #         0.250,
    #         0.246,
    #         0.244,
    #         0.243,
    #         0.243,
    #         0.243,
    #         0.242,
    #         0.242,
    #         0.245,
    #         0.254,
    #         0.271,
    #         0.301,
    #     ],
    #     "L_U": [
    #         -31.6,
    #         -27.2,
    #         -23.0,
    #         -19.1,
    #         -15.9,
    #         -13.0,
    #         -10.3,
    #         -8.1,
    #         -6.2,
    #         -4.5,
    #         -3.1,
    #         -2.0,
    #         -1.1,
    #         -0.4,
    #         0.0,
    #         0.3,
    #         0.5,
    #         0.0,
    #         -2.7,
    #         -4.1,
    #         -1.0,
    #         1.7,
    #         2.5,
    #         1.2,
    #         -2.1,
    #         -7.1,
    #         -11.2,
    #         -10.7,
    #         -3.1,
    #     ],
    #     "T_f": [
    #         78.5,
    #         68.7,
    #         59.5,
    #         51.1,
    #         44.0,
    #         37.5,
    #         31.5,
    #         26.5,
    #         22.1,
    #         17.9,
    #         14.4,
    #         11.4,
    #         8.6,
    #         6.2,
    #         4.4,
    #         3.0,
    #         2.2,
    #         2.4,
    #         3.5,
    #         1.7,
    #         -1.3,
    #         -4.2,
    #         -6.0,
    #         -5.4,
    #         -1.5,
    #         6.0,
    #         12.6,
    #         13.9,
    #         12.3,
    #     ],
    # }
    # References iso2023

    params = {
        "f": [
            20,
            25,
            31.5,
            40,
            50,
            63,
            80,
            100,
            125,
            160,
            200,
            250,
            315,
            400,
            500,
            630,
            800,
            1000,
            1250,
            1600,
            2000,
            2500,
            3150,
            4000,
            5000,
            6300,
            8000,
            10000,
            12500,
        ],
        "alpha_f": [
            0.635,
            0.602,
            0.569,
            0.537,
            0.509,
            0.482,
            0.456,
            0.433,
            0.412,
            0.391,
            0.373,
            0.357,
            0.343,
            0.330,
            0.320,
            0.311,
            0.303,
            0.300,
            0.295,
            0.292,
            0.290,
            0.290,
            0.289,
            0.289,
            0.289,
            0.293,
            0.303,
            0.323,
            0.354,
        ],
        "L_U": [
            -31.5,
            -27.2,
            -23.1,
            -19.3,
            -16.1,
            -13.1,
            -10.4,
            -8.2,
            -6.3,
            -4.6,
            -3.2,
            -2.1,
            -1.2,
            -0.5,
            0.0,
            0.4,
            0.5,
            0.0,
            -2.7,
            -4.2,
            -1.2,
            1.4,
            2.3,
            1.0,
            -2.3,
            -7.2,
            -11.2,
            -10.9,
            -3.5,
        ],
        "T_f": [
            78.1,
            68.7,
            59.5,
            51.1,
            44.0,
            37.5,
            31.5,
            26.5,
            22.1,
            17.9,
            14.4,
            11.4,
            8.6,
            6.2,
            4.4,
            3.0,
            2.2,
            2.4,
            3.5,
            1.7,
            -1.3,
            -4.2,
            -6.0,
            -5.4,
            -1.5,
            6.0,
            12.6,
            13.9,
            12.3,
        ],
    }

    # Calculate
    if fq is None:
        f = np.array(params["f"])
    else:
        f = np.array(fq)

    phon = np.array(phon)
    out_dims = f.shape + phon.shape
    f_squeeze = np.tile(f.flatten(), (len(phon), 1)).T
    spl_squeeze = np.zeros_like(f_squeeze)

    for p in range(len(phon)):
        if fq is not None:
            if np.any(f_squeeze[:, p] > 12500):
                f_r_extrap = params["f"] + [20000]
                alpha_f_r_extrap = params["alpha_f"] + [params["alpha_f"][mirror]]
                L_U_r_extrap = params["L_U"] + [params["L_U"][mirror]]
                T_f_r_extrap = params["T_f"] + [params["T_f"][mirror]]
            else:
                f_r_extrap = params["f"]
                alpha_f_r_extrap = params["alpha_f"]
                L_U_r_extrap = params["L_U"]
                T_f_r_extrap = params["T_f"]

            alpha_f = interpolate.interp1d(
                f_r_extrap, alpha_f_r_extrap, kind="cubic", fill_value="extrapolate"
            )(f_squeeze[:, p])
            L_U = interpolate.interp1d(
                f_r_extrap, L_U_r_extrap, kind="cubic", fill_value="extrapolate"
            )(f_squeeze[:, p])
            T_f = interpolate.interp1d(
                f_r_extrap, T_f_r_extrap, kind="cubic", fill_value="extrapolate"
            )(f_squeeze[:, p])
        else:
            alpha_f = np.array(params["alpha_f"])
            L_U = np.array(params["L_U"])
            T_f = np.array(params["T_f"])

        A_f = 0.00447 * ((10 ** (0.025 * phon[p])) - 1.15) + (
            (0.4 * (10 ** ((T_f + L_U) / 10 - 9))) ** alpha_f
        )

        if phon[p] > 0:
            spl_squeeze[:, p] = ((10 / alpha_f) * np.log10(A_f)) - L_U + 94
        else:
            spl_squeeze[:, p] = T_f

    f = f_squeeze.reshape(out_dims)
    spl = spl_squeeze.reshape(out_dims)

    if sq:
        f = np.squeeze(f)
        spl = np.squeeze(spl)

    return spl, f, params


# https://discourse.psychopy.org/t/generating-sound/2325/2
def normalize_loudness_direct(phon, fq=None, a=0.34, b=111.8):
    # The plot dosnet resemble the ELC , I am not implementing it for now
    """
    Normalize loudness for the given phon level and frequencies, and calculate corresponding volumes.

    Parameters:
    phon : int or float
        Desired phon level.
    fq : array-like, optional
        Frequencies at which to calculate the SPL and volume.
    a : float, optional
        Calibration value for 0.1V RMS (default is 0.34).
    b : float, optional
        dBSPL for 0.1V RMS (default is 111.8).

    Returns:
    volumes : array-like
        Calculated volume values for the given frequencies.
    frequencies : array-like
        Frequencies corresponding to the calculated volumes.
    """
    # Get SPL values for the given phon level and frequencies
    spl, frequencies, _ = iso226(phon, fq)
    # Calculate volume for each SPL value using the calibration formula
    volumes = ((a / 0.1) / (10 ** (b / 20))) * (10 ** (spl / 20))

    return volumes, frequencies


def plot_equal_loudness_curves(frequencies, spl):
    """
    Plot equal-loudness contours for given frequencies and SPL values.

    Parameters:
    frequencies (numpy.ndarray): Frequencies for the loudness contours.
    spl (numpy.ndarray): SPL values corresponding to the frequencies.
    """
    plt.figure(figsize=(10, 6))

    plt.plot(frequencies.flatten(), spl.flatten(), label="Equal-Loudness Contours")

    plt.xscale("log")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("SPL (dB)")
    plt.title("Equal-Loudness Contours")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    phon_level = 60  # Desired phon level
    frequencies = np.array(np.linspace(20, 20000, 1000))  # Example frequencies

    # Normalize loudness and get frequencies
    normalized_volume, frequencies = normalize_loudness_direct(
        phon=phon_level, fq=frequencies
    )

    print("Frequencies (Hz):", frequencies.flatten())
    print("Normalized Volumes :", normalized_volume.flatten())

    # Plotting equal loudness contours
    phon_levels = [phon_level]
    spl, freqs, params = iso226(phon_levels, fq=frequencies)
    plt.plot(frequencies, normalized_volume)
    plot_equal_loudness_curves(freqs, spl)
