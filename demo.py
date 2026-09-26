import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configuración de apariencia
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TelemetriaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MSP430 Console")
        self.geometry("700x650")
        self.resizable(False, False)

        self.ser = None
        self.leyendo = False

        # Datos para la gráfica
        self.times = []
        self.voltages = []
        self.start_time = None

        # --- ENCABEZADO / BRANDING ---
        self.label_team = ctk.CTkLabel(self, text="Málaga Space Team", font=("Roboto", 24, "bold"), text_color="#3B82F6")
        self.label_team.pack(pady=(15, 2))

        self.label_author = ctk.CTkLabel(self, text="@Alexander Fomin lexfomin.com", font=("Roboto", 11), text_color="#9CA3AF")
        self.label_author.pack(pady=(0, 10))

        # --- CONEXIÓN DE PUERTO COM ---
        self.frame_puerto = ctk.CTkFrame(self)
        self.frame_puerto.pack(pady=5, padx=20, fill="x")

        self.combo_puertos = ctk.CTkOptionMenu(self.frame_puerto, values=self.obtener_puertos())
        self.combo_puertos.pack(side="left", padx=10, pady=8)

        self.btn_refresh = ctk.CTkButton(self.frame_puerto, text="Refresh", width=80, fg_color="#374151", command=self.actualizar_puertos)
        self.btn_refresh.pack(side="left", padx=5, pady=8)

        self.btn_conectar = ctk.CTkButton(self.frame_puerto, text="Connect", command=self.conectar_puerto)
        self.btn_conectar.pack(side="right", padx=10, pady=8)

        # --- PANTALLA DE VOLTAJE ---
        self.frame_voltaje = ctk.CTkFrame(self, fg_color="#1F2937", corner_radius=12)
        self.frame_voltaje.pack(pady=10, padx=20, fill="x")

        self.label_voltaje = ctk.CTkLabel(self.frame_voltaje, text="0.00 V", font=("Roboto", 42, "bold"), text_color="#10B981")
        self.label_voltaje.pack(pady=10)

        # --- GRÁFICA MATPLOTLIB (V/t) ---
        self.frame_grafica = ctk.CTkFrame(self, fg_color="#111827", corner_radius=12)
        self.frame_grafica.pack(pady=10, padx=20, fill="both", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor('#111827')
        self.ax.set_facecolor('#1F2937')
        
        self.ax.set_title("Voltage vs Time", color="white", fontsize=10)
        self.ax.set_xlabel("Time (s)", color="#9CA3AF", fontsize=8)
        self.ax.set_ylabel("Voltage (V)", color="#9CA3AF", fontsize=8)
        self.ax.tick_params(colors='#9CA3AF', labelsize=8)
        self.ax.spines['bottom'].set_color('#374151')
        self.ax.spines['top'].set_color('#374151')
        self.ax.spines['left'].set_color('#374151')
        self.ax.spines['right'].set_color('#374151')
        self.ax.grid(True, color="#374151", linestyle="--", linewidth=0.5)

        self.line, = self.ax.plot([], [], color="#3B82F6", marker="o", markersize=3, linewidth=1.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafica)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # --- BARRA DE ESTADO ---
        self.label_estado = ctk.CTkLabel(self, text="Status: Disconnected", font=("Roboto", 11), text_color="#9CA3AF")
        self.label_estado.pack(pady=(0, 10))

    def obtener_puertos(self):
        puertos = [port.device for port in serial.tools.list_ports.comports()]
        return puertos if puertos else ["No ports found"]

    def actualizar_puertos(self):
        puertos = self.obtener_puertos()
        self.combo_puertos.configure(values=puertos)
        if puertos:
            self.combo_puertos.set(puertos[0])

    def conectar_puerto(self):
        if not self.leyendo:
            puerto_seleccionado = self.combo_puertos.get()
            try:
                self.ser = serial.Serial(puerto_seleccionado, 19200, timeout=1)
                self.leyendo = True
                self.start_time = time.time()
                self.times.clear()
                self.voltages.clear()

                self.btn_conectar.configure(text="Disconnect", fg_color="#EF4444")
                self.label_estado.configure(text=f"Connected to {puerto_seleccionado}", text_color="#10B981")
                
                threading.Thread(target=self.leer_datos, daemon=True).start()
            except Exception as e:
                self.label_estado.configure(text="Connection Error", text_color="#EF4444")
        else:
            self.leyendo = False
            if self.ser:
                self.ser.close()
            self.btn_conectar.configure(text="Connect", fg_color="#2563EB")
            self.label_estado.configure(text="Status: Disconnected", text_color="#9CA3AF")

    def leer_datos(self):
        while self.leyendo:
            try:
                linea = self.ser.readline().decode('utf-8').strip()
                if "Voltaje:" in linea:
                    # Extraer el valor numérico
                    partes = linea.split(":")
                    if len(partes) > 1:
                        val_str = partes[1].replace("V", "").strip()
                        v_num = float(val_str)
                        t_actual = round(time.time() - self.start_time, 1)

                        # Mantener los últimos 30 puntos en pantalla para que la gráfica avance
                        self.times.append(t_actual)
                        self.voltages.append(v_num)
                        if len(self.times) > 30:
                            self.times.pop(0)
                            self.voltages.pop(0)

                        # Actualizar interfaz en el hilo principal
                        self.after(0, self.actualizar_interfaz, f"{v_num:.2f} V")
            except:
                break

    def actualizar_interfaz(self, valor_texto):
        self.label_voltaje.configure(text=valor_texto)
        
        # Plotear puntos y líneas
        self.line.set_data(self.times, self.voltages)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

if __name__ == "__main__":
    app = TelemetriaApp()
    app.mainloop()