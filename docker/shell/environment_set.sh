#!/bin/bash

function sintaxe {
    echo ""
    echo "Script para configuração do ambiente de trabalho na confluent cloud"
    echo "v1 - 02/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo ""
    echo "Exemplo:"    
    echo ". ./environment_set.sh"
    echo ""    
 }

 function prop {
    grep "${1}" $PROPERTIES|cut -d'=' -f2
} 

case $1 in

  "/?" | "--help" | "-h")
        sintaxe
        exit 1
    ;;
esac

clear
PROPERTIES=../_keys/environment.properties

cp /app/_keys/netrc ~/.netrc
chmod 600 ~/.netrc

ccloud environment use $(prop 'ccloud-environment')
ccloud kafka cluster use $(prop 'ccloud-cluster')
ccloud api-key store $(prop 'schemaregistry-username') $(prop 'schemaregistry-password') --resource $(prop 'ccloud-cluster')
ccloud api-key store $(prop 'kafka-username') $(prop 'kafka-password') --resource $(prop 'ccloud-cluster')
ccloud api-key use $(prop 'kafka-username') --resource $(prop 'ccloud-cluster')

rm ~/.netrc
