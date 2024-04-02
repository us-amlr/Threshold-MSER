from pathlib import Path
import shutil
import subprocess
import tempfile


def copy_jpg_files(source_dir, destination_dir, print_message = False):
    source_path = Path(source_dir)
    destination_path = Path(destination_dir)

    # Ensure the source directory exists
    if not source_path.is_dir():
        print(f"Source directory '{source_dir}' does not exist.")
        return

    # Ensure the destination directory exists
    if not destination_path.exists():
        destination_path.mkdir(parents=True, exist_ok=True)

    # Recursively search for jpg files and copy them
    for jpg_file in source_path.glob("**/*.jpg"):
        destination_file = destination_path / jpg_file.name
        shutil.copy(jpg_file, destination_file)
        if print_message: print(f"Copied '{jpg_file}' to '{destination_file}'")


# source_directory = "/path/to/source/directory"
# destination_directory = "/path/to/destination/directory"
# copy_jpg_files(source_directory, destination_directory)




if __name__ == "__main__":
	# Set variables. 
	# Assume running from SMW home directory, also the home of the mount points
	raw_mount = Path("/home/sam_woodman_noaa_gov/amlr-gliders-imagery-raw-dev")
	proc_mount = Path("/home/sam_woodman_noaa_gov/amlr-gliders-imagery-proc-dev")

	raw_path  = raw_mount.joinpath("gliders/2022/amlr08-20220513/shadowgraph/images")
	proc_path = proc_mount.joinpath("SANDIEGO/2022/amlr08-20220513/regions-mser")

	# Make directories, if necessary, and mount
	Path(raw_mount).mkdir(parents=True, exist_ok=True)
	Path(proc_mount).mkdir(parents=True, exist_ok=True)

	run(["gcsfuse", "--implicit-dirs", "-o", "ro", "amlr-imagery-raw-dev", raw_mount])
	run(["gcsfuse", "--implicit-dirs", proc_mount, proc_mount])

	# Generate list of Directories to segment
	dir_list = ['Dir0000', 'Dir0001', 'Dir0002'] #, 'Dir0003', 'Dir0004', 'Dir0005']

	segemnt_str = "/opt/Threshold-MSER/build/segment"
	segement_file = Path(segemnt_str)

	print(f"Path to segment file: {segement_file}")
	print(f"Path to raw (in) directories: {raw_path}")
	print(f"Path to proc (out) directories: {proc_path}")

	if segement_file.is_file():
		for i in dir_list:
			print(f"Segmenting images in directoy {i}")
			with tempfile.TemporaryDirectory() as temp_dir:
				# Run segment
				print(f"Running segment, and writing files to {temp_dir}")
				run([segemnt_str, "-i", raw_path.joinpath(i), "-o", temp_dir])

				# Copy to final place
				dest_path = proc_path.joinpath(i)
				print(f"Copying segmented region images to {dest_path}")
				copy_jpg_files(temp_dir, dest_path)

				# TODO: extract CSV files
				# print(f"Copying measurement ")
			print("Cleaning up")

	else:
		print("error")
		return
