# Running the Experiments

* HPC platform: ORNL Summit
* RADICAL-Cybertools stack:
  ```
  
  python               : 3.7.0
  pythonpath           : /autofs/nccs-svm1_sw/summit/.swci/0-core/opt/spack/20180914/linux-rhel7-ppc64le/gcc-4.8.5/py-setuptools-40.4.3-xynpmbuwujfkcw52tegkndot6jj5bye5/lib/python3.7/site-packages:/autofs/nccs-svm1_sw/summit/.swci/0-core/opt/spack/20180914/linux-rhel7-ppc64le/gcc-4.8.5/py-virtualenv-16.0.0-ohsvxc5mf4aornhyrfp4ecea5bzcowon/lib/python2.7/site-packages:/sw/summit/xalt/1.2.0/site:/sw/summit/xalt/1.2.0/libexec
  virtualenv           : /ccs/home/mturilli1/ve/prrte-paper2

  radical.entk         : 1.4.1.post1
  radical.pilot        : 1.4.0-v1.4.0-48-gafbdfc3@devel
  radical.saga         : 1.4.0-v1.4.0-10-ga942e0f@devel
  radical.utils        : 1.4.0-v1.3.1-73-ga7accc7@devel
  ```
* command:
  ```
  cd experiments/summit_prrte/bin
  . setup.sh
  python run_heterogeneous_tasks.py ornl.summit_prte
  ```

