# $Id: Ship.py 31 2010-01-12 15:44:40Z tlev $
# -*- coding: iso-8859-1 -*-

'''
Created on 20. okt. 2009

@author: Odd Andre Hjelkrem
modified by Tomas Levin, corrected units
'''

import SEMBA as S
#Create empty dictionaries to load emission data in
#SHIP = {}



def CreateShip():
  S.load_Ship()
  create_vehicle_list()

Vehicle_Types = {}

def create_vehicle_list():
  for k,v in S.H_SHIP.items():
    k=0
    Vehicle_Types[v[0]]= v[0] +"  "+ v[8]

def ListTypes():
  """
  Lists all ships available in the dataset that is loaded.
  """
  #Function to sort as integers
  def compare(a, b):
    return cmp(int(a), int(b)) # compare as integers

  keys = Vehicle_Types.keys()
  keys.sort(compare)
  print "Ship  ID   ;   Description"
  for key in keys:
    print str(key)+ '   ;    '+ Vehicle_Types[key]

def CalculateAUX(id,Fuel='MGO', DWT=-1, GT=-1):
  """ List of shiptypes
  1 Bulk ship
  2 Dry Cargo
  3 Container
  4 Ro Ro
  5 Reefer
  6 Cargo ferry
  7 Passenger ferry
  8 Tanker (oil)
  9 Tanker (Chemical)
  10 Gas tanker (LNG)
  11 Gas tanker (LPG)
  12 Cruise vessel (mechanical drive)
  13 Cruise vessel (electric drive)
  14 vehicle carrier
  
  AUX emissions are returned as grams per hour
  """
  auxData={}
  auxData[1]=['DWT',35.312,0.3603]
  auxData[2]=['DWT',0.7476,0.7796]
  auxData[3]=['DWT',0.5504,0.8637]
  auxData[4]=['GT',1.347,0.7512]
  auxData[5]=['DWT',0.4827,0.9375]
  auxData[6]=['GT',1.655,0.7658]
  auxData[7]=['GT',1.13,0.8123]
  auxData[8]=['DWT',9.9262,0.703]
  auxData[9]=['DWT',5.5294,0.5863]
  auxData[10]=['DWT',0.0047,1.2147]
  auxData[11]=['DWT',18.043,0.5057]
  auxData[12]=['GT',0.9341,0.9482]
  auxData[13]=['GT',0.0142,1.0059]
  auxData[14]=['GT',0.4916,0.8399]

  
  data=auxData[id]
  k=data[1]
  n=data[2]
  if data[0]=='GT' and GT==-1:
    print "Needs GT to caculate Auxilary engine emission"
    return -1
  if data[0]=='DWT' and DWT==-1:
    print "Needs DWT to caculate Auxilary engine emission"
    return -1
  
  EAux=-1
  if data[0]=='GT':
    EAux=float(k) * pow(GT, float(n))
  if data[0]=='DWT':
    EAux=float(k) * pow(DWT, float(n))
  ELoad=-1
  ELay=-1
  if id==1:
    ELoad=EAux*0.32
    ELay=EAux*0.21
  elif  id ==2:
    ELoad=EAux*0.33
    ELay=EAux*0.27
    
  elif  id ==4:
    ELoad=EAux*0.41
    ELay=EAux*0.25
  
  elif  id==8 or id==9 or id==10 or id==11:
    ELoad=EAux*0.62
    ELay=EAux*0.19
    
  elif  id==14:
    ELoad=EAux*0.62
    ELay=EAux*0.19
  else:
    ELoad=EAux*0.43
    ELay=EAux*0.21
  
  #caculate emissions
  components=[]
  components=componentValues(EAux,4)
  #[FC,NOx,CO,HC,PM] g/kWh, CO2=3.2 times fuel consumption
  FC=components[0]
  NOx=components[1]
  CO=components[2]
  HC=components[3]
  PM=components[4]
  CO2=FC*3.17
  
  SO2Lay=-1
  SO2Load=-1
  if Fuel == 'MDO':
    SO2Lay = FC*ELay*((1.0/100)*(64/32))
    SO2Load = FC*ELoad*((1.0/100)*(64/32))
  if Fuel == 'MGO':
    SO2Lay = FC*ELay*((0.2/100)*(64/32))
    SO2Load = FC*ELoad*((0.2/100)*(64/32))
  if Fuel == 'RO':
    SO2Lay = FC*ELay*((2.0/100)*(64/32))
    SO2Load = FC*ELoad*((2.0/100)*(64/32))
  
  EmissionLoad = [FC*ELoad,NOx*ELoad,CO*ELoad,HC*ELoad,PM*ELoad,CO2*ELoad,SO2Load,'g/h']
  EmissionLay =  [FC*ELay,NOx*ELay,CO*ELay,HC*ELay,PM*ELay,CO2*ELay,SO2Lay,'g/h']
  return EmissionLoad, EmissionLay

def componentValues(EngineSize,stroke):
  """Function to return emissions factors for relevant stroke and engine size
  Stroke is either 2 or 4
  return datalist:
  [FC,NOx,CO,HC,PM] g/kWh, CO2=3.17 times fuel consumption
  """
  
  if(EngineSize < 500):
    if(stroke == 2):
      Components = [-1, 16.24, 0.84, 0.45, -1]
    elif(stroke == 4):
      Components = [186.71, 12.23, 1.30, 0.61, 0.36]
    else:
      Components = [-1, -1, -1, -1, -1]
      return Components
  elif(EngineSize < 2500 and EngineSize > 500):
    if(stroke == 2):
      Components = [-1, 16.37, 0.90, 0.43, 0.40]
    elif(stroke == 4):
      Components = [193.43, 11.59, 0.92, 0.55, 0.19]
    else:
      Components = [-1, -1, -1, -1, -1]
      return Components
  elif(EngineSize < 5000 and EngineSize > 2500):
    if(stroke == 2):
      Components = [210.00, 16.05, 0.56, 0.42, 0.50]
    elif(stroke == 4):
      Components = [186.97, 11.94, 0.51, 0.32, 0.20]
    else:
      Components = [-1, -1, -1, -1, -1]
      return Components
  elif(EngineSize < 7500 and EngineSize > 5000):
    if(stroke == 2):
      Components = [175.00, 18.14, 0.67, 0.52, 0.50]
    elif(stroke == 4):
      Components = [183.93, 12.86, 0.54, 0.23, 0.19]
    else:
      Components = [-1, -1, -1, -1, -1]
      return Components
  elif(EngineSize < 10000 and EngineSize > 7500):
    if(stroke == 2):
      Components = [175.00, 16.80, 0.87, 0.47, 0.50]
    elif(stroke == 4):
      Components = [183.49, 12.73, 0.53, 0.24, 0.20]
    else:
      Components = [-1, -1, -1, -1, -1]
      return Components
  elif(EngineSize < 15000 and EngineSize > 10000):
    if(stroke == 2):
      Components = [170.0, 15.56, 0.91, 0.47, 0.50]
    elif(stroke == 4):
      Components = [181.28, 13.15, 0.59, 0.30, 0.20]
    else:
      Components = [-1, -1, -1, -1, -1]
      return Components
  elif(EngineSize < 25000 and EngineSize > 15000):
    if(stroke == 2):
      Components = [170.0, 16.71, 0.80, 0.44, 0.5]
    elif(stroke == 4):
      Components = [181.30, 12.94, 0.61, 0.26, 0.20]
    else:
      Components = [-1, -1, -1, -1, -1]
      return Components
  elif(EngineSize > 25000):
    if(stroke == 2):
      Components = [167.0, 15.24, 0.6, 0.22, 0.50]
    elif(stroke == 4):
      Components = [178.66, 12.80, 0.93, 0.23, 0.22]
    else:
      Components = [-1, -1, -1, -1, -1]
      return Components
  else:
    Components = [-1, -1, -1, -1, -1]
    return Components
    
  return Components
  
def CalculateShipSail(ShipID, Fuel='MDO', stroke=2, GT= -1, DWT=0):
#1  Bulk ship
#2  Dry cargo
#3  Container
#4  Ro-Ro
#5  Reefer
#6  Cargo ferry
#7  Passenger ferry
#8  High-Speed ferry
#9  Tanker
#10  Gas tanker
#11  Cruise vessel
#12  Vehicle carrier

  WarningText = []
  #Split into weight groups
  if(GT > 0):
    if(GT < 500):
      GTGroup = 1
    elif(GT < 5000):
      GTGroup = 2
    elif(GT < 10000):
      GTGroup = 3
    elif(GT < 25000):
      GTGroup = 4
    elif(GT < 50000):
      GTGroup = 5
    elif(GT < 100000):
      GTGroup = 6
    elif(GT < 250000):
      GTGroup = 7
    elif(GT > 250000):
      GTGroup = 8
    else:
      WarningText.append("GT not in range")
  else:
    if(DWT == -1):
      WarningText.append("GT=-1 && DWT=-1")
      GTGroup = 1
      DWTGroup = 1
    else:
      if(DWT < 500):
        DWTGroup = 1
      elif(DWT < 5000):
        DWTGroup = 2
      elif(DWT < 10000):
        DWTGroup = 3
      elif(DWT < 25000):
        DWTGroup = 4
      elif(DWT < 50000):
        DWTGroup = 5
      elif(DWT < 100000):
        DWTGroup = 6
      elif(DWT < 250000):
        DWTGroup = 7
      else:
        DWTGroup = 8
        #innvariabel til csvfil: shipID og vektklasse
        #Get Data from the Ship dictionary
  if(GT > 0):
    weightgroup = GTGroup
  else:
    weightgroup = DWTGroup
  key = str(ShipID) + "_" + str(weightgroup)
  value = S.H_SHIP[key]
  data = value
  VehicleID = data[0]
  WeightGroup = data[1]
  DWTSpeed = data[2]
  GTSpeed = data[3]
  DWTk = data[4]
  DWTn = data[5]
  GTk = data[6]
  GTn = data[7]

  Emission = -1


  #Step 1: Determination of average speed
   #This step is done in the .csv-file, moved to the semba initialization file

  #Step 2: Determination of main engine power output
  if(GT > 0):
    ME = float(GTk) * pow(GT, float(GTn)) #kW
  elif(DWT > 0): #DWT>0
    ME = float(DWTk) * pow(DWT, float(DWTn))#kW
  else:
    ME = -1

  #Step 3: Identification of main engine type
  #2 or 4 stroke engine, input in function


  #Step 4: Estimation of fuel consumption and emissions:
  Components = [] #[FC,NOx,CO,HC,PM] g/kWh, CO2=3.2 times fuel consumption
  
  Components=componentValues(ME,stroke)
  #WarningText.append(w)
  
  if(GT == -1):
    if(DWT == -1):
      WarningText.append("Can not calculate vessel speed")
    else:
      Speed = DWTSpeed
  else:
    Speed = GTSpeed
  #
  if(Speed != 0):
    kph = float(Speed) * 1.852 #km/h kilometers per hour
  else:
    kph = -1
  
  FC=Components[0]
  NOx=Components[1]
  CO=Components[2]
  HC=Components[3]
  PM=Components[4]
  CO2=FC*3.17

  #Emissions=[FC*ME/kph,NOx*ME/kph,CO*ME/kph,HC*ME/kph,PM*ME/kph,CO2*ME/kph]
         
  #Sulphur calculations are hereSO2 calculations come here    
  #MDO = Marine diesel Oil
  #MGO = Marine gas oil
  #RO  = Residual oil
  SO2=-1
  if Fuel == 'MDO':
    SO2 = FC*ME/kph*((1.0/100)*(64/32))
  if Fuel == 'MGO':
    SO2 = FC*ME/kph*((0.2/100)*(64/32))
  if Fuel == 'RO':
    SO2 = FC*ME/kph*((2.0/100)*(64/32))    
    
  Emissions=[FC*ME/kph,NOx*ME/kph,CO*ME/kph,HC*ME/kph,PM*ME/kph,CO2*ME/kph, SO2,"g/km",  WarningText]   
  return Emissions

###########____Load Data____##################
CreateShip()

print "Hei"
ListTypes()

#Test for TPG ship

#CalculateShip(ShipID, Component, stroke=2, GT= -1, DWT=0, Load=0)
print CalculateShipSail(3, "MGO", stroke=4, GT= -1, DWT=1278)
#CalculateAUX(id,loadingTime,layTime, DWT=-1, GT=-1):
print CalculateAUX(3,'MGO',GT=-1,DWT=1287)