echo ""
echo arguments of script: $0 -- $@
echo ""

let i=0

for df in PV SST NDNF;
do 

    echo "$df"

    if true;
    then
        let i++
        echo $i
    fi

    #if [ (( $i%2 )) -eq 0 ]
    #then
        #echo $i
    #fi
done

space_free=$( df -h | awk '{ print $5 }' | sort -n | tail -n 1 | sed 's/%//' )
echo $space_free

# ----- TESTS ----- #
#Operator 	Description
#! EXPRESSION 	The EXPRESSION is false.
#-n STRING 	The length of STRING is greater than zero.
#-z STRING 	The lengh of STRING is zero (ie it is empty).
#STRING1 = STRING2 	STRING1 is equal to STRING2
#STRING1 != STRING2 	STRING1 is not equal to STRING2
#INTEGER1 -eq INTEGER2 	INTEGER1 is numerically equal to INTEGER2
#INTEGER1 -gt INTEGER2 	INTEGER1 is numerically greater than INTEGER2
#INTEGER1 -lt INTEGER2 	INTEGER1 is numerically less than INTEGER2
#-d FILE 	FILE exists and is a directory.
#-e FILE 	FILE exists.
#-r FILE 	FILE exists and the read permission is granted.
#-s FILE 	FILE exists and it's size is greater than zero (ie. it is not empty).
#-w FILE 	FILE exists and the write permission is granted.
#-x FILE 	FILE exists and the execute permission is granted.
