
function sintaxe {
    echo ""
    echo "Script para update de connector kafka connect"
    echo "v1 - 05/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo ""
    echo "Parametros:"
    echo " <ip:port>     # IP e Porta da API REST do Kafka Connect"
    echo " <nome>        # Nome do connector (nome do arquivo com conteudo)"
    echo ""    
    echo "Exemplo: ./connector_update.sh localhost:8093 SRC_NOME_CONNECTOR"
    echo ""   
 }


FOLDER_CONNECTORS=./connectors

if [ ! -z "$1" ] && [ ! -z "$2" ]; then
    # CREATE CONNECTOR
    curl -i -H 'Content-Type: application/json' -XPUT $1/connectors/$2/config --data "$(cat $FOLDER_CONNECTORS/$2.properties | jq -R -s 'split("\n") | map(select(length > 0)) | map(select(startswith("#") | not)) | map(split("=")) | map({(.[0]): .[1]}) | add ')"
else
    sintaxe
    exit 1
fi

