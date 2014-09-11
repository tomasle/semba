# $Id: Train.py 36 2010-01-14 19:20:52Z tlev $
# -*- coding: iso-8859-1 -*-


"""
Created on 20. okt. 2009
Original code written by Odd A. Hjelkrem, this was later changed by Tomas Levin by segmenting into
functions and a change to numerical integration was used to calculate energy in the acceleration phase.
Format of the input data file was also changed so that calculation of CR is done within the script and not outside
Energy efficiency is included as a last step. Values are stored in the Train data file: ./data/train.csv
For diesle trains there is one factor for all losses from fuel to wheels, for electric trains 2 factors are used one for losses
from the pantograph to the wheels and another factor for losses in the catenary system.
@author: Levin and Hjelkrem
"""
import SEMBA as S
import sys

#Variable for turning on DEBUG printing
#DEBUG = True
DEBUG = False

def CreateTrain():
  S.load_Train()


from math import sqrt

def calcCr(speed, massLoco, massWagons, massTrain, axels, Fsl, Csv, C1, C2,Fat ):
  """ Calculation of Cr
  Data is based on documentation in ARTEMIS deliverabel D7a and D7 part b
  D7A page 28-29 , D7 part B page 30-33
  There are inacuracies between the two reports when it comes to these equations.
  D7a seems to have the correct equations based on comparison of text and examples.
  The equations from D7a are used
  """
  refSpeed = 27.778 # reference speed in m/s
  Fsv = float(Csv)+(Fat*axels)/(massTrain*S.g)
  #print Fsv
  C0 = (float(Fsl)*float(massLoco)+float(Fsv)*float(massWagons))/float(massTrain)
  #print C0
  Cr = C0+C1*(float(speed)/float(refSpeed))+C2*(pow((float(speed)/float(refSpeed)),2))
  #print Cr
  return Cr

def calcCl(CLl,CLw,nWagons):
  """Caclulation of CL
  This function assumes that wagons are homogeneous and loaded, factors for
  locomotive and wagon resistance.
  CLl Loco       -read from file
  CLw Wagon      -read from file
  nWagons        -number of wagons read from file
  """
  CL=float(CLl)+float(CLw)*float(nWagons)
  return CL


def calcAccEnergy(initialSpeed,topSpeed, acceleration,distance,Cl,area,massLoco,massWagons,grade,Csv,C1,C2,Fsl,axels):
  """ Calculate Energy usage in acceleration phase
  Calculates energy usage in acceleration phase, assumes constant distance over segment.
  Numeric integration is used, with 1 meter resolution, rolling and air resistance
  is calculated for every meter then summed up. Equation used is found in ARTEMIS deliverable D7a
  page 13. The user needs to calculate the needed acceleration distance.

  Result is Energy in Mega joule
  """
  #rho = 1.2 # kg/m^3 The Air density
  s=1 # distance increment in integration, one meter used
  v0=initialSpeed
  v=0
  a= acceleration
  calcSpeed =[]
  calcDistance =[]
  massTrain = float(massLoco) + float(massWagons)
  EnergyUsed=[]
  #calcSpeed.append(0)
  #calcDistance.append(0)
  for i in range(0,int(distance)):
      v=sqrt((v0*v0)+(2*a*s))
      if v>topSpeed:
        v=topSpeed
      v0=v
      Cr=calcCr(v, massLoco, massWagons, massTrain, axels, Fsl, Csv, C1, C2,100)
      ERoll = massTrain*(Cr*S.g+S.g*grade+acceleration)
      EAir = 0.5*S.rho*Cl*area*pow(v,2)
      E = (ERoll + EAir)/ 1000000.0 # Convert to MJ
      EnergyUsed.append(E)
      calcSpeed.append(v0)
      calcDistance.append(i)

  time =(v-initialSpeed)/a
  print "Seconds used in acceleration phase: ", time
  E = sum(EnergyUsed)
  return E,calcDistance, calcSpeed

def calcConstEnergy(speed,distance,Cl,area,massLoco,massWagons,grade,Csv,C1,C2,Fsl,axels):
  """ Calculate energy usage along a leg with constant speed
  Equation used is found in ARTEMIS deliverable D7a
  page 13.

  Result is in Mega Joules
  """
  if speed==0:
    distance=0
  massTrain = massLoco + massWagons
  Cr=calcCr(speed, massLoco, massWagons, massTrain, axels, Fsl, Csv, C1, C2,100)
  ERoll = massTrain*(Cr*S.g+S.g*grade)
  EAir = 0.5*S.rho*Cl*area*pow(speed,2)
  E = (ERoll+EAir)*distance/1000000 #result in Mega Joules
  calcSpeed=[]
  calcDistance=[]

  for i in range(1,int(distance)):
    calcSpeed.append(speed)
    calcDistance.append(i)
  return E, calcDistance,calcSpeed

def calcDeccelerationDistance(startSpeed,endSpeed,acc):
  calcSpeed=[]
  calcDistance=[]
  distance = (pow(endSpeed,2)-pow(startSpeed,2))/(2*acc)
  s=1 #resolution is 1 meter
  v0=startSpeed
  for i in range(0,int(distance-0.5)):
      v=sqrt((v0*v0)+(2*acc*s))
      v0=v
      calcSpeed.append(v0)
      calcDistance.append(i)
  return calcDistance, calcSpeed

def calcLink(length, #The total length of the link to becalculated
             entrySpeed, # Then speed when the train enters the link
             avgSpeed, # The wanted average speed on the link
             nStop, # The number og stops on the link
             grade, # The gradient in the direction of travel.
             acc, #the requested acceleration in m/s^2
             decBreak, # The requested deceleration when breaking
             trainID): #Train identification, found in data file
  """Function to calculate distance in three main phases
  Entry phase: adjustment from previous link, 3 sub phases:
    * Decelerate from previous link
    * Constant speed previous link
    * Accelerate from previous link
  Stoping phase: distance for singel and N number of stops
  Constant phase: distance of the link that is traversed with constant speed
  The link max speed and constant speed is higher than average speed due to time
  lost in acceleration sections. The new max speed is found iteratively to give the correct
  average speed on the link

  Energy is reported in Mega Joule
  """
  tc=[] # Create an empty list to store train data
  td = S.H_TRAIN[str(trainID)] #extract the train data from the train hash as a list
  Cl = calcCl(float(td[3]),float(td[4]),float(td[9]))
  area =float(td[5])
  massLoco = float(td[6])
  taraMassWagons =(float(td[7])) # weight of all wagons without payload
  massPayload =(float(td[8]))  #total payload of the train
  totalMassWagons =taraMassWagons+massPayload
  Csv = float(td[10])
  C1 =float(td[11])
  C2= float(td[12])
  Fsl = float(td[13])
  axels =float(td[14])


  ErrorMessages = []
  entryPhaseDistance=0
  stoppingDistance=0
  ConstantPhaseDistance=0

  #Iteratively loop until average speed including stops equals average speed on link
  topSpeed=avgSpeed
  calcAvgSpeed = 0
  difference=1
  EntryMode='NONE' #variable to indicate if one has to accelerate or decelerate when entering link

  #while avgSpeed>calcAvgSpeed:
  while difference>0:
    #Find the three phase distances
    if str(entrySpeed)==str(topSpeed):
      entryPhaseDistance=0
    elif entrySpeed<topSpeed:
      entryPhaseDistance =(pow(topSpeed,2)-pow(entrySpeed,2))/(2*acc)
      EntryMode='ACC'
    elif entrySpeed>topSpeed:
      entryPhaseDistance =(pow(entrySpeed,2)-pow(topSpeed,2))/(2*decBreak)
      EntryMode='DEC'
    #find the distance in the stopping phase
    if nStop==0:
      stoppingDistance=0 #there are no stops
    elif nStop >0:
      stopBreakDist= (pow(topSpeed,2))/(2*decBreak*-1)
      stopAccDist =(pow(topSpeed,2))/(2*acc)
      stoppingDistance=(stopBreakDist+stopAccDist)*nStop
    #calculate constant speed distance
    if entryPhaseDistance >0:
      ConstantPhaseDistance = length - (entryPhaseDistance+stoppingDistance)
    else:
      ConstantPhaseDistance = length - (entryPhaseDistance*-1+stoppingDistance)
    if ConstantPhaseDistance<10:
      ErrorMessages.append('Link is to short for acceleration and stops')
      ErrorMessages.append('The constant part of the segment is to short')
      #If the constant part is to short algorithm for finding new top speed will not converge.
      sys.exit("ERROR: Not enough distance for the requested accelerations\n" +
      "to many stops or to short distance")
    #Calculate time usage in the different phases and new average speed because of this
    if entryPhaseDistance >0:
      tEntry=(topSpeed-entrySpeed)/acc
    else:
      tEntry=(topSpeed-entrySpeed)/decBreak

    tStopp=((topSpeed/decBreak)*-1.0)*nStop
    tStart=(topSpeed/acc)*nStop
    tConstant=ConstantPhaseDistance/topSpeed
    tTotal = tEntry+tStopp+tStart+tConstant
    calcAvgSpeed=length/tTotal
    if EntryMode=='DEC':
      difference = avgSpeed - calcAvgSpeed
    else:
      #difference = calcAvgSpeed - avgSpeed
      difference = avgSpeed - calcAvgSpeed
      if difference<0.001:
        difference=0.0

    if calcAvgSpeed<avgSpeed:
      topSpeed=topSpeed+0.05
    if calcAvgSpeed>avgSpeed:
      topSpeed=topSpeed-0.05
  ### DEBUG Statement
  if DEBUG:
    a=0
    print "Top speed set to : ", topSpeed
    if entryPhaseDistance > 0:
      print "Entry acceleration distance :          " + str(entryPhaseDistance)
      a= entryPhaseDistance
    else:
      print "Entry acceleration distance :          " + str(entryPhaseDistance*-1)
      a= entryPhaseDistance*-1
    print "Stopping distance           :          " + str(stoppingDistance)
    print "Constant distance           :          " + str(ConstantPhaseDistance)
    print "TOTAL distance              :          " + str(a+stoppingDistance+ConstantPhaseDistance)
  #calculate energy usage in the different phases

  #Initialization to hinder errors when no acceleration phase is present or if link entry speed is higher that calculated top speed
  entryPhaseEnergy =[0,0,0]
  singelAccEnergy =[0,0,0]
  ConstantPhaseEnergy=[0,0,0]
  stoppingPhaseEnergy=0

  if entryPhaseDistance>0:
    if entrySpeed<topSpeed: #there is a need to accelerate and energy will be used
      entryPhaseEnergy= calcAccEnergy(entrySpeed,topSpeed,acc,entryPhaseDistance,Cl,area,massLoco,totalMassWagons,grade,Csv,C1,C2,Fsl,axels)
  if nStop >0:
    singelAccEnergy = calcAccEnergy(0,topSpeed,acc,stopAccDist,Cl,area,massLoco,totalMassWagons,grade,Csv,C1,C2,Fsl,axels)
    stoppingPhaseEnergy =singelAccEnergy[0] * nStop     #acc from stopping calculated for all stops
  if ConstantPhaseDistance >0:
    ConstantPhaseEnergy=calcConstEnergy(topSpeed,ConstantPhaseDistance,Cl,area,massLoco,totalMassWagons,grade,Csv,C1,C2,Fsl,axels)
  else:
    ConstantPhaseEnergy=[0,0,0]
  totalLinkEnergy =  entryPhaseEnergy[0]+ singelAccEnergy[0]*nStop+ConstantPhaseEnergy[0]

  #Create data for a distance speed plot.
  totDistance =[]
  totSpeed=[]

  if str(float(entrySpeed))!=str(float(topSpeed))and entryPhaseDistance >0:
    for i in range(0,len(entryPhaseEnergy[1])):
      totDistance.append(entryPhaseEnergy[1][i])
      totSpeed.append(entryPhaseEnergy[2][i])

  tempEntrySpeeds=calcDeccelerationDistance(entrySpeed,topSpeed,decBreak)
  if str(float(entrySpeed))!=str(float(topSpeed))and entryPhaseDistance <0:
    for i in range(0,len(tempEntrySpeeds[0])):
      totDistance.append(tempEntrySpeeds[0][i])
      totSpeed.append(tempEntrySpeeds[1][i])

  stoppingSpeed = calcDeccelerationDistance(topSpeed,0,decBreak)
  if nStop >0:
    for i in range(0,nStop):
      for j in range(0,len(stoppingSpeed[0])):
        totDistance.append(stoppingSpeed[0][j])
        totSpeed.append(stoppingSpeed[1][j])
      #The next two lines enshure that speed reaches 0
      totDistance.append(stoppingSpeed[0][j]+0.5)
      totSpeed.append(0)
      for k in range(0,len(singelAccEnergy[1])):
        totDistance.append(singelAccEnergy[1][k])
        totSpeed.append(singelAccEnergy[2][k])
  ### DEBUG Statement
  if DEBUG:
    a=0
    b=0
    c=0
    if entryPhaseDistance >0:
      print "Entry acceleration distance length:          " + str(len(entryPhaseEnergy[1]))
      a= len(entryPhaseEnergy[1])
    if entryPhaseDistance <0:
      print "Entry deceleration distance length:          " + str(len(tempEntrySpeeds[1]))
      a= len(tempEntrySpeeds[1])
    if nStop > 0:
      print "Acceleration length               :          " + str(len(singelAccEnergy[1])*nStop)
      print "Decceleration length              :          " + str(len(stoppingSpeed[1])*nStop)
      b= len(singelAccEnergy[1])*nStop
      c= len(stoppingSpeed[1])*nStop
    print "Constant phase lenght             :          " + str(len(ConstantPhaseEnergy[1]))
    print "Total length from energy routines :          " + str(a+b+c+len(ConstantPhaseEnergy[1]))

  #we have now come to the constant speed strech
  for i in range(0,int(ConstantPhaseDistance)):
    totDistance.append(i)
    totSpeed.append(topSpeed)
  #Calculate needed energy when we include losses from
  TOTtotalLinkEnergy = CalcEnergyIncludingLoss(totalLinkEnergy,trainID)
  TOTentryPhaseEnergy= CalcEnergyIncludingLoss(entryPhaseEnergy[0],trainID)
  TOTstoppingPhaseEnergy= CalcEnergyIncludingLoss(stoppingPhaseEnergy,trainID)
  TOTConstantPhaseEnergy= CalcEnergyIncludingLoss(ConstantPhaseEnergy[0],trainID)
  grossAvgEnergyUsage = float(TOTtotalLinkEnergy)/((float(length)/1000.0)*(float(totalMassWagons)/1000.0+float(massLoco)/1000.0))
  netAvgEnergyUsage =float(TOTtotalLinkEnergy) / ((float(massPayload)/1000.0)*(float(length)/1000.0))
  #Return energy usage, Total , EntryPhase, StoppingPhase , ConstantPhase
  return TOTtotalLinkEnergy, TOTentryPhaseEnergy, TOTstoppingPhaseEnergy, TOTConstantPhaseEnergy, ErrorMessages, totDistance,totSpeed, grossAvgEnergyUsage, netAvgEnergyUsage

def CalcEnergyIncludingLoss(Energy,TrainID):
  td = S.H_TRAIN[str(TrainID)]
  LocomotiveType = td[1]
  EnergyWithLoss = -1 # used to make sure that the user understands that an error occured
  if LocomotiveType=='DIELSEL':
    EnergyWithLoss = float(Energy) / float(td[15])
  if LocomotiveType=='ELECTRIC':
    EnergyWithLoss = float(Energy)/float(td[15])
  return EnergyWithLoss



###########____Load Data____##################
CreateTrain()

#test segment for debuging purposes
if __name__ == "__main__":
  import matplotlib.pyplot as plt

  """
  #calcE(0,2.7,138)
  #     calcCr(speed, massLoco, massWagons, massTrain, axels, Fsl, Csv, C1, C2,Fat )
  #print calcCr(26.45, 115000, 314000, 429000, 30, 0.004, 0.006, 0.0005, 0.0006,100 )
  #print calcCr(27.778, 123000, 400000, 523000, 20, 0.004, 0.0006, 0.0005, 0.0006,100 )
  #print calcAccEnergy(0,0.15,1000,6,10,115000,858880,0.0,0.0006,0.0005,0.0006,0.004,117)
  test=[]
  aks=[]
  for i in range(-5,5):
    test.append(calcConstEnergy(10,1000,6,10,115000,858880,i/100.0,0.0006,0.0005,0.0006,0.004,117))
    aks.append(i/100.0)
  plt.plot(aks, test)
  plt.show()
  """
  """
  #Data for Berkåk - Oppdal
  a = calcLink(54900, #length, 3
             0.0,       #entrySpeed,
             22.0,    #avgSpeed,
             5,       #nStop,
             -0.000,   #grade,
             0.3,     #acc,
             -0.5,     #decBreak,
             1)       #Train ID
  """

  #Data for Dombås Åndalsnes


  Length = 11000
  EntrySpeed = 0
  AvgSpeed = 22
  NuberOfStops = 1
  Grade = 0
  acc =  0.3
  decBreak= -0.5
  TrainID = 1

  a=calcLink(Length,EntrySpeed,AvgSpeed,NuberOfStops,Grade,acc,decBreak,TrainID)


  #a = calcLink(9089.99999999997,0,19.4289679381212,1,-0.00122112211221121,0.3,-0.5,3)

  Oppover=[]
  Nedover=[]

  Nedover.append(calcLink(9089.99999999997,0,19.4289679381212,0,-0.00122112211221121,0.3,-0.5,3)[0])
  Nedover.append(calcLink(8550.00000000001,19.4289679381212,19.4289679381212,0,-0.00164912280701754,0.3,-0.5,3)[0])
  Nedover.append(calcLink(9099.99999999997,19.4289679381212,19.4289679381212,0,-0.000263736263736262,0.3,-0.5,3)[0])
  Nedover.append(calcLink(10110,19.4289679381212,19.4289679381212,0,0.000148367952522255,0.3,-0.5,3)[0])
  Nedover.append(calcLink(10840,19.4289679381212,19.4289679381212,0,-0.00165129151291513,0.3,-0.5,3)[0])
  Nedover.append(calcLink(9109.99999999996,19.4289679381212,19.4289679381212,0,-0.00445664105378706,0.3,-0.5,3)[0])
  Nedover.append(calcLink(18250,19.4289679381212,19.4289679381212,0,-0.0165095890410959,0.3,-0.5,3)[0])
  Nedover.append(calcLink(13430,19.4289679381212,19.4289679381212,0,-0.0109233060312733,0.3,-0.5,3)[0])
  Nedover.append(calcLink(7640.00000000004,19.4289679381212,19.4289679381212,0,-0.00801047120418844,0.3,-0.5,3)[0])
  Nedover.append(calcLink(10090,19.4289679381212,19.4289679381212,0,-0.00555004955401389,0.3,-0.5,3)[0])
  Nedover.append(calcLink(8029.99999999997,19.4289679381212,19.4289679381212,0,-0.000660024906600251,0.3,-0.5,3)[0])
  print "Energi forbruk nedover"
  for segment in Nedover:
    print segment

  Oppover.append(calcLink(8029.99999999997,0,17.3094056255568,0,0.000660024906600251,0.3,-0.5,3)[0])
  Oppover.append(calcLink(10090,17.3094056255568,17.3094056255568,0,0.00555004955401389,0.3,-0.5,3)[0])
  Oppover.append(calcLink(7640.00000000004,17.3094056255568,17.3094056255568,0,0.00801047120418844,0.3,-0.5,3)[0])
  Oppover.append(calcLink(13430,17.3094056255568,17.3094056255568,0,0.0109233060312733,0.3,-0.5,3)[0])
  Oppover.append(calcLink(18250,17.3094056255568,17.3094056255568,0,0.0165095890410959,0.3,-0.5,3)[0])
  Oppover.append(calcLink(9109.99999999996,17.3094056255568,17.3094056255568,0,0.00445664105378706,0.3,-0.5,3)[0])
  Oppover.append(calcLink(10840,17.3094056255568,17.3094056255568,0,0.00165129151291513,0.3,-0.5,3)[0])
  Oppover.append(calcLink(10110,17.3094056255568,17.3094056255568,0,-0.000148367952522255,0.3,-0.5,3)[0])
  Oppover.append(calcLink(9099.99999999997,17.3094056255568,17.3094056255568,0,0.000263736263736262,0.3,-0.5,3)[0])
  Oppover.append(calcLink(8550.00000000001,17.3094056255568,17.3094056255568,0,0.00164912280701754,0.3,-0.5,3)[0])
  Oppover.append(calcLink(9089.99999999997,17.3094056255568,17.3094056255568,0,0.00122112211221121,0.3,-0.5,3)[0])

  print "Energi forbruk oppover"
  for segment in Oppover:
    print segment

  print "testdata"
  print sum(Nedover)

  print "Total energy used       :", a[0]
  print "Entry phase energy      :", a[1]
  print "Stopping phase energy   :", a[2]
  print "Constant phase energy   :", a[3]
  print "The following error messages where created\n", a[4]

  print '************************************************************'
  print 'Energy per KiloJoul/tkm (Gross tonns): ',   a[7]*1000 , "    ", a[7]*1000/3.6, " Wh"
  print 'Energy per KiloJoul/tkm (Net tonns)  : ',   a[8]*1000, "    " , a[8]*1000/3.6, " Wh"

  i=1

  dist=[]
  pltAvgSpeed=[]
  for i in range(0, len(a[5])):
    dist.append(i)
    pltAvgSpeed.append(22.0)
  #plt.axhline(linewidth=4, color='r')
  plt.plot(dist,a[6])
  plt.plot(dist,pltAvgSpeed)
  """
  avgspd=[]
  d=[]
  for i in range(0,15000):
    avgspd.append(22)
    d.append(i)
  plt.plot(d,avgspd)
  """
  plt.show()


