from pathlib import Path
import shutil
from subprocess import run
import tempfile
import multiprocessing as mp
from itertools import repeat
import time


# def copy_png_files(source_dir, destination_dir, print_message = False):
#     source_path = Path(source_dir)
#     destination_path = Path(destination_dir)

#     # Ensure the source directory exists
#     if not source_path.is_dir():
#         print(f"Source directory '{source_dir}' does not exist.")
#         return

#     # Ensure the destination directory exists
#     if not destination_path.exists():
#         destination_path.mkdir(parents=True, exist_ok=True)

#     # Recursively search for jpg files and copy them
#     for image_file in source_path.glob("**/*.png"):
#         destination_file = destination_path / image_file.name
#         shutil.copy(image_file, destination_file)
#         if print_message: print(f"Copied '{image_file}' to '{destination_file}'")
def copy_png_files(image_file, destination_dir):
    destination_file = Path(destination_dir) / image_file.name
    if not destination_file.is_file():
    	shutil.copy(image_file, destination_file)


# source_directory = "/path/to/source/directory"
# destination_directory = "/path/to/destination/directory"
# copy_jpg_files(source_directory, destination_directory)




if __name__ == "__main__":
	# Set variables. 
	# Assume running from SMW home directory, also the home of the mount points
	raw_bucket = "amlr-imagery-raw-dev" #"amlr-gliders-imagery-raw-dev"
	proc_bucket = "amlr-gliders-imagery-proc-dev"
	segemnt_str = "/opt/Threshold-MSER/build/segment"
	numcores = mp.cpu_count()

	raw_mount = Path("/home/sam_woodman_noaa_gov").joinpath(raw_bucket)
	proc_mount = Path("/home/sam_woodman_noaa_gov").joinpath(proc_bucket)

	# Make directories, if necessary, and mount
	if not raw_mount.exists():
		raw_mount.mkdir(parents=True, exist_ok=True)
	if not proc_mount.exists():
		proc_mount.mkdir(parents=True, exist_ok=True)

	run(["gcsfuse", "--implicit-dirs", "-o", "ro", raw_bucket, str(raw_mount)])
	run(["gcsfuse", "--implicit-dirs", proc_bucket, str(proc_mount)])

	# Generate list of Directories to segment
	dir_list = ['Dir0048', 'Dir0049', 'Dir0050', 'Dir0051', 'Dir0052', 
             'Dir0053', 'Dir0054', 'Dir0055', 'Dir0056']

	segement_file = Path(segemnt_str)

	raw_path  = raw_mount.joinpath("gliders/2022/amlr08-20220513/shadowgraph/images")
	proc_path = proc_mount.joinpath("SANDIEGO/2022/amlr08-20220513/regions-mser")

	print(f"Path to segment file: {segement_file}")
	print(f"Path to raw (in) directories: {raw_path}")
	print(f"Path to proc (out) directories: {proc_path}")

	print(f"Start time of it all: {time.strftime('%Y-%m-%d %H:%M:%S')}")
	if segement_file.is_file():
		for i in dir_list:
			start_time = time.time()
			print(f"Segmenting images in directory {i}, " + 
         			f"start time {time.strftime('%Y-%m-%d %H:%M:%S')}")
   
			with tempfile.TemporaryDirectory() as temp_dir:
				# Run segmentation tool
				print(f"Running segment, and writing files to {temp_dir}")
				run([segemnt_str, "-i", str(raw_path.joinpath(i)), "-o", temp_dir])
				print(f"Segmentation took {(time.time()-start_time)*60} minutes")

				# Copy images to destination directory, in parallel
				destination_path = proc_path.joinpath(i)
				if not destination_path.exists():
					destination_path.mkdir(parents=True, exist_ok=True)
        
				print(f"Copying segmented region images from {temp_dir} " + 
          				f"to {destination_path}, using {numcores} cores")
				with mp.Pool(numcores) as pool: 
					pool.starmap(copy_png_files, zip(Path(temp_dir).glob("**/*.png"), repeat(destination_path)))

				# TODO: extract CSV files
				# print(f"Copying measurement ")
			print(f"Time is {time.strftime('%Y-%m-%d %H:%M:%S')}")
			print(f"All told, this directory took {(time.time()-start_time)*60} minutes")

	else:
		print("error, segment file does not exist")
	
	print("Unmounting buckets")
	run(["fusermount", "-u", str(raw_mount)])
	run(["fusermount", "-u", str(proc_mount)])

	print("Script complete")


# cd /opt/Threshold-MSER && git pull && cd ~/
# sudo chmod -R 755 /opt/Threshold-MSER/python
# python3 /opt/Threshold-MSER/python/segment.py
