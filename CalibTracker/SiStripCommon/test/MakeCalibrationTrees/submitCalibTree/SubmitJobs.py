#!/usr/bin/env python
import urllib
import string
import os
import sys
import commands
import time
import optparse
sys.exit()
usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-r', '--run'        ,    dest='runNumber'          , help='Run number to process (-1 --> Submit all)', default='-1')
parser.add_option('-f', '--firstFile'  ,    dest='firstFile'          , help='first file to process (-1 --> automatic)' , default='-1')
parser.add_option('-l', '--lastFile'   ,    dest='lastFile'           , help='last fil to process (-1 --> automatic)'   , default='-1')
parser.add_option('-d', '--dataset'    ,    dest='datasetType'        , help='Dataset type (Aag or Std)'                , default='all')
parser.add_option('-c', '--corrupted'  ,    dest='corrupted'          , help='Check for corrupted runs'                 , default=False, action="store_true")
(opt, args) = parser.parse_args()

AAG = (opt.datasetType.lower()=="aag")
if not opt.datasetType.lower() in ["std","all","aag"]:
   print "Unknown dataset type : %s" % opt.datasetType
   sys.exit(0)

runId     = int(opt.runNumber   )
firstFile = int(opt.firstFile   )
lastFile  = int(opt.lastFile    )
checkCorrupted = opt.corrupted


DATASET = '/StreamExpress/Run2016B-SiStripCalMinBias%s-Express-v*/ALCARECO'%('AfterAbortGap' if AAG else '')

# Set the correct environment
CMSSWDIR='/afs/cern.ch/cms/tracker/sistrvalidation/Calibration/CalibrationTree/CMSSW_8_0_7_patch1/src/'
RUNDIR = '/afs/cern.ch/cms/tracker/sistrvalidation/Calibration/CalibrationTree/CMSSW_8_0_7_patch1/src/CalibTracker/SiStripCommon/test/MakeCalibrationTrees'

OUTDIR = '/afs/cern.ch/cms/tracker/sistrvalidation/Calibration/CalibrationTree/CMSSW_8_0_7_patch1/src/CalibTracker/SiStripCommon/test/MakeCalibrationTrees/CalibTrees%s/'%("_Aag" if AAG else '')

#CMSSWDIR = '/afs/cern.ch/user/q/querten/workspace/public/CalibTreeUpdate/CMSSW_5_3_8_patch3/src'
#RUNDIR = '/afs/cern.ch/user/q/querten/workspace/public/CalibTreeUpdate/CMSSW_5_3_8_patch3/src/newScript'
CASTORDIR = '/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree/GR16%s'%("_Aag" if AAG else '')
#CASTORDIR = '/castor/cern.ch/cms/store/group/tracker/strip/calibration/calibrationtree/GRIN' # used for GRIN
#CASTORDIR = '/castor/cern.ch/cms/store/group/tracker/strip/calibration/calibrationtree/GR12'

nFilesPerJob=25 #used to split jobs when they are many files for a given run

os.environ['PATH'] = os.getenv('PATH')+':/afs/cern.ch/cms/sw/common/'
os.environ['CMS_PATH']='/afs/cern.ch/cms'
os.environ['FRONTIER_PROXY'] = 'http://cmst0frontier.cern.ch:3128'
os.environ['SCRAM_ARCH']='slc6_amd64_gcc530'

if AAG:
   collection = "ALCARECOSiStripCalMinBiasAfterAbortGap"
else:
   collection = "ALCARECOSiStripCalMinBias"


initEnv=''
initEnv+='cd ' + CMSSWDIR + ';'
initEnv+='source /afs/cern.ch/cms/cmsset_default.sh' + ';'
initEnv+='eval `scramv1 runtime -sh`' + ' '
initEnv+='cd -;' 
#initEnv+='cd ' + RUNDIR + ';'   

#If the script is run without argument, check what was the last run, and check on DBS what are the new runs (with at least 1K events) and run on them
#If on the contrary a runnumber is provided as argument, request the list of input files from DBS in order to run on them and produce calibration trees


if(runId==-1):
   print "Gathering jobs to launch... dataset mode = %s"%("Aag" if AAG else "Std")
   #### FETCH DBS TO FIND ALL RUNS TO PROCCESS

   #cleanup directory for all possible core.* files
   os.system('rm core.*' )

   #PRODUCE A LIST OF FILE WITH ALL NEW RUNS TO BE ANALYZED
   LASTRUN=int(commands.getstatusoutput("tail -n 1 LastRun%s.txt"%('_Aag' if AAG else ''))[1])
   print('Last analyzed Run: %i' % LASTRUN)

   runs = []
   print ("das_client.py  --limit=9999 --query='run dataset="+DATASET+"'")
   r = commands.getstatusoutput(initEnv+"das_client.py  --limit=9999 --query='dataset dataset="+DATASET+"'")[1].splitlines()
   datasets=[]
   for d in r:
      if len(d)<1 or d.startswith('/afs') or "Error" in d or "howing" in d:
         continue
      if not d.startswith('/StreamExpress/') or not d.endswith('ALCARECO'):
         continue
      else:
         datasets.append(d)
   print "Dataset found : %s"%datasets
   results = []
   for dataset in datasets:
      cmd="das_client.py  --limit=9999 --query='run dataset="+dataset+"'"
      print cmd
      cmdReturn=commands.getstatusoutput(initEnv+cmd)[1]
      for x in cmdReturn.splitlines():
         results.append([dataset,x])
   results.sort()
   for entry in results:
      line = entry[1]
      print "New line ! :%s"%line
      if(line.startswith('Showing') or line.startswith('/afs/')):continue
      if(len(line)<=0):continue
      run     = line.split('   ')[0]
      if not run.isdigit():
         print "Unable to get run runNumber: %s"%line
         continue
      else:
         run=int(run)
      if(run<=LASTRUN): continue

      #check that this run at least contains some events
      print("Checking number of events in run %i" % run)
      
      NEventsDasOut = commands.getstatusoutput(initEnv+"das_client.py  --limit=9999 --query='summary dataset="+entry[0]+" run="+str(run)+" | grep summary.nevents'")[1].splitlines()[-1]
      if(not NEventsDasOut.isdigit() ):
         print ("issue with getting number of events from das, skip this run")
         print NEventsDasOut
         continue
      NEvents = int(NEventsDasOut)
      if(NEvents<250):
         print 'run %i containing %i events is going to be skipped' % (run, NEvents)         
         continue
      print 'run %i containing %i events is going to be proccessed' % (run, NEvents)

      NFilesDasOut = commands.getstatusoutput(initEnv+"das_client.py  --limit=9999 --query='summary dataset="+entry[0]+" run="+str(run)+" | grep summary.nfiles'")[1].splitlines()[-1]
      if(NFilesDasOut.isdigit() ):
         NFiles = int(NFilesDasOut)
         FirstFile=0 
         while(FirstFile<NFiles):
             runs.append("%i %i %i"%(run, FirstFile, min(FirstFile+nFilesPerJob, NFiles)))
             FirstFile+=nFilesPerJob
      else:
         runs.append(str(run))

   #APPENDS TO THE LIST OF RUNS FOR WHICH THE PROCESSING FAILLED IN THE PAST
   FAILLEDRUN=commands.getstatusoutput("cat FailledRun%s.txt"%('_Aag' if AAG else ''))[1]
   
   os.system('echo ' + '"   "' + ' > FailledRun%s.txt'%('_Aag' if AAG else '')) #remove the file since these jobs will be resubmitted now
   for line in FAILLEDRUN.splitlines():
      try:
         if(int(line.split(' ')[0])!=-1):
            run = line
            runs.append(str(run))
            print "Job running on run " + str(run) + " failed in the past... Resubmitting"
      except:
         continue   
   ####
   #SUBMIT JOB FOR EACH RUN IN THE LIST (see the second part of the script)
   runs.sort()
   runs = list(set(runs)) #remove duplicates
   runs.sort()
   for run in runs:
      print 'Submitting Run ' + str(run) + "mode = %s"%("Aag" if AAG else "Std")
      run = run.split(" ")
      runId_     = run[0]
      firstFile_ = run[1] if len(run)>1 else '-1'
      lastFile_  = run[2] if len(run)>2 else '-1'
      cmd = 'bsub -q 2nd -J calibTree_' + runId_ + '_' + firstFile_+ '_' + lastFile_ + '_%s'%("Aag" if AAG else 'Std')+' -R "type == SLC6_64 && pool > 30000" ' + ' "'+initEnv+'python '+RUNDIR+'/SubmitJobs.py -r %s -f %s -l %s -d %s "'%(runId_,firstFile_,lastFile_,"Aag" if AAG else 'Std')
      os.system(cmd)
      if(runId_>LASTRUN):
         os.system('echo ' + runId_ + ' > LastRun%s.txt'%("_Aag" if AAG else ''))
         LASTRUN = runId_
   ####

   #### If datamode was 'all', rerun on 'Aag'
   if opt.datasetType.lower()=="all":
      os.system("cd "+ RUNDIR + "; python SubmitJobs.py -d Aag")


elif(not checkCorrupted and runId>-1):
   #### RUN ON ONE PARTICULAR RUN (GIVEN IN ARGUMENT)
   PWDDIR  =os.getcwd() #Current Dir
   os.chdir(RUNDIR);
   run=runId 
   if firstFile<0:firstFile=0
   if lastFile<0 : lastFile=999999
   
   print "run        : %s"%run
   print "firstFile  : %s"%firstFile
   print "lastFile   : %s"%lastFile
   print "collection : %s"%collection
   print "Processing files %i to %i of run %i" % (firstFile,lastFile,run)

   globaltag = '80X_dataRun2_Express_v6' #used for GR15
   
   outfile = 'calibTree_%i_%i.root' % (run, firstFile)
   if(firstFile==0):outfile = 'calibTree_%i.root' % (run)
   dataset = []
   print "das_client.py  --limit=9999 --query='dataset dataset="+DATASET+" run="+str(run)+"'"
   results = commands.getstatusoutput(initEnv+"das_client.py  --limit=9999 --query='dataset dataset="+DATASET+" run="+str(run)+"'")
   for line in results[1].splitlines():
      if line=='' or line[0]!="/":
         continue
      else:
         dataset.append(line)
   if len(dataset)>2:
      print "Error, can't find dataset..."
      print dataset
   else:
      dataset=dataset[-1]
   #reinitialize the afs token, to make sure that the job isn't kill after a few hours of running
   os.system('/usr/sue/bin/kinit -R')

   #GET THE LIST OF FILE FROM THE DATABASE
   files = ''

   results = commands.getstatusoutput(initEnv+"das_client.py  --limit=9999 --query='file dataset="+dataset+" run="+str(run)+"'")
   if(int(results[0])!=0 or results[1].find('Error:')>=0):
      print results
      os.system('echo ' + str(run) + ' >> FailledRun%s.txt'%('_Aag' if AAG else ''))
      sys.exit(1)
   filesList = results[1].splitlines();
   fileIndex=0
   for f in filesList: 
      if(not f.startswith('/store')):continue
      if((fileIndex>=firstFile and fileIndex<lastFile)):
         files+="'"+f+"',"
      fileIndex+=1
   if(files==''):
      print('no files to process for run '+ str(run))
      sys.exit(0)
   ###
#   print files

   #BUILD CMSSW CONFIG, START CMSRUN, COPY THE OUTPUT AND CLEAN THE PROJECT
   cmd='cmsRun produceCalibrationTree_template_cfg.py'
   cmd+=' outputFile="'+OUTDIR+'/'+outfile+'"'
   cmd+=' conditionGT="'+globaltag+'"'
   cmd+=' inputCollection="'+collection+'"'
   if files[-1]==",":files=files[:-1]
   cmd+=' inputFiles="'+files.replace("'","")+'"'
   print cmd
   
#   os.system('sed -e "s@OUTFILE@'+PWDDIR+'/'+outfile+'@g" -e "s@GLOBALTAG@'+globaltag+'@g" -e "s@FILES@'+files+'@g" '+RUNDIR+'/produceCalibrationTree_template_cfg.py > ConfigFile_'+str(run)+'_'+str(firstFile)+'_cfg.py')
#   print 'cmsRun ConfigFile_'+str(run)+'_'+str(firstFile)+'_cfg.py'
   exit_code = os.system(initEnv+cmd)
   if(int(exit_code)!=0):
      print("Job Failed with ExitCode "+str(exit_code))
      os.system('echo %i %i %i >> FailledRun%s.txt' % (run, firstFile, lastFile,'_Aag' if AAG else ''))
   else:
      print initEnv+'eos rm ' + CASTORDIR+'/'+outfile
#      os.system(initEnv+'eos rm ' + CASTORDIR+'/'+outfile) #make sure that the file is overwritten
      FileSizeInKBytes =commands.getstatusoutput('ls  -lth --block-size=1024 '+OUTDIR+'/'+outfile)[1].split()[4]
      if(int(FileSizeInKBytes)>50): 
         print("Preparing for stageout of " + PWDDIR+'/'+outfile + ' on ' + CASTORDIR+'/'+outfile + '.  The file size is %d KB' % int(FileSizeInKBytes))
         os.system('cmsStageOut -f '+OUTDIR+'/'+outfile + ' ' + CASTORDIR+'/'+outfile)
         os.system(initEnv+'eos ls ' + CASTORDIR+'/'+outfile)
      else:
         print('File size is %d KB, this is under the threshold --> the file will not be transfered on EOS' % int(FileSizeInKBytes))
   os.system('ls -lth '+OUTDIR+'/'+outfile)
   os.system('rm -f '+OUTDIR+'/'+outfile)
   os.system('rm -f ConfigFile_'+str(run)+'_'+str(firstFile)+'_cfg.py')
   os.system('cd ' + RUNDIR)
   os.system('rm -rf LSFJOB_${LSB_JOBID}')
   ###

elif(checkCorrupted):
   #### FIND ALL CORRUPTED FILES ON CASTOR AND MARK THEM AS FAILLED RUN

   calibTreeList = ""
   print("Get the list of calibTree from" + CASTORDIR + ")")
   calibTreeInfo = commands.getstatusoutput(initEnv+"eos ls " + CASTORDIR)[1].split('\n');
   NTotalEvents = 0;
   run = 0
   for info in calibTreeInfo:
      subParts = info.split();
      if(len(subParts)<4):continue
       
      run = int(subParts[4].replace("/calibTree_","").replace(".root","").replace(CASTORDIR,""))
      file = "root://eoscms//eos/cms"+subParts[4] 
      print("Checking " + file)
      results = commands.getstatusoutput(initEnv+'root -l -b -q ' + file)
      if(len(results[1].splitlines())>3):
         print(results[1]);
         print("add " + str(run) + " to the list of failled runs")
         os.system('echo ' + str(run) + ' >> FailledRun%s.txt'%('_Aag' if AAG else ''))
   
   #### If mode = All, relaunch with mode = Aag
   if opt.datasetType.lower()=="all":
      system("cd "+RUNDIR+"; python SubmitJobs.py -c -d Aag")

else:
   #### UNKNOWN CASE
   print "unknown argument: make sure you know what you are doing?"
