# The following comments couldn't be translated into the new config version:

# upload to database 

#string timetype = "timestamp"    

import FWCore.ParameterSet.Config as cms

process = cms.Process("Reader")

process.MessageLogger = cms.Service("MessageLogger", 
    debugModules = cms.untracked.vstring(''), 
    destinations = cms.untracked.vstring('SiStripApvGainReader.log') 
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1)
)
process.source = cms.Source("EmptyIOVSource",
    lastValue = cms.uint64(251532),
    timetype = cms.string('runnumber'),
    firstValue = cms.uint64(251522),
    interval = cms.uint64(1)
)
process.PoolDBESSource = cms.ESSource("PoolDBESSource",
    DBParameters = cms.PSet(
        messageLevel = cms.untracked.int32(0),
        authenticationPath = cms.untracked.string('.')
    ),
    toGet = cms.VPSet(cms.PSet(
        record = cms.string('SiStripApvGainRcd'),
        tag = cms.string('SiStripGainFromParticles')
    )),
    connect = cms.string('sqlite_file:Gains_Sqlite.db')
)


process.reader = cms.EDAnalyzer("SiStripApvGainReader",
                              printDebug = cms.untracked.bool(True)
                              )


process.p1 = cms.Path(process.reader)
