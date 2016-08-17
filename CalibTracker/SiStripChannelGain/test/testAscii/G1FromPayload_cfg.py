import FWCore.ParameterSet.Config as cms

process = cms.Process("TEST")
process.PoolDBESSource = cms.ESSource("PoolDBESSource",
    DBParameters = cms.PSet(
        messageLevel = cms.untracked.int32(0),
        authenticationPath = cms.untracked.string('.')
    ),
    toGet = cms.VPSet(cms.PSet(
        record = cms.string('SiStripApvGainRcd'),
        tag = cms.string('SiStripApvGainRcd_v1_hltvalidation')
    )),
    connect = cms.string('sqlite_file:dbfile.db')
)

process.source = cms.Source("EmptyIOVSource",
    lastValue = cms.uint64(251532),
    timetype = cms.string('runnumber'),
    firstValue = cms.uint64(251522),
    interval = cms.uint64(10)
)

process.get = cms.EDAnalyzer("SiStripGainFromPayload",
    toGet = cms.VPSet(cms.PSet(
        record = cms.string('SiStripBadChannel_v1_hltvalidation'),
        data = cms.vstring('SiStripGain')
    )),
    verbose = cms.untracked.bool(True)
)

process.p = cms.Path(process.get)
