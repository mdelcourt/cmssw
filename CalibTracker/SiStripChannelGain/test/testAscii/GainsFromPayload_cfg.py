import FWCore.ParameterSet.Config as cms

process = cms.Process("TEST")

local = False

if local:

   process.PoolDBESSource = cms.ESSource("PoolDBESSource",
       DBParameters = cms.PSet(
           messageLevel = cms.untracked.int32(0),
           authenticationPath = cms.untracked.string('.')
       ),
       toGet = cms.VPSet(cms.PSet(
           record = cms.string('SiStripApvGainRcd'),
           tag = cms.string('SiStripApvGainRcd_v1')
       )),
       connect = cms.string('sqlite_file:Gains_Sqlite.db')
   )
   
   process.source = cms.Source("EmptyIOVSource",
       lastValue = cms.uint64(251532),
       timetype = cms.string('runnumber'),
       firstValue = cms.uint64(251522),
       interval = cms.uint64(10)
   )
   
   process.get = cms.EDAnalyzer("SiStripGainFromPayload",
       toGet = cms.VPSet(cms.PSet(
           record = cms.string('SiStripApvGainRcd'),
           data = cms.vstring('SiStripApvGain')
       )),
       verbose = cms.untracked.bool(True)
   )
else:
    process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
    from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
    process.GlobalTag = GlobalTag(process.GlobalTag, '80X_dataRun2_Express_v7', '') 


process.source = cms.Source("EmptyIOVSource",
    lastValue = cms.uint64(275590),
    timetype = cms.string('runnumber'),
    firstValue = cms.uint64(275585),
    interval = cms.uint64(10)
)
process.get = cms.EDAnalyzer("SiStripGainFromPayload",
    toGet = cms.VPSet(cms.PSet(
        record = cms.string('SiStripGain2Rcd'),
        data = cms.vstring('SiStripGain'),
    )),
    verbose = cms.untracked.bool(True)
)


process.p = cms.Path(process.get)
