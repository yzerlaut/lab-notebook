# for dataset in Asahi;
for dataset in PN;
do 

    ################## assemble dataset to NWB files #################
    if false;
    then
        cd physion/src
        # build NWB files
        python -m physion.assembling.nwb ~/DATA/Adrianna/$dataset/DataTable.xlsx
        # fill the analysis column
        python -m physion.assembling.dataset fill-analysis ~/DATA/Adrianna/$dataset/DataTable.xlsx
        cd ../..
    fi

    ################## build pdf of dataset ##########################
    if true;
    then

        # compute dFoF with following settings:
        echo """{
            \"roi_to_neuropil_fluo_inclusion_factor\":1.0,
            \"neuropil_correction_factor\":0.8,
            \"method_for_F0\":\"sliding_percentile\",
            \"percentile\":10.0,
            \"sliding_window\":300.0
        }
        """ > dFoF-settings.json

        cd physion/src
        python -m physion.analysis.summary_pdf ~/DATA/Adrianna/$dataset/DataTable.xlsx -dFoF ../../dFoF-settings.json
        cd ../..

        # we don't need the dFoF-settings anymore, so delete
        rm dFoF-settings.json

        # then merge all individual datasets into a single Raw-Summary.pdf
        pdftk ~/DATA/Adrianna/$dataset/pdfs/*.pdf cat output ~/DATA/Adrianna/$dataset/Raw-Summary.pdf 
        rm -r ~/DATA/Adrianna/$dataset/pdfs/*.pdf
    fi

done

