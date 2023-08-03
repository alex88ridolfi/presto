#!/usr/bin/env python
import sys
import numpy as np
from optparse import OptionParser
from presto.binary_psr import binary_psr
from presto.psr_constants import SOL
import presto.psr_utils as pu
import matplotlib.pyplot as plt

full_usage = """
usage:  binary_info.py [options] parfile(s)
  [-h, --help]   : Display this help
  [-p, --plot]   : Show plot of "v" velocity or "p" period
  [-t, --time]   : Duration of the calculation or observation (sec)
  [-s, --start]  : Barycentric MJD for the start of the calculation/observation

  Read a parfile of a binary pulsar and compute min/max observed barycentric
  spin periods or velocities as either a function of the orbit (default),
  or for a prescribed duration of time. Also show basic information about the
  binary. Optionally plot the velocity/periods/range.

  Copyright Scott Ransom <sransom@nrao.edu>, 2023
"""
usage = "usage: %prog [options] parfile(s)"

def main():
    parser = OptionParser(usage)
    parser.add_option("-p", "--plot", type="string", dest="plot", default=None,
                      help="Plot the results ('v' velocity or 'p' period)")
    parser.add_option("-t", "--time", type="float", dest="duration", default=0.0,
                      help="Duration of the calculation or observation (sec)")
    parser.add_option("-s", "--start", type="float", dest="T_start", default=0.0,
                      help="Barycentric MJD for the start of the calculation/observation")
    (opts, args) = parser.parse_args()
    if len(args)==0:
        print(full_usage)
        sys.exit(0)

    for pfile in args:
        # Read the parfile(s)
        psr = binary_psr(pfile)
        if hasattr(psr.par, "BINARY"):
            if opts.T_start==0: opts.T_start = psr.T0
            if opts.duration==0: opts.duration = psr.PBsec
            T_end = opts.T_start + opts.duration / 86400.0
            norbits = (T_end - opts.T_start) / psr.par.PB
            times = np.linspace(opts.T_start, T_end, int(norbits * 1000))
            rvs = psr.radial_velocity(times) # km/s
            ps = psr.par.P0*(1.0 + rvs * 1000.0 / SOL) * 1000 # ms
            print("---------------------------------")
            print(f"PSR:          {psr.par.PSR}")
            print(f"Pspin (ms):   {psr.par.P0 * 1000.0:.6f}")
            print(f"  min (ms):   {ps.min():.6f}")
            print(f"  max (ms):   {ps.max():.6f}")
            print(f" diff (ms):   {ps.max() - ps.min():.6f}")
            print(f"Fspin (Hz):   {1.0/psr.par.P0:.6f}")
            print(f"  min (Hz):   {1000.0 / ps.max():.6f}")
            print(f"  max (Hz):   {1000.0 / ps.min():.6f}")
            print(f" diff (Hz):   {1000.0 / ps.min() - 1000.0 / ps.max():.6f}")
            print(f"Porb (days):  {psr.par.PB:.6f}")
            print(f"Porb (hours): {psr.par.PB * 24:.6f}")
            print(f"Eccentricity: {psr.par.ECC:.6g}")
            print(f"Mcmin (Msun): {pu.companion_mass_limit(psr.par.PB, psr.par.A1):.6f}")
            print(f"Mcmed (Msun): {pu.companion_mass(psr.par.PB, psr.par.A1):.6f}")
            if hasattr(psr.par, "OMDOT"):
                print(f"Mtot (Msun):  {pu.OMDOT_to_Mtot(psr.par.OMDOT, psr.par.PB, psr.par.ECC):.6f}")
            if opts.plot:
                if opts.plot=="v":
                    vals = rvs
                    ylab = "Radial Velocity (km/s)"
                elif opts.plot=="p":
                    vals = ps
                    ylab = "Observed Spin Period (ms)"
                else:
                    print("The only plot choices are 'v' and 'p'.")
                    sys.exit()
                if opts.duration == psr.PBsec:
                    times = np.linspace(0, 1, len(times))
                    xlab = "Orbital Phase"
                elif opts.duration < psr.PBsec:
                    times = np.linspace(0, opts.duration, len(times))
                    xlab = "Seconds"
                else:
                    xlab = "MJD"
                plt.plot(times, vals)
                plt.xlabel(xlab)
                plt.ylabel(ylab)
                plt.show()

if __name__=='__main__':
    main()
    
