import os


calibFolder = "/afs/cern.ch/cms/tracker/GainCalibration"

releases = os.listdir(calibFolder)

goodReleases = []

for r in releases:
   folder = calibFolder+"/"+r+"/src/CalibTracker/SiStripChannelGain/test/7TeVData/"
   if not os.path.isdir(folder):
      continue
   folder = calibFolder+"/"+r+"/src/CalibTracker/SiStripChannelGain/test/"
   goodFolder=False
   for x in os.listdir(folder):
      if "Data_Run_" in x:
         goodFolder=True
         break
   if goodFolder:
      print "%s is a good folder !"%r
      goodReleases.append(r)
   else:
      print "%s is a bad folder :("%r

print goodReleases
for r in goodReleases:
   print "Processing release %s"%r
   os.system("python generateTrendPlots.py -i %s/%s/src/CalibTracker/SiStripChannelGain/test/"%(calibFolder,r))

