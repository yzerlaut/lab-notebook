cd ~/lab-notebook/physion/src
#python -m physion.assembling.dataset fill-analysis ~/UNPROCESSED/SST-WT-GluN1KO-GluN3KO-2023/DataTable.xlsx
# copy for Cibele
#python -m physion.assembling.nwb ~/UNPROCESSED/SST-WT-GluN1KO-GluN3KO-2023/SST-OrientTuning-WT-Taddy.xlsx -df ~/CURATED/Cibele/SST-cells_WT_Adult_V1_Taddy/NWBs
cp ~/UNPROCESSED/SST-WT-GluN1KO-GluN3KO-2023/SST-OrientTuning-WT-Taddy.xlsx ~/CURATED/Cibele/SST-cells_WT_Adult_V1_Taddy/DataTable.xlsx
#python -m physion.assembling.nwb ~/UNPROCESSED/SST-WT-GluN1KO-GluN3KO-2023/SST-OrientTuning-GluN1KO-Taddy.xlsx -df ~/CURATED/Cibele/SST-cells_cond-GluN1-KO_Adult_V1_Taddy/NWBs
cp ~/UNPROCESSED/SST-WT-GluN1KO-GluN3KO-2023/SST-OrientTuning-GluN1KO-Taddy.xlsx ~/CURATED/Cibele/SST-cells_cond-GluN1-KO_Adult_V1_Taddy/DataTable.xlsx
cd ~/UNPROCESSED/SST-WT-GluN1KO-GluN3KO-2023

