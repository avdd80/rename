#!/usr/bin/env python
from os.path    import isfile, join
from os         import system, path, listdir, remove, getcwd, rename
from re         import findall
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

    # Remove path_exists file
    if (path.isfile ('path_exists')):
        remove ('path_exists')
    
    # Run the script to check if path exists
    Popen ('./chk.sh ' + target_dir, shell=True, stdout=PIPE).stdout.read()

    # If the path exists, a file named "path_exists" is created in the current directory
    if (path.isfile ('path_exists')):
        remove ('path_exists')
        ret_val = 1
        print 'Path exists - check'
    else:
        print 'Path does not exist - check'

    return ret_val

# Upload file via LFTP
def upload_file (file_name, target_dir):

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
                print 'File transfer successful'
            else:
                print 'File transfer failed. Result = ' + return_result
        else:
            print 'File transfer failed. Result = ' + return_result
        
        # List the files to be linked to iTunes
        Popen ('echo ' + file_name + ' >> link_to_itunes.txt', shell=True, stdout=PIPE).stdout.read()
    else:
        print 'Path does not exist ' + target_dir


for i in onlyfiles:
    length = len (i)
    
    global show_name_path

    
    # Check if the extension is .mp4
    if (i.find ('.mp4') == length - len('.mp4')):
        old_filename_mp4 = i
        print i
        new_filename_mp4 = rename_file (i, '.mp4')
        if (old_filename_mp4 != new_filename_mp4):
            rename (old_filename_mp4, new_filename_mp4)
            upload_file (new_filename_mp4, show_name_path)

    # Check if the extension is .avi
    if (i.find ('.avi') == length - len('.avi')):
        old_filename_avi = i
        new_filename_avi = rename_file (i, '.avi')
        if (old_filename_avi != new_filename_avi):
            rename (old_filename_avi, new_filename_avi)

    # Check if the extension is .m4v
    if (i.find ('.m4v') == length - len('.m4v')):
        new_filename_mp4 = rename_file (i, '.mp4')
        old_filename_m4v = i
        rename (old_filename_m4v, new_filename_mp4)
        upload_file (new_filename_mp4, show_name_path)