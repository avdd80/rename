#!/bin/bash
# Arg1 = target path
echo "Set username and password"           # Delete this line
exit                                       # Delete this line
checkfolder=$(lftp -c "open -u <username>,<password> 192.168.1.8; ls $1")

echo $checkfolder
if [ "$checkfolder" != "" ];
then
echo "folder exist"
touch "path_exists"
else
echo "folder does not exist"
fi