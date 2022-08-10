# Family Budget Overview Tool
The purpose of this tool is to gather manual inputs, process them, and display various statistical reports.

# How to start
Just run `python3 fbot.py` in fbot directory. You should see this:

    ...
               Family Budget Overview Tool v1.1 Beta          
         This project is created by Juraj Honsch (c) 2022     
    
    08/10/2022 08:11:44 PM - INFO: Opening browser at http://127.0.0.1:8080/
    08/10/2022 08:11:44 PM - INFO: Serving on http://127.0.0.1:8080
That opens your default browser by default.
[![Fbot Main Image](fbot_main "Fbot Main Image")](fbot_main.png "Fbot Main Image")

# Configuration
Navigate to `_config` directory and edit `config.toml` file.

# Database
All data are saved in `_config/database.db` (by default) file using pythons sqlite3 library.

# Advenced settings
If you want to do some advenced things with database, you can use `terminal.py`. Functions:
* Change category
	When you rename a category in config file you just changed displaying categories, but some data are saved as old category name. Use this function to rename category in database and prevent future errors.
* Create structure
	Creates structure for specified database file.

# Credits
* Graphjs - MIT License
* Ubuntu Fonts - [Ubuntu Font License](http://font.ubuntu.com/ufl/ "Ubuntu Font License")
* Material Icons Font - Apache 2.0 License

# License
This project is release under GNU General Public License v3.0.
