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
[![Fbot Main Image](fbot_main "Fbot Main Image")](fbot_main.png?raw=true "Fbot Main Image")

# Configuration
Navigate to `_config` directory and edit `config.toml` file.

# Database
All data are saved in `_config/database.db` (by default) file using pythons sqlite3 library.

# Advanced settings
If you want to do some advanced operations with database, you can use `terminal.py`. Functions:
* Change category
	When you rename a category in config file you just change the list of displayed categories in the user interface (dropdown list), but some data records are still saved with old category name. Use this function to rename category in database records and prevent future errors.
* Create structure
	Creates structure for specified database file.

# Credits
* Graphjs - MIT License
* Ubuntu Fonts - [Ubuntu Font License](http://font.ubuntu.com/ufl/ "Ubuntu Font License")
* Material Icons Font - Apache 2.0 License

# License
This project is released under GNU General Public License v3.0.
