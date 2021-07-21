#!/bin/bash

function sintaxe {
    echo ""
    echo "Script para recriar topico e seu schema na confluent cloud"
    echo "v1 - 04/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo ""
    echo "Parametros:"
    echo " -t <topic_name>  <partitions>   # para recriar topico e seu schema e qual suas partitions"
    echo ""    
    echo "Exemplo: ./topic_schema_recreate.sh -t contact-created 10"
    echo ""   
 }

if [ ! -z "$1" ] && [ ! -z "$2" ] && [ ! -z "$3" ] && [ "$1" == "-t" ]; then
    

    read -p "O Topico $2 e os schemas relacionados a este tópico serão excluídos, bem como todas as suas mensagens, confirma (S/N) ? " -n 1 -r

    case $REPLY in 
        s|S)

            echo "Deletando o tópico..."
            ./topic_delete.sh -t $2

            sleep 2
            echo "Deletando o schema da key e value..."            
            ./schema_delete.sh -s $2

            sleep 5
            echo "Criando o tópico..."                        
            ./topic_create.sh -t $2 $3

            sleep 2
            echo "Criando o schema da key..."
            ./schemas_create.sh -s $2-key.json
            
            sleep 2
            echo "Criando o schema do value..."            
            ./schemas_create.sh -s $2-value.json

        ;;

        n|N)
            echo ""
            echo -e "Ok, nada será excluído, saindo..."
            exit 1
        ;;

        *)
            echo ""
            echo -e "Opção inválida, saindo sem fazer nada."
            exit 1
        ;;
    esac




else

    sintaxe
    exit 1

fi

