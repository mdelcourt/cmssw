process.load("CondCore.DBCommon.CondDBCommon_cfi")
process.CondDBCommon.connect = 'sqlite_file:MyPedestals.db'

process.PoolDBESSource = cms.ESSource("PoolDBESSource",
    process.CondDBCommon,
    DumpStat=cms.untracked.bool(True),
    toGet = cms.VPSet(cms.PSet(
        record = cms.string('MyPedestalsRcd'),
        tag = cms.string("myPedestal_test")
    )),
)



process.get = cms.EDAnalyzer("EventSetupRecordDataGetter",
    toGet = cms.VPSet(cms.PSet(
        record = cms.string('MyPedestalsRcd'),
        data = cms.vstring('MyPedestals')
    )
    ),
    verbose = cms.untracked.bool(True)
)
