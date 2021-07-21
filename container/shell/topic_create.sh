#!/bin/bash

function sintaxe {
    echo ""
    echo "Script para criação de topicos kafka na confluent cloud"
    echo "v1 - 02/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo "requer ccloud"
    echo ""
    echo "Parametros:"
    echo " -f                                        # para criar todos os topicos"
    echo " -t <topic_name>  <partitions> <replicas>  # para criar somente o topico informado"    
    echo ""    
    echo "Exemplo: ./topic_create.sh -t account_created 10"   
    echo ""   
 }

function prop {
    grep "${1}" $PROPERTIES|cut -d'=' -f2
} 

clear
PROPERTIES=../_keys/environment.properties
TOPICOS=./topics/topicos.txt

#KC_HOST=$(prop 'bootstrap.servers')

case $1 in

# Cria todos os topicos caso nao exista
-f)

    if [ -z "$1" ]; then
        sintaxe
        exit 1
    else
        cat $TOPICOS | awk '{system("ccloud kafka topic create "$1" --partitions "$2" --if-not-exists -vv")}'
        #cat $TOPICOS | awk '{system("kafka-topics --bootstrap-server "$KC_HOST" --create --topic "$1" --partitions "$2" --replication-factor "$3" ")}'        
    fi

    ;;

# Cria somente um topico
-t)

    if [ ! -z "$2" ] && [ ! -z "$3" ]; then
        ccloud kafka topic create $2 --partitions $3 --if-not-exists -vv
        #kafka-topics --bootstrap-server $(prop 'bootstrap.servers') --create --topic $2 --partitions $3 --replication-factor $4
    else
        sintaxe
        exit 1
    fi
    ;;

# Não usou nenhum parametro valido
*)
    sintaxe
    exit 1
    ;;
esac