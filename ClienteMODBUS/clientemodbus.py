from pymodbus.client import ModbusTcpClient
from time import sleep


class ClienteMODBUS():
    """
    Classe Cliente MODBUS usando pymodbus
    """
    def __init__(self, server_ip, porta, scan_time=1):
        """
        Construtor
        """
        # Cria o cliente TCP
        self._cliente = ModbusTcpClient(host=server_ip, port=porta)
        self._scan_time = scan_time

    def atendimento(self):
        """
        Método para atendimento do usuário
        """
        # Abre a conexão com o servidor MODBUS
        self._cliente.connect()
        try:
            atendimento = True
            while atendimento:
                sel = input("Deseja realizar uma leitura, escrita ou configuração? (1- Leitura | 2- Escrita | 3- Configuração | 4- Sair): ")

                if sel == '1':
                    tipo = input("""Qual tipo de dado deseja ler? (1- Holding Register | 2- Holding Register (DIGITAL) | 3- Coil | 4- Input Register | 5- Discrete Input): """)
                    addr = input("Digite o endereço da tabela MODBUS: ")
                    nvezes = input("Digite o número de vezes que deseja ler: ")
                    for i in range(0, int(nvezes)):
                        print(f"Leitura {i+1}: {self.lerDado(int(tipo), int(addr))}")
                        sleep(self._scan_time)

                elif sel == '2':
                    tipo = input("""Qual tipo de dado deseja escrever? (1- Holding Register | 2- Holding Register(DIGITAL) | 3- Coil): """)
                    if int(tipo) == 2:
                        posicao = input("Digite a posição do dado a ser escrito (0 a 15)")
                    else: posicao = 0

                    addr = input("Digite o endereço da tabela MODBUS: ")
                    valor = input("Digite o valor que deseja escrever: ")
                    if int(addr) not in [1, 2]:
                        ok = self.escreveDado(int(tipo), int(addr), int(valor), int(posicao))
                    else: 
                        ok = self.escreveDado(int(tipo), int(addr), float(valor), int(posicao))
                    
                    print("Escrita realizada." if ok else "Falha na escrita.")

                elif sel == '3':
                    scant = input("Digite o tempo de varredura desejado [s]: ")
                    self._scan_time = float(scant)

                elif sel == '4':
                    atendimento = False
                else:
                    print("Seleção inválida")
        except Exception as e:
            print('Erro no atendimento: ', e.args)
        finally:
            # Fecha a conexão ao sair
            self._cliente.close()

    def lerDado(self, tipo, addr):
        """
        Método para leitura de um dado da Tabela MODBUS
        Retorna o valor lido ou None em caso de falha.

        Registradores 1 e 2 exclusivos para float
        """
        
        # Holding Register
        if tipo == 1:
            if addr not in [1, 2]:
                resp = self._cliente.read_holding_registers(address=addr, count=1, device_id=1)
                if resp and not resp.isError():
                    return resp.registers[0]
                return None
            else: 
                # Read
                resp = self._cliente.read_holding_registers(address=1, count=2, device_id=1)
                valor = self._cliente.convert_from_registers(
                    resp.registers,
                    data_type=self._cliente.DATATYPE.FLOAT32,
                )
                if resp and not resp.isError():
                    return valor
                return None
        
        # Holding Register (DIGITAL)
        if tipo == 2:
                resp = self._cliente.read_holding_registers(address=addr, count=1, device_id=1)
                valor = self._cliente.convert_from_registers(
                    resp.registers,
                    data_type=self._cliente.DATATYPE.BITS,
                    )
                if resp and not resp.isError():
                    return valor
                return None       

        # Coil (função 01)
        if tipo == 3:
            resp = self._cliente.read_coils(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.bits[0]
            return None

        # Input Register (função 04)
        if tipo == 4:
            resp = self._cliente.read_input_registers(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.registers[0]
            return None

        # Discrete Input (função 02)
        if tipo == 5:
            resp = self._cliente.read_discrete_inputs(address=addr, count=1, device_id=1)
            if resp and not resp.isError():
                return resp.bits[0]
            return None

        # Tipo inválido
        return None

    def escreveDado(self, tipo, addr, valor, posicao):
        """
        Método para a escrita de dados na Tabela MODBUS
        Retorna True em caso de sucesso, False em caso de falha.

        Registradores 1 e 2 exclusivos para float
        """
        # Holding Register (função 06 - single)
        
        if tipo == 1:
            if int(addr) not in [1, 2]:
                resp = self._cliente.write_register(address=addr, value=valor, device_id=1)
                return bool(resp and not resp.isError())
            else:
                # Write
                regs = self._cliente.convert_to_registers(
                    valor,
                    data_type=self._cliente.DATATYPE.FLOAT32,
                )
                resp = self._cliente.write_registers(address=1, values = regs, device_id=1)
                return bool(resp and not resp.isError())
        
        if tipo == 2:
                
                resp = self._cliente.read_holding_registers(address=addr, count=1, device_id=1)
                leitura = self._cliente.convert_from_registers(
                    resp.registers,
                    data_type=self._cliente.DATATYPE.BITS
                    )
                leitura[posicao] = bool(valor)
                print(leitura)
                escrita = self._cliente.convert_to_registers(
                    leitura,
                    data_type=self._cliente.DATATYPE.BITS
                    )
                print(escrita)
                resp = self._cliente.write_registers(address=addr, values = escrita, device_id=1)
                return bool(resp and not resp.isError())

        
        # Coil (função 05 - single)
        if tipo == 3:
            # Em coils, valor esperado é 0/1 (False/True)
            resp = self._cliente.write_coil(address=addr, value=bool(valor), device_id=1)
            return bool(resp and not resp.isError())

        # Tipo inválido
        return False
