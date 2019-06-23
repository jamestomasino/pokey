#!/bin/bash

# Takes a port parameter, just so you know which one you're running on.
test -n "$1" || { echo "$0 <port>"; exit 1; }
port=$1

intro="Welcome!\n"
instructions="Instructions: t, time; u, uptime; ctrl-c to quit"
error="Command not found. Type 'h' for help"

function pokey_server () {
  echo -e "$intro"
  echo -e "$instructions"
  echo -n "> "
  while true ; do
    read -r msg
    case $msg in
      t | time )
        date ;;
      u | uptime )
        uptime ;;
      h | help )
        echo -e "$instructions" ;;
      * )
        echo -e "$error" ;;
    esac
    echo -n "> "
  done
}

# Start pokey_server as a background coprocess named POKE
# Its stdin filehandle is ${POKE[1]}, and its stdout is ${POKE[0]}
coproc POKE { pokey_server; }

# Start a netcat server, with its stdin redirected from POKE's stdout,
# and its stdout redirected to POKE's stdin
nc -l "$port" -k <&"${POKE[0]}" >&"${POKE[1]}"
