#This is a project that will give me notifications of new job listings that are internships in the following categories:
  - software development jobs
  - data science jobs
  - information technology jobs
  - cybersecurity jobs

#Installation:
- Step 1: Make sure you have google chrome installed, and if you are on windows, select the windows version to download from the git repository and vice versa for linux. On linux make sure you are on Ubuntu and downloaded chrome through the .deb file on google's website.
- Step 2: Download miniconda or anaconda and make sure to add the path. Website is here: https://docs.conda.io/projects/miniconda/en/latest/
- Step 3: Open up bash linux or the conda terminal in windows and navigate to the directory where the project files are. Navigate to the directory of where the envirnment.yml file is located. In Windows that will be the CustomJobAlertWindows folder. In Linux it will be the CustomJobAlertLinux folder.
- Step 4. In conda terminal or bash type "conda env create -f environment.yml" then press enter.
- Step 5. Type conda activate webscraping to activate the environment and go to /PythonCode and type "python main.py" to run the file.
