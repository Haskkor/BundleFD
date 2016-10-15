#!/bin/bash
#Arguments = -r replace ; -l list ; -h help

. ./script.ini

old_IFS=$IFS
IFS=$'\n'

# Usage function
usage()
{
cat << EOF
Usage: $0 [options]

"-l" or "--list"	"List files whose name contain an illegal character." 
			"Please provide a path."

"-r" or "--replace"	"Replace illegal characters in files name." 
			"Please provide a path."

EOF
exit 1
}

# List or Translate function
listAndTranslate()
{
	for elem in $(find "$1" -print);
	do
        	wod=$(dirname "$elem");
        	won=$(basename "$elem");
        	if [[ ! $(echo "$won" | grep "^[${wc}]*$") ]];
        	then
                	echo "$wod/$won";
                	if [[ "$2" = true ]];
			then
				mv "$wod/$won" "$wod/$(echo $won | tr -c "^[${wc}]*$" A)";
			fi;
        	fi;
	done;	
}

while getopts ":r:l:h" opt; 
do
	case $opt in
		r)
      			echo "-r was triggered, Parameter: $OPTARG. Replacing." >&2
			path="$OPTARG"
			translate="true"
			listAndTranslate "$path" "$translate"
      			;;
		l)
      			echo "-l was triggered, Parameter : $OPTARG. Listing." >&2
			path="$OPTARG"
			tranlate="false"
			listAndTranslate "$path" "$translate"
      			;;
		h)
      			echo "-h was triggered. Help." >&2
			usage
      			;;

    		\?)
      			echo "Invalid option: -$OPTARG" >&2
      			exit 1
      			;;
    		:)
      			echo "Option -$OPTARG requires an argument." >&2
      			exit 1
      			;;
  	esac
done

IFS=$old_IFS

exit 0
