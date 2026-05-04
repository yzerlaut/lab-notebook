#

transfer() {
    # $1 = src
    # $2 = dest
    echo "transfer from "$1
    echo "         to "$2
    # exemple:
    #  rsync admin@10.0.0.3:/volume1/Taddy/sdkjfhsd/TSeries... ~/UNPROCESSED/Alexandre
    rsync -avhP $1 $2
}

convert() {
    # $1 = folder to compress 
    cd ~/work/physion/src
    echo "converting  " $1
    python -m physion.utils.compression.twoP $1
    cd ~
}


# transfer path_on_nas ~/UNPROCESSED/Alexandre
convert ~/UNPROCESSED/Alexandre/TSeries...