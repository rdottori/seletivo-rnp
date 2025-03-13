Teste técnico para processo seletivo da RNP

__Candidato:__ Rodrigo de Oliveira

- [Questão 1](#questão-1)
   * [Instruções](#instruções)
   * [Projeto 1](#projeto-1-monitoramento-de-rede)
   * [Projeto 2](#projeto-2-monitoramento-de-clientes)
- [Questão 2](#questão-2)
   * [Projeto 1: Página de status (Monitoramento)](#projeto-1-página-de-status-monitoramento)
   * [Projeto 2: Implementação de práticas de DevOps em produto interno da empresa (DevOps)](#projeto-2-implementação-de-práticas-de-devops-em-produto-interno-da-empresa-devops)
   * [Projeto 3: Automação de relatórios de backup (Automação)](#projeto-3-automação-de-relatórios-de-backup-automação)

# Questão 1

## Instruções

Dependências:

    docker-compose

Para executar o primeiro projeto (monitoramento de rede), os comandos são:

    git clone https://github.com/rdottori/seletivo-rnp
    cd seletivo-rnp/agente-web
    docker-compose up

Para executar o segundo projeto (monitoramento do ViaIpe), usar a pasta `seletivo-rnp/agente-viaipe` no lugar da `seletivo-rnp/agente-web`.

Em ambos os casos, um .env já foi providenciado para questões de facilidade, mas em uma situação real o mesmo não faria parte do repositório.

Independente do projeto, para acessar o frontend do Grafana, usar a URL:

    http://localhost:3000/
O usuário padrão é `admin` e a senha padrão é `CZ6FDxewpuZjNktR`.

O Grafana deve criar automaticamente os datasources e dashboards; o dashboard já configurado e se chama apenas "Dashboard". Caso esse não exista devido a algum erro, ele pode ser importado usando um .json que fica no caminho `init/grafana/provisioning/dashboards/dashboard.json` dentro da pasta do agente. O datasource deve ter o nome "grafana-postgresql-datasource" para que o dashboard funcione corretamente.

O arquivo `config.json` na pasta `monitor` pode ser editado em tempo real para configurar aspectos do programa como a quantidade de pings por vez e o intervalo entre consultas.

Logs podem ser consultados com `docker logs`.

## Projeto 1: Monitoramento de Rede

### Documentação

#### Resumo

Agente que monitora websites através de pings e requisições, apresentando estatísticas de erro, latência e tempo de resposta para o usuário em um dashboard do Grafana.

#### Arquitetura

O projeto fica todo dentro de uma instância do Docker Compose, separado em três componentes guardando o script de monitoramento, o banco de dados e a instância do Grafana.

| Componente              | Função                                                                                    | Tecnologia    |
|-------------------------|-------------------------------------------------------------------------------------------|---------------|
| Script de monitoramento | Realiza consultas periódicas aos sites e guarda resultados no banco de dados | Python        |
| Banco de dados          | Armazena estatísticas sobre as consultas como latência, códigos de resposta, etc.         | PostgreSQL 13 |
| Grafana                 | Apresenta dashboards usando as estatísticas do banco de dados como base                                     | Grafana       |



![Untitled Diagram drawio](https://github.com/user-attachments/assets/11a9f377-c979-4779-9b0e-930d75061db3)

#### Soluções e decisões de design

As seguintes considerações foram respeitadas:

  * Simplicidade, por ser uma ferramenta de escopo pequeno
  * Flexibilidade e escalabilidade, por ser uma ferramenta própria para adaptações/expansões futuras
  * Configuração em tempo real, pois é uma ferramenta que precisa rodar continuamente para ser útil; portanto, o tempo de inatividade para modificações deve ser minimizado
  * Agilidade no monitoramento, para que a frequência dos dados seja alta o suficiente para que os mesmos sejam úteis para análise

Portanto, foram tomadas as seguintes decisões:

  * Uso de time.sleep() para intervalos entre as checagens. Em um projeto mais complexo seria válido o uso de bibliotecas de agendamento para assegurar a regularidade da execução, mas pela simplicidade foi preferido evitar bibliotecas desnecessárias
  * Uso de funções assíncronas para impedir que a espera pelo resultado dos pings gerasse atrasos excessivos entre as coletas de dados, e para permitir escalabilidade para novos hosts através de um limite configurável de conexões concorrentes
  * O arquivo de configuração com aspectos como timeouts, intervalo entre coletas, etc. é lido em tempo real para que possa ser adaptado a situações novas; por exemplo, podemos aumentar a quantidade de pings caso a configuração padrão não seja suficiente para capturar quedas intermitentes ou breves oscilações na latência
  * Alta modularidade no design de baixo nível do script, para que possa ser adaptado no futuro para funcionalidades e contextos novos

Também é importante destacar as seguintes suposições:

  * Que todos os sites são acessíveis usando o protocolo HTTPS, já que sites que não tem apoio para HTTP são raros hoje em dia
  * Que o propósito da ferramenta é monitorar o status dos sites e não da máquina de onde a ferramenta é executada; assim, por exemplo, erros de conexão devido a quedas de rede local não são considerados nas estatísticas

#### Bibliotecas e recursos usados

    psycopg2
    aiohttp

#### Imagens

![2025-03-09-20:44:00](https://github.com/user-attachments/assets/3907f97b-c273-430c-9864-bfc6d595d54a)

![2025-03-09-20:44:12](https://github.com/user-attachments/assets/5b97427d-01e1-4f83-b543-e5ba7be55d06)

## Projeto 2: Monitoramento de Clientes

### Documentação

#### Resumo

Agente que consulta a API do ViaIpe para monitorar estatísticas de cada cliente como disponibilidade e uso de banda, apresentando os resultados em um dashboard do Grafana.

#### Arquitetura

Como no primeiro projeto, a aplicação fica toda dentro de uma instância do Docker Compose, separada em três componentes guardando o script de monitoramento, o banco de dados e a instância do Grafana.

| Componente              | Função                                                                                    | Tecnologia    |
|-------------------------|-------------------------------------------------------------------------------------------|---------------|
| Script de monitoramento | Realiza consultas periódicas à API, realiza cálculos e guarda resultados no banco de dados | Python        |
| Banco de dados          | Armazena estatísticas calculadas como qualidade da conexão, disponibilidade, etc.         | PostgreSQL 13 |
| Grafana                 | Apresenta dashboards usando as estatísticas do banco de dados como base                                     | Grafana       |


![Untitled Diagram2 drawio](https://github.com/user-attachments/assets/292e12ce-2e00-4188-8595-d9c8cda918cb)

#### Soluções e decisões de design

As considerações são semelhantes às do primeiro projeto:

  * Simplicidade
  * Configuração em tempo real
  * Agilidade no monitoramento

Entretanto, dessa vez nós não consideramos a flexibilidade como importante, pois o agente realiza apenas uma tarefa simples (consultar a API), então o custo de reescrever o programa para se tornar mais modular/escalável seria mínimo, se necessário no futuro.

Também foi suposto que:

  * O retorno da API é sempre confiável, consistente em sua estrutura e não precisa ser higienizado
  * Clientes que no instante da consulta tiverem informações essenciais faltando podem ser ignorados, ao invés de guardarmos resultados parciais
  * Os dados devem ser guardados como especificado no enunciado, já calculados pelo script, ao invés de guardarmos os dados base no banco e usarmos o Grafana para realizar cálculos

Portanto, foram tomadas as seguintes decisões:

  * Como no primeiro projeto, configuração lida em tempo real e uso de time.sleep(), pelos mesmos motivos
  * As requisições são síncronas pois os dados para cada instante são recebidos todos de uma vez; não há congestionamento
  * Erros na conexão com a API ou no processamento de seus dados são a princípio temporários e não resultam na interrupção da execução; nesses casos nós simplesmente não colhemos os dados para aquele instante/cliente

#### Bibliotecas e recursos usados

    psycopg2
    requests

#### Imagens
![2025-03-12-16:47:27](https://github.com/user-attachments/assets/b08dd4a6-d080-4301-a9ff-981f97a4cb2e)


# Questão 2

Apresentação de projetos passados.

## Projeto 1: Página de status (Monitoramento)

### Resumo e objetivo

Página que relata status e incidentes de websites que o cliente deseja monitorar, avisando de quaisquer quedas e problemas atuais, e permitindo que os usuários visualizem um histórico de problemas para cada site. A página foi feita para substituir a Statuspage da Atlassian; isso ajudou a empresa a reduzir custos com ferramentas de terceiros e a melhorar a visibilidade de incidentes em tempo real. A fonte de dados principal é o Zabbix.

### Arquitetura e tecnologias

De forma ampla, o projeto consiste em:

| Componente              | Função                                                                                    | Tecnologia    |
|-------------------------|-------------------------------------------------------------------------------------------|---------------|
| Site principal (frontend e algumas funções de backend) | Busca os dados de componentes e incidentes no banco e os apresenta para o usuário + gerencia autenticação | Escrito em Python, Django e HTML/CSS/JavaScript; hospedado em AWS ECS        |
| Banco de dados          | Armazena dados de componentes, incidentes atuais e passados, etc.         | AWS RDS e PostgreSQL |
| Zabbix                 | Checa status dos sites através de triggers e web scenarios, e aciona scripts (hospedados no próprio servidor do Zabbix) para certos incidentes e hosts para enviar mensagens à fila                                     | Zabbix e bash+Python (para scripts)      |
| Fila de mensagens | Serve de intermediário entre o Zabbix e as funções de atualização de incidente, permitindo recuperação de mensagens perdidas, técnicas para evitar congestionamento, etc. | AWS SQS |
| Scripts de atualização do BD | Fazem queries direto ao BD para atualizar informações sobre incidentes; o uso de scripts separados do site principal permite uso de ferramentas da AWS para monitoramento e gerenciamento sem impactar performance do site | Python e AWS Lambda |
| Load balancer e rede virtual | Regulam tráfego ao site | AWS ELB e AWS VPC |
| Active Directory (gerenciado pelo cliente) | Guarda informações de autenticação dos usuários | Microsoft Entra ID |

### Desafios e soluções

  * O projeto inicialmente usava uma API do site principal (criada com o Django REST Framework) para comunicação com o Zabbix (isso é, os scripts do Zabbix inicialmente faziam requisições à API). Entretanto, como o número de hosts era extremamente alto e precisava de maior escabilidade, essa funcionalidade foi migrada para SQS e Lambda para reduzir o uso de recursos do site em si e permitir gerenciar melhor o congestionamento, além de permitir que fosse monitorada com as próprias ferramentas da AWS como CloudWatch.
  * O número de dados (hosts, web scenarios, etc.) no Zabbix era bem elevado, e só alguns deles eram para ser relatados à página de status; além disso, atributos como descrições e nomes não estavam padronizados, tornando difícil identificar quais dados eram relevantes. Para isso foi necessário um levantamento de padrões entre os dados e a criação de filtros.
  * A fase inicial do projeto foi em ritmo urgente (menos de duas semanas), pois a intenção era evitar os custos elevados da Statuspage da Atlassian antes do final do mês. A coordenação da equipe foi essencial para cumprir esse prazo.

### Minha atuação

Nesse desenvolvimento, me encarreguei de:

  * Desenvolver por completo o frontend e backend do site
  * Criar scripts para interação entre o Zabbix e o SQS + scripts dos lambdas para atualização do BD
  * Criar scripts auxiliares de interação com a API do Zabbix para configurar os hosts/triggers/web scenarios que deviam ser monitorados pela página de status
  * Criar scripts auxiliares para facilitar cadastros de componentes/sites novos no Zabbix e no banco da página simultaneamente, de acordo com as especificações do cliente
  * Configurar SQS, Lambda e CloudWatch para as funções descritas acima

## Projeto 2: Implementação de práticas de DevOps em produto interno da empresa (DevOps)

### Resumo e objetivo

Aprimorar a infraestrutura de um projeto da empresa (um produto interno que realizava principalmente funções de CRUD, escrito em Python e Django) para fazer melhor uso de componentes de nuvem (o projeto já era hospedado na AWS) e para se adequar melhor aos princípios de DevOps. Inicialmente, a arquitetura do software era monolítica com todas as funcionalidades rodando em container no ECS. Implementar essas práticas trouxe mais clareza e agilidade ao desenvolvimento e mais eficiência ao programa em si.

### Minha atuação

Após herdar o desenvolvimento inteiro do produto, também me encarreguei de implementar melhorias no âmbito de cloud/DevOps.

Foram feitas as seguintes tarefas:

  * Criação e implementação de testes de unidade para assegurar a corretude de aspectos importantes do programa, principalmente relacionados a segurança e autenticação
  * Implementação de CI/CD. GitHub Actions foi configurado para executar os testes de unidade em todo pull request, assegurando a corretude do programa antes do deploy. AWS CodeBuild e CodePipeline foram usados para configurar tal que, sempre que há um merge feito para a branch main, é feito build e deploy da imagem nova, reduzindo atrasos gerados pelo build e deploy manual
  * Migração de funcionalidades que faziam uso de agendamento interno do programa para AWS Lambdas, reduzindo uso de recursos do backend (já que passamos a permitir execução sob demanda e fora do container), além de tornar as funcionalidades mais escaláveis e facilitar seu monitoramento
  * Implementação de monitoramento em nuvem: a aplicação foi modificada para que os logs do próprio programa fossem despachados para o CloudWatch, e foram configurados alertas nessa mesma ferramenta para enviar e-mails para membros da equipe de infraestrutura caso o uso de recursos se tornasse excessivo
  * Migração de credenciais e variáveis de ambiente sensíveis para o AWS Secrets Manager
  * Configuração de bucket no AWS S3 para armazenar arquivos estáticos como imagens, CSS, JavaScript, etc.

### Desafios e soluções

  * Como a arquitetura inicial do projeto era monolítica, foi necessário muito cuidado para desacoplar as partes que precisavam ser migradas para Lambda sem afetar a corretude ou funcionamento do código. Para tal, os testes de unidade foram criados primeiro, para dar segurança que a integridade do produto continuava regular, e a migração foi feita de forma gradual e minuciosa

## Projeto 3: Automação de relatórios de backup (Automação)

### Resumo e objetivo

Criação de scripts em PowerShell para capturar dados das APIs de ferramentas de backup (como Veeam e MSP) e gerar relatórios automáticos em .doc, contendo informações críticas sobre quaisquer erros e problemas, utilização de dados e estatísticas semelhantes. No fim, os scripts enviam e-mails contendo os relatórios para membros relevantes da equipe de infraestrutura. A criação dos relatórios automáticos permitiu melhor monitoramento, organização e comunicação das estatísticas e saúde dos sistemas de backup, reduzindo o trabalho manual das equipes de operações e trazendo maior visibilidade sobre a nossa infraestrutura.

### Minha atuação

Me encarreguei de forma integral do desenvolvimento e deploy dos scripts: da interação com as APIs, geração dos arquivos de relatório, envio automático dos arquivos e agendamento da execução.

### Desafios e soluções

  * A API do Veeam era complexa e com vários casos particulares, tornando os scripts longos e com muito potencial para erros. Além disso, a documentação dessa API era pouco detalhada, incompleta e por vezes desatualizada. Foram necessários vários testes e análise manual dos objetos e funções .NET da mesma para montar um mapa detalhado próprio sobre a estrutura da API e das suas funcionalidades.
  * A confiabilidade e regularidade dos relatórios era essencial, então foram necessários verificações de erro e logs detalhados para evitar inconsistência nas informações, principalmente levando em conta a possibilidade de erros silenciosos como atualizações no funcionamento das APIs.
