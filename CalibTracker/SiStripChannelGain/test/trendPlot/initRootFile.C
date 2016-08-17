#include "TROOT.h"
#include "TTree.h"


#include <iostream>

using namespace std;

string treeName="payloadSummary";

void initRootFile(string fName="gainTrend.root"){

   TFile * f = new TFile(fName.c_str(),"RECREATE");
   TTree * t = new TTree(treeName.c_str(),"Tree description");

   float MPV;
   int payloadName;
   t->Branch("MPV_av",&MPV); 
   t->Branch("Gain_av",&MPV); 
   t->Branch("Gain_TIB",&MPV); 
   t->Branch("Gain_TID",&MPV); 
   t->Branch("Gain_TOB",&MPV); 
   t->Branch("Gain_TEC",&MPV); 
   t->Branch("MPV_TIB",&MPV); 
   t->Branch("MPV_TID",&MPV); 
   t->Branch("MPV_TOB",&MPV); 
   t->Branch("MPV_TEC",&MPV); 
   t->Branch("firstRun",&payloadName);
   t->Branch("lastRun",&payloadName);
   t->Branch("Error_av",&MPV);    
   t->Branch("Error_TIB",&MPV);    
   t->Branch("Error_TID",&MPV);    
   t->Branch("Error_TOB",&MPV);    
   t->Branch("Error_TEC",&MPV);    
   t->Branch("Clean_av",&MPV);    
   t->Branch("Clean_TIB",&MPV);       
   t->Branch("Clean_TID",&MPV);       
   t->Branch("Clean_TOB",&MPV);       
   t->Branch("Clean_TEC",&MPV);       
   t->Branch("CleanMPV_av",&MPV);       
   t->Branch("CleanMPV_TIB",&MPV);    
   t->Branch("CleanMPV_TID",&MPV);    
   t->Branch("CleanMPV_TOB",&MPV);    
   t->Branch("CleanMPV_TEC",&MPV);       

   

   string testString="blug";
   t->Branch("PayloadName",&testString);
   MPV=0.0;
   for (int i=0; i<10; i++){
      MPV=i;
   //   t->Fill();
   }
   f->Write();
}
