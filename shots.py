#!/usr/bin/env python3
# SHOT - the Simple Hospital Outbreak Tracker, by Sigbjørn Smelror (c) 2020
# SHOT provides a graphic depiction of the number of outbreak cases by date of illness onset
# Copyright (C) 2020 Sigbjørn "sigg3" Smelror <git@sigg3.net>.
#
# SHOT is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# SHOT is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# URL: <https://www.gnu.org/licenses/old-licenses/gpl-3.0.txt>
#
# Submit issues and get updates at: <https://github.com/sigg3/shot>


import PySimpleGUI as sg
import pandas as pd
import time, csv, datetime
import configparser
from pathlib import Path


# TODO not sure we need time, when 'datetime' fits our needs

# Setup PySimpleGUI
set_theme = 'SystemDefaultForReal'
sg.ChangeLookAndFeel(set_theme) # are these both current?
sg.theme(set_theme)

#fontSize = 16

# sha512 for hashing passwords (not stored)
#from hashlib import sha512

# deprecated
#import rockikz_crypt

# Dictionary
# FNR == Norwegian SSN
# Ref: https://www.skatteetaten.no/person/folkeregister/fodsel-og-navnevalg/barn-fodt-i-norge/fodselsnummer/


# TODO (low priority)
# Check if there are cli arguments
# Argument 1 is file name. If it exists, load it (open); if not, create it (new).

# Set sane defaults
shot = {}
outbreak_filename = None
shot_config_file = Path.cwd()/Path('settings.ini')
default_language_setting = 'English'

# TODO ConfigParser to set is_configured to True
# Required config options are: user, language and unique-method (FNR, free-text string)
# SHOT is built for Norwegian hospitals and relies on FNR up until version 1 at least.
    
# digctionary
# string(hospital) use function for strings?

# Tabbed design (check audio rec)

# Write Configuration file (settings.ini)
def write_config_to(config_file):
    """
    Creates a settings.ini file using configparser
    Only used to set some permanent preferences for ease of use
    And avoid having to re-do hospital information for each CSV file ..
    """
    
    config = configparser.ConfigParser()
    
    # Set the defaults
    config['OPTIONS'] = {
                        'user': shot['conf_user'],
                        'language': shot['conf_lang'],
                        'unique': shot['conf_uniq'],
                        'hospital': shot['conf_hosp'] # This is hospital set
                        }
    
    # See if we have any recent files stored on dict
    # TODO write RECENT sect
    
    
    
    # See if we have set any hospital(s) (Settings->Hospital)
    # These are ALL hospitals that we know of (in file and from earlier config reads)
    
        
    
    
    # Finally, write to file
    with open(str(config_file), 'w') as configfile:
        config.write(configfile)
    
    

    # >>> import configparser
# >>> config = configparser.ConfigParser()
# >>> config['DEFAULT'] = {'ServerAliveInterval': '45',
# ...                      'Compression': 'yes',
# ...                      'CompressionLevel': '9'}
# >>> config['bitbucket.org'] = {}
# >>> config['bitbucket.org']['User'] = 'hg'
# >>> config['topsecret.server.com'] = {}
# >>> topsecret = config['topsecret.server.com']
# >>> topsecret['Port'] = '50022'     # mutates the parser
# >>> topsecret['ForwardX11'] = 'no'  # same here
# >>> config['DEFAULT']['ForwardX11'] = 'yes'
# >>> with open('example.ini', 'w') as configfile:
# ...   config.write(configfile)
    
    


# Read Configuration file (settings.ini)
def read_config_from(config_file):
    """
    Sets shot dict vars based on a .ini settings file in cwd
    Returns bool (True iff configured and False if unconfigured)
    """
    
    config = configparser.ConfigParser()
    config.read(str(config_file))
    
    if 'OPTIONS' in config:
        
        # User is required for setting
        my_user = config.get('OPTIONS', 'user', fallback=None) # NOICE
        if my_user is None: return False
        
        # Language is required for setting
        my_lang = config.get('OPTIONS', 'language', fallback='English')
        if my_lang is None: return False
        
        # Optional values
        my_hospital = config.get('OPTIONS', 'hospital', fallback=None)
        my_unique = config.get('OPTIONS', 'unique', fallback='FNR')
    else:
        return False
    
    
    my_recent_files = []
    if 'RECENT' in config:
        for x in range(1,6):
            if x in config['RECENT']:
                my_recent_files.append(config['RECENT'][x])
    
    
    for sect in config.sections():
        if sect in ('OPTIONS', 'RECENT'): continue
        print(sect)
    
    
    # Load hospital(s) from settings.ini
    # The shot['conf_hosp'] variable == hospital chosen in GUI (settings->Hospital or when creating new outbreak file)
    #
    # settings.ini takes precedence
    # Please note that hospital(s) from settings.ini takes precedence
    # This is to avoid conflicts where both settings.ini file and foreign Outbreak CSV file have changes in identical fields.
    # In such cases, we must defer to conflict resolution, and see whether it's best to update either file or try and merge.
    #
    # Please note that we are only talking about SETTINGS here.
    # The data in the outbreak CSV is the one that is shown ALWAYS, regardless of settings.ini file.
    # The settings.ini is only intended as a time-saver, not having to re-create hospitals for each outbreak.
    #
    # Example
    # >>> for sect in config.sections():
	# if sect in ('OPTIONS', 'RECENT'): continue
	# print(sect)

    # Vestre Viken
    # Oslo Universitetssykehus
    
    
    
    
    if my_hospital is not None:
        pass
    
    # Set vars in config
    shot['conf_user'] = my_user
    shot['conf_lang'] = my_lang 
    shot['conf_uniq'] = my_unique
    shot['conf_hosp'] = my_hospital
    shot['conf_recent'] = my_recent_files # list
        
    


# FUNCTIONS

def is_fnr(fnr):
    """
    Determine whetner input 'fnr' is true FNR or not. Return bool
    If the patient does not have a valid FNR, the age and gender fields will be required.
    """
    assert type(fnr) == str, 'FNR not a string in is_fnr()'
    if fnr.isdigit() and len(fnr) == 11:
        return True
    return False


# TODO
# Just use structure instead of repeating is_fnr(fnr) check all the time (in case check is more specific)
# E.g.
# if is_fnr(fnr):
#   nationality_from_fnr(fnr)
#   age_from_fnr(fnr)
#   etc.

def nationality_from_fnr(fnr):
    """
    If the person has a true FNR, it's a rather safe assumption that s/he has a Norwegian passport.
    """
    if is_fnr(fnr):
        return 'Norwegian'
    return None

def age_from_fnr(fnr):
    """
    Fetch age from 5th and 6th FNR digits.
    Note: For people born between 2000-2039, the last 3 FNR digits are 999-500
    Note: Oldest person alive at time of writing was born in 1902, so skipping earlier.
    """
    if is_fnr(fnr):
        year_now = time.localtime()[0]
        year_then = int(fnr[4:6])
        if int(fnr[-3:]) == 999 or ( int(fnr[-3:]) >= 0 and int(fnr[-3:]) <= 500 ):
            year_then = f'20{year_then}'
        else:
            year_then = f'19{year_then}'
        return year_now - int(year_then)
    else:
        return None
        

def gender_from_fnr(fnr):
    """
    Returns gender string from 'individnummer' from fnr. Even are female and odds are male.
    """
    if is_fnr:
        if (int(fnr[8:9]) % 2) == 0:
            return 'female'
        else:
            return 'male'
    else:
        return None

# Language functions



# GUI functions
#
def get_status_line(**kwargs): # TODO this does not work ..
    """
    returns status line string based on event loop events
    status(s=Save,f=<myfile>) will return Saving <file name> ..
    """
    event = kwargs.get('s', None)
    ofile = kwargs.get('f', None)
    if event is None:
        return shot['status_ready']
    elif event == 'Print':
        if ofile is None: return shot['status_printing']
        return f"{shot['status_printing']} {ofile}"
    elif event == 'Save':
        if ofile is None: return shot['status_saving'] # ? saved None file...?
        return f"{shot['status_saved']} {ofile}"


# Show error popup
def popup_some_error(show_str):
#    sg.popup_error(str(show_str))
#    sg.popup_ok()
    
    
    
    sg.popup(f"{shot['msg_there_has_been_error']}\n\n{str(show_str)}", title=shot['msg_there_has_been_error'], icon=shot['icon_error'])
    
    
    # Popup(args=*<1 or N object>,
    # title=None,
    # button_color=None,
    # background_color=None,
    # text_color=None,
    # button_type=0,
    # auto_close=False,
    # auto_close_duration=None,
    # custom_text=(None, None),
    # non_blocking=False,
    # icon=None,
    # line_width=None,
    # font=None,
    # no_titlebar=False,
    # grab_anywhere=False,
    # keep_on_top=False,
    # location=(None, None))
    
def popup_new_outbreak():
    
    new_outbreak_info = [
       [sg.Text('col Row 1')],
       [sg.Text('col Row 2'), sg.Input('col input 1')],
       [sg.Text('col Row 3'), sg.Input('col input 2')],
       [sg.Text('col Row 4'), sg.Input('col input 3')],
       [sg.Text('col Row 5'), sg.Input('col input 4')],
       [sg.Text('col Row 6'), sg.Input('col input 5')],
       [sg.Text('col Row 7'), sg.Input('col input 6')]
       ]
    
    
    new_outbreak_layout = [
                          [sg.Column(new_outbreak_info)],
                          [sg.In('Last input')],
                          [sg.OK()]
                          ]
    
    new_outbreak = sg.Window(shot['file_new'], new_outbreak_layout)
    # TODO register events here


# Note on HOSPITAL INFO
# A hospital is a "top container" in SHOT (we can only manage 1 at a time)
# A hospital is the parent of buildings, departments and rooms
# Since buildings, rooms and departments do not exist in 1-1 relationship, they are horizontal
#
#            Hospital
#               |
#       ,-------^-------.
#  Buildings       Departments
#          \        /
#             Rooms
#
#
# A room has 2 parents: Department, Building
# A Department has 1 parent: Hospital
# A Building has 1 parent: Hospital
# A hospital might have >1 buildings and >1 departments
#
# Buildings and departments could have been identified, but the separation is one of function.
# Employees in one department might be spread across two buildings.
# Employees in one building might be spread across multiple buildings.
#
# The distinction is necessary to track outbreak both geographically and within hospital functions
# Just my two cents.


def popup_new_building():
    """
    Creates a new building (child of hospital)
    """
    pass
    

def popup_new_department():
    """
    Creates a new department (child of hospital)
    A department may exist in >1 building, but at a minimum 1.
    """
    pass


def popup_new_room():
    """
    Creates a new hospital room (child of hospital)
    Rooms belongs physically to a building and logically to a department
    """
    pass



def popup_new_hospital():
    """
    Creates a new hospital (and a new hospital class entry in config)
    A hospital contains buildings, departments and rooms (which can be physically connected)
    This is a work-in-progress but might provide capability to display infection heatmap onto "map"
    """
    
    # If there is no hospital configured for this user (settings.ini file)
    # Then the new one will automatically be the selected on (in settings.ini file)
    # See configparser functions for more info
    
    # Hospital name (string)
    # 
    
    
    

def new_outbreak_file():
    """
    Runs the popup_new_outbreak
    Returns filename (or None 
    """
    
    # First, set/get username
    
    
    # Get hospital info from config parser
    if shot['is_configured']:
        # TODO get hospital info
        # Note: this might be the wrong hospital, if so, user must change this in Settings->Hospital
        pass
    else:
        # TODO setup hospital info and 
        pass
    
    pass

    
def open_outbreak_file():
    """
    Back-end function that takes care of opening file and creating the dicts
    Destructive: User has already chosen to open (and not been/ignored prompt to save any open stuff
                 so we can relatively safely overwrite the dicts below.
    """
    
    shot['data'] = {}
    shot['events'] = {}
    shot['tseries'] = {}
    shot['admin'] = {}
    shot['hospital'] = {}

#                                       len(shot['hospital']['building'])
#                                                     |
#                                                     |     len(shot['hospital']['department'])
#                                                     |                     |               
#                                                     |                     |        len(shot['hospital']['room'])  
#                                                     |                     |               |
#                                                     v                     v               v
#   shot['hospital'] = {'name': <str>, 'buildings': <int>, 'departments': <int>, 'rooms': <int>, room: <dict>}
#
#   shot['hospital']['room'] = []
#   shot['hospital']['room'] = [<id-str>,<name-str>,<building>,<dep>,
#       
        # hospital: buildings, dept, room
    
#    shot['rooms'] = {}
    
    
    # Headers
    # Note: tstamps values are always automatic timestamps of when record was created (or changed).
    shot['headers'] = {}
    shot['headers']['generic'] = ['rec_type', 'col_1', 'col_2', 'col_3', 'col_4', 'col_5', 'col_6', 'col_7', 'col_8', 'col_9', 'col_10', 'col_11', 'col_12', 'col_13', 'col_14', 'col_15', 'col_16', 'col_17', 'col_18', 'col_19']
    
    # TODO This ^ is ludicrious, get rid of it.
    # The entire point of this excercise is to use csv.DictReader's ability to _set headers manually_, so we can assert one of the groups (below) based on rectyp column.
    #
    # e.g.
    # example_reader = csv.DictReader(input_file, ['my', 'manually', 'asserted', 'headers'])
    # for row in example_reader:
    #   print(row['my'], row['asserted'], 'headers']) etc.
    #
    # because 'asserted' field might not be pertinent for this rec_type. etc.
    
    
    
    shot['headers']['outbreak'] = ['shot_user', 'shot_version', 'tstamp', 'title', 'hospital', 'start', 'end', 'infection type', 'incubation start', 'incubation end', 'incubation mid', 'sample_types' ]
    shot['headers']['data'] = ['data', 'author', 'tstamp', 'ch_auth', 'ch_tstamp', 'sample_date', 'sample_type', 'fnr', 'lastname', 'firstname', 'DOB', 'age', 'gender', 'fam_kode', 'role', 'department', 'team', 'room', 'bed', 'spa-type', 'risks']
    shot['headers']['events'] = ['event', 'author', 'tstamp', 'ch_auth', 'ch_tstamp', 'date', 'title', 'contents']
    shot['headers']['tseries'] = ['time series', 'author', 'tstamp', 'ch_auth', 'ch_tstamp', 'title', 'start', 'end', 'details' ]
    
       
    global outbreak_filename
    
    outbreak_file = open(outbreak_filename)
    outbreak_reader = csv.DictReader(outbreak_file, delimiter=';')

#    for row in outbreak_reader:
        
    
    outbreak_file.close()
    


def outbreak_file_sanity_pass(my_outbreak_file):
    """
    Collection of sanity checks of outbreak files run before loading and saving csv files
    Returns bool. Only True iff all required checks pass.
    """
    
    # Convert str to path
    # TODO latest python does not require string object for Path
    if my_outbreak_file is None:
        return False
    else:
        try:
            my_outbreak_file = Path(str(my_outbreak_file))
        except:
            try:
                my_outbreak_file = Path(my_outbreak_file) # might be useful for newer pythons..?
            except:
                popup_some_error(f"{shot['err_weird_data_string']}")
                return False
    

    # TODO
    # Check that file is not open/locked + perm
    
    
    # Note to self:
    # Path has an OPEN and a READ command
    #
    # |  open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None)
    # |  Open the file pointed by this path and return a file object, as
    # |  the built-in open() function does.
    #
    # |  read_text(self, encoding=None, errors=None)
    # |  Open the file in text mode, read it, and close the file.
    # 
    # TODO I am not sure whether to use open() or Path.open(). Must educate self.
    
    
    
    # Sanity checks
    # Note: Using readline() solved all my CSV sniffer problems. Use instead of read(1024) in docs.
    if my_outbreak_file.is_file():
        test_outbreak_file = open(my_outbreak_file,'r')
        #test_outbreakf = test_outbreak_file.read(9999) # .sniff(csvfile.read(1024),delimiters=',"')
        #dialect = csv.Sniffer().sniff(test_outbreak_file.readline())
        test_outbreak_file.seek(0)
        
        if csv.Sniffer().sniff(test_outbreak_file.readline()).delimiter == ";":
            print('file has delim') # debug
            
            if csv.Sniffer().has_header(test_outbreak_file.readline()):
                print('file has headers')  # debug
                
                test_first_row = []
                test_outbreak_file.seek(0) # re-set reader
                for row in csv.reader(test_outbreak_file, delimiter = ";"):
                    test_first_row.append(row)
                    break
                
                if (test_first_row[0][0] == 'rec_type') and (test_first_row[0][1] == 'col0') and (test_first_row[0][2] == 'col1'):
                    test_outbreak_file.close()
                    print('OK format') # debug
                    return True
                else:
                    popup_some_error(shot['err_wrong_data_format'])
            else:
                popup_some_error(shot['err_no_headers'])
        else:
            popup_some_error(shot['err_incorrect_delim'])
    else:
        popup_some_error(shot['err_input_notafile'])
        
        
    # close file and leave function
    test_outbreak_file.close()
    return False

# File Open popup
def popup_open_outbreak_file():
    """
    graphical user interface part of locating and opening files.
    'if popup_open_outbreak_file():' conditional will return True if file is sane.
    returns bool: True if file open success. (If True, set outbreak_filename global to input).
    """
    
    # This is weird but it works
    my_outbreak_file = sg.popup_get_file(shot['file_open'], title=shot['file_open'], save_as=False, multiple_files=False, file_types=(('Outbreak CSV', '*.csv'),), no_window=True, keep_on_top=True)

    if type(my_outbreak_file) is str and my_outbreak_file != '':
            print(f'my_outbreak_file={my_outbreak_file}') # debug
            print(f'type(my_outbreak_file)={type(my_outbreak_file)}') # debug
    else:
        # User clicked cancel
        # bugfix Cancel op: sg.popup_get_file returns tuple
        # bugfix cancel x2: 2nd time the sg.popup_get_file which normally is tuple returns empty string
        return False
    
    # set global filename var
    global outbreak_filename

    # sanity check
    if outbreak_file_sanity_pass(my_outbreak_file):
        outbreak_filename = my_outbreak_file
        return True
    else:
        outbreak_filename = None
        return False
    


# Main Tabs
# With the exception of welcome tab, all tabs' visibility/active state is conditional
# All tab functions _return a list_ for PySGUI

# Tab 0: welcome
def tab_welcome(outbreak_filename):
    """
    Returns list containing Welcome tab contents. Content is conditional on file being loaded.
    """
    
    if outbreak_filename is None:
        welcome_tab_filename = shot['msg_no_file_loaded']
        welcome_tab_loadfile = f"{shot['msg_no_file_loaded']} {shot['msg_no_file_tip']}"
        welcome_tab_user_key = ' ' * ( len(shot['msg_user']) + 3 )
        welcome_tab_username = ' ' * 120
    else:
        welcome_tab_filename = outbreak_filename
        welcome_tab_loadfile = shot['msg_file_loaded_ok']
        welcome_tab_user_key = f"{shot['msg_user']}: "
        welcome_tab_username = 'user-name-string-here'
        
    
    # TODO
    shot['version'] = "0.01 alpha" # TODO set dict_version from global string atop
    my_welcome_tab = [[sg.T(' ')],
                      [sg.Image(filename=None, data=shot['icon_logo'], size=(120,120), pad=(2,2)), sg.T(f"Simple Hospital Outbreak Tracker\nA Free and Open Source Public Health Software Project\nCopyright (C) 2020, GNU GPL v.3. Version: {shot['version']}", font=('Sans serif', 16))],
                      [sg.T(f"\n{shot['tab']['tip']['welcome']}\n")],
                      [sg.T(welcome_tab_user_key, key='welcome_tab_username_infokey'), sg.T(welcome_tab_username, key='welcome_tab_username_infoval')],
                      [sg.T(f"{shot['file_file']}: "), sg.InputText(welcome_tab_filename, key='welcome_tab_file_loaded_infobar', size=(75,1), background_color=None, enable_events=True, disabled=True)],
                      [sg.T(welcome_tab_loadfile, key='welcome_tab_file_loaded_ok')],
                      [sg.T(' '), sg.In(' ', visible=False, key=f"+{shot['icon_key_open']}+")],
                      [sg.Button(shot['icon_new_str'], key=f"-{shot['icon_key_new']}-", size=(24,3), font=("Helvetica", 16)), sg.Button(shot['icon_open_str'], key=f"-{shot['icon_key_open']}-", size=(24,3), font=("Helvetica", 16))],
                      [sg.T(' \n')]
                      ]                          

    return my_welcome_tab
    

# Tab 1: outbreak
def tab_outbreak():
    pass
    

def tab_epicurve():
    pass


            # # if filename not None
            # # display 1 tab: "Welcome"
            # # This tab shows 2 buttons (New and Open)
            # # When new and open leads to verified file => 3 more tabs become accessible: Overview | Linelist | Epicurve
            # # So that the tab-line becomes
            # #
            # # Welcome | Overview | Linelist | Epicurve
            # # Welcome | Outbreak | Linelist | Epicurve
            # # Velkommen | Utbrudd | Tilfeller | Epikurve
            
            
        
    
    
    # if self.content_type == 'table':
        # self.table_data = []
        
        # if self.frame_title == 'overview':
            # # Read data from file into dictionary
            # pass
            
            # # Put dictionary into PySGUI table list

            
    # # Use this somewhere else..? For putting up the csv, of course.



def import_from_csv(input_file):
    # df.loc[df['column_name'] == some_value]
    
    # Read csv into list structure
    df = pd.read_csv(filename, sep=';', engine='python', header=None)
    outbreak_data = df.values.tolist() # read everything else into a list of rows
    #outbreak_inf    
   

# tab_outbreak_intro = 'Outbreak Overview'
# outbreak_info = {}
# outbreak_info['created'] = '2020-05-09'
# outbreak_info['outbreak began'] = '2020-05-01'
# outbreak_info['outbreak ended'] = 'N/A'
# outbreak_info['type'] = 'influenza typeB'
# outbreak_info['outbreak'] = f"{outbreak_info['type']} outbreak {outbreak_info['outbreak began']}"
# outbreak_info['basename'] = f"{outbreak_info['outbreak began']}_{outbreak_info['type']}"
# outbreak_info['filename'] = f"{outbreak_info['basename']}.out"
# outbreak_info['datafile'] = f"{outbreak_info['basename']}.csv"




# LINELIST tab functions
def add_linelist_cases():
    """
    Table-view to add >1 case
    """

def add_linelist_case():
    """
    Application-view to add cases one-by-one
    Built to spec
    """
    pass
    
    # LEGEND OF DATABASE FIELDS (by spec)
    #
    # NO                        EN              Tool tip
    # ID <auto increment>
    # P-Dato                    Sample date     Dato prøvetaking (bærerskap), eller symptom start (illness onset)
    # P-Mat                     Sample type     Prøvematriale, select from drop-down corresponding to infection type OR freetext
    # Fnr                       SSN             
    # Etternavn
    # Fornavn 
    # Fødselsdato               DOB             Fra FNR på Norsk
    # Alder                     Age             Fra FNR på Norsk
    # Kjønn                     Sex             Fra FNR på Norsk
    # Fam. kode                                 ???
    # Status                    Status          Pasient, pårørende, ansatt, ekstern
    # Avdeling                  Dept
    # Arbeids team              Team
    # Rom                       Room            Choose from hospital settings
    # Seng                      Bed             Choose from hospital settings
    # Spa-type                                  Type MRSA (sjekk "spa type" på engelsk)
    # Risikofaktorer            Risk factors    Factors that amplify risk for infection or outcome
    
    # NOTA BENE
    # P-mat avhengig av infeksjonstype
    # Hvilken sykdom det er snakk om
    # 
    # Noro - oppkast, diare
    # Influensa - dyp neseprøve
    # ESBL - 
    # 
    #
    #
    #
    
    

#     Graphical User Interface
WIN_W: int = 90
WIN_H: int = 25

text_size_cols = 90
text_size_rows = 25



def set_gui_strings(language):
    """
    This function sets the visible strings for the GUI according to internal language preference.
    Translation is done by appending this function with an elif clause appropriate for your language.
    
    Use ISO-3166 2-letter country code: 
    # Usage 
    # set_gui_strings() # Use default (English)
    # set_gui_strings('NO') # Sets Norwegian
    # set_gui_strings('EN') # Sets English
    
    For reference: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Decoding_table
    """
    
    # Init GUI strings dictionary
    # TODO is it sane to include initialization here..? We might run set_gui_string from a change_language function..
    #global shot
    shot['available_languages'] = []
    
    # Initialize string dictionary using a default language (English)
    # In case translation is missing strings the application will still work.
    # file_new: str = 'New............(CTRL+N)'
    shot['file_file'] = 'File'
    shot['file_new'] = 'New Outbreak'
    shot['file_open'] = 'Open Outbreak'
    shot['file_close'] = 'Close file'
    shot['file_save'] = 'Save'
    shot['file_save_as'] = 'Save As ...'
    shot['file_import'] = 'Import from spreadsheet'
    shot['file_export_sheet'] = 'Export data spreadsheet'
    shot['file_export_image'] = 'Export plot image'
    shot['file_print'] = 'Print'
    shot['file_exit'] = 'Exit'
    
    shot['stats_stats'] = 'Statistics'
    shot['stats_linelist'] = 'Linelist'
    shot['stats_epicurve'] = 'Epicurve'
    shot['stats_gchart'] = 'G-Chart'
    shot['stats_compare'] = 'Outbreak comparison'
    shot['stats_filtering'] = 'Filtering'
    
    # Settings
    shot['settings_settings'] = 'Settings'
    shot['settings_encryption'] = 'Data file encryption'
    shot['settings_language'] = 'Language'
    shot['settings_language_str'] = 'Your current language is'
    shot['settings_language_set'] = 'English'
    shot['settings_language_change'] = 'Change language'

    # Settings > Hospital
    shot['settings_hospital'] = 'Hospital'
    shot['settings_hospital_manage'] = 'Manage hospitals'
    shot['settings_hospital_rooms'] = 'Room editor'

    # Help menu
    shot['help_help'] = 'Help'
    shot['help_help_help'] = 'Help'
    shot['help_online'] = 'Online help'
    shot['help_license'] = 'License'
    shot['help_participate'] = 'Report issue'
    shot['help_about'] = 'About'
    
    # Text strings for GUI icons
    shot['icon_new'] = 'New'
    shot['icon_save'] = 'Save'
    shot['icon_open'] = 'Open'
    shot['icon_list'] = 'Line list'
    shot['icon_plot'] = 'Epicurve'
    shot['icon_image'] = 'Export plot'
    shot['icon_print'] = 'Send to printer'
    shot['icon_list_add'] = 'Add line'
    shot['icon_list_rem'] = 'Remove line'
    shot['icon_new_str'] = 'Register New Outbreak'
    shot['icon_open_str'] = 'Open Existing Outbreak'
    
    # Strings for status messages
    # These are used by themselves or in front of file names.
    # Eg. in string "Saving {output_file} .." 'Saving' is the translated term.
    shot['status_ready'] = 'Ready'
    shot['status_printing'] = 'Printing'
    shot['status_printed'] = 'Printed'
    shot['status_saving'] = 'Saving'
    shot['status_saved'] = 'Saved'
    
    
    # Strings for tab headers and tab tooltips
    shot['tab_welcome'] = 'Welcome'
    shot['tip_welcome'] = 'Welcome to the Simple Hospital Outbreak Tracker'
    shot['tab_overview'] = 'Overview'
    shot['tip_overview'] = 'Outbreak overview'
    shot['tip_linelist'] = 'View or add cases to the linelist'
    shot['tab_events'] = 'Events'
    shot['tip_events'] = 'View or add pertinent events to timeline'
    shot['tip_epicurve'] = 'Plot the data from the linelist'
    shot['tip_g-chart'] = 'Plot data from linelist in g-chart'
    
    # Some general warnings and errors
    shot['msg_user'] = 'User'
    shot['msg_user_unset'] = 'User not set'
    shot['msg_user_change'] = 'Change User'
    shot['msg_no_file_loaded'] = 'No outbreak file loaded.'
    shot['msg_file_loaded_ok'] = 'Outbreak file ready.'
    shot['msg_no_file_tip'] = 'In order to proceed, please create a new outbreak or opening an existing outbreak file.'
    shot['msg_there_has_been_error'] = 'There has been an error!'
    
    shot['err_wrong_data_format'] = 'Incorrect file type. Does not seem to contain the right data.'
    shot['err_incorrect_delim'] = 'Incorrect file type. Incorrect delimiter detected.'
    shot['err_no_headers'] = 'Incorrect file type. File did not contain any headers..'
    shot['err_weird_data_string'] = 'Weird. Cannot convert input file string to Path object.'
    shot['err_input_notafile'] = 'Incorrect input. Input is not a file.'
    
    # Set translated language string
    if language == 'English':
        pass # We already have English
    elif language == 'Norwegian': # Norwegian
        shot['file_file'] = 'Fil'
        shot['file_new'] = 'Nytt utbrudd'
        shot['file_open'] = 'Åpne utbrudd'
        shot['file_close'] = 'Lukk fil'
        shot['file_save'] = 'Lagre'
        shot['file_save_as'] = 'Lagre som ..'
        shot['file_import'] = 'Importer fra regneark'
        shot['file_export_sheet'] = 'Eksporter regneark'
        shot['file_export_image'] = 'Eksporter bilde'
        shot['file_print'] = 'Skriv ut'
        shot['file_exit'] = 'Avslutt'
        
        shot['stats_stats'] = 'Statistikk'
        shot['stats_linelist'] = 'Linelist'
        shot['stats_epicurve'] = 'Epikurve'
        shot['stats_gchart'] = 'G-kurve'
        shot['stats_compare'] = 'Sammenligne utbrudd'
        shot['stats_filtering'] = 'Filter'
        
        shot['settings_settings'] = 'Innstillinger'
        shot['settings_encryption'] = 'Datafilkryptering'
        shot['settings_language_set'] = 'Norsk'
        shot['settings_language_str'] = 'Gjeldende språkinnstilling er'
        shot['settings_language'] = 'Endre språk'
        shot['settings_language_change'] = 'Endre språk'
        
        shot['settings_hospital'] = 'Sykehus'
        shot['settings_hospital_manage'] = 'Administrere sykehus'
        shot['settings_hospital_rooms'] = 'Administrere rom'

        shot['help_help'] = 'Hjelp'
        shot['help_help_help'] = 'Hjelp'
        shot['help_online'] = 'Online hjelp'
        shot['help_license'] = 'Lisens'
        shot['help_participate'] = 'Gi tilbakemelding'
        shot['help_about'] = 'Om SHOT'
        
        # Text strings for GUI icons
        shot['icon_new'] = 'Ny'
        shot['icon_save'] = 'Lagre'
        shot['icon_open'] = 'Åpne'
        shot['icon_list'] = 'Line list'
        shot['icon_plot'] = 'Epikurve'
        shot['icon_image'] = 'Eksporter graf'
        shot['icon_print'] = 'Send til skriver'
        shot['icon_list_add'] = 'Legg til'
        shot['icon_list_rem'] = 'Fjern'
        shot['icon_new_str'] = 'Nytt utbrudd'
        shot['icon_open_str'] = 'Åpne eksisterende'
    

        # Strings for status messages
        shot['status_ready'] = 'Klar'
        shot['status_printing'] = 'Skriver ut'
        shot['status_printed'] = 'Skrev ut'
        shot['status_saving'] = 'Lagrer'
        shot['status_saved'] = 'Lagret'
        
        # Strings for tab headers and tab tooltips
        shot['tab_welcome'] = 'Velkommen'
        shot['tip_welcome'] = 'Velkommen til Simple Hospital Outbreak Tracker'
        shot['tab_overview'] = 'Oversikt'
        shot['tip_overview'] = 'Utbruddsoversikt'        
        shot['tip_linelist'] = 'Rediger eller legge til data til linelist'
        shot['tab_events'] = 'Hendelser'
        shot['tip_events'] = 'Rediger eller legg til hendelser som er relevante for utbruddet'
        shot['tip_epicurve'] = 'Plott en epikurve av linelisten'
        shot['tip_g-chart'] = 'Plott en G chart graf av linelisten'
        
        # Some general warnings and errors
        shot['msg_user'] = 'Bruker'
        shot['msg_user_unset'] = 'Mangler bruker'
        shot['msg_change'] = 'Endre'
        shot['msg_no_file_loaded'] = 'Ingen utbruddsfil er valgt.'
        shot['msg_file_loaded_ok'] = 'Utbruddsfil klar.'
        shot['msg_no_file_tip'] = 'Vennligst lag en ny utbruddsfil eller åpne en eksisterende for å fortsette.'
        shot['msg_there_has_been_error'] = 'Det har skjedd en feil.'
        
            
        shot['err_wrong_data_format'] = 'Feil filtype. Filen har ikke riktig type data.'
        shot['err_incorrect_delim'] = 'Feil filtype. Filen har ikke riktig delimiter.'
        shot['err_no_headers'] = 'Feil filtype. Filen har ingen overskrifter.'
        shot['err_input_notafile'] = 'Feil objekt. Inndata er ikke en fil.'
        
        
        # Finally, append this language to list (towards the bottom of the function)
        
    elif language == 'Swedish':
        pass # copy dictionary keys above and start translating
    elif language == 'Spanish':
        pass
    elif language == 'Finnish': # Finnish
        pass
    elif language == 'Italian': # Italian
        pass
    elif language == 'Russian': # Russian
        pass
    
    # etc. etc. etc.

    # Re-use strings for tab headers
    shot['tab_epicurve'] = shot['stats_epicurve']
    shot['tab_linelist'] = shot['stats_linelist']
    shot['tab_g-chart'] = shot['stats_gchart']
    
    
    # Remember to activate a translation, by adding it to the list
    shot['available_languages'].append('Norwegian')
    shot['available_languages'].append('English')
    shot['available_languages'] = list(set(shot['available_languages'])) # unique (lazy fix) # CURRENTLY unnecessary bc we init list at the top


    
    
def set_gui_icons():
    try:
        # Keys for icons
        # These cannot be changed (used for input)
        # Note: Do not translate these strings
        shot['icon_key_new'] = 'Button_New'
        shot['icon_key_save'] = 'Button_Save'
        shot['icon_key_open'] = 'Button_Open'
        shot['icon_key_list'] = 'Button_List'
        shot['icon_key_plot'] = 'Button_Plot'
        shot['icon_key_image'] = 'Button_Export'
        shot['icon_key_print'] = 'Button_Print'
        shot['icon_key_list_add'] = 'Button_Add_line'
        shot['icon_key_list_rem'] = 'Button_Remove_line'
        
        # Icon files (public domain Tango set 32x32 px base64 encoded)
        shot['icon_bin_open'] = b'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'
        shot['icon_bin_list'] = b'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'
        shot['icon_bin_plot'] = b'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'
        shot['icon_bin_image'] = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAJ2AAACdgBx6C5rQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAASdEVYdFRpdGxlAEdlbnJpYyBJbWFnZfKTN1kAAAAUdEVYdEF1dGhvcgBKYWt1YiBTdGVpbmVy5vv3LwAAAFh0RVh0Q29weXJpZ2h0AENDMCBQdWJsaWMgRG9tYWluIERlZGljYXRpb24gaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvcHVibGljZG9tYWluL3plcm8vMS4wL8bjvfkAAASvSURBVFiF7ZXNjxRFGIef/pzunl0WlmUjAaJhhYCBhJCoB0y4cPNv8H/w6smjEU+G+BGPxrOJJiYaNsbEqETEKKAuGz6isLNhZ+ere+ezu97XQ0/v7DgsIBgPypt0qrqqq35P/+qtKngS//ewFhcXd5dnypd27dg19W8IqiprtbWfTp86fQbAxeXkoYOH9g36A1dVcyrLmhi03WR/9z2KIrA4UbS5hWCn0+Hq8h0acQJYFAyqoCiqikpeig5LUVQFKeqiiMpmn6jkbZKPOXH0GY4fOTgG5RYVy7L4+eoSdzsBtm0BBUEuYIYTGZHx0ggigrlfXQRPNrDVbA8A4HkOpak92LaNY8PsTJen5lPSzPBHpUS95WIMGBEcyaGcoYhd1I3iDIGNyb8TVeit4zj2xDKOAbi2ReR7OLbF3rkOp5+3OTD/HKJ9rq/c4vy3hrV6kFu6xQWRSYdEhy4Uy4GHaz8AwLIgLHk4jnJ0IWNh34v47j5AOXzA587Cr3S604gwEhFFNpelyA3BCJviRoRMPRzH2h5AVbEtCH0XzxGmInDsqEDDd6fZEUE5cDFiDRNwlGCFE1k2IKlcIZx9FtvfkbcZQ7fvTuwugL94YhGUXFzPp9502OgtI5JgpEarfZ16HBKWPKLAIwpHTzn0KEc+5chjUL1CqVSitryIrX08zyYMPALfwbYKp0cgYw5YKGHJA2CtNs/l5bvs3bNKJsLKqksSzxOWXEARGW1PkXx8Uq/QqFxjfuEUSbOGe+MbFk6+nIv2fFzXnnBhHMBSosAbeuGxWg2p1gagMMg8fM/G9/JvVYflcGyWDvjh0hfEcczh2d0ANO/eJPIErxRiOh6uLdsD5KIQDR0YRQkFXGcEWpxvBUhmhO8vfE6rUaUUlAl9e7N/KvIpBQH9wMd10gc4oMJUOLlVCsVc2oLh6SgCaWZYWb3FraVLAExNT9NtrQKwcPg4e+dmAOiHDradTUw9BrBej/ny66uTAORHMuR/LCJ0+ylpmiEmo1O/SbQrP+F6YnPpwld4wU7qvSk+W/wxB2hXOXFkDsuytk/C/mBAN4u3vYyyzNAfZKRZho7WgXYnoz8YjAbY80g/o9+ImdYAsMh6XUTukwOqyqDfp5nG+fvwMjEmf9LMbHsr4s0AAUmzyqC3gVeKCMJpGpXfqdWq7Jzbh23aiDEAiMgmxSaAMYZGs8VKK91e6AHhBjOo5dOOqwzSDMUlbtZIM2G6HGBM/hPr69XyBABAmqXESfxI4lvDCXfR6yWceekYh56ex/NLqBpmZyKu/nKFjXYiEwCWZWGMIUm6jw1QxNzsDC+cPE6WZXQ6HarVKpWVimDrm2MAqmoBGJOx0398B4pI+y3a7Q06nS6NRoM4ibXb7148+8bZt8YAIHfg9ddencjUe9Uftv/Gres0my2SJKEZN00cNy++c+69VyqVymgJVLWbpmm2f/9+Zyv9vW6uh+nb2r+0/Bu19Tpx0oqvXVs69/67H3wINIHeJkCj2vhuyV36SEWPGWMcEbFV1UK5v8oDwNI0ddeqa7tv3759/pOPP3378uXLVaANtMbG3GMeF/AA5x59jxopkAHmH5zzSfxH4k/pCDFuBN/TvgAAAABJRU5ErkJggg=='
        shot['icon_bin_print'] = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAJ2AAACdgBx6C5rQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAANdEVYdFRpdGxlAFByaW50ZXIIJrITAAAAFHRFWHRBdXRob3IASmFrdWIgU3RlaW5lcub79y8AAAAhdEVYdFNvdXJjZQBodHRwOi8vamltbWFjLm11c2ljaGFsbC5jemlm414AAABYdEVYdENvcHlyaWdodABDQzAgUHVibGljIERvbWFpbiBEZWRpY2F0aW9uIGh0dHA6Ly9jcmVhdGl2ZWNvbW1vbnMub3JnL3B1YmxpY2RvbWFpbi96ZXJvLzEuMC/G4735AAAD5UlEQVRYheWXz08bRxTHv7P2rH9hYxlkSCI5TqCNqrZwyw2h3qtekLhW4oDaKzf+gFTyuYJLxV+Q5tYcaGklJKuVqMQRqJNIVmQ5NODYxoDt2Zl5PewPvBgbG0tVpT75ad/O7O77zPsxuwb+78L6TeZyuaeMsYejOFBKFdfX1/8cGiCXyz1dWFj4LZvNxkYBKBaLF7u7u1/0ggj2JGPsYTabjQkhRvGPbDYby+fzWQDDAXSADOSIiIYCGwiAMQbOORqNBtrt9lDOJycnvWeMBBAMBsE5h9Z6YOcAwDkHgJ73DQzAOUcsFkM4HB7YeSfAbTU0EIDW+sZQDgJgWdbdAQzDAOcczWaz50pCoRASiUTPZ4xcA5xzTExM+MaHqXjDMO4OIITA8fExhBBQSvnA+tmMMUSjUQCAlPLuAJVKBUIICCF81TwIQCQSAQAEAoG+AL4Era2tfTk/P/9DKpUyz87q5v37D8aklF01cD2vN50nk0kAdrpKpdL52FhMvHt33D44OFja2Nj4owtgdXV1fHFxsbC8vJwGgEKhgL29PZimObDTztpw55vNJubm5pDJZBAOh7G1tVUqFAqfbG5ungMdKZiamtpaWlpKu+epVArpdHqggutX6fF4HMlkEkSEdruNlZWVB989e7YB4GvfhTs7OxWtFSnVrVLKLrUs61YVQnSplJK2t7crrl8vArVaVZXLZbRaTUQjERARDMMAETlRIJAmEJw2pP42nPtc+7LZxMnJCRKJcdTrdd0FYFkSRIRyuYyPZmdR+fABJjeRyWRuTUFvIfeHWq2G12/eYCweh7QsL6/eLiGlRUSEV69e4/KyiZ+3f8H09PQIzgGAAYyBMYZqtYp6rQbSGlYHgBcBKSUREdLpNH56+RLjySSe//jCW0XHmm5cpX+Eui4+rZzi888+he4NYEfgyZOPMTvzGG0h7BxqDe3m02e7ObbHiciec2wigu6wZ2YeOWMEIcRNAIqI7NowDAOhUOgWgG6n/QDcnZTIHwGvBoSw2F0/q4YRrTUsefWK9gAsyzL+FQAitFqtAJxd2E3B2Pv3f18cHR0hEAgCTjivep9gt7h2juTrc2+fcK4BwQm/W5BXz1FS4fT0tAFgHEDNBTB3dn799qxef/7ocSZumiZMzuEeuckRMAJQWkNfU6WVbavuOU+VhtK2vn1bOsvnf/8GAO+MgLW/v//XvXtT3zfOL75iDAG7fQ0wp489IX+b+W270Ox6s8ftrBIYA2kNVa1WXhweHhYBWID/dZwEkAAQdcBu/c8wpEgAGsAlgAaAKgB9/TUWBBCGHZ7+XxLDi3IgWnBW/5+QfwAGzP/HEoYxvAAAAABJRU5ErkJggg=='
        shot['icon_bin_find'] = b'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'
        shot['icon_bin_settings'] = b'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'
        shot['icon_bin_save'] = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAJ2AAACdgBx6C5rQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAQMSURBVFiF5ZfPixxVEMc/73VPehyyO0k8uDHEKKyuPyIaPUSMeBAkiGtQj0JAj/on5BS86i0g/gGezFVESASRkENAEM0S4w8wB8km6JrdzIyZ6a4qD+91T/fujAF31osFzbx+Pd31fZ+qV9UN/3dz5eD5N059trR48CksnJ/Y09uDaTiJc2ZW3Whx0lVXx3PVjFoYO/j0984tMMyMX69d/+7S5x8uA6SlkEcfPvTsC8eXF9Z6BWAcPvPaWGbdsVnjvDFm+rVv3zk7ZxhznRT96lx6idMeTmspADX44/aIM6fe4rkT73H8h++nYvs3tro2wDBEshqzMQFMFVPl6PK77F14iAc+PttAvh1zzmFXNApQ6grS+h9FlfsXn8Ew5l89NhPnpenKBcAwLUVsEmBmmCqqTYWzMtNIQLXx9HEOiKFq1R8B1tfXGQ6H23KcZRndbrdamIk2krNGQFG1BoFut7st53UrF6aBcqWgEiAGGhPRdiAEFQHVRnJXApypmTRzYJYhsBh7mSagulgjMMsQhIWBiiCTBIj8F7sgCpGJSWhbCAyHQ4qi2JbjNE3JsmxMQBVjQh0oE2THCUjYbVsElFuwTiDLMrIsm4mA4DT6mFwHLKrb2Uo4VYBak8DJ98+H8iwjtH8jPKRst7HNYxbnyuIWVhlatsPa9wJJeE68Hhdp4JsCMK0RGPf9ZPU8jz+4QJomOO/xzpMkHucc3id47/He4ZxHVSlEUFHyouDy1YvcnjsWn0UkIA0ytXbszEyrZMHCSuYzz5Gnn2Rt7U+++PIiPtkFwNLiAV5+6UUA8jynKAryPG+Mf/rlGhsR+SYCbCGgKCJjASUB5zztdpter8ctDqHpfsDorl5mNBpNdV4URVn3Y4is1gumFKJSXZ2A9452u02r1WqgU1X6/f4Wp/VfEYm1v3yfDO8CNf/NOqAqEwmkaYpIM3YiQcBmp/VxhbtGwFRBJxSi8D6g1X61SMDiSkejvClAhcFg8I8hEB0TKImKymQCZiF7y21YEhBVBoPBlq6ocvcQqEiTQKw1Nvl9QF3ia327ukHo9/uoCi1ZoxgqzoFrcfcQqGI6XkwlYEIhstXfbp47cPDmm3Odfbt7gyEucEBiCLrdeY4sDhiNeqgqnc59U0PQ+ICpOY/ZiJq5LQRWvv7obZy0lh47/Hq7s/sec6F43BlscPXHnxERVEOYRIT1jR4iEuZjEdtspjmp9EL3s9APhn0YDP66Ax8Y1D7NorlHjp58Jc+LfSZ5S7Vo7d/rnlAtUjNNzCzBcGbmwZzF+8PnmTPnnOIw55w45wV8cWPdrXif5i5p5Umya4Rz1pLiwpVvPrk+ScBmc5HSLqAVx0k8XO1+i4fEowByYBTHs+9us7K/AfK2J+E/6eoRAAAAAElFTkSuQmCC'
        shot['icon_bin_readonly'] = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAJ2AAACdgBx6C5rQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAWdEVYdFRpdGxlAFJlYWQgT25seSBFbWJsZW2TGUkUAAAAFHRFWHRBdXRob3IASmFrdWIgU3RlaW5lcub79y8AAAAhdEVYdFNvdXJjZQBodHRwOi8vamltbWFjLm11c2ljaGFsbC5jemlm414AAABYdEVYdENvcHlyaWdodABDQzAgUHVibGljIERvbWFpbiBEZWRpY2F0aW9uIGh0dHA6Ly9jcmVhdGl2ZWNvbW1vbnMub3JnL3B1YmxpY2RvbWFpbi96ZXJvLzEuMC/G4735AAADdUlEQVRYheWWT28bRRjGf7te/1mnIcEBWoSc1k1cQS8Ug1QhkHLjmjtXTvkACCknbvkA3FOUiC+QDxAp4pCGJEUq7anOHyUpFOMQslnb0Xq9y6EZd7w7s7uVKi480mhHM+/M87zvvDPvwv8dRnRgZWXl61Kp9F2lUpkyDCOfuNh4tTwMw0SibrfrOo7zzHGcbxYWFp4rBayurn7faDS+rdVqZc/ztGRZIYsyTRPDMNjY2Hh+fHx8X4iwhMHy8vK71Wp1YXp6unx6ejpCKpNnESKIo1/TNJmbm/tgbW3tAfDViADgfr1er7iuGyNWCckCwzAIw3D4DYIAgMnJyTvCZiggl8vVisWi5XneCKHO+6gYOdyCUIUgCCiXy8WYAB2JynvXvaDV+pNOt8vA9ynZNmNj13j/xg0sK68VoYqgFTVIC//h4T7N/SYoHDw43Kdx71PGx8dH9oxGRytARyz6rntBc7+JaZjMzM5y/b3rFAoFer0eB4cHvHjxB789fcwXn38ZV6eJhJwD2kiIfrv9FwYGN2/eYub27NC+UChy7+NP+Nm9oNvp0Ov1KJfLqeQApspA1/p9H4BKZUo5P1WZAqDff5nI4u7LLYrEHIj2w6uDt3I59WaWFVsrQ1xJrQA5RCoBqiZvDlfjplqACpmTcOuXh/xzfgbAo193Mc3Y6TEIBgDs7u4wMzNL7dbt1xcQFSPa2dnfr4gGAwaDQcxeXDff93HOz5VRiEYulgMq8qxPsZgXZ53lGFJzICmDdeVYJ1j1PCuPIIlc55XsvQ4qRxJrQXRRlpDKFTCLfTyVE9RmtdFVU3lOIHMEkjZKC3/SfOo1FKjX79DtdEbGVUkYhiFhGFKtTqdWwlQBMj768O5INMQ7L5OKFgTBsJ8GbQ78VxgK8DzPVb1uAlFvol7LY2l7+L4fxAScnJw8abVaHVHRVBtGSVUidGsFcrkc7Xb7IiqgsLS09PvW1tYzeFlWddkfPWv5vGVS1TNu2zZ7e3uXzWbzB8AGEL9BBd/3rx0dHT2ybfuziYmJt2zbtmQiUYDkvtx834/1hcAgCLi8vAx3dnbO19fXf1pcXPwR6AGe7N47wNv5fH5yfn6+UavV6sVisaQ7z9eF4zjtzc3Nh9vb2wfAGXAKDKIXcxwYA/JX7U3CB/pAF3C4+q9Oemvf9BUNVIP/Apto0DxVtwCRAAAAAElFTkSuQmCC'
        shot['icon_bin_list_add'] = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAJ2AAACdgBx6C5rQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAJdEVYdFRpdGxlAEFkZAzpDSgAAAAWdEVYdEF1dGhvcgBBbmRyZWFzIE5pbHNzb24r7+SjAAAAGHRFWHRDcmVhdGlvbiBUaW1lADIwMDYtMDEtMDTXvFLIAAAAH3RFWHRTb3VyY2UAaHR0cDovL3RhbmdvLXByb2plY3Qub3Jn7+KWDQAAAFh0RVh0Q29weXJpZ2h0AENDMCBQdWJsaWMgRG9tYWluIERlZGljYXRpb24gaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvcHVibGljZG9tYWluL3plcm8vMS4wL8bjvfkAAAJQSURBVFiF7ZZNaxNRFIafO6kmFoLF+rGwG6lQRJAuXFhE3FT3IqgLcacgKO6lbtS9CxFEunNV9CdYFBRx0foDVAiUFluqSZs0xrS553UxM81QmphMwQ/ICzcnOTP3nOeec+dOoKeeevrLcmkmnb41dT/j3HjS10DT7x9fvtdtrL40AIELxh/ePDtWq3sA9mT7uPv0tQP+DABArW4sFGsAHB7sTxuGIPXMhCT9vwCpWwACHAIsff70FbAIAYF2QNCyAievP794/MjByf0D/etJvyRwZGMCKYQZPXrg2IlH00uK3dFHqfJzd2F+5cbM5NWXXQHIBcG5U8MDuVy26YusGRSr68StX6k2GBsd3isL75HCtkhitVJVYf5j9xUInAJvRrm2kfC6zaTehAQNEz/qhpdoeGFeNCS8j3ZJY3278B0AmHPLq3UW16pknEM4zMLEcculECheNYnvimCzLiWAnIKv3yocGsxjJiTh49Ia5PP9FJZqCBjal6NUXsNMmIEQ3sAQxVK57XHfEsBj797MFi5tdy3bl3lw4fzoSLxaL/F25vOn+oafaJHkQ9cAs8+uzQFz2107c3vqjhcjcdnNRJAJirNPrrxoFa9rgN/Jok0owqcirToBcIQHVsLKmRRtOIfX5n27aJ5RHWG1A4gTZrbYQFJgFiYPW2BIFgDZKLEBPmF3BJAcGSCDcKWVCjkXYBirZXCSi+JtTdi2Gu0AkpOUsPZ98cvEq9LyEJLDufCVsFFboLnq5Gj7ouj0L1myGi4xkhLN1Vrid089/dv6BdgRPgK2XHcfAAAAAElFTkSuQmCC'
        shot['icon_bin_list_rem'] = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAJ2AAACdgBx6C5rQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAMdEVYdFRpdGxlAFJlbW92ZWd7O2IAAAAWdEVYdEF1dGhvcgBBbmRyZWFzIE5pbHNzb24r7+SjAAAAGHRFWHRDcmVhdGlvbiBUaW1lADIwMDYtMDEtMDTXvFLIAAAAH3RFWHRTb3VyY2UAaHR0cDovL3RhbmdvLXByb2plY3Qub3Jn7+KWDQAAAFh0RVh0Q29weXJpZ2h0AENDMCBQdWJsaWMgRG9tYWluIERlZGljYXRpb24gaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvcHVibGljZG9tYWluL3plcm8vMS4wL8bjvfkAAAEtSURBVFiF7ZE9TgNBDIWfJz8SShoaKBAlBXUkGsQN6LkEJUfhDnACCkoOkIYK0SABaSJARFmCMms/Cu+ukjD89JmvGcv2jN/zAJlMJpPJrDuSSh6eXl4d7O8MQqJKElw4QcII0AxW17zsPfR7dw8vzzfnJ4PV99opAa0QesdHe1tv07g8vDrNlsVYVaChEue5ur7RDXgaD0epWUkBgMg8EpNZXM03jtTcnZrHSkIVsCYmDAJVYrPfRqn8NuVHAQTl8bXA/WiKEACBQM2dlcpmE6QLql1jIWYllgQ+YwlVSypIb4CUyfsHtvstGN0VSWi9WndtZSyj+j/TQBgINTZ3jICItIqpdJTa+beAYhbPLq5vd5PiKsQwF0HxW497QZcBPTEb/9WbyWQymfXkCzx4zn+rdofCAAAAAElFTkSuQmCC'
        shot['icon_bin_new'] = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAJ2AAACdgBx6C5rQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAASdEVYdFRpdGxlAE5ldyBEb2N1bWVudByQzcsAAAAUdEVYdEF1dGhvcgBKYWt1YiBTdGVpbmVy5vv3LwAAACF0RVh0U291cmNlAGh0dHA6Ly9qaW1tYWMubXVzaWNoYWxsLmN6aWbjXgAAAFh0RVh0Q29weXJpZ2h0AENDMCBQdWJsaWMgRG9tYWluIERlZGljYXRpb24gaHR0cDovL2NyZWF0aXZlY29tbW9ucy5vcmcvcHVibGljZG9tYWluL3plcm8vMS4wL8bjvfkAAAPkSURBVFiFtZffbuNEFMZ/Z8Z2bXfbkP3TbLnoghCCC0D0eu94AMQD8Rq8QZ+g7wA3qBKUvwK22q26qOmftGnSJI09c7hI000TO04W+KSRR3E83zffmXOOLfxPUCUB1uknEUl/CFyJ0J/+n/znxC1qROH7EDVQqSEmRH2GaBuGTVazAxGuSgXs7Ox8s7W19ZUxRowxt7tRVBXnHN77u6uq4r2/G1F4ah6kr8I0ObXxyqWNgoGI5JI70eHNim+env/8xfNvv0YGv8oDjgGCaQGbm5tfbm9vvzsYDFBVgiDAez9SK4KqIjJrnHBFYPax0sJKCyMZQgeRHCUEiYmT9HNs/CkOVAc9Ea5mBAAyHA7pdrs454jjGOfcnYCiK0Bo/kCCA4x9gQQvMaaDyAYQMwr939TX8wCNPsZoj2vXguyHGQGq+kaJyD2yMgFCH2tbBPaMwJ5gbRcxH4HZQmQN1Q6ihyTpjxaC9/B5E4kOVbOkVMCYcHoUCTB0sOYaY7oY00bkyYjcfAKygXACXjDmGGg+QWwdlRrXrJsiAUWE0/PJYaxDxCGSI2QgMSLrIA0keA40gAdAAioxIhFiQkwSzThQFO+qUECISAiEIBHoALQDeoLm34E2gS4wAPQG1SHqM3x/WBiCst0Wxl8EpIayhuoaXmsYTlD/apTjsgZ0wB/i/THgThF3AdpmtSALJlNukd2PrinKYzwbeL3A+z7G/Im6C5B45Ahn9HuhS8L8JeJew7ApQr/QAVWl1+uRJMnd71VOeJ7h9QrnR9XW0kS4RGiN6gBPuWj33MN3fvsdvTlgNTuAgkI0DkGapowr4WLnoIbnQwQBTVH3EJHbQqQBIjVal6+zD54NfoLBL+NyXJqGxhi896XkRU4oT3GkqNZQOUe0A5qjarFBndNzk7M6+H6yF8wIyPN8hmReGIqd+Aylj0gHdDgKgdY5v2znk+SFAsaHsIh0ESfeIEU1HbmKggT3qmypgHmVcBEnylB2v9KB6UWq0nMeFnJg3OfLCMvcGM+XFTDTC5xziAhHR0eFD0wTLzrKUHoGGo0GQXD/dlWHXCQM05hxYHwGoii6c6Nq8ZnuaMzC4ip7wTws6sS8UM59I6oinido0XULD+G/wbwqWoS3cmAeln2+8I2oapGyV/NpEePWvswZsN57mVykimQZqOqM6kkBdeBRlmWBtZYoivDeY62dm1bL9AHnnAW2gDOgNynAACtAur+//2J3dze11qKqUpX/RfOizQO6t7f3F5DccvXg/rdhBDwC1uv1+mNrbaiqM1nyNjDG5M65rNVqnQBt4PxWVOnXsQHsnPvLwk+Me/gHOHDkjx+6e6QAAAAASUVORK5CYII='
        
        # Messages/popups
        shot['icon_error'] = b'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'
        
        # Logo for SHOT
        shot['logo_image'] = b'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'
#        shot['logo_image_2'] = b'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'
        shot['icon_logo'] = b'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'
    except:
        print('Error: shot dict not set. NameError will commence')




# Read config
if shot_config_file.is_file():
    print(f'Reading {shot_config_file}')
    shot['is_configured'] = read_config_from(shot_config_file)
else:
    # A session turns into a configured session once the user saves a file ..
    # Once a user saves a file, a settings.ini is created.
    shot['is_configured'] = False

if shot['is_configured']:
    print('Running SHOT in configured mode.')
else:
    print('Running SHOT in unconfigured mode.')
    shot['conf_user'] = None
    shot['conf_lang'] = default_language_setting
    shot['conf_uniq'] = 'FNR'
    shot['conf_hosp'] = None
    shot['conf_recent'] = None


# Set GUI dependining on config (if any)
#set_gui_strings('Norwegian')
set_gui_strings(shot['conf_lang'])
set_gui_icons()




def popup_language():
    change_lang_win = [
                    [sg.T(shot['settings_language'])],
                    [sg.Combo(shot['available_languages'], default_value=shot['settings_language_set'])],
                    [sg.Button(shot['settings_language_change'])]
                    ]
    
    
    do_change_language = sg.popup_yes_no(f"{ shot['settings_language_str']}: {shot['settings_language_set']}\n{shot['settings_language_change']}?", title=shot['settings_language'], auto_close=False)
    if do_change_language == 'Yes': # TODO, change to language-button
        lang_win= sg.Window(shot['settings_language'], layout=change_lang_win, margins=(2, 2), resizable=True, return_keyboard_events=True)
        lang_win.read(timeout=1)
        while True:             # Event Loop
            lang_event, lang_values = lang_win.read()
#            print(f"lang_event={lang_event}, lang_values={lang_values}") # use for debugging (remove when finished)
            if lang_event is None:
                break
            elif str(lang_event) == shot['settings_language_change']: # if event is "Change language" 
#                print(f"change language to {lang_values[0]}")
                print(f"lang set: {shot['settings_language_set']}")
                set_gui_strings(lang_values[0])
                print(f"lang set: {shot['settings_language_set']}")
#                popup_language
                break
        lang_win.close()




#        sg.PopupQuick(f"{ shot['settings_language_str']}: {shot['settings_language_set']}\n\n{language_list}", title=shot['settings_language'], auto_close=False)
        
    







#file_new: str = 'New............(CTRL+N)'


# WORKAROUND
# TODO fix these color stuff
COLOR_SYSTEM_DEFAULT = '#CCCCCC' # workaround
icon_bkg = '#FFFFFF' # workaround
#icon_bkg = sg.theme_background_color()

assert icon_bkg is not None, 'icon_bkg variable set to None (must not happen)'
# assert icon_bkg == COLOR_SYSTEM_DEFAULT, 'icon_bkg variable set to system default (must not happen)'

# WORKAROUND ^ 



# Setup top menu
# Using string variables allows for easier translations

menu_layout = [
               [shot['file_file'], [shot['file_new'], shot['file_open'], shot['file_save'], shot['file_save_as'], shot['file_close'], shot['file_import'], shot['file_export_sheet'], shot['file_export_image'], shot['file_print'], shot['file_exit']]],
               [shot['stats_stats'], [shot['stats_epicurve'], shot['stats_gchart'], shot['stats_compare'], shot['stats_filtering']]],
               [shot['settings_settings'], [shot['settings_encryption'], shot['settings_hospital'], [shot['settings_hospital_manage'], shot['settings_hospital_rooms']], shot['settings_language']]],
               [shot['help_help'], [shot['help_help_help'], shot['help_online'], shot['help_license'], shot['help_participate'], shot['help_about']]]
               ]



# menu_layout = [
               # [file_file, [file_new, file_open, file_save, file_save_as, file_import, file_export_sheet, file_export_image, file_print, file_exit]],
               # [stats_stats, [stats_epicurve, stats_compare, stats_filtering]],
               # [settings_settings, [settings_encryption, settings_hospital, [settings_hospital_manage, settings_hospital_rooms], settings_language]],
               # [help_help, [help_help_help, help_online, help_license, help_participate, help_about]]
               # ]
menu_menu = [sg.Menu(menu_layout)]

# Setup sub menu (icons)
# Using base64 encoded PNG files (32x32 px)
# menu_icons = [ sg.Button('', image_data=shot['icon_bin_new'], button_color=(icon_bkg,icon_bkg), border_width=0, key=shot['icon_key_new']),
               # sg.Button('', image_data=shot['icon_bin_open'], button_color=(icon_bkg,icon_bkg), border_width=0, key=shot['icon_key_open']),
               # sg.Button('', image_data=shot['icon_bin_save'], button_color=(icon_bkg,icon_bkg), border_width=0, key=shot['icon_key_save']),
               # sg.Button('', image_data=shot['icon_bin_list'], button_color=(icon_bkg,icon_bkg), border_width=0, key=shot['icon_key_list']),
               # sg.Button('', image_data=shot['icon_bin_plot'], button_color=(icon_bkg,icon_bkg), border_width=0, key=shot['icon_key_plot']),
               # sg.Button('', image_data=shot['icon_bin_image'], button_color=(icon_bkg,icon_bkg), border_width=0, key=shot['icon_key_image']),
               # sg.Button('', image_data=shot['icon_bin_print'], button_color=(icon_bkg,icon_bkg), border_width=0, key=shot['icon_key_print'])
             # ]

menu_icons = [ sg.Button('', image_data=shot['icon_bin_new'], border_width=0, key=shot['icon_key_new']),
               sg.Button('', image_data=shot['icon_bin_open'], border_width=0, key=shot['icon_key_open']),
               sg.Button('', image_data=shot['icon_bin_save'], border_width=0, key=shot['icon_key_save']),
               sg.Button('', image_data=shot['icon_bin_list'], border_width=0, key=shot['icon_key_list']),
               sg.Button('', image_data=shot['icon_bin_plot'], border_width=0, key=shot['icon_key_plot']),
               sg.Button('', image_data=shot['icon_bin_image'], border_width=0, key=shot['icon_key_image']),
               sg.Button('', image_data=shot['icon_bin_print'], border_width=0, key=shot['icon_key_print'])
             ]
    

# Setup tabs
# These are the focus windows' layouts

#expand(expand_x=False,
#    expand_y=False,
#    expand_row=True)


# dummy data
# idea: __dict__ read from shelve file + dict read from csv file(s)
tab_outbreak_intro = 'Outbreak Overview'
outbreak_info = {}
outbreak_info['created'] = '2020-05-09' # dummy
outbreak_info['outbreak began'] = '2020-05-01' # dummy
outbreak_info['outbreak ended'] = 'N/A' # dummy
outbreak_info['type'] = 'influenza typeB' # dummy


outbreak_info['basename'] = f"{outbreak_info['outbreak began']}_{outbreak_info['type']}"
outbreak_info['outbreak'] = f"{outbreak_info['type']} outbreak {outbreak_info['outbreak began']}"
outbreak_info['filename'] = f"{outbreak_info['basename']}.out"
outbreak_info['datafile'] = f"{outbreak_info['basename']}.csv"


# TODO swap columns with table
# It can specify "layout" like old html tables

# Column layout - create outbreak
add_outbreak_cols = '' # TODO use sg.Input instead of sg.Text on col2
#                     [sg.Text('Date:'), sg.Input('col input 2')],
#                     [sg.Text('Type:'), sg.Input('col input 3')],

# Column layout - show outbreak info
tab_outbreak_overview = [[sg.Text(tab_outbreak_intro)],
                        [sg.Text(' ')]] #spacer

for idx, info_type in enumerate(outbreak_info):
    tab_outbreak_overview.append([sg.Text(str(info_type.capitalize()+':')), sg.Text(outbreak_info[info_type])])


# OBSOLETED
    #tab_outbreak_overview = [[sg.Text(tab_outbreak_intro)],
    #                         [sg.Text(' ')], #spacer
     #                        [sg.Text('Outbreak:'), sg.T(outbreak_inf)],
    #                         [sg.Text('Status:'), 
    #                         [sg.Text('Date:'), sg.Input('col input 2')],
    #                         [sg.Text('Type:'), sg.Input('col input 3')],
    #                         [sg.Text(''), sg.Input('col input 4')],
    #                         [sg.Text(' ')], # spacer
    #                         [sg.Text('Infected:'), sg.Input('col input 5')],
     #                        [sg.Text('col Row 7'), sg.Input('col input 6')]
      #                      ]
# OBSOLETED




### OBSOLETE
    # Create default (mostly empty and invisible) tabs
    # legend: name, frame_title, tooltip, content type, default visibility
### OBSOLETE


# Testing new idea:
shot['tab'] = {}
shot['tab']['title'] = {}
shot['tab']['tip'] = {}
shot['tab']['show'] = {}
shot['tab']['contents'] = {}

shot['tab']['title']['welcome'] = shot['tab_welcome']
shot['tab']['tip']['welcome'] = shot['tip_welcome']
shot['tab']['show']['welcome'] = True


shot['tab']['title']['overview'] = shot['tab_overview']
shot['tab']['tip']['overview'] = shot['tip_overview']
shot['tab']['show']['overview'] = True


shot['tab']['title']['epicurve'] = shot['tab_epicurve']
shot['tab']['tip']['epicurve']= shot['tip_epicurve']
shot['tab']['show']['epicurve'] = False

shot['tab']['title']['linelist'] = shot['tab_linelist']
shot['tab']['tip']['linelist'] = shot['tip_linelist']
shot['tab']['show']['linelist'] = True

shot['tab']['title']['events'] = shot['tab_events']
shot['tab']['tip']['events']= shot['tip_events']
shot['tab']['show']['events'] = False


shot['tab']['title']['g-chart'] = shot['tab_g-chart']
shot['tab']['tip']['g-chart'] = shot['tip_g-chart']
shot['tab']['show']['g-chart'] = True


#tab_welcome_contents = print(tab_welcome)
#tab_welcome_tooltip = tab_welcome.tooltip()

#tab_outbreak_title = 'Outbreak'
#tab_outbreak_tip = 'Outbreak Overview'
#tab_outbreak =
#tab_outbreak = tab_outbreak_overview
#tab_overview = tab_outbreak

# Uses dummy data from for-loop construction above:
shot['tab']['contents']['overview'] = tab_outbreak_overview


#tab_linelist_title = 'Linelist'
#tab_linelist_tip = 'View or add cases to the linelist'
#tab_linelist = [[sg.T('Linelist')], [sg.In(key='LIST_in')]]

# Dummy contents for tabs here
shot['tab']['contents']['linelist'] = [[sg.T('Linelist')], [sg.In(key='LIST_in')]]

shot['tab']['contents']['g-chart'] = [[sg.T('G-chart')], [sg.In(key='GCHART_in')]]

shot['tab']['contents']['epicurve'] = [[sg.T('Epicurve')], [sg.In(key='EPI_in')]]

shot['tab']['contents']['events'] = [[sg.T('Events')], [sg.In(key='EVE_in')]]

#shot['tab']['contents']['welcome'] = [[sg.T(shot['tab']['tip']['welcome'])],
#                                       [sg.T('Creating a new or opening an existing outbreak file is required in order to proceed.')],
#                                       [sg.T(' ')],
#                                       [sg.Button('This is a button', image_data=shot['icon_bin_new'])],
#                                       [sg.T(' ')],
#                                       [sg.Button('', image_data=shot['icon_bin_new'], button_color=(icon_bkg,icon_bkg), border_width=0, key=shot['icon_key_new']), sg.T(shot['icon_new_str'], font=("Helvetica", 16))],
#                                       [sg.T(' ')],
#                                       [sg.Button('', image_data=shot['icon_bin_open'], button_color=(icon_bkg,icon_bkg), border_width=0, key=shot['icon_key_open']), sg.T(shot['icon_open_str'], font=("Helvetica", 16))]
#                                       ]

# TEST
shot['tab']['contents']['welcome'] = tab_welcome(outbreak_filename)
# TEST


# font=("Helvetica", 25)

# Attempt at table below


#tab_epicurve_title = 'Epicurve'
#tab_epicurve_tip = 'Plot the data from the linelist'
#tab_epicurve = 



# Testing:

menu_tabs = [sg.TabGroup(          # line 3..n
            [
                [
                sg.Tab(shot['tab']['title']['welcome'],  shot['tab']['contents']['welcome'],  key=shot['tab']['title']['welcome'],  tooltip=shot['tab']['tip']['welcome'],  visible=shot['tab']['show']['welcome'], pad=(2,2)),
                sg.Tab(shot['tab']['title']['overview'], shot['tab']['contents']['overview'], key=shot['tab']['title']['overview'], tooltip=shot['tab']['tip']['overview'], visible=shot['tab']['show']['overview']),
                sg.Tab(shot['tab']['title']['linelist'], shot['tab']['contents']['linelist'], key=shot['tab']['title']['linelist'], tooltip=shot['tab']['tip']['linelist'], visible=shot['tab']['show']['linelist']),
                sg.Tab(shot['tab']['title']['events'],   shot['tab']['contents']['events'],   key=shot['tab']['title']['events'],   tooltip=shot['tab']['tip']['events'],   visible=shot['tab']['show']['events']),
                sg.Tab(shot['tab']['title']['g-chart'],  shot['tab']['contents']['g-chart'],  key=shot['tab']['title']['g-chart'],  tooltip=shot['tab']['tip']['g-chart'],  visible=shot['tab']['show']['g-chart']),
                sg.Tab(shot['tab']['title']['epicurve'], shot['tab']['contents']['epicurve'], key=shot['tab']['title']['epicurve'], tooltip=shot['tab']['tip']['epicurve'], visible=shot['tab']['show']['epicurve'])
                ]
            ]
            )
            ]




text_size_cols = 90
text_size_rows = 25

status_message = None # Will display 'Ready' string at bootup
menu_status = [sg.StatusBar(get_status_line(), relief='flat')]



# Build Main window from blocks above
layout = [
        menu_menu,  # line 1
        menu_icons, # line 2
#        [sg.Text(' ')], # empty line
        menu_tabs,  # line 3...n
#        [sg.Text(' ')], # empty line
        menu_status # line -1
        ]



# TODO
# We need to move window creation to a function, in order to destroy and re-start window upon change of language


# Set window properties
# Get title from file name
if outbreak_filename is None:
    gui_window_title = 'Simple Hospital Outbreak Tracker'
else:
    gui_window_title = f'{outbreak_filename} - Simple Hospital Outbreak Tracker'

gui_window_title_set = gui_window_title

# Get screen size and determine sane dimensons
screen_width, screen_height = sg.Window.get_screen_size()
window_width = screen_width//3
window_height = int(screen_height/1.5)

window = sg.Window(gui_window_title, layout=layout, margins=(0, 0), size=(window_width,window_height), resizable=True, return_keyboard_events=True)
window.read(timeout=1)
#window.maximize()
#window['_BODY_'].expand(expand_x=True, expand_y=True)


# Expand one of the tabs for great justice
#window.FindElement(shot['tab']['title']['welcome']).expand(expand_y=True)


# FOR STATUS MESSAGE SEE THIS: Updating elements in active window
# https://pysimplegui.readthedocs.io/en/latest/#updating-elements-changing-elements-values-in-an-active-window


# FOR ini filer (se eksempelvis shot.ini)
# https://docs.python.org/3/library/configparser.html


# TODO if __name__ == '__main__' all of the runtime stuff

# TODO rewrite event conditionals to use this format:
#  if sect in ('OPTIONS', 'RECENT'):


while True:             # Event Loop
    if outbreak_filename is None:
        for tab_keys in shot['tab']['title'].keys():
            if tab_keys == 'welcome': continue
            window.FindElement(shot['tab']['title'][str(tab_keys)]).Update(disabled=True)
        
        # Empty welcome tab info bars (file and username strings)
        window['welcome_tab_file_loaded_infobar'].update(shot['msg_no_file_loaded'])
        window['welcome_tab_file_loaded_ok'].update(f"{shot['msg_no_file_loaded']} {shot['msg_no_file_tip']}")
        window['welcome_tab_username_infokey'].update(' ' * (len(shot['msg_user']) + 3 )) # blank space to write over
        window['welcome_tab_username_infoval'].update(' ' * (len('shot[username] here'))) # blank space to write over
        
        # Set <empty> window title string
        gui_window_title = 'Simple Hospital Outbreak Tracker'

                
    else:
        for tab_keys in shot['tab']['title'].keys():
            if tab_keys == 'welcome': continue
            # TODO check if num cases >2 for graphical plots (otherwise, it's a chore)
            # If there is 0-1 data record(s), show/activate linelist
            window.FindElement(shot['tab']['title'][str(tab_keys)]).Update(disabled=False)

        # Set window title string
        gui_window_title = f'{Path(outbreak_filename).name} - Simple Hospital Outbreak Tracker'
    
    
    # Set window title
    # TODO think this is tkinter only
    if gui_window_title != gui_window_title_set:
        window.TKroot.title(gui_window_title) # Might give errors on non-tkinter
        gui_window_title_set = gui_window_title
    
    event, values = window.read()
    #print(event, values) # use for debugging (remove when finished)
    
    print(f'event is:   {event}')
    print(f'values are: {values}')
    
    if event in (None, 'Exit', shot['file_exit']):
        break
    elif event in shot['settings_language']:
        popup_language()
    elif event in shot['stats_epicurve']:
        shot['tab']['show']['epicurve'] = True # TODO live update
    elif event in shot['icon_key_print'] or event in shot['file_print']:
        print('Changing status_message')
        window.Finalize()
        status_message = 'Printing ..'
    elif event in shot['file_new'] or event in f"-{shot['icon_key_new']}-" or event in shot['icon_key_new']:
        
        
        
        popup_some_error('File-> New not implemented yet.')
        outbreak_filename = None
    
    elif event in shot['file_close']:
        # todo
        popup_some_error('Will prompt user to save if changes were made, then re-set and file = None')
        outbreak_filename = None
        
    elif event in shot['file_open'] or event in f"-{shot['icon_key_open']}-" or event in shot['icon_key_open']:
        
        if outbreak_filename is not None:
            # TODO check if changes have been made to open file
            # if so, prompt to save these to file
            # if no changes, just close the file.
            pass
        
        if popup_open_outbreak_file():
            window['welcome_tab_file_loaded_infobar'].update(str(outbreak_filename))
            window['welcome_tab_file_loaded_ok'].update(shot['msg_file_loaded_ok'])
            window['welcome_tab_username_infokey'].update(shot['msg_user'])
            window['welcome_tab_username_infoval'].update('shot[username] here')
            

    
    # Required for status bar
    window.Finalize()
    
    # Update status bar string
    if status_message is None: status_message = event
    if outbreak_filename is None:
        menu_status[0].Update(value=get_status_line(s=event))
    else:
        menu_status[0].Update(value=get_status_line(s=event, f=outbreak_filename))
    

window.close()












