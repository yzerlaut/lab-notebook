src=user@10.0.0.1:CURATED/Cibele/PV-cells_WT_Adult_V1
dest=~/CURATED/Cibele/PV-cells_WT_Adult_V1
rsync -avhP --include="*/" --include="*.nwb" --exclude="*" $src $dest