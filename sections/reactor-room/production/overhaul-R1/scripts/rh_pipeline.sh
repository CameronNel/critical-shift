#!/bin/sh
# Hall pass chain: usage: rh_pipeline.sh <hall_base.blend> <out_dir>   (needs /tmp/bv/bin/python; stages run in series on one blend)
set -e
P=${PY:-/tmp/bv/bin/python}; B=$1; O=$2; mkdir -p $O; D=$(dirname $0)
cd $D
$P rh_floor.py -- $B $O/s1_floor.blend > $O/s1.log 2>&1
$P rh_walls.py -- $O/s1_floor.blend $O/s2_walls.blend > $O/s2.log 2>&1
$P rh_stations.py -- $O/s2_walls.blend $O/s3_stations.blend > $O/s3.log 2>&1
$P rh_services.py -- $O/s3_stations.blend $O/s4_services.blend > $O/s4.log 2>&1
$P rh_pool_surround.py -- $O/s4_services.blend $O/s5_pool.blend > $O/s5.log 2>&1
$P rh_light.py -- $O/s5_pool.blend $O/s5b_light.blend > $O/s5b.log 2>&1
$P rh_final.py -- $O/s5b_light.blend $O/hall_final.blend > $O/s6.log 2>&1
echo chain-ok > $O/chain.ok
