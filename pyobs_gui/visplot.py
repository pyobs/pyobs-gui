from astroplan import Observer
from astropy.time import TimeDelta
import astropy.units as u
import pylab as plt
import numpy as np

from pyobs.utils.time import Time


class VisPlot:
    def __init__(self, figure, observer):
        """Inits the dialog."""
        self.figure = figure
        self.observer = observer  # type: Observer

    def plot(self, coords):
        """Plot visibility plots for the given coordinates starting from now."""

        # clear plot
        self.figure.clf()
        ax = self.figure.add_axes([0.15, 0.35, 0.65, 0.6], polar=True)

        # get now and now+12hrs
        time = Time.now()
        end = time + TimeDelta(24 * u.hour)

        # now start iterating until alt < 0 or next 24 hrs
        x = []
        alt = []
        az = []
        while time < end:
            # convert to alz/az
            altaz = self.observer.altaz(time, coords)
            if altaz.alt < 0:
                break

            # store
            x.append(time.to_datetime())
            alt.append(altaz.alt.degree)
            az.append(altaz.az.degree)

            # next timestep
            time += TimeDelta(15 * u.minute)

        # convert arrays
        x = np.array(plt.date2num(x))
        alt = np.array(alt)
        az = np.array(az)

        font = {"family": "monospace", "weight": "normal", "size": 10}

        plt.rc("font", **font)

        # axes
        ax.set_theta_zero_location("N")
        ax.set_ylim(0.0, 60.0)
        d = "\N{DEGREE SIGN}"
        ax.set_xticks(
            np.deg2rad([0.0, 45.0, 90.0, 135, 180, 225, 270, 315]),
            [
                "N/0" + d,
                "45" + d,
                "E/90" + d,
                "135" + d,
                "S/180" + d,
                "225" + d,
                "W/270" + d,
                "315" + d,
            ],
        )
        ax.set_yticks([20, 45, 60], (70, 45, 30))

        # plot tracks and store handle
        ax.plot_cartesian(np.deg2rad(az), abs(90.0 - alt), linewidth=2, ls="-", c="r")

        # steps are 15min; 4 steps for 1hr
        for i in range(len(x)):
            if i % 4 != 0:
                continue

            # plot it
            ax.plot_cartesian(
                np.deg2rad(az[i]),
                abs(90.0 - alt[i]),
                marker="+",
                mew=2.0,
                ms=6,
                ls="None",
                color="r",
            )
