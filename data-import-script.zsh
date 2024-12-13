pip install kaggle   # Install kaggle CLI tool
kaggle datasets download -d uom190346a/sleep-health-and-lifestyle-dataset   # Import data directory from kaggle
if test -d "data"; then
    # Do nothing if 'data' directory already exists
else
    mkdir data  # Create data directory if it doesn't exist
fi
unzip -d data sleep-health-and-lifestyle-dataset.zip  # Unzip sleep data into data directory
rm sleep-health-and-lifestyle-dataset.zip   # Delete sleep data zip file