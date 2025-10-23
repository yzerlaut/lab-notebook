# in windows to copy without wmv files: scp -r [!.wmv]* Cibele\SST* user@10.0.0.1:CURATED
# --------------------
# ALL FOLDERS
# --------------------
#PV-cells-GCamp8M-test_WT_Adult_V1
#PV-cells_cond-GluN1-KO_Adult_V1
#PV-cells_cond-GluN1-KO_Young_V1
#PV-cells_WT_Adult_V1
#PV-cells_WT_Young_V1
#PYR-PV-SynGCaMP_Young_V1
#SST-cells_cond-GluN1-KO-Adult-V1-Taddy
#SST-cells_cond-GluN1-KO-Young-V1
#SST-cells_WT_Adult_V1
#SST-cells_WT_Young_V1
cd physion/src
python -m physion.assembling.nwb ../../../PV-cells_cond-GluN1-KO_Adult_V1/DataTable.xlsx
python -m physion.assembling.nwb ../../../SST-cells_WT_Adult_V1/DataTable.xlsx
python -m physion.assembling.nwb ../../../SST-cells_cond-GluN1-KO-Adult-V1-Taddy/DataTable.xlsx
python -m physion.assembling.nwb ../../../SST-cells_cond-GluN1-KO-Young-V1/DataTable.xlsx
python -m physion.assembling.nwb ../../../SST-cells_WT_Young_V1/DataTable.xlsx
python -m physion.assembling.nwb ../../../PV-cells_WT_Adult_V1/DataTable.xlsx
cd ../..
