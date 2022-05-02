# MVcolor
MVcolor is a color encoding recommendation system that uses a unified color scheme on the entire MV to assist maintaining color encoding consistencu under a limited number of colors. 
- [demo](https://youtu.be/mqJS7xz704o)
## Requirements
- Python 3.8
- [Anaconda](https://docs.anaconda.com/anaconda/install/index.html)
    - Install pip 
      ```
      conda install -c anaconda pip 
      ```
- [Django](https://docs.djangoproject.com/en/4.0/topics/install/)
  ```
  python -m pip install Django
  ```
- [Django REST Framework](https://www.django-rest-framework.org/#installation)
  ```
  pip install djangorestframework
  ```
- [DEAP](https://github.com/DEAP/deap)
  ```
  pip install deap
  ```
- [Gurobi](https://support.gurobi.com/hc/en-us)
  To use Gurobi, first download the software and then get a license key.
    - [Install Gurobi](https://support.gurobi.com/hc/en-us/articles/360044290292-How-do-I-install-Gurobi-for-Python-)
      ```
      python -m pip install gurobipy
      ```
    - [Retrieving a Free Academic license](https://www.gurobi.com/documentation/9.5/quickstart_mac/retrieving_a_free_academic.html)
        - Register an account
        - Home Page > Downloads & Licenses > [Request an Academic License](https://www.gurobi.com/downloads/end-user-license-agreement-academic/)
          (e.g., grbgetkey 253e22f3-...).
          ```
          grbgetkey <Key Code>
          ```
          <font color=firebrick>grbgetkey will ask for the name of the directory in which to store your license key file (gurobi.lic). </font>
        - [Guide: How to retrieving a free academic license](https://www.gurobi.com/documentation/9.5/quickstart_mac/retrieving_a_free_academic.html#subsection:academiclicense)
    - Set an environment variable  **GRB_LICENSE_FILE** to the license key file
      e.g., 
      ```
      GRB_LICENSE_FILE=/Library/gurobi/gurobi.lic
      ```
- [Pybind](https://pybind11.readthedocs.io/en/stable/)
    - Use `pip` or `conda` to install pybind11 
      ```
      pip install pybind11
      ```
    - Complie ciede2000.cpp and generate a .so file
        ```
        cd mvcolor/src/util 
        g++ -O3 -Wall -shared -std=c++11 -undefined dynamic_lookup `python3 -m pybind11 --includes` ciede2000.cpp -o ciede2000`python3-config --extension-suffix`
        ```
       !! Do NOT use python except python3 on the command above.
- Node.js
    - [Downloads (includes npm)](https://nodejs.org/en/download/)
    - Install webpack
      ```
      npm install webpack
      ```
## Set Up
- Back-end
    - For the first time or if there are changes in `/mvcolor/models.py`, run these commands.
      ```
      python manage.py makemigrations mvcolor
      python manage.py migrate
      ```
    - Run server
      ```
      python manage.py runserver
      ```
- Front-end
    - Build
      ```
      npm run build
      ```
      or 
      ```
      npm run dev
      ```
- Browser
    - 127.0.0.1:8000