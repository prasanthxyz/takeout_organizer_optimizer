# Takeout Organizer and Optimizer

## How to run?
0. Install dependency: `ffmpeg`
1. Clone the repo, cd to it, create a virtual environment, and install pip requirements  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the command:
   ```bash
   python -m takeout_organizer optimize --input-dir='INPUT_DIR' --output-dir='OUTPUT_DIR'
   ```  
   Optionally, pass in the argument `--delete-original-files`
