"""
    simo_030-1D_grating.py is a simulation example for EMUstack.

    Copyright (C) 2013  Bjorn Sturmberg

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Example coming once 1.5D EMUstack is created...
"""

import time
import datetime
import numpy as np
import sys
from multiprocessing import Pool
sys.path.append("../backend/")

import objects
import materials
import plotting
from stack import *

start = time.time()

# Remove results of previous simulations.
plotting.clear_previous('.txt')
plotting.clear_previous('.pdf')
plotting.clear_previous('.log')

################ Simulation parameters ################
# Select the number of CPUs to use in simulation.
num_cores = 2

################ Light parameters #####################
wl_1     = 400
wl_2     = 800
no_wl_1  = 2
wavelengths = np.linspace(wl_1, wl_2, no_wl_1)
light_list  = [objects.Light(wl, max_order_PWs = 1, theta = 0.0, phi = 0.0) for wl in wavelengths]

# The period must be consistent throughout a simulation!
period = 300

# Define each layer of the structure, as in last example.
superstrate = objects.ThinFilm(period, height_nm = 'semi_inf',
    material = materials.Air)
grating = objects.NanoStruct('1D_array', period, int(round(0.75*period)), height_nm = 2900, 
    background = materials.Material(1.46 + 0.0j), inclusion_a = materials.Material(5.0 + 0.0j), 
    loss = True, make_mesh_now = True, force_mesh = False, lc_bkg = 0.1, lc2= 3.0)
substrate   = objects.ThinFilm(period, height_nm = 'semi_inf',
    material = materials.Air)

def simulate_stack(light):    
    ################ Evaluate each layer individually ##############
    sim_superstrate = superstrate.calc_modes(light)
    sim_grating = grating.calc_modes(light)
    sim_substrate   = substrate.calc_modes(light)
    ################ Evaluate stacked structure ##############
    """ Now when defining full structure order is critical and
    stack MUST be ordered from bottom to top!
    """
# Put semi-inf substrate below thick mirror so that propagating energy is defined.
    stack = Stack((sim_substrate, sim_grating, sim_superstrate))
    stack.calc_scat(pol = 'TM')

    return stack

pool = Pool(num_cores)
# stacks_list = pool.map(simulate_stack, light_list)
stacks_list = map(simulate_stack, light_list)
# Save full simo data to .npz file for safe keeping!
simotime = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
np.savez('Simo_results'+simotime, stacks_list=stacks_list)

######################## Post Processing ########################
# The total transmission should be zero.
plotting.t_r_a_plots(stacks_list)

######################## Wrapping up ########################
print '\n*******************************************'
# Calculate and record the (real) time taken for simulation,
elapsed = (time.time() - start)
hms     = str(datetime.timedelta(seconds=elapsed))
hms_string = 'Total time for simulation was \n \
    %(hms)s (%(elapsed)12.3f seconds)'% {
            'hms'       : hms,
            'elapsed'   : elapsed, }
print hms_string
print '*******************************************'
print ''

# and store this info.
python_log = open("python_log.log", "w")
python_log.write(hms_string)
python_log.close()