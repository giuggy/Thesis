#!/bin/bash

# Script to run topology and controllers: Floodlight, Local and Super controller

SESSION_NAME="giulia"

tmux has-session -t ${SESSION_NAME}

if [ $? != 0 ]
then
  # Create the session
  tmux new -d -s ${SESSION_NAME} 
  #tmux rename-window ${SESSION_NAME}
  # shell (1)
  tmux send-keys -t ${SESSION_NAME}:0 './Project/activation/controllers/super_script.sh' C-m
  
  # mysql (2)
  tmux split-window -h -t ${SESSION_NAME}:0
  tmux send-keys -t ${SESSION_NAME}:0 './Project/activation/controllers/floodlight_script.sh' C-m
  
  # server/debug log (3)
  tmux split-window -h -t ${SESSION_NAME}:0
  tmux send-keys -t ${SESSION_NAME}:0 './Project/activation/controllers/local_script.sh' C-m
  
  tmux select-layout even-horizontal

  # rails console (4)
  tmux split-window -v -t ${SESSION_NAME}:0
  tmux send-keys -t ${SESSION_NAME}:0 './Project/activation/controllers/single_mininet_script.sh' C-m
  

  # Start out on the first window when we attach
  tmux select-window -t ${SESSION_NAME}:0
  
fi
tmux attach -t ${SESSION_NAME}
