# HandBrake Video Conversion & File Archiving Scripts

This project includes two shell scripts for automated video processing:

- `handbrake_convert.sh`: Converts videos using HandBrakeCLI.
- `move_vids.sh`: Moves processed videos into an archive directory to prevent conflicts with AWS DataSync.

## Full Setup & Usage Instructions

### Make Both Scripts Executable

`chmod +x /path_to_script/handbrake_convert.sh`
`chmod +x /path_to_script/move_vids.sh`

## To run the `handbrake_convert.sh` script follow these steps

1. Ensure the source and destination directory are created and entered into the script based on the paths listed in the SOURCE and DESTINATION variables for your working directories

2. The script can be ran with nohup to keep it running in the background 
	If coreutils is missing it must be installed for nohup 
		Command: `sudo dnf install coreutils -y`

3. Then simply run it in the terminal CLI 
	Command: `nohup /path_to_script/handbrake_convert.sh`

4. To stop the process: `pkill -f handbrake_convert.sh`

## To run the `move.sh` script so files are moved into the archived directory to avoid conflicts with AWS DataSync

1. Ensure the source and destination directory are created and entered into the script based on the paths listed in the SOURCE and DESTINATION variables for your working directories

2. Add to crontab
	Command: `crontab -e`

3. Runs at midnight but script above moves every other night
	Command to add to crontab: `0 0 * * *  /path_to_script/move_vids.sh`
