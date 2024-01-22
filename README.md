# snowNetTools

Este repositório contém uma coleção de ferramentas de rede desenvolvidas para diferentes propósitos, incluindo projetos acadêmicos, aulas de monitoria em redes de computadores e aprendizado pessoal.

## Ferramentas Disponíveis

### 1. Traceroute

O traceroute é uma ferramenta que permite visualizar a rota que os pacotes estão tomando através de uma rede. Utilizando diretamente sockets, a implementação aqui presente utiliza o protocolo UDP como padrão e ICMP como protocolo secundário caso o UDP seja ignorado. Além disso, inclui uma solução para testar a rota reversa do trace.

### 2. Poisoner

O Poisoner é uma ferramenta desenvolvida para realizar ARP Poisoning e ataques Man-in-the-Middle em uma rede local. Utilizando a biblioteca Scapy e em poucas linhas de código, utilizei essa ferramenta para ilustar um artigo para o projeto de extensão da Poli-UPE chamado Tarponise.
### 3. Cheaper Nmap

Criado com o intuito de explicar o funcionamento do Nmap e como ele utiliza o protocolo TCP em uma aula de monitoria de redes de computadores, o Cheaper Nmap é uma versão simplificada da famosa ferramenta de varredura de rede. Este projeto utiliza apenas sockets TCP para ilustrar os princípios fundamentais por trás da funcionalidade do Nmap.
