# assumes that :
    # - your are in the "lab-notebook" folder with physion as a submodule
    # - you have a "Dataset_Organization_cibele.py" file (see lab-notebook history)
    # - you have a "Tuning-Dataset-cibele.py" script (see lab-notebook history)
    # - you have a "Contrats-Dataset-cibele.py" script (see lab-notebook history)
# 
root_folder=~/CURATED/Cibele
mkdir $root_folder/pdfs

# for datafolder in PV-cells_WT_Adult_V1 SST-cells_cond-GluN1-KO-Adult-V1-Taddy  SST-cells_WT_Young_V1 PV-cells_cond-GluN1-KO_Adult_V1  PV-cells_WT_Young_V1  
for datafolder in PV-cells_WT_Adult_V1 SST-cells_WT_Young_V1 PV-cells_cond-GluN1-KO_Adult_V1  PV-cells_WT_Young_V1  
do 
    # short string reformatting
    short=${datafolder//-cells_/-}
    short=${short//_/-}
    short=${short//-V1/}
    short=${short//-cond-GluN1-KO/-KO}

    cd physion/src
    ##############################################################
    ###    preprocessing --- generate NWB files ##################
    ##############################################################
    # (DONE)
    # python -m physion.assembling.nwb $root_folder/$datafolder/DataTable.xlsx

    ##############################################################
    ###    fill analysis columns in DataTable.xlsx  ##############
    ##############################################################
    python -m physion.assembling.dataset fill-Analysis $root_folder/$datafolder/DataTable.xlsx

    ##############################################################
    ###    generate summary pdf files for each session   #########
    ##############################################################

    mkdir $root_folder/$datafolder/pdfs # generate temporary pdf subfolder

    python -m physion.analysis.summary_pdf $root_folder/$datafolder/DataTable.xlsx --for_protocol 8orientation --sorted_by subject
    python -m physion.analysis.summary_pdf $root_folder/$datafolder/DataTable.xlsx --for_protocol 8contrast --sorted_by subject
    pdftk $root_folder/$datafolder/pdfs/8contrast/*.pdf cat output $root_folder/pdfs/$short-CONTRAST.pdf
    pdftk $root_folder/$datafolder/pdfs/8orientation/*.pdf cat output $root_folder/pdfs/$short-TUNING.pdf

    rm -r $root_folder/$datafolder/pdfs # delete temporary pdf subfolder

    cd ../..
    ##############################################################
    ###  generate summary analysis over the different datasets  ##
    ##############################################################

    python Tuning-Dataset-cibele.py
    # python Contrast_Dataset_cibele.py

done
