<h1 align="center">Jamf in a Shell</h1>
<h2 align="center">A Command Line Utility for the Jamf API</h2>

Created by: Chris Riendeau\
First Build: March 2022

<h3 align="center">About:</h3>
    This utility uses the Jamf Pro and Jamf Classic APIs to retrieve data from a Jamf instance. It combines cross referencing features that have been out there on MacAdmins and elsewhere. With great respect for those who came before me and created those scripts, I'm trying to put all of these in one place with some kind of user interface. Search scripts by string, find all polices with a certain group in scope, etc. It also allows simple searches for computers, and can pull basic information. The idea is that it can be expanded to add functionalities not available in the Jamf Pro GUI online, or not available to Jamf Pro Cloud users, who can't do database queries on a local instance.


<h3 align="center">Authentication:</h3>
    Jamf in a Shell uses bearer token authentication, since that is required for the Pro API, and also works with Classic API.

   Two options for authentication. You can comment out the "jamfcreds" lines and uncomment the prompts to use an interactive prompt. Or you can do the opposite. If you go with the non-prompt route, you'll need to make your own "jamfcreds.py" to store your credentials. The line "import jamfcreds" is just pulling username and password for a read-only Jamf Pro user account from that local file, to avoid having to type in username/password. This is a .py file in a place in the python3 path (e.g. /usr/local/lib/python3.9/site-packages) with two variables declared, for username and password. It is plaintext, but if you utilize any non-read-only functionalities in the future as they get added, it may be worth hashing/encoding in some way. Handle your passwords how you like! Be safe.
   
   Currently there is no ongoing check for token validity, so if you remain in the program for too long, it may end up erroring out if the token expires. An ongoing check/renewal (maybe with a prompt) may be added in the future.


<h3 align="center">Commands:</h3>
    Each command will print a prompt for further input. These don't work like some BASH-style script commands where you enter the command and the argument in one line. So for example you cannot type "info 210" and expect info for JSS ID 210. You type info, press enter/return, then are prompted for the JSS ID.
+ Computer Search by Name ("search"):\
    Will search computers by name based on the string you input. Returns a list of computers with that string in their name, alongside their JSS ID. Possible future feature will be to search for name and/or serial number matches in this function, but currently just looks at the 'name' field.

+ Policy Search by Name ("policy-search"):
    Similar to the computer search, this will return all policies with the queried string in their name, alongside their ID numbers.

+ Group Search by Name ("group-search"):
    Similar to the computer search, this will return all groups with the queried string in their name, alongside their ID numbers.

+ Computer Search by Asset Tag ("asset-search"):
    Searches for computers by the Asset Tag and outputs Computer Name and JSS ID.

+ Basic Computer Information ("info"):
    Pulls basic information about a computer by its JSS ID. Will print: Computer Name, Asset Tag, User, IP Address, and Last Check-In. Will prompt to output more detailed information about the computer via a set of sub-commands.
    Computer Info Sub-commands:
        Extension Attributes ("ext"): Prints list of all extension attributes and their values.
        Hardware Information ("hardware"): Prints hardware information such as Make, Model, Processor, MAC Address, Serial Number, etc.
        Group Membership ("groups"): Prints list of all groups in which the computer is a member.
        Return Home ("home"): Exits the computer information sub-command process and returns to the     initial Jamf in a Shell command prompt.
+ Search for all Policies Scoped to a Group ("group-policy"):
    This will list all policies scoped to a particular group. It requires the Group ID number for the group in question, which can be retrieved via the Group Search by Name function. Notably missing from the Jamf Pro GUI, the ability to see what policies are scoped to a group is super useful. This will prompt you to ouput the results list to a file if you wish, a simple 2 column CSV with policy ID numbers and policy names.
+ Search for all Configuration Profiles Scoped to a Group ("group-config"):
    This will list all configuration profiles scoped to a particular group. It requires the Group ID number for the group in question, which can be retrieved via the Group Search by Name function. Basically the same as the group-policy function, but with config profiles. Outputs to csv if you want, with ID numbers and config profile names.
+ Search all Scripts by String ("script-string"):
    Will search all scripts in your Jamf Pro instance for a particular string. Spaces and special characters should be fine, but best to avoid any quotation marks or escape characters in the search field (there is not any checking/error handling for that kind of thing yet). Outputs list of Scripts that have that string in the body of the script. Prompts to output results list to file if you wish.
+ Get App Usage for an Application by Group ("group-app-usage"):
    Will total app usage for all computers in a group for a particular application in a given date range. Inputs are the Group ID, start and end dates (YYYY-MM-DD format), and a string for the application name. Partial strings will come up with matches, so this can save you some time if you just search 'Chrome' instead of 'Google Chrome.app', but be warned that if you search 'Adobe' it will return results for all apps with Adobe in the name, so more specificity will lead to more accuracy. Outputs total usage across all computers in minutes, by day, so you can chart daily usage, or just sum the total in a spreadsheet.
+ List all Groups ("group-list"):
    Prints list of all Group names and ID numbers.
+ List all Policies ("policy-list"):
    Prints list of all Policies and their ID numbers. Can be pretty long, you're likely better served by using policy-search.
+ Write to File:\
    This is not a specific command, but a prompt that appears for certain functions, so you can output your results to a file and not have to copy/paste from the shell. You will need to type in a valid directory path and a file name as one entry, for example: /users/username/Documents/testfile.txt. It will check if the directory is valid, but does not check filetype. Currently outputting tabulated text files, but hope to change that to csv in the near future.
+ Help ("help"):
    It isn't that helpful, but it does print the list of commands!



