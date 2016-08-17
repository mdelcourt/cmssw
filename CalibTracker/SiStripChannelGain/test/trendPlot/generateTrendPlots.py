from ROOT import *
from array import array
import os, optparse, json
from commands import getstatusoutput

pwd = os.path.realpath(__file__)
pwd = pwd[:-len(pwd.split("/")[-1])-1]
print "Working dir : %s"%pwd

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--in'        ,    dest='inputDir'          , help='Folder containing payloads', default=pwd[:-len(pwd.split("/")[-1])])
parser.add_option('-o', '--out'       ,    dest='outputDir'         , help='Folder to publish plots'   , default='.')
(opt, args) = parser.parse_args()

print "Input dir  = %s"%opt.inputDir
print "Output dir = %s"%opt.outputDir



veto = json.load(open(pwd+"/badRuns.json","r")) # ["Data_Run_247992_to_247992_CalibTree"]
print veto
canvases=[]
graphs=[]
legends=[]
def execute(script,args):
   argstr=""
   for a in args:
      argstr+="%s,"%a
   argstr=argstr[:-1]
   cmd="echo 'gROOT->LoadMacro(\"%s/%s_C.so\"); %s(%s,\"%s\"); gSystem->Exit(0);' | root -b -l"%(pwd,script,script,argstr,pwd)
   out=getstatusoutput(cmd)[1]
   print cmd
   if "segmentation violation" in out:
      print "Seg fault !"
      return(-1)
   else:
      print "ok"
      print out
      return(1)


def drawPlot(data ,header="MPV", Yleg = "MPV (adc/mm)",Ymin=200,Ymax=350,showAv=False,small=False):
   names=data[0].keys()
   names.sort()
   canvases.append(TCanvas())
   payloadId = [int(x[len("Data_Run_"):x.find("_",len("Data_Run")+1)]) for x in names]
   colours = [kBlack,kRed+1,kGreen+1,kBlue+1,kOrange+1]
   leg=TLegend(0.15,0.75,0.35,0.97)
   leg.SetHeader(header)
   g_Name=["Averaged","TIB","TID","TOB","TEC"]
   if not showAv:
      g_Name=g_Name[1:]
      colours=colours[1:]
      data=data[1:]
   for i in range(len(data)):
      sortedMPV=[data[i][pName] for pName in names]
      graphs.append(TGraph(len(data[0]),array('f',payloadId),array('f',sortedMPV)))
      graphs[-1].SetLineColor(colours[i])
      graphs[-1].SetMarkerColor(colours[i])
      leg.AddEntry(graphs[-1],g_Name[i],"lp")
      if (i==0):
         graphs[-1].SetTitle(header)
         graphs[-1].Draw("ALP*")
         graphs[-1].GetYaxis().SetRangeUser(Ymin,Ymax)
         graphs[-1].GetXaxis().SetTitle("Payload Number")
         graphs[-1].GetYaxis().SetTitle(Yleg)
         if small:
            lRun = payloadId[-1]
            graphs[-1].GetXaxis().SetRangeUser(lRun-5000,lRun+100)
      else:
         graphs[-1].Draw("LP*same")
   leg.Draw()
   legends.append(leg)
   pictureName="/trend_"+header.replace(" ","_")
   if small:
      pictureName+="_last"
   pictureName+=".png"
   canvases[-1].Print(opt.outputDir+pictureName)


#payloadFolder = "/afs/cern.ch/cms/tracker/GainCalibration/CMSSW_8_0_7_patch1/src/CalibTracker/SiStripChannelGain/test/"
payloadFolder = opt.inputDir
collector="computeSummary"


#Get files to process
f=TFile(pwd+"/gainTrend.root")
t=f.Get("payloadSummary")

processedRuns = [ str(payload.PayloadName) for payload in t ]


toProcess = [ payload if "Data_Run" in payload and not payloadFolder+"/"+payload in veto and not payload in processedRuns and "Gains.root" in os.listdir(payloadFolder+"/"+payload) else '' for payload in os.listdir(payloadFolder)]
while '' in toProcess:toProcess.remove('')
print "Left to process : %s"%toProcess
f.Close()



#Process files
#Compile
if len(toProcess)>0 : os.system("root -b -l -q %s.C+"%collector)
for payload in toProcess:
      fullPath='\"'+payloadFolder+"/"+payload+"/Gains.root\""
      arg=[fullPath,'\"'+payload+'\"']
      status = execute(collector,arg)
      if status < 0:
         veto.append(payloadFolder+"/"+payload)



#Plotter :
f=TFile(pwd+"/gainTrend.root")
t=f.Get("payloadSummary")


names = [str(payload.PayloadName) for payload in t]
names.sort()
MPV   = [{} for i in range(5)]
Error = [{} for i in range(5)]
Clean = [{} for i in range(5)]
for payload in t:
   if payload.MPV_av==0:
      names.remove(payload.PayloadName)
      continue
   if payload.Error_av<1:
      MPV[0][str(payload.PayloadName)]=float(payload.MPV_av    )  
      MPV[1][str(payload.PayloadName)]=float(payload.MPV_TIB)
      MPV[2][str(payload.PayloadName)]=float(payload.MPV_TID)
      MPV[3][str(payload.PayloadName)]=float(payload.MPV_TOB)
      MPV[4][str(payload.PayloadName)]=float(payload.MPV_TEC)
   if payload.Error_av<1:
      Error[0][str(payload.PayloadName)]=float(payload.Error_av )  
      Error[1][str(payload.PayloadName)]=float(payload.Error_TIB)
      Error[2][str(payload.PayloadName)]=float(payload.Error_TID)
      Error[3][str(payload.PayloadName)]=float(payload.Error_TOB)
      Error[4][str(payload.PayloadName)]=float(payload.Error_TEC)
      Clean[0][str(payload.PayloadName)]=float(payload.CleanMPV_av )  
      Clean[1][str(payload.PayloadName)]=float(payload.CleanMPV_TIB)
      Clean[2][str(payload.PayloadName)]=float(payload.CleanMPV_TID)
      Clean[3][str(payload.PayloadName)]=float(payload.CleanMPV_TOB)
      Clean[4][str(payload.PayloadName)]=float(payload.CleanMPV_TEC)
#MPV.append({ float(payload.MPV) for payload in t}))
#MPV.append([ float(payload.MPV_TIB) for payload in t]) 
#MPV.append([ float(payload.MPV_TID) for payload in t])
#MPV.append([ float(payload.MPV_TOB) for payload in t])
#MPV.append([ float(payload.MPV_TEC) for payload in t])
linear = [i for i in range(len(MPV[0]))]


drawPlot(MPV)
drawPlot(Error,"Error","Relative error",0,0.05)
drawPlot(Clean,"Clean MPV")

drawPlot(MPV,small=True)
drawPlot(Error,"Error","Relative error",0,0.05,small=True)
drawPlot(Clean,"Clean MPV",small=True)
open(pwd+"/badRuns.json","w").write(json.dumps(veto))

#payloadId = [int(x[len("Data_Run_"):x.find("_",len("Data_Run")+1)]) for x in names]
#
#colours = [kBlack,kRed+1,kGreen+1,kBlue+1,kOrange+1]
#leg=TLegend(0.75,0.75,0.97,0.97)
#leg.SetHeader("MPV")
#g_Name=["Averaged","TIB","TID","TOB","TEC"]
#g_MPV = []
#for i in range(len(MPV)):
#   sortedMPV=[MPV[i][pName] for pName in names]
#   g_MPV.append(TGraph(len(MPV[0]),array('f',payloadId),array('f',sortedMPV)))
#   g_MPV[-1].SetLineColor(colours[i])
#   g_MPV[-1].SetMarkerColor(colours[i])
#   leg.AddEntry(g_MPV[-1],g_Name[i],"lp")
#   if (i==1):
#      g_MPV[-1].Draw("ALP*")
#      g_MPV[-1].GetYaxis().SetRangeUser(220,500)
#      g_MPV[-1].GetXaxis().SetTitle("Payload Number")
#      g_MPV[-1].GetYaxis().SetTitle("MPV (adc/mm)")
#   else: 
#      g_MPV[-1].Draw("LP*same")
#leg.Draw()

