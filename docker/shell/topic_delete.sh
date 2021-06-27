#!/bin/bash

function sintaxe {
    echo ""
    echo "Script para deleção de topico no cluster kafka na confluent cloud"
    echo "v1 - 02/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo ""
    echo "Parametros:"
    echo " -t <topic_name>    # para deletar o topico informado"
    echo ""    
    echo "Exemplo: ./topic_delete.sh -t topic-name" 
    echo ""   
 }

function prop {
    grep "${1}" $PROPERTIES|cut -d'=' -f2
} 

clear
PROPERTIES=../_keys/environment.properties

KC_HOST=$(prop 'bootstrap.servers')

if [ ! -z "$1" ] && [ ! -z "$2" ] && [ "$1" == "-t" ]; then
    echo ""
    kafka-topics --bootstrap-server $(prop 'bootstrap.servers') --delete --topic $2
else
    sintaxe
    exit 1
fi

