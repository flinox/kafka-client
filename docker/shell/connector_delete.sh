
function sintaxe {
    echo ""
    echo "Script para delecao de connector kafka connect"
    echo "v1 - 05/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo ""
    echo "Parametros:"
    echo " <ip:port>     # IP e Porta da API REST do Kafka Connect"
    echo " <nome>        # Nome do connector (nome do arquivo com conteudo)"
    echo ""    
    echo "Exemplo: ./connector_delete.sh localhost:8083 SRC_NOME_CONNECTOR"
    echo ""   
 }


FOLDER_CONNECTORS=./connectors

if [ ! -z "$1" ] && [ ! -z "$2" ]; then
    # DELETAR CONNECTOR
    curl -i -H 'Content-Type: application/json' -XDELETE $1/connectors/$2
else
    sintaxe
    exit 1
fi



