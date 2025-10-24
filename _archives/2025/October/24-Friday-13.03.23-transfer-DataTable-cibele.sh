# need to set passwd in the shell before
for datafolder in PV-cells_WT_Adult_V1 SST-cells_cond-GluN1-KO-Adult-V1-Taddy  SST-cells_WT_Young_V1 PV-cells_cond-GluN1-KO_Adult_V1  PV-cells_WT_Young_V1  
do 
    sshpass -p $passwd scp a.yann.zerlaut@10.0.0.4:D:/2Photon-DATA-CibelePhD/CURATED/Cibele/$datafolder/DataTable.xlsx ~/CURATED/Cibele/$datafolder/DataTable.xlsx
done