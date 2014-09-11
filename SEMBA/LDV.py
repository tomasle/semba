# $Id: LDV.py 31 2010-01-12 15:44:40Z tlev $
# -*- coding: iso-8859-1 -*-

'''
Created on 20. okt. 2009

@author: levin
'''
import SEMBA as S
#Create empty dictionaries to load emission data in
Vehicle_Types = {}

def CreateLDV():
  S.load_LDV()
  create_vehicle_list()
  
def create_vehicle_list():
  for k,v in S.H_LDV.items():
    k=0
    Vehicle_Types[v[0]]= v[1] +v[1]  + v[2]+v[3]

def CalculateLDV(LDVID, Component, Speed, Load=0):
  """
  Calculation of emissions from light duty vehicles
  UNITS:
     Speed km/h
     Emission calculated is g/km

  No maximum speed given in Artemis
  """
  key = str(LDVID) + "_" + Component
  data = S.H_LDV[key]
  #print rad
  #Her laster vi faktorer inn i bedre variabel navn
  #VehicleID;FuelType;WeightCathegory;EUROClass;EmissionComponent;a;b;c;d;e;f;g;h;i;MinEmission;MinLoad;MaxLoad
  VehicleID = int(data[0])
  FuelType = data[1]
  WeightCathegory = data[2]
  EUROClass = data[3]
  EmissionComponent = data[4]
  a = float(data[5])
  b = float(data[6])
  c = float(data[7])
  d = float(data[8])
  e = float(data[9])
  f = float(data[10])
  g = float(data[11])
  h = float(data[12])
  i = float(data[13])
  MinEmission = float(data[14])
  MinLoad = float(data[15])
  MaxLoad = float(data[16])

  Emission = -1
  WarningText = []

  if Load < MinLoad :
    Load = MinLoad
    WarningText.append("Load to low, minimum load used")

  if Load > MaxLoad :
    Load = MaxLoad
    WarningText.append("Load to high, maximum load used")


  Emission = (float(a) * pow(float(Speed), 2) + float(b) * float(Speed) + c) * pow(float(Load), 2) + \
           (float(d) * pow(float(Speed), 2) + float(e) * float(Speed) + f) * float(Load) + \
           float(g) * pow(float(Speed), 2) + \
           float(h) * float(Speed) + float(i)

  if Emission < MinEmission :
    Emission = MinEmission
    WarningText.append("Minimal Emission level used")

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
CreateLDV()


#test segment for debuging purposes
if __name__ == "__main__":
  import matplotlib.pyplot as plt
  a = []
  b = []
  c = []
  d = []
  e = []
  for i in range(6, 120):
    b.append(i)
    #CalculateLDV(LDVID, Component, Speed, Gradient=0, Load=0):
    a.append(CalculateLDV(9, 'FC', 80, i)[0])
    c.append(CalculateLDV(9, 'FC', i, 100)[0])
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
  ListTypes()


