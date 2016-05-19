#!/usr/bin/env python
from os.path    import isfile, join
from os         import system, path, listdir, remove, getcwd, rename
from re         import findall
from time       import sleep
from subprocess import Popen, PIPE


current_path = getcwd ()
onlyfiles = [ f for f in listdir(current_path) if isfile(join(current_path,f)) ]

global show_name_path

def rename_file (video_file_name_extn, extn):
    
    global show_name_path
    show_name_path = '/Series/'

    # Extract the meta data into a temporary file "meta.txt"
    Popen ('ffmpeg -i \"' + video_file_name_extn + '\" -f ffmetadata ' + ' meta.txt' , shell=True, stdout=PIPE).stdout.read()

    # Extract the show name
    show_name = Popen ('grep show= meta.txt' , shell=True, stdout=PIPE).stdout.read()
    
    # Do not rename if it is not a show
    if (show_name == ''):
        system ('rm -rf meta.txt')
        return (video_file_name_extn)
    show_name = show_name.replace ('show=', '')

    # Remove trailing year in the show name - if any. e.g. The Americans (2013)
    show_name = show_name.replace ('(2013)', '')
    show_name = show_name.replace ('(2014)', '')
    show_name = show_name.replace ('(2015)', '')
    show_name = show_name.replace ('(2016)', '')

    show_name = show_name.rstrip()

    # Construct the expected path to the show to upload the file to
    show_name_path = show_name_path + show_name + '/'

    # Extract the season number
    season = Popen ('grep season_number meta.txt' , shell=True, stdout=PIPE).stdout.read()
    season = season.replace ('season_number=', '')
    season = season.rstrip()

    if (show_name == 'The Simpsons'):
        show_name_path = show_name_path + season + '/'
    else:
        show_name_path = show_name_path + 'Season ' + season + '/'

    # Extract the episode number
    episode_sort = Popen ('grep episode_sort meta.txt' , shell=True, stdout=PIPE).stdout.read()
    episode_sort = episode_sort.replace ('episode_sort=', '')
    episode_sort = episode_sort.rstrip()

    # Extract the episode title
    episode_name = Popen ('grep title= meta.txt' , shell=True, stdout=PIPE).stdout.read()
    episode_name = episode_name.replace ('title=', '')
    episode_name = episode_name.rstrip()
    
    # Delete temporary "meta.txt" file.
    system ('rm -rf meta.txt')

    # Construct the complete file name
    final_episode_name = ''
    if (int(season)<10):
        final_episode_name = final_episode_name + show_name + ' S0' + season
    else:
        final_episode_name = final_episode_name + show_name + ' S'  + season


    if (int(episode_sort) < 10):
        final_episode_name = final_episode_name + 'E0' + episode_sort
    else:
        final_episode_name = final_episode_name + 'E' + episode_sort

    final_episode_name = final_episode_name + ' ' + episode_name + extn

    print final_episode_name

    # Return the constructed file name
    return final_episode_name

# Function to check if the remote path exists
def does_ftp_path_exist (target_dir):

    ret_val = 0

    print 'Uploading via FTP'

    # Remove path_exists file
    if (path.isfile ('path_exists')):
        remove ('path_exists')
    
    # Run the script to check if path exists
    Popen ('./chk.sh ' + target_dir, shell=True, stdout=PIPE).stdout.read()

    # If the path exists, a file named "path_exists" is created in the current directory
    if (path.isfile ('path_exists')):
        remove ('path_exists')
        ret_val = 1
    else:
        print 'Path does not exist - check'

    return ret_val


def link_file_to_itunes (file_name, file_path):
    absolute_path = '/Volumes/avdeshpa'
    absolute_path = absolute_path + file_path + file_name
    print absolute_path
    ret_val = Popen ('open -a iTunes -g "' + absolute_path + '"', shell=True, stdout=PIPE).stdout.read()
    sleep (1)
    Popen ('osascript -e \'tell application "iTunes" to stop\'', shell=True, stdout=PIPE).stdout.read()
    print ret_val


# If the file name has an apostrophe ('), LFTP upload fails. Try
# copying the file via MAC file system.
def copy_file_mac_copy (file_name, target_dir):
    
    transfer_status = 0
    
    print 'Uploading via MAC Copy'
    
    absolute_path = '"/Volumes/avdeshpa' + target_dir + file_name + '"'

    Popen ('cp -f "' + file_name + '" ' + absolute_path, shell=True, stdout=PIPE).stdout.read()

    local_file_size   = path.getsize (file_name)
    remote_file_size  = path.getsize (absolute_path[1:len(absolute_path)-1])


    if (isfile (absolute_path[1:len(absolute_path)-1])):

        if (local_file_size == remote_file_size):
            remove (file_name)
            transfer_status = 1
    else:
        print 'Target path does not exist: ' + absolute_path
    return transfer_status


# Upload file via LFTP
def upload_file_FTP (file_name, target_dir):

    
    transfer_status = 1


    # Check if the path exists
    if (does_ftp_path_exist('"' + target_dir + '"')):
        print 'Upload: Target dir = ' + target_dir + ' Filename = ' + file_name
        return_result = Popen ('lftp -e "set net:timeout 10;put \'' + file_name + '\' -o \'' + target_dir + '\'; bye" -u avdeshpa,sharedpass 192.168.1.8', shell=True, stdout=PIPE).stdout.read()
        
        # Check if file transfer was successful
        if (len (return_result) > 0):
            remote_file_size = int(return_result.split()[0])
            local_file_size  = path.getsize (file_name)
            if (remote_file_size == local_file_size):
                remove (file_name)
            else:
                print 'File transfer failed. Result = ' + return_result
                transfer_status = 0
        else:
            print 'File transfer failed. Result = ' + return_result
            transfer_status = 0

    else:
        print 'Path does not exist ' + target_dir
        transfer_status = 0

    return transfer_status

# This function decides whether to use FTP or MAC copy to upload the file
# It also links the media file to iTunes
def upload_file (file_name, target_dir):

    
    # If the filename has an apostrophe, use MAC copy
    #    if (file_name.find ('\'') > 0):
    #       transfer_status = copy_file_mac_copy (file_name, target_dir)
    # else use FTP to upload the file
    #else:
    #    transfer_status = upload_file_FTP (file_name, target_dir)

    transfer_status = copy_file_mac_copy (file_name, target_dir)

    if (transfer_status == 1):
        
        print 'File transfer successful'
        
        # Link the file to iTunes
        link_file_to_itunes (file_name, target_dir)
    else:
        print 'File transfer failed!'
        # List the files to be manually linked to iTunes
        Popen ('echo ' + file_name + ' >> link_to_itunes.txt', shell=True, stdout=PIPE).stdout.read()


for i in onlyfiles:
    length = len (i)
    
    global show_name_path
    
    lower_case_path = i.lower()

    
    # Check if the extension is .mp4
    if (lower_case_path.find ('.mp4') == length - len('.mp4')):
        old_filename_mp4 = i
        print i
        new_filename_mp4 = rename_file (i, '.mp4')
        if (old_filename_mp4 != new_filename_mp4):
            rename (old_filename_mp4, new_filename_mp4)
        upload_file (new_filename_mp4, show_name_path)

    # Check if the extension is .avi
    if (lower_case_path.find ('.avi') == length - len('.avi')):
        old_filename_avi = i
        new_filename_avi = rename_file (i, '.avi')
        if (old_filename_avi != new_filename_avi):
            rename (old_filename_avi, new_filename_avi)

    # Check if the extension is .m4v
    if (lower_case_path.find ('.m4v') == length - len('.m4v')):
        new_filename_mp4 = rename_file (i, '.mp4')
        old_filename_m4v = i
        rename (old_filename_m4v, new_filename_mp4)
        upload_file (new_filename_mp4, show_name_path)
