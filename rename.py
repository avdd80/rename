#!/usr/bin/env python
from os.path    import isfile, join
from os         import system, listdir, getcwd, rename
from re         import findall
from subprocess import Popen, PIPE
from shutil     import move


current_path = getcwd ()
onlyfiles = [ f for f in listdir(current_path) if isfile(join(current_path,f)) ]



def rename_file (video_file_name_extn, extn):

    # Extract the meta data into a temporary file "meta.txt"
    Popen ('ffmpeg -i \"' + video_file_name_extn + '\" -f ffmetadata ' + ' meta.txt' , shell=True, stdout=PIPE).stdout.read()

    # Extract the show name
    show_name = Popen ('grep show= meta.txt' , shell=True, stdout=PIPE).stdout.read()
    
    # Do not rename if it is not a show
    if (show_name == ''):
        system ('rm -rf meta.txt')
        return (video_file_name_extn)
    show_name = show_name.replace ('show=', '')
    show_name = show_name.rstrip()

    # Extract the season number
    season = Popen ('grep season_number meta.txt' , shell=True, stdout=PIPE).stdout.read()
    season = season.replace ('season_number=', '')
    season = season.rstrip()

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

    # Return the constructed file name
    return final_episode_name


for i in onlyfiles:
    length = len (i)

    
    # Check if the extension is .mp4
    if (i.find ('.mp4') == length - len('.mp4')):
        old_filename_mp4 = i
        print i
        new_filename_mp4 = rename_file (i, '.mp4')
        if (old_filename_mp4 != new_filename_mp4):
            #move (old_filename_mp4, new_filename_mp4)
            rename (old_filename_mp4, new_filename_mp4)

    # Check if the extension is .avi
    if (i.find ('.avi') == length - len('.avi')):
        old_filename_avi = i
        new_filename_avi = rename_file (i, '.avi')
        if (old_filename_avi != new_filename_avi):
            rename (old_filename_avi, new_filename_avi)

    # Check if the extension is .m4v
    if (i.find ('.m4v') == length - len('.m4v')):
        new_filename_mp4 = rename_file (i, 'mp4')
        rename (i, new_filename_mp4)