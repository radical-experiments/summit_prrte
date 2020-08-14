module load python/3.7.0
module load py-virtualenv/16.0.0
module load py-setuptools/40.4.3-py3
module load zeromq
module load vim
. ~/experiments/summit_prrte/ve/prrte-paper2-multi/bin/activate
export RADICAL_PILOT_DBURL="mongodb://129.114.17.185:27017/rct" 
export RADICAL_LOG_LVL="DEBUG"
export RADICAL_PROFILE="TRUE"
