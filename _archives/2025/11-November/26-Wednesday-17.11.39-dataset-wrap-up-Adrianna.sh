# for dataset in Asahi;
for dataset in PN_cond-NDNF-CB1_WT-vs-KD;
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
            \"method_for_F0\":\"sliding_percentile\",
            \"percentile\":10.0,
            \"sliding_window\":300.0,
            \"with_computed_neuropil_fact\":true
        }
        """ > dFoF-settings.json

        # for protocol in vision-survey Asahi surround-mod
        for protocol in Asahi;
        do
            cd physion/src
            python -m physion.analysis.summary_pdf ~/DATA/Adrianna/$dataset/DataTable.xlsx -dFoF ../../dFoF-settings.json --for_protocol $protocol
            cd ../..

            # then merge all individual datasets into a single Raw-Summary.pdf
            pdftk ~/DATA/Adrianna/$dataset/pdfs/$protocol/*.pdf cat output ~/DATA/Adrianna/$dataset/$protocol-Raw-Summary.pdf 
            rm -r ~/DATA/Adrianna/$dataset/pdfs/$protocol
        done

        # we don't need the dFoF-settings anymore, so delete:
        rm dFoF-settings.json

    fi

done

