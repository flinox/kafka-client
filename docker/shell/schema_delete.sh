#!/bin/bash

function sintaxe {
    echo ""
    echo "Script para deleção de schemas no schema registry na confluent cloud"
    echo "v1 - 02/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo ""
    echo "Parametros:"
    echo " -s <schema_file>   # para deletar o schema informado"
    echo ""    
    echo "Exemplo: ./schema_delete.sh -s affiliation-created"
    echo ""   
 }


function prop {
    grep "${1}" $PROPERTIES|cut -d'=' -f2
} 

clear
PROPERTIES=../_keys/environment.properties
SCHEMAS_FOLDER=./schemas

SR_KEY=$(prop 'schemaregistry-username')
SR_SECRET=$(prop 'schemaregistry-password')
SR_HOST=$(prop 'schemaregistry-url')
AUTHORIZATION="$(echo -n $SR_KEY:$SR_SECRET | base64 -w 0)"


if [ ! -z "$1" ] && [ ! -z "$2" ] && [ "$1" == "-s" ]; then
    echo "Deletando o schema $2-key..."
    curl -i -s -X DELETE -H "Authorization: Basic $AUTHORIZATION" $SR_HOST/subjects/$2-key
    sleep 2
    curl -i -s -X DELETE -H "Authorization: Basic $AUTHORIZATION" $SR_HOST/subjects/$2-key?permanent=true
    sleep 2
    echo "Deletando o schema $2-value..."
    curl -i -s -X DELETE -H "Authorization: Basic $AUTHORIZATION" $SR_HOST/subjects/$2-value
    sleep 2
    curl -i -s -X DELETE -H "Authorization: Basic $AUTHORIZATION" $SR_HOST/subjects/$2-value?permanent=true

else
    sintaxe
    exit 1
fi


unset AUTHORIZATION
