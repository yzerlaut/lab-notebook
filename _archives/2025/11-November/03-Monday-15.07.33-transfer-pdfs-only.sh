src=user@10.0.0.1:CURATED/Cibele/*
dest=~/CURATED/Cibele
rsync -avhP --include="*/" --include="*.pdf" --exclude="*" $src $dest
