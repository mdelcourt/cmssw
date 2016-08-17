#include "TROOT.h"
#include "TTree.h"
#include "TFile.h"
#include <iostream>



using namespace std;


string saveFile="gainTrend.root";

void computeSummary(string fileName_="",string payloadName_="",string saveFolder=""){
   if (fileName_==""){cout<<"No file specified."<<endl; return;}
   saveFile=saveFolder+"/"+saveFile;
   TFile * f = new TFile(saveFile.c_str(),"UPDATE");
   TTree * t = (TTree*)f->Get("payloadSummary"); 
   if (!t)return;
   float  MPV[5];
   float  Gain[5];
   float  Error[5];
   float  CleanMPV[5];
   float  Clean[5];

   gROOT->ProcessLine("#include <iostream>");
   string *payloadName = new string;
   payloadName->assign(payloadName_); 
   t->SetBranchAddress("MPV_av"        ,&MPV[0]           );
   t->SetBranchAddress("Gain_av"       ,&Gain[0]          );
   t->SetBranchAddress("MPV_TIB"    ,&MPV[1]           );
   t->SetBranchAddress("MPV_TID"    ,&MPV[2]           );
   t->SetBranchAddress("MPV_TOB"    ,&MPV[3]           );
   t->SetBranchAddress("MPV_TEC"    ,&MPV[4]           );
   t->SetBranchAddress("Gain_TIB"   ,&Gain[1]          );
   t->SetBranchAddress("Gain_TID"   ,&Gain[2]          );
   t->SetBranchAddress("Gain_TOB"   ,&Gain[3]          );
   t->SetBranchAddress("Gain_TEC"   ,&Gain[4]          );

   t->SetBranchAddress("Error_av"       ,&Error[0]          );
   t->SetBranchAddress("Error_TIB"   ,&Error[1]          );
   t->SetBranchAddress("Error_TID"   ,&Error[2]          );
   t->SetBranchAddress("Error_TOB"   ,&Error[3]          );
   t->SetBranchAddress("Error_TEC"   ,&Error[4]          );
   
   t->SetBranchAddress("Clean_av"       ,&Clean[0]          );
   t->SetBranchAddress("Clean_TIB"   ,&Clean[1]          );
   t->SetBranchAddress("Clean_TID"   ,&Clean[2]          );
   t->SetBranchAddress("Clean_TOB"   ,&Clean[3]          );
   t->SetBranchAddress("Clean_TEC"   ,&Clean[4]          );

   t->SetBranchAddress("CleanMPV_av"       ,&CleanMPV[0]          );
   t->SetBranchAddress("CleanMPV_TIB"   ,&CleanMPV[1]          );
   t->SetBranchAddress("CleanMPV_TID"   ,&CleanMPV[2]          );
   t->SetBranchAddress("CleanMPV_TOB"   ,&CleanMPV[3]          );
   t->SetBranchAddress("CleanMPV_TEC"   ,&CleanMPV[4]          );

   t->SetBranchAddress("PayloadName",&payloadName      );
   
   float NAPV[5];
   for(int i=0; i<5; i++){MPV[i]=0; Gain[i]=0; NAPV[i]=0; Clean[i]=0; Error[i]=0; CleanMPV[i]=0;}
   
   TFile * f2 = new TFile(fileName_.c_str());
   TTree * t2 = (TTree*) f2->Get("SiStripCalib/APVGain");
   float MPV_origin; double Gain_origin; UChar_t subDet; bool isMasked; float Error_origin;
   t2->SetBranchAddress("FitMPV"  ,&MPV_origin );
   t2->SetBranchAddress("Gain"    ,&Gain_origin);
   t2->SetBranchAddress("SubDet"  ,&subDet     );
   t2->SetBranchAddress("isMasked",&isMasked   );
   t2->SetBranchAddress("FitMPVErr",&Error_origin   );

   //Looping over tree...
   printf("Progressing Bar              :0%%       20%%       40%%       60%%       80%%       100%%\n");
   printf("Looping on the Tree          :");
   int TreeStep = t2->GetEntries()/50;if(TreeStep==0)TreeStep=1;
   for (unsigned int ientry = 0; ientry < t2->GetEntries(); ientry++) {
      if(ientry%TreeStep==0){printf(".");fflush(stdout);}
      t2->GetEntry(ientry);

      if(subDet>2 && Gain_origin > 0 && MPV_origin > 0 && ! isMasked){
         NAPV[subDet-2]++;
         NAPV[0]++;
         
         Error[0]+=Error_origin*1./MPV_origin;
         Gain[0]+=Gain_origin;
         MPV[0]+=MPV_origin;


         Error[subDet-2]+=Error_origin*1./MPV_origin;
         Gain[subDet-2]+=Gain_origin;
         MPV [subDet-2]+=MPV_origin;
         if ((Error_origin*1./MPV_origin)<0.005){
            Clean[0]++;
            CleanMPV[0]+=MPV_origin;
            Clean[subDet-2]++;
            CleanMPV[subDet-2]+=MPV_origin;
         }
      }

   }
   cout<<endl;
   f2->Close();
   
   for (int i=0; i<5; i++){
      if (NAPV[i]==0){
         MPV[i]=0;Gain[i]=0;Error[i]=0;
         }
      else{
         MPV[i]/=NAPV[i];
         Gain[i]/=NAPV[i];
         Error[i]/=NAPV[i];
      }
      if (Clean[i]==0){
         CleanMPV[i]=0;
      }
      else{
         CleanMPV[i]/=Clean[i];
      }
      }

   f->cd();
   
   t->Fill();
   t->Write();
   f->Save();
   delete payloadName;
   f->Close();
}


