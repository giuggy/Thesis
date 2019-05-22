#!/usr/bin/env bash

job1=$1
param1=$2
param2=$3
job2=$4
param3=$5
param4=$6
param5=$7

$job1 $param1 $param2 & $job2 $param3 $param4 $param5 && fg