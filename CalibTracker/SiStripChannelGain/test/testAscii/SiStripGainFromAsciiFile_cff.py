import FWCore.ParameterSet.Config as cms


SiStripCalib = cms.EDAnalyzer("SiStripGainFromAsciiFile",
   InputFileName = cms.untracked.vstring(""),
   referenceValue = cms.untracked.double(0)
)

SiStripCalibValidation = SiStripCalib.clone()
SiStripCalibValidation.InputFileName       = cms.string('Validation_ASCII.txt')
SiStripCalibValidation.referenceValue      = cms.double(1.)

