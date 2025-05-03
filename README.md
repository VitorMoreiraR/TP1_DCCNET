# TP1 - DCCNET

Este projeto implementa um protocolo de rede customizado chamado **DCCNET**, utilizado para envio e recepção de arquivos e mensagens autenticadas entre cliente e servidor.

---

# 📁 Estrutura do Projeto — Explicação

## `apps/`
Contém as aplicações principais que utilizam o protocolo **DCCNET**.

### `file_transfer/`
Implementa um sistema de envio e recepção de arquivos.

- **`client.py`**
- **`server.py`**

### `md5_client/`
Implementa um cliente que envia uma mensagem **G.A.S.**, com autenticação baseada em MD5.

- **`main.py`**: Código principal que realiza a autenticação MD5 e envia a mensagem ao servidor.

---

## `dccnet/`
Biblioteca do protocolo **DCCNET**, responsável por toda a lógica de rede e estrutura dos dados.

- **`autentication.py`**: Realiza o processo de autenticação MD5 entre cliente e servidor.
- **`comunication.py`**: Define a lógica da comunicação após a autenticação.
- **`connection.py`**: Gerencia a conexão assíncrona do file_transfer com `asyncio`.
- **`constants.py`**: Armazena constantes globais do projeto.
- **`manipulation_frame.py`**: Responsável por montar e validar os quadros de dados usados na transmissão.
- **`utils.py`**: Reúne funções auxiliares como configuração de `logger` e `sockets`.

---

## `temp/`
Diretório usado para armazenar arquivos de entrada e saída durante o file_transfer

---

## `tests/`
Diretório destinado à criação de **testes automatizados** para garantir o funcionamento correto do protocolo.

---

## `docs/`
Pasta reservada para **documentação** do projeto.

---

## ⚙️ Pré-requisitos

- Python 3.10+

---

## 🚀 Como Executar - MD5_Client

```bash
# Formato: python -m apps.md5_client.main HOST:PORTA "mensagem"
python -m apps.md5_client.main pugna.snes.dcc.ufmg.br:51510 2022036012:9:f54785da897269878c579a489838a618fda9ff76637707cf39c2f91e8040d53b+497cba28f5feca797a65d4b9f75555674318703add10f6000071d2a5de7e7d0d
```

## 🚀 Como Executar - File_Transfer

```bash
# Formato: python -m apps.file_transfer.server -s PORTA INPUT OUTPUT
python -m apps.file_transfer.server -s 8080 server_input.txt server_output.txt

# Formato: python -m apps.file_transfer.client -c IP:PORTA INPUT OUTPUT
python -m apps.file_transfer.client -c 127.0.0.1:8080 temp/client_input.txt client_output.txt
```
