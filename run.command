#!/bin/bash

homebrew_check() {
	if ! which brew >/dev/null 2>&1; then
		echo 'Installing Homebrew...'
		echo 'You will be asked for your password'
		read -p 'Press <Enter> to continue'
		/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	fi
	if ! which brew >/dev/null 2>&1; then
		echo
		echo 'ERROR: Unable to install Homebrew'
		echo 'Please contact Justin <justinnhli@oxy.edu> for support'
		# FIXME make it obvious that an error has occurred
	fi
}

python_check() {
	if ! which python3 >/dev/null 2>&1; then
		echo 'Python not detected; installing...'
		homebrew_check && brew install python3
	fi
	if ! which python3 >/dev/null 2>&1; then
		echo
		echo 'ERROR: Unable to install Python'
		echo 'Please contact Justin <justinnhli@oxy.edu> for support'
		# FIXME make it obvious that an error has occurred
		exit 1
	fi
}

tesseract_check() {
	if ! which tesseract >/dev/null 2>&1; then
		echo 'tesseract not detected; installing...'
		homebrew_check && brew install tesseract
	fi
	if ! which tesseract >/dev/null 2>&1; then
		echo
		echo 'ERROR: Unable to install tesseract'
		echo 'Please contact Justin Li <justinnhli@oxy.edu> for support'
		# FIXME make it obvious that an error has occurred
		exit 1
	fi
}

git_check() {
	if ! which git >/dev/null 2>&1; then
		echo 'tesseract not detected; installing...'
		homebrew_check && brew install git
	fi
	if ! which git >/dev/null 2>&1; then
		echo
		echo 'ERROR: Unable to install git'
		echo 'Please contact Justin Li <justinnhli@oxy.edu> for support'
		# FIXME make it obvious that an error has occurred
		exit 1
	fi
}

pip_check() {
	if ! which pip3 >/dev/null 2>&1; then
		echo 'pip3 not detected; installing...'
		# FIXME
	fi
	if ! which pip3 >/dev/null 2>&1; then
		echo
		echo 'ERROR: Unable to install pip3'
		echo 'Please contact Justin Li <justinnhli@oxy.edu> for support'
		exit 1
	fi
	cat requirements.txt | sed 's/=.*//' | while read module; do
		if ! pip3 list 2>/dev/null | grep "$module" >/dev/null 2>&1; then
			pip3 install -r requirements.txt
			break
		fi
	done
}

# leave some space from the top
clear

# change to the current directory
cd "$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

# check that everything is installed
if ! ( tesseract_check && pip_check ); then
	# FIXME make it more obvious that an error has occurred
	echo
	echo 'AN ERROR HAS OCCURRED'
	echo 'Please copy the text in this window in your email to <justinnhli@oxy.edu>'
	echo
	read -p 'Press <Enter> to continue (and close this window)'
	exit
fi

# run the database updates
python3 database.py

# update the repository with the new database
git pull && \
	git add filecount.txt metadata.txt && \
	git add completed_text_files/*.txt && \
	git commit -m 'add more scanned files' && \
	git push

# ask the user to close the window
read -p 'Press <Enter> to close this window'
exit
