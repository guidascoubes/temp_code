import tkinter as tk
from tkinter import messagebox, filedialog
import serial
import time
import threading
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
from scrapy.extensions.httpcache import RFC2616Policy


# Função para conectar à porta serial
def conectar_serial():
    try:
        global serial_port
        serial_port = serial.Serial('COM3', 115200, timeout=1)  # Ajustar a porta conforme necessário
        time.sleep(2)  # Dar tempo para inicializar a conexão
        messagebox.showinfo("Conexão", "Conectado ao ESP32!")
        iniciar_leitura_serial()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar à porta serial: {str(e)}")


# Contador de linhas lidas
linhas_lidas = 0  # Variável para contar as linhas lidas

# Função para ler dados da porta serial
def iniciar_leitura_serial():
    def ler_dados():
        global tempo_inicio, linhas_lidas
        tempo_inicio = time.time()  # Registra o tempo de início
        while True:
            if serial_port.is_open:
                linha = serial_port.readline().decode('utf-8').strip()  # Ler e decodificar a linha
                if linha:
                    linhas_lidas += 1  # Incrementar o contador de linhas lidas
                    if linhas_lidas > 10:  # Ignorar as primeiras 10 linhas
                        atualizar_valores(linha)

    thread_leitura = threading.Thread(target=ler_dados)
    thread_leitura.daemon = True
    thread_leitura.start()


# Função para atualizar os valores e gráfico
def atualizar_valores(dados):
    try:
        temperaturas = list(map(float, dados.split(',')))  # Converter os valores de string para float
        if len(temperaturas) == 3:
            convertemp(temperaturas)
            sensor1_valor.set(f"{temperaturas[0]:.2f} °C")
            sensor2_valor.set(f"{temperaturas[1]:.2f} °C")
            sensor3_valor.set(f"{temperaturas[2]:.2f} °C")

            # Atualizar o gráfico com o tempo decorrido
            tempo_atual = time.time() - tempo_inicio  # Calcula o tempo decorrido
            x_data.append(tempo_atual)  # Adiciona o tempo decorrido
            sensor1_data.append(temperaturas[0])
            sensor2_data.append(temperaturas[1])
            sensor3_data.append(temperaturas[2])

            ax.clear()
            ax.plot(x_data, sensor1_data, label="Sensor NTC")
            ax.plot(x_data, sensor2_data, label="Sensor LM35")
            ax.plot(x_data, sensor3_data, label="Sensor DS18B20")
            ax.legend(loc="upper left")
            ax.set_title("Temperatura em Tempo Real")
            ax.set_xlabel("Tempo (s)")
            ax.set_ylabel("Temperatura (°C)")
            canvas.draw()

    except ValueError:
        messagebox.showerror("Erro", "Erro ao converter os dados recebidos.")

def convertemp(temperaturas):

    V_o = temperaturas[0]
    V_dd = 3.3
    R1 = 10000
    R2 = 10000
    R5 = 10000
    R3 = 10000
    # Calcula o paralelo R1 // R2
    R1_parallel_R2 = (R1 * R2) / (R1 + R2)

    # Calcula C1 e C2
    C1 = V_dd * (1 + R5 / R1_parallel_R2)
    C2 = V_dd * (R2 / (R2 + R1)) * (R5 / R1_parallel_R2)

    # Calcula R4
    numerator = -(V_o + C2) * R3
    denominator = (V_o + C2) - C1
    Rntc = numerator / denominator

    beta = 3950
    T0=25+273
    R0 = 10000

    T = beta / ((beta / T0) + math.log(Rntc / R0))

    temperaturas[0] = T-273
    temperaturas[1] = (temperaturas[1] / 7.82)*100
# Função para controlar o relay
def controlar_rele():
    if rele_estado.get() == 1:
        serial_port.write(b'RELAY_ON\n')  # Ativar o relay (ligar a ventoinha)
    else:
        serial_port.write(b'RELAY_OFF\n')  # Desativar o relay (desligar a ventoinha)


# Função para exportar os dados para um ficheiro CSV
def exportar_csv():
    # Abrir diálogo para selecionar o local onde o ficheiro será guardado
    ficheiro = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

    if ficheiro:
        try:
            # Criar e escrever no ficheiro CSV
            with open(ficheiro, mode='w', newline='') as f:
                escritor_csv = csv.writer(f)
                escritor_csv.writerow(["Tempo (s)", "Sensor NTC (°C)", "Sensor LM35 (°C)", "Sensor DS18B20 (°C)"])
                for i in range(len(x_data)):
                    escritor_csv.writerow([x_data[i], sensor1_data[i], sensor2_data[i], sensor3_data[i]])
            messagebox.showinfo("Sucesso", "Dados exportados com sucesso para CSV!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para CSV: {str(e)}")


# Função para reiniciar o gráfico
def reiniciar_grafico():
    global x_data, sensor1_data, sensor2_data, sensor3_data, linhas_lidas
    # Limpar os dados do gráfico
    x_data = []
    sensor1_data = []
    sensor2_data = []
    sensor3_data = []
    linhas_lidas = 0  # Reiniciar o contador de linhas lidas

    ax.clear()  # Limpar o gráfico
    ax.set_title("Temperatura em Tempo Real")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Temperatura (°C)")
    canvas.draw()  # Redesenhar o canvas


# Configuração da janela principal
root = tk.Tk()
root.title("Sistema de Medição de Temperatura")

# Variáveis para exibir os valores dos sensores
sensor1_valor = tk.StringVar(value="---")
sensor2_valor = tk.StringVar(value="---")
sensor3_valor = tk.StringVar(value="---")

# Frame para exibir as leituras dos sensores
frame_leituras = tk.Frame(root)
frame_leituras.pack(pady=10)

tk.Label(frame_leituras, text="Sensor NTC:").grid(row=0, column=0, padx=5, pady=5)
tk.Label(frame_leituras, textvariable=sensor1_valor).grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_leituras, text="Sensor LM35:").grid(row=1, column=0, padx=5, pady=5)
tk.Label(frame_leituras, textvariable=sensor2_valor).grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_leituras, text="Sensor DS18B20:").grid(row=2, column=0, padx=5, pady=5)
tk.Label(frame_leituras, textvariable=sensor3_valor).grid(row=2, column=1, padx=5, pady=5)

# Botão para conectar à porta serial
btn_conectar = tk.Button(root, text="Conectar ao ESP32", command=conectar_serial)
btn_conectar.pack(pady=10)

# Controle do relay
rele_estado = tk.IntVar()
chk_rele = tk.Checkbutton(root, text="Controle Manual do Relay", variable=rele_estado, command=controlar_rele)
chk_rele.pack(pady=10)

# Botão para reiniciar o gráfico
btn_reiniciar_grafico = tk.Button(root, text="Reiniciar Gráfico", command=reiniciar_grafico)
btn_reiniciar_grafico.pack(pady=10)

# Gráfico de temperatura
fig, ax = plt.subplots()
x_data = []
sensor1_data = []
sensor2_data = []
sensor3_data = []

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(pady=10)

# Botão para exportar os dados para CSV
btn_exportar_csv = tk.Button(root, text="Exportar para CSV", command=exportar_csv)
btn_exportar_csv.pack(pady=10)

root.mainloop()
