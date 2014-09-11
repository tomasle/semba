# $Id: HDV.py 31 2010-01-12 15:44:40Z tlev $
# -*- coding: iso-8859-1 -*-

'''
Created on 20. okt. 2009

@author: levin
'''
import SEMBA as S
from math import *


Vehicle_Types = {}

def create_vehicle_list():
  for k,v in S.H_HDV.items():
    k=0
    Vehicle_Types[v[0]]= v[2]

def CreateHDV():
  S.load_HDV()
  create_vehicle_list()

def extractAndCalc(data,Speed):
  WarningText=[]
  VehicleID = data[0]
  VehicleDescription = data[1]
  EUROClass = data[2]
  Gradient = float(data[3])
  Load = float(data[4])
  EmissionComponent = data[5]
  PythonEquation = data[6]
  if data[7] == '':
    data[7] = 0
  if data[8] == '':
    data[8] = 0
  if data[9] == '':
    data[9] = 0
  if data[10] == '':
    data[10] = 0
  if data[11] == '':
    data[11] = 0
  if data[12] == '':
    data[12] = 0
  if data[13] == '':
    data[13] = 0
  a = float(data[7])
  b = float(data[8])
  c = float(data[9])
  d = float(data[10])
  e = float(data[11])
  MinSpeed = float(data[12])
  MaxSpeed = float(data[13])
  Emission = -1
  y = -1
  if Speed <= MaxSpeed and Speed >= MinSpeed:
    x = Speed
  if Speed < MinSpeed:
    x = MinSpeed
    WarningText.append("Speed is below minimum, minimum speed is used ->" + str(MinSpeed))
  if Speed > MaxSpeed:
    x = MaxSpeed
    WarningText.append("Speed is above maximum, maximum speed is used ->" + str(MaxSpeed))

  exec PythonEquation
  return y,WarningText


def CalculateHDV(HDVID, Component, Speed, Grad, Load):
  """
  Calculation of emissions from heavy duty vehicles
  UNITS:
     Speed km/h
     Gradient 6 is  6%
     Emission calculated is g/km
  CO2 calculated from Fuel consumption
  No maximum speed is given for each equation.
  """
  Gradient=0.0
  WarningText = []
  if Grad <= -6 :
    Gradient = -6
    WarningText.append("Used maximum gradient -6%")
  elif Grad > -6 and Grad <= -4:
    Gradient = -4
    WarningText.append("Used standard gradient -4%")
  elif Grad > -4 and Grad <= -2 :
    Gradient = -2
    WarningText.append("Used standard gradient -2%")
  elif Grad > -2 and Grad < 2 :
    Gradient = 0
    WarningText.append("Used standard gradient 0%")
  elif Grad >= 12:
    Grad = 12
    WarningText.append("Maximum grade 12 % is selected")
    #This limits us from using unrealistic grades

  CalculateCO2fromFC = False
  if Component == "CO2":
    Component = "FC"
    CalculateCO2fromFC = True

  CalculateEnergy = False
  if Component == "E":
    Component = "FC"
    CalculateEnergy = True


  if Component == "HC":
    Component = "THC"
  if Grad <0:
    key = str(HDVID) + "_" + Component + "_" + str(int(Gradient)) + "_" + str(int(Load))
    data = S.H_HDV[key]
    ans=[]
    ans=extractAndCalc(data,Speed)
    Emission = ans[0]
    WarningText.append(ans[1])
  else:
    X=[]
    Y=[]
    key = str(HDVID) + "_" + Component + "_" + str(int(0)) + "_" + str(int(Load))
    data0 = S.H_HDV[key]
    X.append(0)
    Y.append(extractAndCalc(data0,Speed)[0])
    key = str(HDVID) + "_" + Component + "_" + str(int(2)) + "_" + str(int(Load))
    data2 = S.H_HDV[key]
    X.append(2)
    Y.append(extractAndCalc(data2,Speed)[0])
    key = str(HDVID) + "_" + Component + "_" + str(int(4)) + "_" + str(int(Load))
    data4 = S.H_HDV[key]
    X.append(4)
    Y.append(extractAndCalc(data4,Speed)[0])
    key = str(HDVID) + "_" + Component + "_" + str(int(6)) + "_" + str(int(Load))
    data6 = S.H_HDV[key]
    X.append(6)
    Y.append(extractAndCalc(data6,Speed)[0])
    a,b,rr=S.linreg(X,Y)
    #print X
    #print Y
    #print a,b,rr
    Emission = a*Grad + b



  if CalculateCO2fromFC:
    Emission = Emission * 3.17 # http://www.klif.no/Tema/Klima-og-ozon/Klimagasser/--MENY/Sporsmal-og-svar/
    WarningText.append("CO2 emissions calculated from fuel consumption")

  if CalculateEnergy:
    Emission = Emission * (S.EDensity_Diesel/1000.0)
    WarningText.append("Energy calculated from fuel consumption")

  if (len(WarningText) == 0):
    WarningText.append("No Warnings")

  return Emission, "g/km", WarningText

def ListTypes():
  """
  Lists all heavy duty vehicles available in the dataset that is loaded.
  """
  #Function to sort as integers
  def compare(a, b):
    return cmp(int(a), int(b)) # compare as integers

  keys = Vehicle_Types.keys()
  keys.sort(compare)
  print "HDV ID   ;   Description"
  for key in keys:
    print str(key)+ '   ;    '+ Vehicle_Types[key]
###########____Load Data____##################
CreateHDV()

#test segment for debuging purposes
if __name__ == "__main__":
  import matplotlib.pyplot as plt
  xvar=[]
  a = []
  b = []
  c = []
  d = []
  e = []
  f = []
  g = []
  h = []
  j = []
  k = []
  l = []
  m = []
  n = []


  for i in range(6, 90):
    b.append(i)
    #def CalculateHDV(HDVID, Component, Speed, Gradient, Load):
    a.append(CalculateHDV(41, 'FC', i, 0.0 , 100)[0])
    b.append(CalculateHDV(47, 'FC', i, 0.0 , 100)[0])
    c.append(CalculateHDV(53, 'FC', i, 0.0 , 100)[0])
    d.append(CalculateHDV(59, 'FC', i, 0.0 , 100)[0])
    e.append(CalculateHDV(65, 'FC', i, 0.0 , 100)[0])
    f.append(CalculateHDV(71, 'FC', i, 0.0 , 100)[0])
    g.append(CalculateHDV(77, 'FC', i, 0.0 , 100)[0])
    h.append(CalculateHDV(83, 'FC', i, 0.0 , 100)[0])
    j.append(CalculateHDV(89, 'FC', i, 0.0 , 100)[0])
    k.append(CalculateHDV(95, 'FC', i, 0.0 , 100)[0])
    l.append(CalculateHDV(101, 'FC', i, 0.0 , 100)[0])
    m.append(CalculateHDV(107, 'FC', i, 0.0 , 100)[0])
    n.append(CalculateHDV(113, 'FC', i, 0.0 , 100)[0])
    #a.append(CalculateHDV(91, 'NOx', i, 0.0 , 100)[0])
    #c.append(CalculateHDV(92, 'NOx', i, 0.0 , 100)[0])
    #d.append(CalculateHDV(93, 'NOx', i, 0.0 , 100)[0])
    #e.append(CalculateHDV(94, 'NOx', i, 0.0 , 100)[0])
    #f.append(CalculateHDV(95, 'NOx', i, 0.0 , 100)[0])
    #g.append(CalculateHDV(96, 'NOx', i, 0.0 , 100)[0])
    #h.append(CalculateHDV(95, 'NOx', i, 6.0 , 100)[0])

    #  plt.plot(b, a,label ='EURO 0')
    #  plt.plot(b, c,label ='EURO I' )
    #  plt.plot(b, d,label ='EURO II')
    #  plt.plot(b, e,label ='EURO III')
    #  plt.plot(b, f,label ='EURO IV')
    #  plt.plot(b, g,label ='EURO V')
    #plt.plot(b, h,label ='+6 %')

  print b
  # print a[10]
  #print c[10]
  #print e[10]
  #print d[10]


  plt.ylabel('NOx gram/km')
  plt.xlabel('Vehicle average speed')
  plt.title('SEMBA, EURO IV 34- 40ton truck')
#  leg = plt.legend(loc=1,ncol=2)
#  for t in leg.get_texts():
#    t.set_fontsize('x-small')    # the legend text fontsize

  plt.show()

  #ListTypes()

  #CalculateHDV(101, 'NOx', i, 0.0 , 100)[0])
  #CalculateHDV(101, 'NOx', i, 0.0 , 100)[0])
  #CalculateHDV(101, 'NOx', i, 0.0 , 100)[0])