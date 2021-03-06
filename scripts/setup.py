#!/usr/bin/python3

import os,sys

abspath = os.path.dirname(os.path.abspath(__file__)) 

def write_cronjob(ticker,type):
	'''
	Writes a cronjob that executes price_scrape.py and saves the data
	to the ticker's corrseponding file
	param ticker: string - ticker
	param type: string - 'stocks' or 'crypto'
	'''
	#create sting that indicates time
	time = '* * * * *'
	if type == 'stocks':
		time = '* 14-21 * * 1-5'
	#create strng that indicates output file
	path = os.path.abspath(__file__)
	outfile = f'{abspath}/../data/{type}_csvs/minute/m{ticker}.csv'
	errfile = f'{abspath}/../data/log/error.log'
	#combine into cmd
	cmd = f'{time} {abspath}/price_scrape.py {ticker} >> {outfile} 2>> {errfile}'
	#write command in crontab
	command = f'(crontab -l; echo "{cmd}") | sort - | uniq - | crontab -' #sort and uniq are added to ensure no duplicates
	#sys.stdout.write(command + '\n')
	#execute command
	os.system(command)

def write_reset_data(tickers):
	'''
	Creates and writes a bash script that will be used to clear
	data files.
	'''
	with open(f'{abspath}/reset_data.sh','w',encoding='utf-8') as file:
	#write shebang line
		file.write("#!/bin/bash\n")
	#write initial printf
		file.write('printf "" ')
		for ticker, type in tickers:
			path = f'{abspath}/../data/{type}_csvs/minute/m{ticker}.csv'
			file.write(f'> {path} ')


def write_rest(reset):
	'''
	Writes one by one the rest cron jobs.
	param reset: bool
	'''
	#time
	time = '0 * * * *'
	#write convert_data.py command
	errfile = f'{abspath}/../data/log/error.log'
	cmd1 = f'{abspath}/convert_data.py 2>> {errfile}'
	#write reset_data.sh command
	if reset:
		cmd2 = f'{abspath}/reset_data.sh 2>> {errfile}'
	else:
		cmd2 = 'false'
	#write final crontab command
	cmd = f'{time} {cmd1} ; {cmd2} ;'
	#write command in crontab
	command = f'(crontab -l; echo "{cmd}") | sort - | uniq - | crontab -' #sort and uniq are added to ensure no duplicates
	os.system(command)

def change_perms(reset):
	'''
	Changes permissions to all files that will need to be executed in crontab
	'''
	files = os.listdir(abspath)

	for file in files:
		os.system(f'sudo chmod +x {abspath}/{file}')

	sys.stdout.write('Successfully changed all permissions.\n')

def remove_placeholders():
	'''
	Removes placeholder files from the repo
	'''
	for dir1 in ['crypto_csvs','stocks_csvs']:
		for dir2 in ['minute','hour']:
			path = os.path.join(abspath,'..','data',dir1,dir2,'placeholder')
			if os.path.exists(path):
				os.remove(path)

def install_reqs():
	'''
	Installs required libraries by executing the requirements.sh file.
	'''
	os.system(f'sudo chmod +x {abspath}/requirements.sh')
	os.system(f'{abspath}/requirements.sh')

if __name__ == '__main__':
	#empty crontab
	if '-e' in sys.argv:
		os.system('echo "" | crontab -')

	#use sys.stdin to read input
	tickers = []
	for i in sys.stdin:
		#use regular expressions to get name of ticker and type
		ticker, type = i[:i.find(',')], i[i.find(',')+1:].strip()
		write_cronjob(ticker,type)
		tickers.append((ticker,type))

	#setup reset_data.sh
	if '-r' in sys.argv:
		write_reset_data(tickers)
		#change permissions for reset_data.sh
		os.system(f'sudo chmod +x {abspath}/reset_data.sh')
	#install required libraries
	if '-d' in sys.argv:
		install_reqs()

	write_rest('-r' in sys.argv)
	sys.stdout.write('Crontab setup complete.\n')
	change_perms('-r' in sys.argv)
	remove_placeholders()

