# Salesforce Scripts

## Usage

1. **Move application to your Users folder**

	Find out where you're at in the terminal. Eg. `C:\Users\harrylau>`. Drag and Drop this application folder to this folder. 

	After doing so, you should be able to see it when you type `ls` on Mac or `dir` on Windows.

	If you do not see this `salesforce-script` application folder, try going back 1 step with `cd ..` and see if you can find out where you are. 

	Once you `ls` or `dir` and see `salesforce-script` folder, `cd salesforce-script` to enter this folder directory in the terminal. 

2. **Install Python dependencies**

	You'll only need to do this the first time.

	```
	pip install -r requirements.txt
	```

	or if that didn't work, try this:

	```
	python -m pip install -r requirements.txt
	```

3. **Download ChromeDriver**

	Check your Chrome version in Chrome Settings. 

	Download ChromeDriver in that version in this link. [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)

	Move ChromeDriver to one level up from the application folder. 

	Eg. 
	`C:\Users\harrylau\salesforce-script>`: is the application folder
	`C:\Users\harrylau\`: is where we want to save the ChromeDriver

4. **Update secrets.txt**

	In main folder, open `secrets.txt` in the application folder and change the placeholder email and password. On the first line, input `True` if you need two-factor authentication, `False` if you don't.

5. **Run script**

	`cd salesforce-script` to enter the application folder. 

	Run following command:
	```
	python main.py
	```

	This will start the script. Other common commands you'll want to know: 

	- `Ctrl + c` or `Cmd + c`: Terminate application
	- `Ctrl + d` or `Cmd + d`: Exit application
	- `Ctrl + l` or `Cmd + l`: Clear the screen
	- `Ctrl + t` or `Cmd + t`: Open new tab
	- `cd sale + Tab`: `cd` is change directory (folder), you don't need to type out the folder name each time. You can click Tab after a few letters and terminal will auto complete.
	- `cd ..`: Going back one folder
	- `cd`: With nothing after, will return you to the main Users folder (where we placed the application folder and ChromeDriver to)

## Installing Python 

1. **Mac**

	Mac already has Python installed, try steps in **Usage** first. If it doesn't work try doing these steps in the terminal. 

	- Install xcode
	```
	xcode-select --install
	```

	- Install Homebrew
	```
	ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	```

	- Check you installed Homebrew successfully (you should see Homebrew X.X.XX - some version number)
	```
	brew --version
	```

	- Install python3
	```
	brew install python3
	```

	- Run the script following the steps in **Usage**. Replace `python` with `python3` in Step 2 and 5.

2. **Windows**
	
	To-do


## Category Assigments and CSV 'Uploads'

1. In your folder, open `csv` folder. You'll find `categories_XX` CSV files. These are the templates which you'll need to update. 

2. In category assignments, you can only categorize one site at a time. The script will ask you: `HK: Hong Kong JP: Japan UK: EMEA AU: AU/NZ`. This will determin the template file the script uses to run the program. 

3. You can run multiple Chromedriver windows at the same time. 
