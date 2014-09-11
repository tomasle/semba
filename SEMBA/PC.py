# $Id: PC.py 31 2010-01-12 15:44:40Z tlev $
# -*- coding: iso-8859-1 -*-

'''
Created on 20. okt. 2009

@author: levin
'''
from math import *

import SEMBA as S

#Create empty dictionaries to load emission data in

Vehicle_Types = {}

def create_vehicle_list():
  for k,v in S.H_PC.items():
    k=0
    Vehicle_Types[v[0]]= v[2] +"  "+ v[3]+"  "+v[4]


def CreatePC():
  S.load_PC()
  S.load_PCGradient()
  create_vehicle_list()

def findGrade(gradient,TrafficSituation):
    """
    Find gradent value for lookuptable

    Finds the correct gradient value for lookup based on road category and
    gadient. Three traffic situations exist:
    urban
    road
    motorway
    """
    g = 999999
    if gradient <= -9 : g = -10
    elif gradient <= -7 and gradient > -9 : g = -8
    elif gradient <= -5 and gradient > -7 : g = -6
    elif gradient <= -3 and gradient > -5 : g = -4
    elif gradient <= -1 and gradient > -3 : g = -2
    elif gradient <= 1 and gradient > -1 : g = 0
    elif gradient <= 3 and gradient > 1 : g = 2
    elif gradient <= 5 and gradient > 3 : g = 4
    elif gradient <= 7 and gradient > 5 : g = 6
    elif gradient <= 9 and gradient > 7 : g = 8
    elif gradient > 9 : g = 10

    if TrafficSituation =='urban' or TrafficSituation =='motorway':
        #limits road gradients to supported gradients
        if g < -6 : g = -6
        if g > 6 : g = 6
    return g



def CalculatePC(PCID, Component, Speed, Gradient, Engine, TrafficSituation):
  """
  Calculation of emissions from private cars
  UNITS:
     Speed km/h
     Gradient 0.06 is  6%
     Emission calculated is g/km
     Fuel is calculated from CO2 emissions by factors from SFT, Norway
  Maximum speed is 125 km/h

  Engine size:
    PETROL
    small   < 1.4 liters
    medium    1.4 -> 2.0 liters
    large   >2.0 liters
    DIESEL
    medium  <2.0 liters
    large   >2.0 liters
  """
  WarningText = []
  CalculateFCfromCO2 = False
  #Finds the correct gradient
  Gradient = findGrade(Gradient,TrafficSituation)


  if Component == "FC":
    Component = "CO2"
    CalculateFCfromCO2 = True

  if not (Component == "C02" or Component == "FC") :
    Engine = 'all'


  if Speed >= 6:
    #Get Data from the PC dictionary
    key = str(PCID) + "_" + Component + "_" + Engine
    value = S.H_PC[key]
    data = value
    VehicleID = data[0]
    EmissionComponent = data[1]
    FuelType = data[2]
    EngineSize = data[3]
    EuroClass = data[4]
    EquationType = data[5]
    Order = data[6]
    a0 = float(data[7])
    a1 = float(data[8])
    a2 = float(data[9])
    a3 = float(data[10])
    a4 = float(data[11])
    a5 = float(data[12])
    Emission = -1


    if EquationType == 'Polyn.':
      Emission = float(a0) + \
               float(a1) * float(Speed) + \
               float(a2) * pow(float(Speed), 2) + \
               float(a3) * pow(float(Speed), 3) + \
               float(a4) * pow(float(Speed), 4) + \
               float(a5) * pow(float(Speed), 5)

    if EquationType == 'Power':
      Emission = a0 * pow(Speed, a1)

    if CalculateFCfromCO2:
      if FuelType == "DIESEL":
        Emission = Emission / 3.18
        WarningText.append("Fuel Calculated from CO2 emission factor 3.18")
      if FuelType == "PETROL":
        Emission = Emission / 3.13
        WarningText.append("Fuel Calculated from CO2 emission factor 3.13")

    #Her ligger feilsjekkingsrutiner
    if Speed > 125 :
      WarningText.append("Emission Function used outside valid area")

    if (len(WarningText) == 0):
      WarningText.append("No Warnings")

  if Speed < 6:
    Emission = 0
    WarningText.append("Speed Under 6kmh")

  #Here comes correction for gradient
  corrFactor = 0
  GradeKey = EuroClass + "_" + TrafficSituation + "_" + str(Gradient)
  value = S.H_PCGrade[GradeKey]
  if FuelType == 'PETROL':
    if Component == 'CO':
      corrFactor = value[3]
    if Component == 'HC':
      corrFactor = value[4]
    if Component == 'NOx':
      corrFactor = value[5]
    if Component == 'FC':
      corrFactor = value[6]
    if Component == 'CO2':
      corrFactor = value[6]
    if Component == 'PM':
      corrFactor = 1 # ARTEMIS does not correct PM for gasoline for grades
  elif FuelType == 'DIESEL':
    if Component == 'CO':
      corrFactor = value[7]
    if Component == 'HC':
      corrFactor = value[8]
    if Component == 'NOx':
      corrFactor = value[9]
    if Component == 'PM':
      corrFactor = value[10]
    if Component == 'FC':
      corrFactor = value[11]
    if Component == 'CO2':
      corrFactor = value[11]

  CorrectedEmission = float(Emission) * float(corrFactor)

  egps = S.Convert_gpkm_to_gps(CorrectedEmission, Speed)
  return CorrectedEmission, "g/km", egps[0], egps[1], WarningText

def ListTypes():
  """
  Lists all heavy duty vehicles available in the dataset that is loaded.
  """
  #Function to sort as integers
  def compare(a, b):
    return cmp(int(a), int(b)) # compare as integers

  keys = Vehicle_Types.keys()
  keys.sort(compare)
  print "Private car ID   ;   Description"
  for key in keys:
    print str(key)+ '   ;    '+ Vehicle_Types[key]


###########____Load Data____##################
CreatePC()



#test segment for debuging purposes
if __name__ == "__main__":
  import matplotlib.pyplot as plt #@UnresolvedImport
  a = []
  b = []
  c = []
  d = []
  e = []
  for i in range(6, 120):
    b.append(i)
    #def CalculateHDV(HDVID, Component, Speed, Gradient, Load):
    a.append(CalculatePC(4,"FC",i,0.02,all,"urban")[0])
    c.append(CalculatePC(4,"FC",i,0,all,"urban")[0])
  plt.plot(b, a)
  plt.plot(b, c)
  #plt.plot(b, c,label='Diesel Euro 4')
  #leg = plt.legend(loc=1)
  #for t in leg.get_texts():
  #  t.set_fontsize('x-small')    # the legend text fontsize
  #plt.axis(ymin=0)
  #plt.grid(True)
  plt.ylabel('Fuel consumption Liter/10km')
  plt.xlabel('Vehicle average speed')
  plt.title('SEMBA PC Vehicle fuel consumption')

  plt.ylim(ymin=0)
  plt.show()


  #PCID, Component, Speed, Gradient, Engine, TrafficSituation
  print CalculatePC(3,"FC",100,0,all,"urban")

