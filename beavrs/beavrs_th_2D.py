#!/usr/bin/env python

"""
PWR OpenMC Model Generator

Allows for tweaking of specifications for the PWR OpenMC model, producing:
  geometry.xml
  materials.xml
  settings.xml
  plot.xml
  tallies.xml

"""

from __future__ import division

import copy
import math

from templates import *

############## Material paramters ##############

h2oDens = 0.73986
nominalBoronPPM = 975

############## Geometry paramters ##############

## 2-D or 3-D core
core_D = "2-D"
twoDlower = 220.0
twoDhigher = 230.0

## control rod insertion
controlStep = 0                       # bite position is D bank at 213 steps withdraw (228-213=16)

## pincell parameters
pelletOR        = 0.39218  # 
cladIR          = 0.40005  # 
cladOR          = 0.45720  # 
rodGridSide_tb  = 1.24416  #
rodGridSide_i   = 1.21962  #
guideTubeIR     = 0.56134  # 
guideTubeOR     = 0.60198  # 
guideTubeDashIR = 0.50419  # 
guideTubeDashOR = 0.54610  #
controlPoisonOR = 0.43310  #
controlRodIR    = 0.43688  # this is actually the CR clad only
controlRodOR    = 0.48387  # this is actually the CR clad only
burnabs1        = 0.21400  # 
burnabs2        = 0.23051  # 
burnabs3        = 0.24130  # 
burnabs4        = 0.42672  # 
burnabs5        = 0.43688  # 
burnabs6        = 0.48387  # 
burnabs7        = 0.56134  # 
burnabs8        = 0.60198  # 
instrTubeIR     = 0.43688  # no source                           
instrTubeOR     = 0.48387  # no source                           
plenumSpringOR  = 0.06459  # frapcon source - see beavrs_spring.ods

## lattice parameters
pinPitch        = 1.25984  # 
latticePitch    = 21.50364 #
gridstrapSide   = 21.47270 # 

## <!--- axials copied straight from axials_beavrs.ods

## axial paramters    
lowestExtent         =      0.000  # 
bottomSupportPlate   =     20.000  # arbitrary amount of water below core
topSupportPlate      =     25.000  # guessed
bottomLowerNozzle    =     25.000  # same as topSupportPlate
topLowerNozzle       =     35.160  # approx from ******* NDR of 4.088in for lower nozzle height
bottomFuelRod        =     35.160  # same as topLowerNozzle
topLowerThimble      =     36.007  # approx as 1/3 of inch, this is exact ******** NDR value for bottom thimble
bottomFuelStack      =     36.007  # same as topLowerThimble
activeCoreHeight     =    365.760  # provided by D***
topActiveCore        =    401.767  # bottomFuelStack + activeCoreHeight
botBurnAbs           =     41.087  # approx from ***** NDR of 1.987in for space between bot of BAs and bot of active fuel
   
# from Watts Bar Unit 2 safety analysis report   
topFuelRod           =    423.272  # fig 4.2-3 from Watts Bar Unit 2 safety analysis report
topPlenum            =    421.223  # fig 4.2-3 from Watts Bar Unit 2 safety analysis report
bottomUpperNozzle    =    426.617  # fig 4.2-3 from Watts Bar Unit 2 safety analysis report
topUpperNozzle       =    435.444  # fig 4.2-3 from Watts Bar Unit 2 safety analysis report
                       
highestExtent        =    455.444  # arbitrary amount of water above core
   
# grid z planes (centers provided by D***)  (heights 1.65 top/bottom, 2.25 intermediate)   
grid1Center          =     39.974  # bottomFuelStack + 1.562in
grid1bot             =     37.879  # grid1Center - 1.65/2
grid1top             =     42.070  # grid1Center + 1.65/2
grid2Center          =    102.021  # bottomFuelStack + 25.990in
grid2bot             =     99.164  # grid2Center - 2.25/2
grid2top             =    104.879  # grid2Center + 2.25/2
grid3Center          =    154.218  # bottomFuelStack + 46.540in
grid3bot             =    151.361  # grid3Center - 2.25/2
grid3top             =    157.076  # grid3Center + 2.25/2
grid4Center          =    206.415  # bottomFuelStack + 67.090in
grid4bot             =    203.558  # grid4Center - 2.25/2
grid4top             =    209.273  # grid4Center + 2.25/2
grid5Center          =    258.612  # bottomFuelStack + 87.640in
grid5bot             =    255.755  # grid5Center - 2.25/2
grid5top             =    261.470  # grid5Center + 2.25/2
grid6Center          =    310.809  # bottomFuelStack + 108.190in
grid6bot             =    307.952  # grid6Center - 2.25/2
grid6top             =    313.667  # grid6Center + 2.25/2
grid7Center          =    363.006  # bottomFuelStack + 128.740in
grid7bot             =    360.149  # grid7Center - 2.25/2
grid7top             =    365.864  # grid7Center + 2.25/2
grid8Center          =    414.624  # bottomFuelStack + 149.062in
grid8bot             =    412.529  # grid8Center - 1.65/2
grid8top             =    416.720  # grid8Center + 1.65/2
   
# control rod step heights   
step0H               =     45.079  # chosen to match the step size calculated for intervals between other grids
step36H              =    102.021  # grid2Center
step69H              =    154.218  # grid3Center
step102H             =    206.415  # grid4Center
step135H             =    258.612  # grid5Center
step168H             =    310.809  # grid6Center
step201H             =    363.006  # grid7Center
step228H             =    405.713  # set using calculated step width (27*stepWidth + step201H)
stepWidth            =    1.58173  # calculated from grid center planes

## -- axials copied straight from axials_beavrs.ods -->

## radial paramters
coreBarrelIR       = 187.9600 # Fig 2.1 from NDR 2-8              
coreBarrelOR       = 193.6750 # Fig 2.1 from NDR 2-8              
baffleWidth        =   2.2225 # Fig 2.1 from NDR 2-8              
rpvIR              = 230.0
rpvOR              = 251.9

neutronShieldOR    = 199.3900 # coreBarrelOR+2 find real number    TODO
neutronShield_NWbot_SEtop = "1 {0} 0 0".format(math.tan(math.pi/3))
neutronShield_NWtop_SEbot = "1 {0} 0 0".format(math.tan(math.pi/6))
neutronShield_NEbot_SWtop = "1 {0} 0 0".format(math.tan(-math.pi/3))
neutronShield_NEtop_SWbot = "1 {0} 0 0".format(math.tan(-math.pi/6))

## cmfd parameters
cmfd_pin_to_box_factor = 1.0
cmfd_albedo = "0.0 0.0 0.0 0.0 1.0 1.0"
cmfd_mesh_dim = 17
cmfd_axial_dim = 5
cmfd_map = """
      1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
      1 1 1 1 1 2 2 2 2 2 2 2 1 1 1 1 1
      1 1 1 2 2 2 2 2 2 2 2 2 2 2 1 1 1
      1 1 2 2 2 2 2 2 2 2 2 2 2 2 2 1 1
      1 1 2 2 2 2 2 2 2 2 2 2 2 2 2 1 1
      1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 1
      1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 1
      1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 1
      1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 1
      1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 1
      1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 1
      1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 1
      1 1 2 2 2 2 2 2 2 2 2 2 2 2 2 1 1
      1 1 2 2 2 2 2 2 2 2 2 2 2 2 2 1 1
      1 1 1 2 2 2 2 2 2 2 2 2 2 2 1 1 1
      1 1 1 1 1 2 2 2 2 2 2 2 1 1 1 1 1
      1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1"""
cmfd_energy = "0.0 0.625e-6 20.0"
cmfd_begin = 5
cmfd_active_flush = 81
cmfd_keff_tol = 99.9
cmfd_feedback = ".true."

def init_data():
  """All model parameters set here

  Materials, surfaces, cells, and lattices are defined here and automatically written
  to the proper files later.  Dictionary keys need to match those in the templates.

  The order each item is written is the order of appearance as written below

  Notes about core construction:
    The entire axial extent for each pincell is constructed in universes, and then added to fuel assembly lattices
    The fuel assembly lattices are then added to one master core lattice


  """

  global cmfd_axial_dim

  matIDs  = set()
  surfIDs = set()
  cellIDs = set()
  univIDs = set()
  plotIDs = set()

  ass_list = [                   'L1' , 'K1' , 'J1' , 'H1' , 'G1' , 'F1' , 'E1' ,
                   'N2' , 'M2' , 'L2' , 'K2' , 'J2' , 'H2' , 'G2' , 'F2' , 'E2' , 'D2' , 'C2',
            'P3' , 'N3' , 'M3' , 'L3' , 'K3' , 'J3' , 'H3' , 'G3' , 'F3' , 'E3' , 'D3' , 'C3' , 'B3',
            'P4' , 'N4' , 'M4' , 'L4' , 'K4' , 'J4' , 'H4' , 'G4' , 'F4' , 'E4' , 'D4' , 'C4' , 'B4',
     'R5' , 'P5' , 'N5' , 'M5' , 'L5' , 'K5' , 'J5' , 'H5' , 'G5' , 'F5' , 'E5' , 'D5' , 'C5' , 'B5' , 'A5',
     'R6' , 'P6' , 'N6' , 'M6' , 'L6' , 'K6' , 'J6' , 'H6' , 'G6' , 'F6' , 'E6' , 'D6' , 'C6' , 'B6' , 'A6',
     'R7' , 'P7' , 'N7' , 'M7' , 'L7' , 'K7' , 'J7' , 'H7' , 'G7' , 'F7' , 'E7' , 'D7' , 'C7' , 'B7' , 'A7',
     'R8' , 'P8' , 'N8' , 'M8' , 'L8' , 'K8' , 'J8' , 'H8' , 'G8' , 'F8' , 'E8' , 'D8' , 'C8' , 'B8' , 'A8',
     'R9' , 'P9' , 'N9' , 'M9' , 'L9' , 'K9' , 'J9' , 'H9' , 'G9' , 'F9' , 'E9' , 'D9' , 'C9' , 'B9' , 'A9',
     'R10', 'P10', 'N10', 'M10', 'L10', 'K10', 'J10', 'H10', 'G10', 'F10', 'E10', 'D10', 'C10', 'B10', 'A10',
     'R11', 'P11', 'N11', 'M11', 'L11', 'K11', 'J11', 'H11', 'G11', 'F11', 'E11', 'D11', 'C11', 'B11', 'A11',
            'P12', 'N12', 'M12', 'L12', 'K12', 'J12', 'H12', 'G12', 'F12', 'E12', 'D12', 'C12', 'B12',
            'P13', 'N13', 'M13', 'L13', 'K13', 'J13', 'H13', 'G13', 'F13', 'E13', 'D13', 'C13', 'B13',
                   'N14', 'M14', 'L14', 'K14', 'J14', 'H14', 'G14', 'F14', 'E14', 'D14', 'C14',
                                 'L15', 'K15', 'J15', 'H15', 'G15', 'F15', 'E15']

  ass_format = []
  for i in ass_list:
   if len(i) == 2:
     ass_format.append(i[0]+'___'+i[1])
   else:
     ass_format.append(i[0]+'__'+i[1:])

  # create material indexing up front
  # fix dummy and baffle to 0
  mat_offset = 1
  mat_index_dict = {
 'dummy': 0,
 'bafn_': 0,
 'bafne': 0,
 'bfcne': 0,
 'bafe_': 0,
 'bafse': 0,
 'bfcse': 0,
 'bafs_': 0,
 'bafsw': 0,
 'bfcsw': 0,
 'bafw_': 0,
 'bafnw': 0,
 'bfcnw': 0 }

  for i in ass_format:
    mat_index_dict.update({i:ass_format.index(i)+1+mat_offset})

  mat_index = coreLattice_t.format(**mat_index_dict)
 
  print mat_index
     

  ################## materials ##################
  print 'Creating Materials...'

  mo = {'n': 0}
  mats = {}

  from boron_ppm import Water

  h2o = Water()

  borwatmats = h2o.get_water_mats(h2oDens,nominalBoronPPM)
# h2o.print_latex()

  mats['water-mod'] =   { 'order':    inc_order(mo),
                              'comment':  "Moderator",
                              'id':       new_id(matIDs),
                              'density':  '{den:8.6f}'.format(den=h2o.rhoBW), 'unit': 'g/cc',
                              'nuclides': [ {'n':'B-10',   'xs':'71c','woao':'ao','a':h2o.NB10},
                                            {'n':'B-11',   'xs':'71c','woao':'ao','a':h2o.NB11},
                                            {'n':'H-1',    'xs':'71c','woao':'ao','a':h2o.NH1},
                                            {'n':'H-2',    'xs':'71c','woao':'ao','a':h2o.NH2},
                                            {'n':'O-16',   'xs':'71c','woao':'ao','a':h2o.NO16},
                                            {'n':'O-17',   'xs':'71c','woao':'ao','a':h2o.NO17+h2o.NO18},],
                              'sab':      [ {'name': 'lwtr', 'xs': '15t'}]}

  for ass_id in ass_list:
    mats['water-cool'+ass_id] =   { 'order':    inc_order(mo),
                              'comment':  "Coolant Bundle " + ass_id,
                              'id':       new_id(matIDs),
                              'density':  '{den:8.6f}'.format(den=h2o.rhoBW), 'unit': 'g/cc',
                              'nuclides': [ {'n':'B-10',   'xs':'71c','woao':'ao','a':h2o.NB10},
                                            {'n':'B-11',   'xs':'71c','woao':'ao','a':h2o.NB11},
                                            {'n':'H-1',    'xs':'71c','woao':'ao','a':h2o.NH1},
                                            {'n':'H-2',    'xs':'71c','woao':'ao','a':h2o.NH2},
                                            {'n':'O-16',   'xs':'71c','woao':'ao','a':h2o.NO16},
                                            {'n':'O-17',   'xs':'71c','woao':'ao','a':h2o.NO17+h2o.NO18},],
                              'sab':      [ {'name': 'lwtr', 'xs': '15t'}]}

  mats['helium'] =          { 'order':    inc_order(mo),
                              'comment':  "Helium for gap",
                              'id':       new_id(matIDs),
                              'density':  0.001598, 'unit': 'g/cc',
                              'nuclides': [ {'n':'He-4',  'xs':'71c','woao':'ao','a':2.4044e-04},]}

  mats['air'] =             { 'order':    inc_order(mo),
                              'comment':  "Air for instrument tubes",
                              'id':       new_id(matIDs),
                              'density':  0.006160, 'unit': 'g/cc',
                              'nuclides': [ {'n':'C-Nat',  'xs':'71c','woao':'ao','a':6.8296E-09},
                                            {'n':'O-16',  'xs':'71c','woao':'ao','a':5.2864e-06},
                                            {'n':'O-17',  'xs':'71c','woao':'ao','a':1.2877E-08},
                                            {'n':'N-14',  'xs':'71c','woao':'ao','a':1.9681e-05},
                                            {'n':'N-15',  'xs':'71c','woao':'ao','a':7.1900e-08},
                                            {'n':'Ar-36', 'xs':'71c','woao':'ao','a':7.9414e-10},
                                            {'n':'Ar-38', 'xs':'71c','woao':'ao','a':1.4915e-10},
                                            {'n':'Ar-40', 'xs':'71c','woao':'ao','a':2.3506e-07},]}

  mats['inconel'] =         { 'order':    inc_order(mo),
                              'comment':  "Inconel 718",
                              'id':       new_id(matIDs),
                              'density':  8.2, 'unit': 'g/cc',
                              'nuclides': [ {'n':'Si-28','xs':'71c','woao':'ao','a':5.6753E-04},
                                            {'n':'Si-29','xs':'71c','woao':'ao','a':2.8831E-05},
                                            {'n':'Si-30','xs':'71c','woao':'ao','a':1.9028E-05},
                                            {'n':'Cr-50','xs':'71c','woao':'ao','a':7.8239E-04},
                                            {'n':'Cr-52','xs':'71c','woao':'ao','a':1.5088E-02},
                                            {'n':'Cr-53','xs':'71c','woao':'ao','a':1.7108E-03},
                                            {'n':'Cr-54','xs':'71c','woao':'ao','a':4.2586E-04},
                                            {'n':'Mn-55','xs':'71c','woao':'ao','a':7.8201E-04},
                                            {'n':'Fe-54','xs':'71c','woao':'ao','a':1.4797E-03},
                                            {'n':'Fe-56','xs':'71c','woao':'ao','a':2.3229E-02},
                                            {'n':'Fe-57','xs':'71c','woao':'ao','a':5.3645E-04},
                                            {'n':'Fe-58','xs':'71c','woao':'ao','a':7.1392E-05},
                                            {'n':'Ni-58','xs':'71c','woao':'ao','a':2.9320E-02},
                                            {'n':'Ni-60','xs':'71c','woao':'ao','a':1.1294E-02},
                                            {'n':'Ni-61','xs':'71c','woao':'ao','a':4.9094E-04},
                                            {'n':'Ni-62','xs':'71c','woao':'ao','a':1.5653E-03},
                                            {'n':'Ni-64','xs':'71c','woao':'ao','a':3.9864E-04},]}

  mats['SS304'] =           { 'order':    inc_order(mo),
                              'comment':  "Stainless Steel 304",
                              'id':       new_id(matIDs),
                              'density':  8.03, 'unit': 'g/cc',
                              'nuclides': [ {'n':'Si-28','xs':'71c','woao':'ao','a':9.5274E-04},
                                            {'n':'Si-29','xs':'71c','woao':'ao','a':4.8400E-05},
                                            {'n':'Si-30','xs':'71c','woao':'ao','a':3.1943E-05},
                                            {'n':'Cr-50','xs':'71c','woao':'ao','a':7.6778E-04},
                                            {'n':'Cr-52','xs':'71c','woao':'ao','a':1.4806E-02},
                                            {'n':'Cr-53','xs':'71c','woao':'ao','a':1.6789E-03},
                                            {'n':'Cr-54','xs':'71c','woao':'ao','a':4.1791E-04},
                                            {'n':'Mn-55','xs':'71c','woao':'ao','a':1.7604E-03},
                                            {'n':'Fe-54','xs':'71c','woao':'ao','a':3.4620E-03},
                                            {'n':'Fe-56','xs':'71c','woao':'ao','a':5.4345E-02},
                                            {'n':'Fe-57','xs':'71c','woao':'ao','a':1.2551E-03},
                                            {'n':'Fe-58','xs':'71c','woao':'ao','a':1.6703E-04},
                                            {'n':'Ni-58','xs':'71c','woao':'ao','a':5.6089E-03},
                                            {'n':'Ni-60','xs':'71c','woao':'ao','a':2.1605E-03},
                                            {'n':'Ni-61','xs':'71c','woao':'ao','a':9.3917E-05},
                                            {'n':'Ni-62','xs':'71c','woao':'ao','a':2.9945E-04},
                                            {'n':'Ni-64','xs':'71c','woao':'ao','a':7.6261E-05},]}
                                            
  mats['carbon steel'] =    { 'order':    inc_order(mo),
                              'comment':  "Carbon Steel ASTM A533 Grade B",
                              'id':       new_id(matIDs),
                              'density':  7.8, 'unit': 'g/cc',
                              'nuclides': [ {'n':'C-Nat','xs':'71c','woao':'ao','a':9.7772E-04},
                                            {'n':'Si-28','xs':'71c','woao':'ao','a':4.2417E-04},
                                            {'n':'Si-29','xs':'71c','woao':'ao','a':2.1548E-05},
                                            {'n':'Si-30','xs':'71c','woao':'ao','a':1.4221E-05},
                                            {'n':'Mn-55','xs':'71c','woao':'ao','a':1.1329E-03},
                                            {'n':'P-31','xs':'71c','woao':'ao','a':3.7913E-05},
                                            {'n':'Mo-92','xs':'71c','woao':'ao','a':3.7965E-05},
                                            {'n':'Mo-94','xs':'71c','woao':'ao','a':2.3725E-05},
                                            {'n':'Mo-96','xs':'71c','woao':'ao','a':4.2875E-05},
                                            {'n':'Mo-97','xs':'71c','woao':'ao','a':2.4573E-05},
                                            {'n':'Mo-98','xs':'71c','woao':'ao','a':6.2179E-05},
                                            {'n':'Mo-100','xs':'71c','woao':'ao','a':2.4856E-05},
                                            {'n':'Fe-54','xs':'71c','woao':'ao','a':4.7714E-03},
                                            {'n':'Fe-56','xs':'71c','woao':'ao','a':7.4900E-02},
                                            {'n':'Fe-57','xs':'71c','woao':'ao','a':1.7298E-03},
                                            {'n':'Fe-58','xs':'71c','woao':'ao','a':2.3020E-04},
                                            {'n':'Ni-58','xs':'71c','woao':'ao','a':2.9965E-04},
                                            {'n':'Ni-60','xs':'71c','woao':'ao','a':1.1543E-04},
                                            {'n':'Ni-61','xs':'71c','woao':'ao','a':5.0175E-06},
                                            {'n':'Ni-62','xs':'71c','woao':'ao','a':1.5998E-05},
                                            {'n':'Ni-64','xs':'71c','woao':'ao','a':4.0742E-06},]}

  mats['zirc'] =            { 'order':    inc_order(mo),
                              'comment':  "Zircaloy-4",
                              'id':       new_id(matIDs),
                              'density':  6.55, 'unit': 'g/cc',
                              'nuclides': [ {'n':'O-16','xs':'71c','woao':'ao','a':3.0743E-04},
                                            {'n':'O-17','xs':'71c','woao':'ao','a':7.4887E-07},
                                            {'n':'Cr-50','xs':'71c','woao':'ao','a':3.2962E-06},
                                            {'n':'Cr-52','xs':'71c','woao':'ao','a':6.3564E-05},
                                            {'n':'Cr-53','xs':'71c','woao':'ao','a':7.2076E-06},
                                            {'n':'Cr-54','xs':'71c','woao':'ao','a':1.7941E-06},
                                            {'n':'Fe-54','xs':'71c','woao':'ao','a':8.6699E-06},
                                            {'n':'Fe-56','xs':'71c','woao':'ao','a':1.3610E-04},
                                            {'n':'Fe-57','xs':'71c','woao':'ao','a':3.1431E-06},
                                            {'n':'Fe-58','xs':'71c','woao':'ao','a':4.1829E-07},
                                            {'n':'Zr-90','xs':'71c','woao':'ao','a':2.1827E-02},
                                            {'n':'Zr-91','xs':'71c','woao':'ao','a':4.7600E-03},
                                            {'n':'Zr-92','xs':'71c','woao':'ao','a':7.2758E-03},
                                            {'n':'Zr-94','xs':'71c','woao':'ao','a':7.3734E-03},
                                            {'n':'Zr-96','xs':'71c','woao':'ao','a':1.1879E-03},
                                            {'n':'Sn-112','xs':'71c','woao':'ao','a':4.6735E-06},
                                            {'n':'Sn-114','xs':'71c','woao':'ao','a':3.1799E-06},
                                            {'n':'Sn-115','xs':'71c','woao':'ao','a':1.6381E-06},
                                            {'n':'Sn-116','xs':'71c','woao':'ao','a':7.0055E-05},
                                            {'n':'Sn-117','xs':'71c','woao':'ao','a':3.7003E-05},
                                            {'n':'Sn-118','xs':'71c','woao':'ao','a':1.1669E-04},
                                            {'n':'Sn-119','xs':'71c','woao':'ao','a':4.1387E-05},
                                            {'n':'Sn-120','xs':'71c','woao':'ao','a':1.5697E-04},
                                            {'n':'Sn-122','xs':'71c','woao':'ao','a':2.2308E-05},
                                            {'n':'Sn-124','xs':'71c','woao':'ao','a':2.7897E-05},]}

  mats['UO2 1.6'] =         { 'order':    inc_order(mo),
                              'comment':  "UO2 Fuel 1.6 w/o",
                              'id':       new_id(matIDs),
                              'density':  10.31362, 'unit': 'g/cc',
                              'nuclides': [ {'n':'U-234','xs':'71c','woao':'ao','a':3.0131E-06},
                                            {'n':'U-235','xs':'71c','woao':'ao','a':3.7503E-04},
                                            {'n':'U-238','xs':'71c','woao':'ao','a':2.2626E-02},
                                            {'n':'O-16','xs':'71c','woao':'ao','a':4.5896E-02},
                                            {'n':'O-17','xs':'71c','woao':'ao','a':1.1180E-04},]}

  mats['UO2 2.4'] =         { 'order':    inc_order(mo),
                              'comment':  "UO2 Fuel 2.4 w/o",
                              'id':       new_id(matIDs),
                              'density':  10.29769, 'unit': 'g/cc',
                              'nuclides': [ {'n':'U-234','xs':'71c','woao':'ao','a':4.4843e-06},
                                            {'n':'U-235','xs':'71c','woao':'ao','a':5.5815e-04},
                                            {'n':'U-238','xs':'71c','woao':'ao','a':2.2408e-02},
                                            {'n':'O-16','xs':'71c','woao':'ao','a':4.5829e-02},
                                            {'n':'O-17','xs':'71c','woao':'ao','a':1.1164E-04},]}

  mats['UO2 3.1'] =         { 'order':    inc_order(mo),
                              'comment':  "UO2 Fuel 3.1 w/o",
                              'id':       new_id(matIDs),
                              'density':  10.30187, 'unit': 'g/cc',
                              'nuclides': [ {'n':'U-234','xs':'71c','woao':'ao','a':5.7988e-06},
                                            {'n':'U-235','xs':'71c','woao':'ao','a':7.2176e-04},
                                            {'n':'U-238','xs':'71c','woao':'ao','a':2.2254e-02},
                                            {'n':'O-16','xs':'71c','woao':'ao','a':4.5851e-02},
                                            {'n':'O-17','xs':'71c','woao':'ao','a':1.1169E-04},]}

  mats['control rod'] =     { 'order':    inc_order(mo),
                              'comment':  "Ag-In-Cd Control Rod",
                              'id':       new_id(matIDs),
                              'density':  10.16, 'unit': 'g/cc',
                              'nuclides': [ {'n':'Ag-107','xs':'71c','woao':'ao','a':2.3523E-02},
                                            {'n':'Ag-109','xs':'71c','woao':'ao','a':2.1854E-02},
                                            {'n':'In-113','xs':'71c','woao':'ao','a':3.4291E-04},
                                            {'n':'In-115','xs':'71c','woao':'ao','a':7.6504E-03},
                                            {'n':'Cd-106','xs':'71c','woao':'ao','a':3.4019E-05},
                                            {'n':'Cd-108','xs':'71c','woao':'ao','a':2.4221E-05},
                                            {'n':'Cd-110','xs':'71c','woao':'ao','a':3.3991E-04},
                                            {'n':'Cd-111','xs':'71c','woao':'ao','a':3.4835E-04},
                                            {'n':'Cd-112','xs':'71c','woao':'ao','a':6.5669E-04},
                                            {'n':'Cd-113','xs':'71c','woao':'ao','a':3.3257E-04},
                                            {'n':'Cd-114','xs':'71c','woao':'ao','a':7.8188E-04},
                                            {'n':'Cd-116','xs':'71c','woao':'ao','a':2.0384E-04},]}

  mats['borosilicate'] =    { 'order':    inc_order(mo),
                              'comment':  "Borosilicate Glass in BA rod",
                              'id':       new_id(matIDs),
                              'density':  2.26, 'unit': 'g/cc',
                              'nuclides': [ {'n':'B-10','xs':'71c','woao':'ao','a':9.6506E-04},
                                            {'n':'B-11','xs':'71c','woao':'ao','a':3.9189E-03},
                                            {'n':'O-16','xs':'71c','woao':'ao','a':4.6511E-02},
                                            {'n':'O-17','xs':'71c','woao':'ao','a':1.1330E-04},
                                            {'n':'Al-27','xs':'71c','woao':'ao','a':1.7352E-03},
                                            {'n':'Si-28','xs':'71c','woao':'ao','a':1.6924E-02},
                                            {'n':'Si-29','xs':'71c','woao':'ao','a':8.5977E-04},
                                            {'n':'Si-30','xs':'71c','woao':'ao','a':5.6743E-04},]}
  
  ################## surfaces ##################
  print 'Creating pin surfaces...'

  so = {'n': 0}
  surfs = {}
  surfs['dummy outer'] =        { 'order':   inc_order(so),
                                  'section': comm_t.format("Pincell surfaces"),
                                  'comm':    comm_t.format("dummy outer boundary"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"sphere"',
                                  'coeffs':  '0.0 0.0 0.0 4000',}
  surfs['pellet OR'] =          { 'order':   inc_order(so),
                                  'comm':    comm_t.format("pellet OR"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(pelletOR)}
  surfs['plenum spring OR'] =   { 'order':   inc_order(so),
                                  'comm':    comm_t.format("fuel rod plenum spring OR"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(plenumSpringOR)}
  surfs['clad IR'] =            { 'order':   inc_order(so),
                                  'comm':    comm_t.format("clad IR"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(cladIR)}
  surfs['clad OR'] =            { 'order':   inc_order(so),
                                  'comm':    comm_t.format("clad OR"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(cladOR)}
  surfs['guide tube IR'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("guide tube IR above dashpot"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(guideTubeIR)}
  surfs['guide tube OR'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("guide tube OR above dashpot"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(guideTubeOR)}
  surfs['GT dashpot IR'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("guide tube IR at dashpot"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(guideTubeDashIR)}
  surfs['GT dashpot OR'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("guide tube OR at dashpot"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(guideTubeDashOR)}
  surfs['burnabs rad 1'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("burnable absorber rod inner radius 1"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(burnabs1)}
  surfs['burnabs rad 2'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("burnable absorber rod inner radius 2"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(burnabs2)}
  surfs['burnabs rad 3'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("burnable absorber rod inner radius 3"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(burnabs3)}
  surfs['burnabs rad 4'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("burnable absorber rod inner radius 4"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(burnabs4)}
  surfs['burnabs rad 5'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("burnable absorber rod inner radius 5"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(burnabs5)}
  surfs['burnabs rad 6'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("burnable absorber rod inner radius 6"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(burnabs6)}
  surfs['burnabs rad 7'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("burnable absorber rod inner radius 7"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(burnabs7)}
  surfs['burnabs rad 8'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("burnable absorber rod inner radius 8"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(burnabs8)}
  surfs['instr tube IR'] =         copy.copy(surfs['burnabs rad 5'])
  surfs['instr tube IR']['dupe'] = True
  surfs['instr tube OR'] =         copy.copy(surfs['burnabs rad 6'])
  surfs['instr tube OR']['dupe'] = True 


  # lattice surfaces
  surfs['lat box xtop'] =            { 'order':   inc_order(so),
                                  'section': comm_t.format("Lattice surfaces"),
                                  'comm':    comm_t.format("lattice X max"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"x-plane"',
                                  'coeffs':  '{0:0<8.6}'.format(17*pinPitch/2)}
  surfs['lat box xbot'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("lattice X min"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"x-plane"',
                                  'coeffs':  '-{0:0<8.6}'.format(17*pinPitch/2)}
  surfs['lat box ytop'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("lattice Y max"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"y-plane"',
                                  'coeffs':  '{0:0<8.6}'.format(17*pinPitch/2)}
  surfs['lat box ybot'] =      { 'order':   inc_order(so),
                                  'comm':    comm_t.format("lattice Y min"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"y-plane"',
                                  'coeffs':  '-{0:0<8.6}'.format(17*pinPitch/2)}
  # axial surfaces
  surfs['lowest extent'] =      { 'order':   inc_order(so),
                                  'section': comm_t.format("Axial surfaces"),
                                  'comm':    comm_t.format("lowest extent"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-plane"',
                                  'coeffs':  '{0:0<8.6}'.format(lowestExtent)}
  surfs['highest extent'] =     { 'order':   inc_order(so),
                                  'comm':    comm_t.format("highest extent"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-plane"',
                                  'coeffs':  '{0:0<8.6}'.format(highestExtent)}

  # outer radial surfaces
  surfs['core barrel IR'] =     { 'order':   inc_order(so),
                                  'comm':    comm_t.format("core barrel IR"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(coreBarrelIR)}
  surfs['core barrel OR'] =     { 'order':   inc_order(so),
                                  'comm':    comm_t.format("core barrel OR"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(coreBarrelOR)}
  surfs['neut shield OR'] =     { 'order':   inc_order(so),
                                  'comm':    comm_t.format("neutron shield OR"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(neutronShieldOR)}
  surfs['neut shield NWbot SEtop'] =     { 'order':   inc_order(so),
                                  'comm':    comm_t.format("neutron shield planes"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"plane"',
                                  'coeffs':  neutronShield_NWbot_SEtop}
  surfs['neut shield NWtop SEbot'] =     { 'order':   inc_order(so),
                                  'comm':    "",
                                  'id':      new_id(surfIDs),
                                  'type':    '"plane"',
                                  'coeffs':  neutronShield_NWtop_SEbot}
  surfs['neut shield NEbot SWtop'] =     { 'order':   inc_order(so),
                                  'comm':    "",
                                  'id':      new_id(surfIDs),
                                  'type':    '"plane"',
                                  'coeffs':  neutronShield_NEbot_SWtop}
  surfs['neut shield NEtop SWbot'] =     { 'order':   inc_order(so),
                                  'comm':    "",
                                  'id':      new_id(surfIDs),
                                  'type':    '"plane"',
                                  'coeffs':  neutronShield_NEtop_SWbot}
  surfs['RPV IR'] =             { 'order':   inc_order(so),
                                  'comm':    comm_t.format("RPV IR"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(rpvIR)}
  surfs['RPV OR'] =             { 'order':   inc_order(so),
                                  'comm':    comm_t.format("RPV OR"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-cylinder"',
                                  'coeffs':  '0.0 0.0 {0:0<8.6}'.format(rpvOR),
                                  'bc':      'vacuum'}
  surfs['upper bound'] =        { 'order':   inc_order(so),
                                  'comm':    comm_t.format("upper problem boundary"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-plane"',
                                  'coeffs':  '{0:0<8.6}'.format(highestExtent),
                                  'bc':      'vacuum'}
  surfs['lower bound'] =        { 'order':   inc_order(so),
                                  'comm':    comm_t.format("lower problem boundary"),
                                  'id':      new_id(surfIDs),
                                  'type':    '"z-plane"',
                                  'coeffs':  '{0:0<8.6}'.format(lowestExtent),
                                  'bc':      'vacuum'}
  if core_D == '2-D':
    surfs['upper bound'].update( {  'coeffs':  '{0:0<8.6}'.format(twoDhigher),
                                    'bc':      'reflective'} )
    surfs['lower bound'].update( {  'coeffs':  '{0:0<8.6}'.format(twoDlower),
                                    'bc':      'reflective'} )


  ################## cells ##################
  print 'Creating pin cells...'

  # (if not a fill cell, set 'fill': None.  if not None, 'mat' is ignored)

  co = {'n': 0}
  cells = {}
  cells['water pin mod'] =          { 'order':   inc_order(co),
                                  'section': comm_t.format("Empty water pincell universes"),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}
  for ass_id in ass_list:
   cells['water pin cool'+ass_id] =          { 'order':   inc_order(co),
                                  'section': "",
                                  'comm':    comm_t.format("Empty water pincell universe Bundle "+ass_id),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-cool'+ass_id]['id'],
                                  'fill':    None,
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}
  # Loop around all assemblies
  for ass_id in ass_list:

    # GUIDE TUBE PIN CELLS
    make_pin('GT empty'+ass_id,'Pincells Bundle '+ass_id,co,cells,new_id(univIDs),cellIDs,
              [surfs['guide tube IR']['id'],
               surfs['guide tube OR']['id']],
              [(mats['water-mod']['id'],"empty guide tube"),
               (mats['zirc']['id'],""),
               (mats['water-cool'+ass_id]['id'],""),])

    # final combination of all axial pieces for empty guide tube
#   stackSurfs = [surfs['lowest extent']['id'],
#                surfs['highest extent']['id']]
#   make_stack('GT empty stack'+ass_id,co,cells,new_id(univIDs),cellIDs,
#             stackSurfs,
#              [cells['GT empty'+ass_id]['univ']])           # reg
#   make_stack('GT empty stack instr'+ass_id,co,cells,new_id(univIDs),cellIDs,
#             stackSurfs,
#              [cells['GT empty'+ass_id]['univ']])          # reg

    # INSTRUMENT TUBE PIN CELL
    make_pin('GT instr'+ass_id,"",co,cells,new_id(univIDs),cellIDs,
              [surfs['instr tube IR']['id'],
               surfs['instr tube OR']['id'],
               surfs['guide tube IR']['id'],
               surfs['guide tube OR']['id']],
              [(mats['air']['id'],"instr guide tube above dashpot"),
               (mats['zirc']['id'],""),
               (mats['water-mod']['id'],""),
               (mats['zirc']['id'],""),
               (mats['water-cool'+ass_id]['id'],""),])

    # final combination of all axial pieces for instrument tube
#   make_stack('GT instr stack'+ass_id,co,cells,new_id(univIDs),cellIDs,
#             stackSurfs,
#              [cells['GT instr'+ass_id]['univ']])          # reg

    # BURNABLE ABSORBER PIN CELLS
    # These suckers don't go all the way down to the bottom of the fuel rods, but
    # they do extend into the dashpot, ending in the middle of grid 1.

    make_pin('burn abs'+ass_id,"",co,cells,new_id(univIDs),cellIDs,
              [surfs['burnabs rad 1']['id'],
               surfs['burnabs rad 2']['id'],
               surfs['burnabs rad 3']['id'],
               surfs['burnabs rad 4']['id'],
               surfs['burnabs rad 5']['id'],
               surfs['burnabs rad 6']['id'],
               surfs['burnabs rad 7']['id'],
               surfs['burnabs rad 8']['id'],],
              [(mats['air']['id'],"burnable absorber pin"),
               (mats['SS304']['id'],""),
               (mats['air']['id'],""),
               (mats['borosilicate']['id'],""),
               (mats['air']['id'],""),
               (mats['SS304']['id'],""),
               (mats['water-mod']['id'],""),
               (mats['zirc']['id'],""),
               (mats['water-cool'+ass_id]['id'],""),])

    # final combination of all axial pieces burnable absorber rod
    stackSurfsBA = [surfs['lowest extent']['id'],
                    surfs['highest extent']['id']]
                
#   make_stack('burn abs stack'+ass_id,co,cells,new_id(univIDs),cellIDs,
#              stackSurfsBA,
#              [cells['burn abs'+ass_id]['univ']])                  # reg

    # FUEL PIN CELLS
    ## 1.6 w/o
  
    make_pin('Fuel 1.6 w/o'+ass_id,"",co,cells,new_id(univIDs),cellIDs,
              [surfs['pellet OR']['id'],
               surfs['clad IR']['id'],
               surfs['clad OR']['id'],],
              [(mats['UO2 1.6']['id'],"UO2 Fuel 1.6 w/o"),
               (mats['helium']['id'],""),
               (mats['zirc']['id'],""),
               (mats['water-cool'+ass_id]['id'],""),])

    # final combination of all axial pieces for Fuel 1.6 w/o
#   make_stack('Fuel 1.6 w/o stack'+ass_id,co,cells,new_id(univIDs),cellIDs,
#              stackSurfs,
#              [cells['Fuel 1.6 w/o'+ass_id]['univ']])          # reg

    ## 2.4 w/o

    make_pin('Fuel 2.4 w/o'+ass_id,"",co,cells,new_id(univIDs),cellIDs,
              [surfs['pellet OR']['id'],
               surfs['clad IR']['id'],
               surfs['clad OR']['id'],],
              [(mats['UO2 2.4']['id'],"UO2 Fuel 2.4 w/o"),
               (mats['helium']['id'],""),
               (mats['zirc']['id'],""),
               (mats['water-cool'+ass_id]['id'],""),])

    # final combination of all axial pieces for Fuel 2.4 w/o
#   make_stack('Fuel 2.4 w/o stack'+ass_id,co,cells,new_id(univIDs),cellIDs,
#              stackSurfs,
#              [cells['Fuel 2.4 w/o'+ass_id]['univ']])           # reg

    ## 3.1 w/o

    make_pin('Fuel 3.1 w/o'+ass_id,"",co,cells,new_id(univIDs),cellIDs,
              [surfs['pellet OR']['id'],
               surfs['clad IR']['id'],
               surfs['clad OR']['id'],],
              [(mats['UO2 3.1']['id'],"UO2 Fuel 3.1 w/o"),
               (mats['helium']['id'],""),
               (mats['zirc']['id'],""),
               (mats['water-cool'+ass_id]['id'],""),])

    # final combination of all axial pieces for Fuel 3.1 w/o
#   make_stack('Fuel 3.1 w/o stack'+ass_id,co,cells,new_id(univIDs),cellIDs,
#             stackSurfs,
#             [cells['Fuel 3.1 w/o'+ass_id]['univ']])           # reg


################## Baffle construction ##################
  print 'Creating baffle...'

  lo = {'n': 0}
  latts = {}

  # baffle north

  surfs['baffle surf north'] =  { 'order':   inc_order(so),
                                  'section': comm_t.format("Baffle surfaces"),
                                  'comm':    comm_t.format("chosen for 2x2 baffle lattice, so w={0}".format(baffleWidth)),
                                  'id':      new_id(surfIDs),
                                  'type':    '"y-plane"',
                                  'coeffs':  '{0:0<8.5}'.format(latticePitch/4 - baffleWidth)}
  cells['baffle dummy north'] = { 'order':   inc_order(co),
                                  'section': comm_t.format("Baffle cells"),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '{0}'.format(surfs['baffle surf north']['id'])}
  cells['baf dummy north 2'] =  { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baffle dummy north']['univ'],
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0}'.format(surfs['baffle surf north']['id'])}
  latts['baffle north'] =       { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle north"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{0:>3} {0:>3}
{1:>3} {1:>3}
""".format(cells['baffle dummy north']['univ'],cells['water pin mod']['univ'])}
  cells['baffle north'] =       { 'order':   inc_order(co),
                                  'comm':    comm_t.format("north baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle north']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}

  # baffle south

  surfs['baffle surf south'] =  { 'order':   inc_order(so),
                                  'comm':    "",
                                  'id':      new_id(surfIDs),
                                  'type':    '"y-plane"',
                                  'coeffs':  '{0:0<8.6}'.format(baffleWidth - latticePitch/4)}
  cells['baffle dummy south'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '{0}'.format(surfs['baffle surf south']['id'])}
  cells['baf dummy south 2'] =  { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baffle dummy south']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0}'.format(surfs['baffle surf south']['id'])}
  latts['baffle south'] =       { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle south"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{1:>3} {1:>3}
{0:>3} {0:>3}
""".format(cells['baffle dummy south']['univ'],cells['water pin mod']['univ'])}
  cells['baffle south'] =       { 'order':   inc_order(co),
                                  'comm':    comm_t.format("south baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle south']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}

  # bafffle east

  surfs['baffle surf east'] =   { 'order':   inc_order(so),
                                  'comm':    "",
                                  'id':      new_id(surfIDs),
                                  'type':    '"x-plane"',
                                  'coeffs':  '{0:0<8.5}'.format(latticePitch/4 - baffleWidth)}
  cells['baffle dummy east'] =  { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '{0}'.format(surfs['baffle surf east']['id'])}
  cells['baf dummy east 2'] =   { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baffle dummy east']['univ'],
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0}'.format(surfs['baffle surf east']['id'])}
  latts['baffle east'] =       { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle east"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{1:>3} {0:>3}
{1:>3} {0:>3}
""".format(cells['baffle dummy east']['univ'],cells['water pin mod']['univ'])}
  cells['baffle east'] =       { 'order':   inc_order(co),
                                  'comm':    comm_t.format("east baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle east']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}

  # baffle west

  surfs['baffle surf west'] =   { 'order':   inc_order(so),
                                  'comm':    "",
                                  'id':      new_id(surfIDs),
                                  'type':    '"x-plane"',
                                  'coeffs':  '{0:0<8.6}'.format(baffleWidth - latticePitch/4)}
  cells['baffle dummy west'] =  { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '{0}'.format(surfs['baffle surf west']['id'])}
  cells['baf dummy west 2'] =   { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baffle dummy west']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0}'.format(surfs['baffle surf west']['id'])}
  latts['baffle west'] =       { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle west"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{0:>3} {1:>3}
{0:>3} {1:>3}
""".format(cells['baffle dummy west']['univ'],cells['water pin mod']['univ'])}
  cells['baffle west'] =       { 'order':   inc_order(co),
                                  'comm':    comm_t.format("west baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle west']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}


  # baffle NW edges

  cells['baf dummy edges NW'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '{0} -{1}'.format(surfs['baffle surf west']['id'],surfs['baffle surf north']['id'])}
  cells['baf dmy edges NW 2'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy edges NW']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '{0} {1}'.format(surfs['baffle surf west']['id'],surfs['baffle surf north']['id'])}
  cells['baf dmy edges NW 3'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy edges NW']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0}'.format(surfs['baffle surf west']['id'])}
  latts['baffle edges NW'] =    { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle NW edges"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{0:>3} {1:>3}
{2:>3} {3:>3}
""".format(cells['baf dummy edges NW']['univ'],cells['baffle dummy north']['univ'],cells['baffle dummy west']['univ'],cells['water pin mod']['univ'])}
  cells['baffle edges NW'] =       { 'order':   inc_order(co),
                                  'comm':    comm_t.format("NW edges baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle edges NW']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}


  # baffle NE edges

  cells['baf dummy edges NE'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0} -{1}'.format(surfs['baffle surf north']['id'],surfs['baffle surf east']['id'])}
  cells['baf dmy edges NE 2'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy edges NE']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '{0} -{1}'.format(surfs['baffle surf north']['id'],surfs['baffle surf east']['id'])}
  cells['baf dmy edges NE 3'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy edges NE']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '{0}'.format(surfs['baffle surf east']['id'])}
  latts['baffle edges NE'] =    { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle NE edges"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{0:>3} {1:>3}
{2:>3} {3:>3}
""".format(cells['baffle dummy north']['univ'],cells['baf dummy edges NE']['univ'],cells['water pin mod']['univ'],cells['baffle dummy east']['univ'])}
  cells['baffle edges NE'] =       { 'order':   inc_order(co),
                                  'comm':    comm_t.format("NE edges baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle edges NE']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}

  # baffle SW edges

  cells['baf dummy edges SW'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '{0} {1}'.format(surfs['baffle surf south']['id'],surfs['baffle surf west']['id'])}
  cells['baf dmy edges SW 2'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy edges SW']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0} {1}'.format(surfs['baffle surf south']['id'],surfs['baffle surf west']['id'])}
  cells['baf dmy edges SW 3'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy edges SW']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0}'.format(surfs['baffle surf west']['id'])}
  latts['baffle edges SW'] =    { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle SW edges"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{0:>3} {1:>3}
{2:>3} {3:>3}
""".format(cells['baffle dummy west']['univ'],cells['water pin mod']['univ'],cells['baf dummy edges SW']['univ'],cells['baffle dummy south']['univ'])}
  cells['baffle edges SW'] =       { 'order':   inc_order(co),
                                  'comm':    comm_t.format("NE edges baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle edges SW']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}

  # baffle SE edges

  cells['baf dummy edges SE'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '{0} -{1}'.format(surfs['baffle surf south']['id'],surfs['baffle surf east']['id'])}
  cells['baf dmy edges SE 2'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy edges SE']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0} -{1}'.format(surfs['baffle surf south']['id'],surfs['baffle surf east']['id'])}
  cells['baf dmy edges SE 3'] = { 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy edges SE']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '{0}'.format(surfs['baffle surf east']['id'])}
  latts['baffle edges SE'] =    { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle SE edges"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{0:>3} {1:>3}
{2:>3} {3:>3}
""".format(cells['water pin mod']['univ'],cells['baffle dummy east']['univ'],cells['baffle dummy south']['univ'],cells['baf dummy edges SE']['univ'])}
  cells['baffle edges SE'] =       { 'order':   inc_order(co),
                                  'comm':    comm_t.format("NE edges baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle edges SE']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}

  # baffle NW corner

  cells['baf dummy corner NW'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0} -{1}'.format(surfs['baffle surf west']['id'],surfs['baffle surf north']['id'])}
  cells['baf dmy corner NW 2'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy corner NW']['univ'],
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '{0}'.format(surfs['baffle surf west']['id'])}
  cells['baf dmy corner NW 3'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy corner NW']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '{0} -{1}'.format(surfs['baffle surf north']['id'],surfs['baffle surf west']['id'])}
  latts['baffle corner NW'] =   { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle NW corner"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{0:>3} {1:>3}
{1:>3} {1:>3}
""".format(cells['baf dummy corner NW']['univ'],cells['water pin mod']['univ'])}
  cells['baffle corner NW'] =   { 'order':   inc_order(co),
                                  'comm':    comm_t.format("NW corner baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle corner NW']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}

  # baffle NE corner

  cells['baf dummy corner NE'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '{0} -{1}'.format(surfs['baffle surf east']['id'],surfs['baffle surf north']['id'])}
  cells['baf dmy corner NE 2'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy corner NE']['univ'],
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0}'.format(surfs['baffle surf east']['id'])}
  cells['baf dmy corner NE 3'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy corner NE']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '{0} {1}'.format(surfs['baffle surf north']['id'],surfs['baffle surf east']['id'])}
  latts['baffle corner NE'] =   { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle NE corner"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{1:>3} {0:>3}
{1:>3} {1:>3}
""".format(cells['baf dummy corner NE']['univ'],cells['water pin mod']['univ'])}
  cells['baffle corner NE'] =   { 'order':   inc_order(co),
                                  'comm':    comm_t.format("NE corner baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle corner NE']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}

  # baffle SE corner

  cells['baf dummy corner SE'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '{0} {1}'.format(surfs['baffle surf east']['id'],surfs['baffle surf south']['id'])}
  cells['baf dmy corner SE 2'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy corner SE']['univ'],
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0}'.format(surfs['baffle surf east']['id'])}
  cells['baf dmy corner SE 3'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy corner SE']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0} {1}'.format(surfs['baffle surf south']['id'],surfs['baffle surf east']['id'])}
  latts['baffle corner SE'] =   { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle SE corner"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{1:>3} {1:>3}
{1:>3} {0:>3}
""".format(cells['baf dummy corner SE']['univ'],cells['water pin mod']['univ'])}
  cells['baffle corner SE'] =   { 'order':   inc_order(co),
                                  'comm':    comm_t.format("SE corner baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle corner SE']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}

  # baffle SW corner

  cells['baf dummy corner SW'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0} {1}'.format(surfs['baffle surf west']['id'],surfs['baffle surf south']['id'])}
  cells['baf dmy corner SW 2'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy corner SW']['univ'],
                                  'mat':     mats['water-mod']['id'],
                                  'fill':    None,
                                  'surfs':  '{0}'.format(surfs['baffle surf west']['id'])}
  cells['baf dmy corner SW 3'] ={ 'order':   inc_order(co),
                                  'comm':    "",
                                  'id':      new_id(cellIDs),
                                  'univ':    cells['baf dummy corner SW']['univ'],
                                  'mat':     mats['SS304']['id'],
                                  'fill':    None,
                                  'surfs':  '-{0} -{1}'.format(surfs['baffle surf south']['id'],surfs['baffle surf west']['id'])}
  latts['baffle corner SW'] =   { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Baffle SW corner"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     2,
                                  'lleft':   -latticePitch/2,
                                  'width':   latticePitch/2,
                                  'univs':   """
{1:>3} {1:>3}
{0:>3} {1:>3}
""".format(cells['baf dummy corner SW']['univ'],cells['water pin mod']['univ'])}
  cells['baffle corner SW'] =   { 'order':   inc_order(co),
                                  'comm':    comm_t.format("SW corner baffle universe"),
                                  'id':      new_id(cellIDs),
                                  'univ':    new_id(univIDs),
                                  'fill':    latts['baffle corner SW']['id'],
                                  'surfs':  '-{0}'.format(surfs['dummy outer']['id'])}

  baffle = {}
  baffle['bafn_'] = cells['baffle south']['univ']
  baffle['bafs_'] = cells['baffle north']['univ']
  baffle['bafe_'] = cells['baffle west']['univ']
  baffle['bafw_'] = cells['baffle east']['univ']
  baffle['bafnw'] = cells['baffle corner SE']['univ']
  baffle['bafne'] = cells['baffle corner SW']['univ']
  baffle['bafsw'] = cells['baffle corner NE']['univ']
  baffle['bafse'] = cells['baffle corner NW']['univ']
  baffle['bfcnw'] = cells['baffle edges SE']['univ']
  baffle['bfcne'] = cells['baffle edges SW']['univ']
  baffle['bfcsw'] = cells['baffle edges NE']['univ']
  baffle['bfcse'] = cells['baffle edges NW']['univ']

  ################## lattices ##################
  gridSurfaces = None

  latDims = { 'dim':17, 'lleft':-17*pinPitch/2, 'width':pinPitch}

  ## 1.6 w/o assemblies
  print 'Creating 1.6% Assemblies...'
  for cen_type,comment1 in [('GTI',""),('INS'," + instr")]:
    if cen_type == 'GTI':
      sss = "Core Lattice universes"
      assy_list = ['K4','F4','J5','D6','L7','E7','L9','M10','G11','F12','M6','G7','J9',
                   'D9','J11','K8','H10','F2','P6','B10','K14','P10','P8','K10','F10',
                   'F6','H14','H8','J3','G3','N7','N9','C9','J13','G13','C11','N5','L3',
                   'E3','N11','E13','M8','H12']
    else:
      sss = None
      assy_list = ['L5', 'G5', 'E5', 'J7', 'G9', 'E9', 'D10', 'L11', 'E11', 'K12','H6',
                   'F8','K2','B6','F14','H2','K6','B8','C7','L13','C5','H4','D8']

    # No BAs
    for ass_id in assy_list:
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 1.6 w/o'+comment1+ass_id,comm="Assembly 1.6 w/o no BAs"+comment1+ass_id, sect=sss,
                                   univs=pinLattice_t.format(cells['Fuel 1.6 w/o'+ass_id]['univ'],
                                                      a=gtu,  b=gtu,  c=gtu,
                                              d=gtu,                          e=gtu,
                                              f=gtu,  g=gtu,  h=gtu,  i=gtu,  j=gtu,
                                              k=gtu,  l=gtu,  m=cen, n=gtu,  o=gtu,
                                              p=gtu,  q=gtu,  r=gtu,  s=gtu,  t=gtu,
                                              u=gtu,                          v=gtu,
                                                      w=gtu,  x=gtu,  y=gtu,),**latDims)

  ## 2.4 w/o assemblies
  print 'Creating 2.4% Assemblies...'
  for cen_type,comment1 in [('GTI',""),('INS'," + instr")]:

    # No BAs
    if cen_type == 'GTI':
      assy_list = ['M4','D4','M12']
    else:
      assy_list = ['D12']

    for ass_id in assy_list:
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 2.4 w/o'+comment1+ass_id,comm="Assembly 2.4 w/o no BAs"+comment1+ass_id, sect=sss,
                                   univs=pinLattice_t.format(cells['Fuel 2.4 w/o'+ass_id]['univ'],
                                                      a=gtu,  b=gtu,  c=gtu,
                                              d=gtu,                          e=gtu,
                                              f=gtu,  g=gtu,  h=gtu,  i=gtu,  j=gtu,
                                              k=gtu,  l=gtu,  m=cen, n=gtu,  o=gtu,
                                              p=gtu,  q=gtu,  r=gtu,  s=gtu,  t=gtu,
                                              u=gtu,                          v=gtu,
                                                      w=gtu,  x=gtu,  y=gtu,),**latDims)

    # 12 BAs
    comment2 = ' + 12BA'
    if cen_type == 'GTI':
      assy_list = ['J4', 'F5', 'L6', 'J6', 'G6', 'E6', 'D7', 'F8', 'K9', 'F9', 'D9', 'E10', 'K11', 'F11',
                   'J12', 'G4', 'K5', 'H5', 'K7', 'M9', 'G10', 'E8']
    else:
      assy_list = ['M7', 'F7', 'L8', 'L10', 'J10', 'H11', 'G12']

    for ass_id in assy_list:
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 2.4 w/o'+comment1+comment2+ass_id,comm="Assembly 2.4 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 2.4 w/o'+ass_id]['univ'],
                                                    a=bas,  b=gtu,  c=bas,
                                            d=bas,                          e=bas,
                                            f=bas,  g=gtu,  h=gtu,  i=gtu,  j=bas,
                                            k=gtu,  l=gtu,  m=cen,  n=gtu,  o=gtu,
                                            p=bas,  q=gtu,  r=gtu,  s=gtu,  t=bas,
                                            u=bas,                          v=bas,
                                                    w=bas,  x=gtu,  y=bas,),**latDims)

    # 16 BAs
    comment2 = ' + 16BA'
    if cen_type == 'GTI':
      assy_list = ['M3', 'K3', 'L4', 'E4', 'C4', 'M5', 'D5', 'C6', 'G8', 'H9', 'N10', 'M11', 'D11', 'N12', 
                   'L12', 'E12', 'M13', 'K13', 'F13', 'D13', 'H7', 'C10', 'C12']
    else:
      assy_list = ['H3', 'F3', 'D3', 'N4', 'N6', 'N8', 'J8', 'C8', 'H13']

    for ass_id in assy_list:
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 2.4 w/o'+comment1+comment2+ass_id,comm="Assembly 2.4 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 2.4 w/o'+ass_id]['univ'],
                                                    a=bas,  b=bas,  c=bas,
                                            d=bas,                          e=bas,
                                            f=bas,  g=gtu,  h=gtu,  i=gtu,  j=bas,
                                            k=bas,  l=gtu,  m=cen,  n=gtu,  o=bas,
                                            p=bas,  q=gtu,  r=gtu,  s=gtu,  t=bas,
                                            u=bas,                          v=bas,
                                                    w=bas,  x=bas,  y=bas,),**latDims)
    
  ## 3.1 w/o assemblies
  print 'Creating 3.1% Assemblies'
  for cen_type,comment1 in [('GTI',""),('INS'," + instr")]:

    # no BAs
    if cen_type == 'GTI':
      assy_list = ['G1', 'E1', 'C2', 'A5', 'R7', 'R9', 'A11', 'P13', 'G15', 'E15', 'L1', 'P3', 
                   'R5', 'A7', 'C14', 'J15','M2','B4','B12','M14','D2','P12']
    else:
      assy_list = ['J1', 'N2', 'B3', 'A9', 'R11', 'B13', 'N14', 'L15','P4','D14']

    for ass_id in assy_list:
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+ass_id,comm="Assembly 3.1 w/o no BAs"+comment1+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=gtu,  b=gtu,  c=gtu,
                                            d=gtu,                          e=gtu,
                                            f=gtu,  g=gtu,  h=gtu,  i=gtu,  j=gtu,
                                            k=gtu,  l=gtu,  m=cen,  n=gtu,  o=gtu,
                                            p=gtu,  q=gtu,  r=gtu,  s=gtu,  t=gtu,
                                            u=gtu,                          v=gtu,
                                                    w=gtu,  x=gtu,  y=gtu,),**latDims)
    
    # 20 BAs
    comment2 = ' + 20BA'
    if cen_type == 'GTI':
      assy_list = ['G2', 'B9', 'J2', 'P7', 'B7', 'G14']
    else:
      assy_list = [ 'P9', 'J14']

    for ass_id in assy_list:
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+comment2+ass_id,comm="Assembly 3.1 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=bas,  b=bas,  c=bas,
                                            d=bas,                          e=bas,
                                            f=bas,  g=bas,  h=gtu,  i=bas,  j=bas,
                                            k=bas,  l=gtu,  m=cen,  n=gtu,  o=bas,
                                            p=bas,  q=bas,  r=gtu,  s=bas,  t=bas,
                                            u=bas,                          v=bas,
                                                    w=bas,  x=bas,  y=bas,),**latDims)

    # 16 BAs
    comment2 = ' + 16BA'
    if cen_type == 'GTI':
      assy_list = ['L2', 'E2', 'P5', 'B5', 'P11', 'B11', 'L14', 'E14']
    else:
      assy_list = [None]

    for ass_id in assy_list:
      if ass_id == None:
        continue
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+comment2+ass_id,comm="Assembly 3.1 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=bas,  b=bas,  c=bas,
                                            d=bas,                          e=bas,
                                            f=bas,  g=gtu,  h=gtu,  i=gtu,  j=bas,
                                            k=bas,  l=gtu,  m=cen,  n=gtu,  o=bas,
                                            p=bas,  q=gtu,  r=gtu,  s=gtu,  t=bas,
                                            u=bas,                          v=bas,
                                                    w=bas,  x=bas,  y=bas,),**latDims)
    
    # 15 BAs NW
    comment2 = ' + 15BANW'
    if cen_type == 'GTI':
      assy_list = ['N3']
    else:
      assy_list = [None]

    for ass_id in assy_list:
      if ass_id == None:
        continue
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+comment2+ass_id,comm="Assembly 3.1 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=gtu,  b=gtu,  c=gtu,
                                            d=gtu,                          e=gtu,
                                            f=gtu,  g=bas,  h=bas,  i=bas,  j=bas,
                                            k=gtu,  l=bas,  m=cen,  n=bas,  o=bas,
                                            p=gtu,  q=bas,  r=bas,  s=bas,  t=bas,
                                            u=gtu,                          v=bas,
                                                    w=bas,  x=bas,  y=bas,),**latDims)

    # 15 BAs NE
    comment2 = ' + 15BANE'
    if cen_type == 'GTI':
      assy_list = ['C3']
    else:
      assy_list = [None]

    for ass_id in assy_list:
      if ass_id == None:
        continue
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+comment2+ass_id,comm="Assembly 3.1 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=gtu,  b=gtu,  c=gtu,
                                            d=gtu,                          e=gtu,
                                            f=bas,  g=bas,  h=bas,  i=bas,  j=gtu,
                                            k=bas,  l=bas,  m=cen,  n=bas,  o=gtu,
                                            p=bas,  q=bas,  r=bas,  s=bas,  t=gtu,
                                            u=bas,                          v=gtu,
                                                    w=bas,  x=bas,  y=bas,),**latDims)
    
    # 15 BAs SW
    comment2 = ' + 15BASW'
    if cen_type == 'GTI':
      assy_list = [None]
    else:
      assy_list = ['N13']
    for ass_id in assy_list:
      if ass_id == None:
        continue
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+comment2+ass_id,comm="Assembly 3.1 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=bas,  b=bas,  c=bas,
                                            d=gtu,                          e=bas,
                                            f=gtu,  g=bas,  h=bas,  i=bas,  j=bas,
                                            k=gtu,  l=bas,  m=cen,  n=bas,  o=bas,
                                            p=gtu,  q=bas,  r=bas,  s=bas,  t=bas,
                                            u=gtu,                          v=gtu,
                                                    w=gtu,  x=gtu,  y=gtu,),**latDims)
    
    # 15 BAs SE
    comment2 = ' + 15BASE'
    if cen_type == 'GTI':
      assy_list = ['C13']
    else:
      assy_list = [None]
    for ass_id in assy_list:
      if ass_id == None:
        continue
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+comment2+ass_id,comm="Assembly 3.1 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=bas,  b=bas,  c=bas,
                                            d=bas,                          e=gtu,
                                            f=bas,  g=bas,  h=bas,  i=bas,  j=gtu,
                                            k=bas,  l=bas,  m=cen,  n=bas,  o=gtu,
                                            p=bas,  q=bas,  r=bas,  s=bas,  t=gtu,
                                            u=gtu,                          v=gtu,
                                                    w=gtu,  x=gtu,  y=gtu,),**latDims)
    
    # 6 BAs N
    comment2 = ' + 6BAN'
    if cen_type == 'GTI':
      assy_list = ['K1', 'H1']
    else:
      assy_list = ['F1']
    for ass_id in assy_list:
      if ass_id == None:
        continue
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+comment2+ass_id,comm="Assembly 3.1 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=gtu,  b=gtu,  c=gtu,
                                            d=gtu,                          e=gtu,
                                            f=gtu,  g=gtu,  h=gtu,  i=gtu,  j=gtu,
                                            k=gtu,  l=gtu,  m=cen,  n=gtu,  o=gtu,
                                            p=bas,  q=gtu,  r=gtu,  s=gtu,  t=bas,
                                            u=bas,                          v=bas,
                                                    w=bas,  x=gtu,  y=bas,),**latDims)
    
    # 6 BAs S
    comment2 = ' + 6BAS'
    if cen_type == 'GTI':
      assy_list = ['K15', 'F15']
    else:
      assy_list = ['H15']
    for ass_id in assy_list:
      if ass_id == None:
        continue
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+comment2+ass_id,comm="Assembly 3.1 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=bas,  b=gtu,  c=bas,
                                            d=bas,                          e=bas,
                                            f=bas,  g=gtu,  h=gtu,  i=gtu,  j=bas,
                                            k=gtu,  l=gtu,  m=cen,  n=gtu,  o=gtu,
                                            p=gtu,  q=gtu,  r=gtu,  s=gtu,  t=gtu,
                                            u=gtu,                          v=gtu,
                                                    w=gtu,  x=gtu,  y=gtu,),**latDims)

    # 6 BAs W
    comment2 = ' + 6BAW'
    if cen_type == 'GTI':
      assy_list = ['R10']
    else:
      assy_list = ['R6', 'R8']
    for ass_id in assy_list:
      if ass_id == None:
        continue
      gtu = cells['GT empty'+ass_id]['univ']
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']
      ins = cells['GT instr'+ass_id]['univ']
      if cen_type == 'GTI':
        cen = gti
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+comment2+ass_id,comm="Assembly 3.1 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=gtu,  b=gtu,  c=bas,
                                            d=gtu,                          e=bas,
                                            f=gtu,  g=gtu,  h=gtu,  i=gtu,  j=bas,
                                            k=gtu,  l=gtu,  m=cen,  n=gtu,  o=gtu,
                                            p=gtu,  q=gtu,  r=gtu,  s=gtu,  t=bas,
                                            u=gtu,                          v=bas,
                                                    w=gtu,  x=gtu,  y=bas,),**latDims)
    
    # 6 BAs E
    comment2 = ' + 6BAE'
    if cen_type == 'GTI':
      assy_list = ['A6', 'A8', 'A10']
    else:
      assy_list = [None]
    for ass_id in assy_list:                        
      if ass_id == None:                    
        continue                            
      gtu = cells['GT empty'+ass_id]['univ']  
      gti = cells['GT empty'+ass_id]['univ']
      bas = cells['burn abs'+ass_id]['univ']                          
      ins = cells['GT instr'+ass_id]['univ']  
      if cen_type == 'GTI':      
        cen = gti                
      else:
        cen = ins
      newCells = make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, mats['water-cool'+ass_id]['id'],
                  'Fuel 3.1 w/o'+comment1+comment2+ass_id,comm="Assembly 3.1 w/o"+comment1+comment2+ass_id,
                                 univs=pinLattice_t.format(cells['Fuel 3.1 w/o'+ass_id]['univ'],
                                                    a=bas,  b=gtu,  c=gtu,
                                            d=bas,                          e=gtu,
                                            f=bas,  g=gtu,  h=gtu,  i=gtu,  j=gtu,
                                            k=gtu,  l=gtu,  m=cen,  n=gtu,  o=gtu,
                                            p=bas,  q=gtu,  r=gtu,  s=gtu,  t=gtu,
                                            u=bas,                          v=gtu,
                                                    w=bas,  x=gtu,  y=gtu,),**latDims)


  ################## Main Core Lattices ##################
  print 'Creating core...'
  latts['Main Core'] =          { 'order':   inc_order(lo),
                                  'comm':    comm_t.format("Main Core Lattice"),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular',
                                  'dim':     19,
                                  'lleft':   -19*latticePitch/2,
                                  'width':   latticePitch,
                                  'univs':   coreLattice_t.format(
dummy = cells['water pin mod']['univ'],
L___1 = cells['Fuel 3.1 w/oL1 lattice']['univ'],
K___1 = cells['Fuel 3.1 w/o + 6BANK1 lattice']['univ'],
J___1 = cells['Fuel 3.1 w/o + instrJ1 lattice']['univ'], # Sp spare location
H___1 = cells['Fuel 3.1 w/o + 6BANH1 lattice']['univ'],
G___1 = cells['Fuel 3.1 w/oG1 lattice']['univ'],
F___1 = cells['Fuel 3.1 w/o + instr + 6BANF1 lattice']['univ'],
E___1 = cells['Fuel 3.1 w/oE1 lattice']['univ'],
N___2 = cells['Fuel 3.1 w/o + instrN2 lattice']['univ'],
M___2 = cells['Fuel 3.1 w/oM2 lattice']['univ'],
L___2 = cells['Fuel 3.1 w/o + 16BAL2 lattice']['univ'],
K___2 = cells['Fuel 1.6 w/o + instrK2 lattice']['univ'],
J___2 = cells['Fuel 3.1 w/o + 20BAJ2 lattice']['univ'],
H___2 = cells['Fuel 1.6 w/o + instrH2 lattice']['univ'],
G___2 = cells['Fuel 3.1 w/o + 20BAG2 lattice']['univ'], #really should be 23BA1P
F___2 = cells['Fuel 1.6 w/oF2 lattice']['univ'],
E___2 = cells['Fuel 3.1 w/o + 16BAE2 lattice']['univ'],
D___2 = cells['Fuel 3.1 w/oD2 lattice']['univ'],
C___2 = cells['Fuel 3.1 w/oC2 lattice']['univ'],
P___3 = cells['Fuel 3.1 w/oP3 lattice']['univ'],
N___3 = cells['Fuel 3.1 w/o + 15BANWN3 lattice']['univ'],
M___3 = cells['Fuel 2.4 w/o + 16BAM3 lattice']['univ'],
L___3 = cells['Fuel 1.6 w/oL3 lattice']['univ'],
K___3 = cells['Fuel 2.4 w/o + 16BAK3 lattice']['univ'],
J___3 = cells['Fuel 1.6 w/oJ3 lattice']['univ'],
H___3 = cells['Fuel 2.4 w/o + instr + 16BAH3 lattice']['univ'],
G___3 = cells['Fuel 1.6 w/oG3 lattice']['univ'],
F___3 = cells['Fuel 2.4 w/o + instr + 16BAF3 lattice']['univ'],
E___3 = cells['Fuel 1.6 w/oE3 lattice']['univ'],
D___3 = cells['Fuel 2.4 w/o + instr + 16BAD3 lattice']['univ'],
C___3 = cells['Fuel 3.1 w/o + 15BANEC3 lattice']['univ'],
B___3 = cells['Fuel 3.1 w/o + instrB3 lattice']['univ'],
P___4 = cells['Fuel 3.1 w/o + instrP4 lattice']['univ'],
N___4 = cells['Fuel 2.4 w/o + instr + 16BAN4 lattice']['univ'],
M___4 = cells['Fuel 2.4 w/oM4 lattice']['univ'],
L___4 = cells['Fuel 2.4 w/o + 16BAL4 lattice']['univ'],
K___4 = cells['Fuel 1.6 w/oK4 lattice']['univ'],      #4 secondary source rods here
J___4 = cells['Fuel 2.4 w/o + 12BAJ4 lattice']['univ'],
H___4 = cells['Fuel 1.6 w/o + instrH4 lattice']['univ'],
G___4 = cells['Fuel 2.4 w/o + 12BAG4 lattice']['univ'],
F___4 = cells['Fuel 1.6 w/oF4 lattice']['univ'],
E___4 = cells['Fuel 2.4 w/o + 16BAE4 lattice']['univ'],
D___4 = cells['Fuel 2.4 w/oD4 lattice']['univ'],
C___4 = cells['Fuel 2.4 w/o + 16BAC4 lattice']['univ'],
B___4 = cells['Fuel 3.1 w/oB4 lattice']['univ'],
R___5 = cells['Fuel 3.1 w/oR5 lattice']['univ'],
P___5 = cells['Fuel 3.1 w/o + 16BAP5 lattice']['univ'],
N___5 = cells['Fuel 1.6 w/oN5 lattice']['univ'],
M___5 = cells['Fuel 2.4 w/o + 16BAM5 lattice']['univ'],
L___5 = cells['Fuel 1.6 w/o + instrL5 lattice']['univ'],
K___5 = cells['Fuel 2.4 w/o + 12BAK5 lattice']['univ'],
J___5 = cells['Fuel 1.6 w/oJ5 lattice']['univ'],
H___5 = cells['Fuel 2.4 w/o + 12BAH5 lattice']['univ'],
G___5 = cells['Fuel 1.6 w/o + instrG5 lattice']['univ'],
F___5 = cells['Fuel 2.4 w/o + 12BAF5 lattice']['univ'],
E___5 = cells['Fuel 1.6 w/o + instrE5 lattice']['univ'],
D___5 = cells['Fuel 2.4 w/o + 16BAD5 lattice']['univ'],
C___5 = cells['Fuel 1.6 w/o + instrC5 lattice']['univ'],
B___5 = cells['Fuel 3.1 w/o + 16BAB5 lattice']['univ'],
A___5 = cells['Fuel 3.1 w/oA5 lattice']['univ'],
R___6 = cells['Fuel 3.1 w/o + instr + 6BAWR6 lattice']['univ'],
P___6 = cells['Fuel 1.6 w/oP6 lattice']['univ'],
N___6 = cells['Fuel 2.4 w/o + instr + 16BAN6 lattice']['univ'],
M___6 = cells['Fuel 1.6 w/oM6 lattice']['univ'],
L___6 = cells['Fuel 2.4 w/o + 12BAL6 lattice']['univ'],
K___6 = cells['Fuel 1.6 w/o + instrK6 lattice']['univ'],
J___6 = cells['Fuel 2.4 w/o + 12BAJ6 lattice']['univ'],
H___6 = cells['Fuel 1.6 w/o + instrH6 lattice']['univ'],
G___6 = cells['Fuel 2.4 w/o + 12BAG6 lattice']['univ'],
F___6 = cells['Fuel 1.6 w/oF6 lattice']['univ'],
E___6 = cells['Fuel 2.4 w/o + 12BAE6 lattice']['univ'],
D___6 = cells['Fuel 1.6 w/oD6 lattice']['univ'],
C___6 = cells['Fuel 2.4 w/o + 16BAC6 lattice']['univ'],
B___6 = cells['Fuel 1.6 w/o + instrB6 lattice']['univ'],
A___6 = cells['Fuel 3.1 w/o + 6BAEA6 lattice']['univ'],
R___7 = cells['Fuel 3.1 w/oR7 lattice']['univ'],
P___7 = cells['Fuel 3.1 w/o + 20BAP7 lattice']['univ'],
N___7 = cells['Fuel 1.6 w/oN7 lattice']['univ'],
M___7 = cells['Fuel 2.4 w/o + instr + 12BAM7 lattice']['univ'],
L___7 = cells['Fuel 1.6 w/oL7 lattice']['univ'],
K___7 = cells['Fuel 2.4 w/o + 12BAK7 lattice']['univ'],
J___7 = cells['Fuel 1.6 w/o + instrJ7 lattice']['univ'],
H___7 = cells['Fuel 2.4 w/o + 16BAH7 lattice']['univ'],
G___7 = cells['Fuel 1.6 w/oG7 lattice']['univ'],
F___7 = cells['Fuel 2.4 w/o + instr + 12BAF7 lattice']['univ'],
E___7 = cells['Fuel 1.6 w/oE7 lattice']['univ'],
D___7 = cells['Fuel 2.4 w/o + 12BAD7 lattice']['univ'],
C___7 = cells['Fuel 1.6 w/o + instrC7 lattice']['univ'],
B___7 = cells['Fuel 3.1 w/o + 20BAB7 lattice']['univ'],
A___7 = cells['Fuel 3.1 w/oA7 lattice']['univ'], # Sp spare location
R___8 = cells['Fuel 3.1 w/o + instr + 6BAWR8 lattice']['univ'],
P___8 = cells['Fuel 1.6 w/oP8 lattice']['univ'],
N___8 = cells['Fuel 2.4 w/o + instr + 16BAN8 lattice']['univ'],
M___8 = cells['Fuel 1.6 w/oM8 lattice']['univ'],
L___8 = cells['Fuel 2.4 w/o + instr + 12BAL8 lattice']['univ'],
K___8 = cells['Fuel 1.6 w/oK8 lattice']['univ'],
J___8 = cells['Fuel 2.4 w/o + instr + 16BAJ8 lattice']['univ'],
H___8 = cells['Fuel 1.6 w/oH8 lattice']['univ'],
G___8 = cells['Fuel 2.4 w/o + 16BAG8 lattice']['univ'],
F___8 = cells['Fuel 1.6 w/o + instrF8 lattice']['univ'],
E___8 = cells['Fuel 2.4 w/o + 12BAE8 lattice']['univ'],
D___8 = cells['Fuel 1.6 w/o + instrD8 lattice']['univ'],
C___8 = cells['Fuel 2.4 w/o + instr + 16BAC8 lattice']['univ'],
B___8 = cells['Fuel 1.6 w/o + instrB8 lattice']['univ'],
A___8 = cells['Fuel 3.1 w/o + 6BAEA8 lattice']['univ'],
R___9 = cells['Fuel 3.1 w/oR9 lattice']['univ'], # Sp spare location
P___9 = cells['Fuel 3.1 w/o + instr + 20BAP9 lattice']['univ'],
N___9 = cells['Fuel 1.6 w/oN9 lattice']['univ'],
M___9 = cells['Fuel 2.4 w/o + 12BAM9 lattice']['univ'],
L___9 = cells['Fuel 1.6 w/oL9 lattice']['univ'],
K___9 = cells['Fuel 2.4 w/o + 12BAK9 lattice']['univ'],
J___9 = cells['Fuel 1.6 w/oJ9 lattice']['univ'],
H___9 = cells['Fuel 2.4 w/o + 16BAH9 lattice']['univ'],
G___9 = cells['Fuel 1.6 w/o + instrG9 lattice']['univ'],
F___9 = cells['Fuel 2.4 w/o + 12BAF9 lattice']['univ'],
E___9 = cells['Fuel 1.6 w/o + instrE9 lattice']['univ'],
D___9 = cells['Fuel 2.4 w/o + 12BAD9 lattice']['univ'],
C___9 = cells['Fuel 1.6 w/oC9 lattice']['univ'],
B___9 = cells['Fuel 3.1 w/o + 20BAB9 lattice']['univ'],
A___9 = cells['Fuel 3.1 w/o + instrA9 lattice']['univ'],
R__10 = cells['Fuel 3.1 w/o + 6BAWR10 lattice']['univ'],
P__10 = cells['Fuel 1.6 w/oP10 lattice']['univ'],
N__10 = cells['Fuel 2.4 w/o + 16BAN10 lattice']['univ'],
M__10 = cells['Fuel 1.6 w/oM10 lattice']['univ'],
L__10 = cells['Fuel 2.4 w/o + instr + 12BAL10 lattice']['univ'],
K__10 = cells['Fuel 1.6 w/oK10 lattice']['univ'],
J__10 = cells['Fuel 2.4 w/o + instr + 12BAJ10 lattice']['univ'],
H__10 = cells['Fuel 1.6 w/oH10 lattice']['univ'],
G__10 = cells['Fuel 2.4 w/o + 12BAG10 lattice']['univ'],
F__10 = cells['Fuel 1.6 w/oF10 lattice']['univ'],
E__10 = cells['Fuel 2.4 w/o + 12BAE10 lattice']['univ'],
D__10 = cells['Fuel 1.6 w/o + instrD10 lattice']['univ'],
C__10 = cells['Fuel 2.4 w/o + 16BAC10 lattice']['univ'],
B__10 = cells['Fuel 1.6 w/oB10 lattice']['univ'],
A__10 = cells['Fuel 3.1 w/o + 6BAEA10 lattice']['univ'],
R__11 = cells['Fuel 3.1 w/o + instrR11 lattice']['univ'],
P__11 = cells['Fuel 3.1 w/o + 16BAP11 lattice']['univ'],
N__11 = cells['Fuel 1.6 w/oN11 lattice']['univ'],
M__11 = cells['Fuel 2.4 w/o + 16BAM11 lattice']['univ'],
L__11 = cells['Fuel 1.6 w/o + instrL11 lattice']['univ'],
K__11 = cells['Fuel 2.4 w/o + 12BAK11 lattice']['univ'],
J__11 = cells['Fuel 1.6 w/oJ11 lattice']['univ'],
H__11 = cells['Fuel 2.4 w/o + instr + 12BAH11 lattice']['univ'],
G__11 = cells['Fuel 1.6 w/oG11 lattice']['univ'],
F__11 = cells['Fuel 2.4 w/o + 12BAF11 lattice']['univ'],
E__11 = cells['Fuel 1.6 w/o + instrE11 lattice']['univ'],
D__11 = cells['Fuel 2.4 w/o + 16BAD11 lattice']['univ'],
C__11 = cells['Fuel 1.6 w/oC11 lattice']['univ'],
B__11 = cells['Fuel 3.1 w/o + 16BAB11 lattice']['univ'],
A__11 = cells['Fuel 3.1 w/oA11 lattice']['univ'],
P__12 = cells['Fuel 3.1 w/oP12 lattice']['univ'],
N__12 = cells['Fuel 2.4 w/o + 16BAN12 lattice']['univ'],
M__12 = cells['Fuel 2.4 w/oM12 lattice']['univ'],
L__12 = cells['Fuel 2.4 w/o + 16BAL12 lattice']['univ'],
K__12 = cells['Fuel 1.6 w/o + instrK12 lattice']['univ'],
J__12 = cells['Fuel 2.4 w/o + 12BAJ12 lattice']['univ'],
H__12 = cells['Fuel 1.6 w/oH12 lattice']['univ'],
G__12 = cells['Fuel 2.4 w/o + instr + 12BAG12 lattice']['univ'],
F__12 = cells['Fuel 1.6 w/oF12 lattice']['univ'],      #4 secondary source rods here
E__12 = cells['Fuel 2.4 w/o + 16BAE12 lattice']['univ'],
D__12 = cells['Fuel 2.4 w/o + instrD12 lattice']['univ'],
C__12 = cells['Fuel 2.4 w/o + 16BAC12 lattice']['univ'],
B__12 = cells['Fuel 3.1 w/oB12 lattice']['univ'],
P__13 = cells['Fuel 3.1 w/oP13 lattice']['univ'],
N__13 = cells['Fuel 3.1 w/o + instr + 15BASWN13 lattice']['univ'],
M__13 = cells['Fuel 2.4 w/o + 16BAM13 lattice']['univ'],
L__13 = cells['Fuel 1.6 w/o + instrL13 lattice']['univ'],
K__13 = cells['Fuel 2.4 w/o + 16BAK13 lattice']['univ'],
J__13 = cells['Fuel 1.6 w/oJ13 lattice']['univ'],
H__13 = cells['Fuel 2.4 w/o + instr + 16BAH13 lattice']['univ'],
G__13 = cells['Fuel 1.6 w/oG13 lattice']['univ'],
F__13 = cells['Fuel 2.4 w/o + 16BAF13 lattice']['univ'],
E__13 = cells['Fuel 1.6 w/oE13 lattice']['univ'],
D__13 = cells['Fuel 2.4 w/o + 16BAD13 lattice']['univ'],
C__13 = cells['Fuel 3.1 w/o + 15BASEC13 lattice']['univ'],
B__13 = cells['Fuel 3.1 w/o + instrB13 lattice']['univ'],
N__14 = cells['Fuel 3.1 w/o + instrN14 lattice']['univ'],
M__14 = cells['Fuel 3.1 w/oM14 lattice']['univ'],
L__14 = cells['Fuel 3.1 w/o + 16BAL14 lattice']['univ'],
K__14 = cells['Fuel 1.6 w/oK14 lattice']['univ'],
J__14 = cells['Fuel 3.1 w/o + instr + 20BAJ14 lattice']['univ'],
H__14 = cells['Fuel 1.6 w/oH14 lattice']['univ'],
G__14 = cells['Fuel 3.1 w/o + 20BAG14 lattice']['univ'], #really should be 23BA1P
F__14 = cells['Fuel 1.6 w/o + instrF14 lattice']['univ'],
E__14 = cells['Fuel 3.1 w/o + 16BAE14 lattice']['univ'],
D__14 = cells['Fuel 3.1 w/o + instrD14 lattice']['univ'],
C__14 = cells['Fuel 3.1 w/oC14 lattice']['univ'],
L__15 = cells['Fuel 3.1 w/o + instrL15 lattice']['univ'],
K__15 = cells['Fuel 3.1 w/o + 6BASK15 lattice']['univ'],
J__15 = cells['Fuel 3.1 w/oJ15 lattice']['univ'],
H__15 = cells['Fuel 3.1 w/o + instr + 6BASH15 lattice']['univ'],
G__15 = cells['Fuel 3.1 w/oG15 lattice']['univ'], # Sp spare location
F__15 = cells['Fuel 3.1 w/o + 6BASF15 lattice']['univ'],
E__15 = cells['Fuel 3.1 w/oE15 lattice']['univ'],
**baffle)}



  ################## universe 0 cells ##################

  # the axial pincell universes contained in the lattices include the nozzles and bot support plate
  cells['inside core barrel'] ={ 'order':  inc_order(co),
                                'section': comm_t.format("Main universe cells"),
                                'comm':    comm_t.format("inside core barrel"),
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'fill':    latts['Main Core']['id'],
                                'surfs':  '-{0} {1} -{2}'.format(surfs['core barrel IR']['id'],
                                                                 surfs['lower bound']['id'],
                                                                 surfs['upper bound']['id'])}
  cells['core barrel'] =      { 'order':   inc_order(co),
                                'comm':    comm_t.format("core barrel"),
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['SS304']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} {2} -{3}'.format(surfs['core barrel IR']['id'],surfs['core barrel OR']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}
                                                                     
  cells['shield panel NW'] =   { 'order':   inc_order(co),
                                'comm':    comm_t.format("neutron shield panel NW"),
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['SS304']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} {2} -{3} {4} -{5}'.format(surfs['core barrel OR']['id'],surfs['neut shield OR']['id'],
                                                                     surfs['neut shield NWbot SEtop']['id'],surfs['neut shield NWtop SEbot']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}
  cells['shield panel N'] =   { 'order':   inc_order(co),
                                'comm':    "",
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['water-mod']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} {2} -{3} {4} -{5}'.format(surfs['core barrel OR']['id'],surfs['neut shield OR']['id'],
                                                                     surfs['neut shield NWtop SEbot']['id'],surfs['neut shield NEtop SWbot']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}
  cells['shield panel SE'] = { 'order':   inc_order(co),
                                'comm':    comm_t.format("neutron shield panel SE"),
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['SS304']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} -{2} {3} {4} -{5}'.format(surfs['core barrel OR']['id'],surfs['neut shield OR']['id'],
                                                                     surfs['neut shield NWbot SEtop']['id'],surfs['neut shield NWtop SEbot']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}
  cells['shield panel E'] =   { 'order':   inc_order(co),
                                'comm':    "",
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['water-mod']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} {2} {3} {4} -{5}'.format(surfs['core barrel OR']['id'],surfs['neut shield OR']['id'],
                                                                     surfs['neut shield NWbot SEtop']['id'],surfs['neut shield NEbot SWtop']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}
  cells['shield panel NE'] =  { 'order':   inc_order(co),
                                'comm':    comm_t.format("neutron shield panel NE"),
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['SS304']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} {2} -{3} {4} -{5}'.format(surfs['core barrel OR']['id'],surfs['neut shield OR']['id'],
                                                                     surfs['neut shield NEbot SWtop']['id'],surfs['neut shield NEtop SWbot']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}
  cells['shield panel S'] =   { 'order':   inc_order(co),
                                'comm':    "",
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['water-mod']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} -{2} {3} {4} -{5}'.format(surfs['core barrel OR']['id'],surfs['neut shield OR']['id'],
                                                                     surfs['neut shield NWtop SEbot']['id'],surfs['neut shield NEtop SWbot']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}
  cells['shield panel SW'] =  { 'order':   inc_order(co),
                                'comm':    comm_t.format("neutron shield panel SW"),
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['SS304']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} -{2} {3} {4} -{5}'.format(surfs['core barrel OR']['id'],surfs['neut shield OR']['id'],
                                                                     surfs['neut shield NEbot SWtop']['id'],surfs['neut shield NEtop SWbot']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}
  cells['shield panel W'] =   { 'order':   inc_order(co),
                                'comm':    "",
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['water-mod']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} -{2} -{3} {4} -{5}'.format(surfs['core barrel OR']['id'],surfs['neut shield OR']['id'],
                                                                     surfs['neut shield NWbot SEtop']['id'],surfs['neut shield NEbot SWtop']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}                                                                     
                                                                   
                                                                     
  cells['downcomer'] =        { 'order':   inc_order(co),
                                'comm':    comm_t.format("downcomer"),
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['water-mod']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} {2} -{3}'.format(surfs['neut shield OR']['id'],surfs['RPV IR']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}
  cells['rpv'] =              { 'order':   inc_order(co),
                                'comm':    comm_t.format("pressure vessel"),
                                'id':      new_id(cellIDs),
                                'univ':    0,
                                'mat':     mats['carbon steel']['id'],
                                'fill':    None,
                                'surfs':  '{0} -{1} {2} -{3}'.format(surfs['RPV IR']['id'],surfs['RPV OR']['id'],
                                                                     surfs['lower bound']['id'],
                                                                     surfs['upper bound']['id'])}

  


  # plot parameters
  plots = {}
  
  colSpecMat = {  mats['water-mod']['id']: "198 226 255",  # water:  light blue
                  mats['inconel']['id'] : "101 101 101",       # inconel dgray
                  mats['carbon steel']['id'] : "0 0 0",        # carbons black
                  mats['zirc']['id']:  "201 201 201",          # zirc:   gray
                  mats['SS304']['id']:  "0 0 0",               # ss304:  black
                  mats['air']['id']:  "255 255 255",           # air:    white
                  mats['helium']['id']:  "255 218 185",        # helium: light orange
                  mats['borosilicate']['id']: "0 255 0",       # BR:     green
                  mats['control rod']['id']: "255 0 0",        # CR:     bright red
                  mats['UO2 1.6']['id']: "142 35 35",          # 1.6:    light red
                  mats['UO2 2.4']['id']: "255 215 0",          # 2.4:    gold
                  mats['UO2 3.1']['id']: "0 0 128",            # 3.1:    dark blue
               }
  
#  plots["main cells"] =     { 'id':     new_id(plotIDs),
#                              'fname':  'center_cells',
#                              'type':   'slice', 
#                              'col':    'cell',
#                              'background': '255 255 255',
#                              'origin': '0.0 0.0 {0}'.format((highestExtent-lowestExtent)/2),
#                              'width':  '{0} {0}'.format(coreBarrelIR*2+10),
#                              'basis':  'xy',
#                              'pixels': '3000 3000',}
  plots["main mats"] =      { 'id':     new_id(plotIDs),
                              'fname':  'center_mats',
                              'type':   'slice', 
                              'col':    'mat',
                              'background': '255 255 255',
                              'origin': '0.0 0.0 {0}'.format((highestExtent-lowestExtent)/2),
                              'width':  '{0} {0}'.format(rpvOR*2+10),
                              'basis':  'xy',
                              'pixels': '6000 6000',
                              'spec':   colSpecMat,}

  # BA position plot
#  mask = []
#  colors = {}
#  mask.append(cells['burn abs']['id'])
#  mask.append(cells['burn abs1']['id'])
#  mask.append(cells['burn abs2']['id'])
#  mask.append(cells['burn abs3']['id'])
#  mask.append(cells['burn abs4']['id'])
#  mask.append(cells['burn abs5']['id'])
#  mask.append(cells['burn abs6']['id'])
#  colors[cells['burn abs']['id']] = "0 0 0"
#  colors[cells['burn abs1']['id']] = "0 0 0"
#  colors[cells['burn abs2']['id']] = "0 0 0"
#  colors[cells['burn abs3']['id']] = "0 0 0"
#  colors[cells['burn abs4']['id']] = "0 0 0"
#  colors[cells['burn abs5']['id']] = "0 0 0"
#  colors[cells['burn abs6']['id']] = "0 0 0"
#  for assembly,cellList in assemblyCells.items():
#    mask.append(cells[cellList[-1]]['id'])
#    mask.append(cells[cellList[-2]]['id'])
#    mask.append(cells[cellList[-3]]['id'])
#    mask.append(cells[cellList[-4]]['id'])
#    colors[cells[cellList[-1]]['id']] = "0 0 0"
#    colors[cells[cellList[-2]]['id']] = "0 0 0"
#    colors[cells[cellList[-3]]['id']] = "0 0 0"
#    colors[cells[cellList[-4]]['id']] = "0 0 0"
#  for cellName,cell in cells.items():
#    if 'baf' in cellName and 'mat' in cell:
#      if cell['mat'] == mats['SS304']['id']:
#        mask.append(cell['id'])
#        colors[cell['id']] = "0 0 0"

#  plots["ba pos"] =         { 'id':         new_id(plotIDs),
#                              'fname':      'ba_positions',
#                              'type':       'slice',
#                              'col':        'cell',
#                              'background': '255 255 255',
#                              'origin':     '0.0 0.0 {0}'.format((highestExtent-lowestExtent)/2),
#                              'width':      '{0} {0}'.format(rpvOR*2+10),
#                              'basis':      'xy',
#                              'pixels':     '6000 6000',
#                              'spec':       colors,
#                              'msk':        { 'maskrgb':  '255 255 255',
#                                              'comps':    '\n          '.join([str(m) for m in mask])},}

  # instr tube position plot
#  mask = []
#  mask.append(cells['GT instr']['id'])
#  mask.append(cells['GT instr1']['id'])
#  mask.append(cells['GT instr2']['id'])
#  for assembly,cellList in assemblyCells.items():
#    mask.append(cells[cellList[-1]]['id'])
#    mask.append(cells[cellList[-2]]['id'])
#    mask.append(cells[cellList[-3]]['id'])
#    mask.append(cells[cellList[-4]]['id'])
#  for cellName,cell in cells.items():
#    if 'baf' in cellName and 'mat' in cell:
#      if cell['mat'] == mats['SS304']['id']:
#        mask.append(cell['id'])

#  plots["instr pos"] =      { 'id':         new_id(plotIDs),
#                              'fname':      'instr_positions',
#                              'type':       'slice',
#                              'col':        'cell',
#                              'background': '255 255 255',
#                              'origin':     '0.0 0.0 {0}'.format((highestExtent-lowestExtent)/2),
#                              'width':      '{0} {0}'.format(rpvOR*2+10),
#                              'basis':      'xy',
#                              'pixels':     '6000 6000',
#                              'msk':        { 'maskrgb':  '255 255 255',
#                                              'comps':    '\n          '.join([str(m) for m in mask])},}


  # settings parameters
  entrX = 15*17
  entrY = 15*17
  entrZ = 100
  xbot = -15*latticePitch/2
  ybot = -15*latticePitch/2
  zbot = bottomFuelStack
  xtop = 15*latticePitch/2
  ytop = 15*latticePitch/2
  ztop = topActiveCore
  if core_D == '2-D':
    entrZ = 1
    zbot = twoDlower
    ztop = twoDhigher 
  sett = { 
            'xslib':        '/home/wbinventor/Documents/NSE-CRPG-Codes/mcnpdata/binary/cross_sections.xml',
            'batches':      350,
            'inactive':     250,
            'particles':    int(4e6),
            'verbosity':    7,
            'entrX':        entrX, 
            'entrY':        entrY,
            'entrZ':        entrZ,
            'xbot':   xbot, 'ybot':  ybot, 'zbot': zbot,
            'xtop':   xtop, 'ytop':  ytop, 'ztop': ztop}



  tallies = {}

  meshDim = 15*17
  meshLleft = -15*latticePitch/2
  tallies['testmesh'] = {'ttype': 'mesh',
                      'id': 1,
                      'type': 'rectangular',
                      'origin': '0.0 0.0',
                      'width': '{0} {0}'.format(-meshLleft*2/meshDim),
                      'lleft': '{0} {0}'.format(meshLleft),
                      'dimension': '{0} {0}'.format(meshDim)}
  tallies['test'] = { 'ttype': 'tally',
                      'id': 1,
                      'mesh':tallies['testmesh']['id'],
                      'scores':'nu-fission'}

  # cmfd calculation
  cmfd = {}
  cmfd_mesh_pitch = latticePitch/cmfd_pin_to_box_factor
  cmfd_bottom = bottomFuelStack
  cmfd_top = topActiveCore
  cmfd_axial_map = cmfd_map
  if cmfd_axial_dim > 1:
    axial_pitch = (cmfd_top - cmfd_bottom)/float(cmfd_axial_dim)
    cmfd_bottom = cmfd_bottom - axial_pitch
    cmfd_top = cmfd_top + axial_pitch
    cmfd_axial_dim = cmfd_axial_dim + 2
    cmfd_axial_map = ""
    cmfd_axial_map += cmfd_map.replace('2','1') + '\n'
    j = 0
    while j < cmfd_axial_dim-2:
      cmfd_axial_map += cmfd_map + '\n'
      j += 1
    cmfd_axial_map += cmfd_map.replace('2','1')
  if core_D == '2-D':
    cmfd_axial_dim = 1
    cmfd_bottom = twoDlower 
    cmfd_top = twoDhigher
    cmfd_axial_map = cmfd_map
  cmfd = {'lleft': '{0} {0} {1}'.format(-cmfd_mesh_pitch*cmfd_mesh_dim/2,cmfd_bottom),
          'uright': '{0} {0} {1}'.format(cmfd_mesh_pitch*cmfd_mesh_dim/2,cmfd_top),
          'dimension': '{0} {0} {1}'.format(cmfd_mesh_dim,cmfd_axial_dim),
          'map': cmfd_axial_map,
          'albedo': cmfd_albedo,
          'energy': cmfd_energy}

  return mats,surfs,cells,latts,sett,plots,tallies,cmfd





def write_materials(mats,outFile):

  # main id sets, along with function new_id, ensure no duplicates
  matIDs = set()

  outStr = """<?xml version="1.0" encoding="UTF-8"?>\n"""
  outStr += "<materials>\n"
  outStr += "\n"
  outStr += comm_t.format("This file auto-generated by beavrs.py")
  outStr += "\n"
  outStr += "\n"

  matItems = mats.items()
  matItems.sort(key=lambda d: d[1]['order'])

  for mat,matDict in matItems:
    nucs = ""
    for nuc in matDict['nuclides']:
      nucs += nucl_t.format(**nuc)
    matDict['nuclides'] = nucs
    sab = ""
    if 'sab' in matDict:
      for sabDict in matDict['sab']:
        sab += sab_t.format(**sabDict)
    matDict['sab'] = sab
    outStr += comm_t.format(matDict['comment']) + '\n'
    outStr += mat_t.format(**matDict)
    outStr += "\n"
  outStr += "</materials>"

  # write file
  with open(outFile,'w') as fh:
    fh.write(outStr)


def write_geometry(surfs,cells,lats,outFile):

  surfItems= surfs.items()
  surfItems.sort(key=lambda d: d[1]['order'])
  cellItems= cells.items()
  cellItems.sort(key=lambda d: d[1]['order'])
  lattItems= lats.items()
  lattItems.sort(key=lambda d: d[1]['order'])

  outStr = """<?xml version="1.0" encoding="UTF-8"?>\n"""
  outStr += "<geometry>\n"
  outStr += "\n"
  outStr += comm_t.format("This file auto-generated by beavrs.py")
  outStr += "\n"
  for surf,surfDict in surfItems:
    if 'dupe' in surfDict: continue
    if 'section' in surfDict:
      outStr += "\n"
      outStr += surfDict['section'] + '\n'
    if 'bc' in surfDict:
      outStr += surf_t_bc.format(**surfDict)
    else:
      outStr += surf_t.format(**surfDict)
  outStr += "\n"
  for cell,cellDict in cellItems:
    if 'dupe' in surfDict: continue
    if 'section' in cellDict:
      outStr += "\n"
      outStr += cellDict['section'] + '\n'
    if cellDict['fill']:
      outStr += cell_t_fill.format(**cellDict)
    else:
      outStr += cell_t_mat.format(**cellDict)
  outStr += "\n"
  for latt,latDict in lattItems:
    if 'dupe' in surfDict: continue
    outStr += "\n"
    outStr += latt_t.format(**latDict)
  outStr += "\n"
  outStr += "</geometry>"

  # write file
  with open(outFile,'w') as fh:
    fh.write(outStr)

def write_settings(sett,outFile):

  # write file
  with open(outFile,'w') as fh:
    fh.write(settings_t.format(**sett))


def write_plots(plots,outFile):

  outStr = """<?xml version="1.0" encoding="UTF-8"?>\n"""
  outStr += "<plots>\n"
  outStr += "\n"
  outStr += comm_t.format("This file auto-generated by beavrs.py")
  outStr += "\n"
  for plot,plotDict in plots.items():
    spec = ""
    mask = ""
    if 'spec' in plotDict:
      for id_,rgb in plotDict['spec'].items():
        spec += plot_col_spec_t.format(id=id_,rgb=rgb)
    if 'msk' in plotDict:
      mask = plot_mask_t.format(**plotDict['msk'])
    outStr += plot_t.format(col_spec=spec,mask=mask,**plotDict)
  outStr += "\n"
  outStr += "</plots>"

  # write file
  with open(outFile,'w') as fh:
    fh.write(outStr)

def write_tallies(tallies,outFile):

  outStr = """<?xml version="1.0" encoding="UTF-8"?>\n"""
  outStr += "<tallies>\n"
  outStr += "\n"
  outStr += comm_t.format("This file auto-generated by beavrs.py")
  outStr += "\n\n"
  
  for key,item in tallies.items():
    if item['ttype'] == 'mesh':
      outStr += tallymesh_t.format(**item)
    elif item['ttype'] == 'tally':
      outStr += tally_t.format(**item)
  outStr += "\n"
  outStr += "</tallies>"

  # write file
  with open(outFile,'w') as fh:
    fh.write(outStr)

def write_cmfd(cmfd,outFile):

  outStr = """<?xml version="1.0" encoding="UTF-8"?>\n"""
  outStr += "<cmfd>\n"
  outStr += "\n"
  outStr += comm_t.format("This file auto-generated by beavrs.py")
  outStr += "\n"
  outStr += cmfdmesh_t.format(**cmfd)
  outStr += "  <begin>{0}</begin>\n".format(cmfd_begin)
  outStr += "  <active_flush>{0}</active_flush>\n".format(cmfd_active_flush)
  outStr += "  <keff_tol>{0}</keff_tol>\n".format(cmfd_keff_tol)
  outStr += "  <feedback>{0}</feedback>\n".format(cmfd_feedback)
  outStr += "\n"
  outStr += "</cmfd>"

  # write file
  with open(outFile,'w') as fh:
    fh.write(outStr)

def make_pin(name,section,co,cells,univ,cellIDs,radSurfList,matList,
             grid=False, surfs=None, gridMat=None, gridType=None):
  """Populates the cells dictionary with a radial pincell universe
  
    name       - string, name of the cell as well as  outKeys = [name] the comment to be written
    section    - section comment - not written if left as ""
    co         - cells order dictionary
    cells      - cells dictionary
    univ       - new universe id number for this pincell
    cellIDs    - set of already used cell IDs
    radSurfList- list of surface IDs, from inside to outside
    matList    - list of tuples of material IDs and comments, from inside to outside.
                 length should be one more than radSurfList.
                 first material will be the inside of the first surface,
                 last last will be outside the last surface.
                 if comments are "", no comment will be written

    Since box surfaces aren't fully implemented yet, square grids around the
    outside of pins need to be added manually here.

    grid       - flag for whether or not to make the grid
    surfs      - full surfaces dictionary.  This routine uses the 'rod grid box'
                 surfaces
    gridMat    - material for the grid
    gridType   - either 'i' or 'tb' for intermediate or top/bottom
    
  """

  cells[name] = { 'order':   inc_order(co),
                  'comm':    "",
                  'id':      new_id(cellIDs),
                  'univ':    univ,
                  'mat':     matList[0][0],
                  'fill':    None,
                  'surfs':   '-{0}'.format(radSurfList[0])}
  if section != "":
    cells[name]['section'] = comm_t.format(section)
  if matList[0][1] != "":
    cells[name]['comm'] = comm_t.format(matList[0][1])

  for i,(matIDcomment,outSurf) in enumerate(zip(matList[1:-1],radSurfList[:-1])):
    cells[name +' '+ str(i)] = {  'order':   inc_order(co),
                              'comm':    "",
                              'id':      new_id(cellIDs),
                              'univ':    univ,
                              'mat':     matIDcomment[0],
                              'fill':    None,
                              'surfs':  '{0} -{1}'.format(outSurf,radSurfList[i+1])}
    if matIDcomment[1] != "":
      cells[name+' '+ str(i)]['comm'] = comm_t.format(matIDcomment[1])
      
  cells[name + ' last'] = {  'order':   inc_order(co),
                            'comm':    "",
                            'id':      new_id(cellIDs),
                            'univ':    univ,
                            'mat':     matList[-1][0],
                            'fill':    None,
                            'surfs':  '{0}'.format(radSurfList[-1])}

def make_stack(name,co,cells,univ,cellIDs,axSurfList,fillList):
  """Populates the cells dictionary with an axial stack universe
  
    name       - string, name of the cell as well as the comment to be written
    co         - cells order dictionary
    cells      - cells dictionary
    univ       - new universe id number for this stack
    cellIDs    - set of already used cell IDs
    axSurfList - list of surface IDs, from botom to top
    fillList   - list of fill universe IDs, from bottom to top.
                 length should be one more than axSurfList.
                 first fill universe will be below the first surface,
                 last fill universe will be above the last surface
  """
  
  cells[name] = { 'order':   inc_order(co),
                  'comm':    comm_t.format(name),
                  'id':      new_id(cellIDs),
                  'univ':    univ,
                  'fill':    fillList[0],
                  'surfs':  '-{0}'.format(axSurfList[0])}

  for i,(fillU,botSurf) in enumerate(zip(fillList[1:-1],axSurfList[:-1])):
    cells[name + str(i)] = {  'order':   inc_order(co),
                              'comm':    "",
                              'id':      new_id(cellIDs),
                              'univ':    univ,
                              'fill':    fillU,
                              'surfs':  '{0} -{1}'.format(botSurf,axSurfList[i+1])}
  cells[name + 'last'] = {  'order':   inc_order(co),
                            'comm':    "",
                            'id':      new_id(cellIDs),
                            'univ':    univ,
                            'fill':    fillList[-1],
                            'surfs':  '{0}'.format(axSurfList[-1])}


def make_assembly(latts, cells, surfs, lo, co, univIDs, cellIDs, water, name,
                  comm=None,sect=None, dim=None,lleft=None,width=None,univs=None):
  """Populates the cells and latts dictionary with an assembly

    The cell universe handle to use will be:  cells[name+' lattice']['univ']
  
    cells      - cells dictionary
    surfs      - surfs dictionary
    lo         - latts order dictionary
    co         - cells order dictionary
    univIDs    - set of already used universe IDs
    cellIDs    - set of already used cell IDs
    name       - string, name of the latt/cell family
    water      - material to put outside the lattice
    comm       - optional comment for the lattice and cell family
    sect       - optional section comment
    dim        - required lattice dimension
    lleft      - required lattice lower_left
    width      - required lattice width
    univs      - required lattice universe string.  Should be made with pinLattice_t

    returns list of all the created cell keys

  """

  name = str(name)

  # first make the lattice

  latts[name] =                 { 'order':   inc_order(lo),
                                  'id':      new_id(univIDs),
                                  'type':    'rectangular'}
  if comm:
    latts[name]['comm'] = comm_t.format(comm)
  else:
    latts[name]['comm'] = ""
  if sect:
    latts[name]['section'] = comm_t.format(sect)

  for key in ['dim','lleft','width','univs']:
    if not locals()[key]:
      raise Exception('make_assembly requires {0}'.format(key))
    else:
      latts[name][key] = locals()[key]
  
  # add lattice to bounding cell
  cells[name+' lattice'] =    { 'order':   inc_order(co),
                                'id':      new_id(cellIDs),
                                'univ':    new_id(univIDs),
                                'fill':    latts[name]['id'],
                                'surfs':  '-{0} {1} -{2} {3}'.format(surfs['lat box xtop']['id'],surfs['lat box xbot']['id'],surfs['lat box ytop']['id'],surfs['lat box ybot']['id'])}
  if comm:
    cells[name+' lattice']['comm'] = comm_t.format(comm)
  else:
    cells[name+' lattice']['comm'] = ""
  if sect:
    cells[name+' lattice']['section'] = comm_t.format(sect)

  # get lattice universt
  univ = cells[name+' lattice']['univ']

  # add water around lattice
  # west of lattice capped by y planes
  cells[name+' woflattice'] = { 'order':   inc_order(co),
                                'id':      new_id(cellIDs),
                                'univ':    univ,
                                'fill':    water,
                                'comm':    comm_t.format('water west of lattice'),
                                'surfs':  '-{xbot} -{ytop} {ybot}'.format(xbot=surfs['lat box xbot']['id'], ytop=surfs['lat box ytop']['id'], ybot=surfs['lat box ybot']['id'])}

  # north of lattice
  cells[name+' noflattice'] =  { 'order':   inc_order(co),
                                 'id':      new_id(cellIDs),
                                 'univ':    univ,
                                 'fill':    water,
                                 'comm':    comm_t.format('water north of lattice'),
                                 'surfs':  '{ytop}'.format(ytop=surfs['lat box ytop']['id'])}

  # east of lattice capped by y planes
  cells[name+' eoflattice'] = { 'order':   inc_order(co),
                                'id':      new_id(cellIDs),
                                'univ':    univ,
                                'fill':    water,
                                'comm':    comm_t.format('water east of lattice'),
                                'surfs':  '{xtop} -{ytop} {ybot}'.format(xtop=surfs['lat box xtop']['id'], ytop=surfs['lat box ytop']['id'], ybot=surfs['lat box ybot']['id'])}

  # south of lattice
  cells[name+' soflattice'] =  { 'order':   inc_order(co),
                                 'id':      new_id(cellIDs),
                                 'univ':    univ,
                                 'fill':    water,
                                 'comm':    comm_t.format('water south of lattice'),
                                 'surfs':  '-{ybot}'.format(ybot=surfs['lat box ybot']['id'])}


  return 0


def control_bank_axials(step):
  """Given the total number of steps withdrawn, returns a dictionary of control rod axial surfaces

  Starting from all out, we follow this sequence:
  First D moves in alone, until it gets to 113 steps withdrawn
  Now D and C move together until C gets to 113 steps withdrawn (D is all the way in by C at 115)
  Now C and B move together until B gets to 113 steps withdrawn (C is all the way in by B at 115)
  Now B and A move together until A gets to 0 steps withdrawn (B is all the way in by A at 115)

  Assuming only movement of each control rod bank by one step, in total this sequence yields 574 unique positions,
  which we specify with step.  If step=1, all control rods are out of the core, and if step=574, all are fully inserted.

  For example for BOL normal operation if you want the D bank at the bite position of 184 steps withdrawn,
  set step=228-184+1=45

  """

  if step < 0 or step > 574:
    raise Exception("Invalid control bank step specification {0}".format(step))

  bankDstep = max(0.0,228-step)
  bankCstep = (bankDstep<113)*max(0.0,228-step+113  +3) + (bankDstep>=113)*228
  bankBstep = (bankCstep<113)*max(0.0,228-step+113*2+5) + (bankCstep>=113)*228
  bankAstep = (bankBstep<113)*max(0.0,228-step+113*3+7) + (bankBstep>=113)*228

  bankAbot = step0H + stepWidth*bankAstep
  bankBbot = step0H + stepWidth*bankBstep
  bankCbot = step0H + stepWidth*bankCstep
  bankDbot = step0H + stepWidth*bankDstep

  bankAtop = bankAbot + stepWidth*228
  bankBtop = bankBbot + stepWidth*228
  bankCtop = bankCbot + stepWidth*228
  bankDtop = bankDbot + stepWidth*228

  return locals()


def new_id(set_,range_=None):
  """Returns a new id unique to set_, within desired range_, and adds it to that set

      range_ should be a tuple or list where range_[0] = lower bound, inclusive
                                             range_[1] = upper bound, inclusive
  """

  if not range_:
    range_ = [1,1000000]

  id_ = range_[0]

  while id_ in set_:
    id_ += 1
    if id_ > range_[1]:
      raise Exception("no more unique ids in range {0}".format(range_))

  set_.add(id_)

  return id_


def inc_order(o):
  o['n'] += 1
  return o['n']


def main():

  mats,surfs,cells,latts,sett,plots,tallies,cmfd = init_data()

  write_materials(mats,"materials.xml")
  write_geometry(surfs,cells,latts,"geometry.xml")
  write_settings(sett,"settings.xml")
  write_plots(plots,"plots.xml")
  write_tallies(tallies,"tallies.xml")
  write_cmfd(cmfd,"cmfd.xml")


if __name__ == "__main__":
  main()
