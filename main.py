import socket
import threading
import time

# ==========================================
# 1. ESTRUCTURA Y LÓGICA DEL ÁRBOL BINARIO (BST)
# ==========================================
class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izq = None
        self.der = None

class ArbolBinarioBusqueda:
    def __init__(self):
        self.raiz = None

    def insertar(self, valor):
        if self.raiz is None:
            self.raiz = Nodo(valor)
        else:
            self._insertar_rec(self.raiz, valor)

    def _insertar_rec(self, actual, valor):
        if valor < actual.valor:
            if actual.izq is None:
                actual.izq = Nodo(valor)
            else:
                self._insertar_rec(actual.izq, valor)
        elif valor > actual.valor:
            if actual.der is None:
                actual.der = Nodo(valor)
            else:
                self._insertar_rec(actual.der, valor)

    def recorrido_inorden(self):
        elementos = []
        self._inorden_rec(self.raiz, elementos)
        return elementos

    def _inorden_rec(self, actual, elementos):
        if actual:
            self._inorden_rec(actual.izq, elementos)
            elementos.append(actual.valor)
            self._inorden_rec(actual.der, elementos)

    def nodos_con_dos_hijos(self):
        nodos = []
        self._dos_hijos_rec(self.raiz, nodos)
        return nodos

    def _dos_hijos_rec(self, actual, nodos):
        if actual:
            if actual.izq and actual.der:
                nodos.append(actual.valor)
            self._dos_hijos_rec(actual.izq, nodos)
            self._dos_hijos_rec(actual.der, nodos)

    def nodos_con_un_hijo_par(self):
        nodos = []
        self._un_hijo_par_rec(self.raiz, nodos)
        return nodos

    def _un_hijo_par_rec(self, actual, nodos):
        if actual:
            if (actual.izq and not actual.der) or (not actual.izq and actual.der):
                hijo = actual.izq if actual.izq else actual.der
                if hijo.valor % 2 == 0:
                    nodos.append(actual.valor)
            self._un_hijo_par_rec(actual.izq, nodos)
            self._un_hijo_par_rec(actual.der, nodos)

    def suma_de_hijos(self):
        resultados = []
        self._suma_hijos_rec(self.raiz, resultados)
        return resultados

    def _suma_hijos_rec(self, actual, resultados):
        if actual:
            suma = 0
            if actual.izq:
                suma += actual.izq.valor
            if actual.der:
                suma += actual.der.valor
            resultados.append((actual.valor, suma))
            self._suma_hijos_rec(actual.izq, resultados)
            self._suma_hijos_rec(actual.der, resultados)

    def buscar_camino(self, valor_buscado):
        camino = []
        encontrado = self._camino_rec(self.raiz, valor_buscado, camino)
        return camino if encontrado else []

    def _camino_rec(self, actual, valor_buscado, camino):
        if actual is None:
            return False
        camino.append(actual.valor)
        if actual.valor == valor_buscado:
            return True
        if valor_buscado < actual.valor:
            if self._camino_rec(actual.izq, valor_buscado, camino):
                return True
        else:
            if self._camino_rec(actual.der, valor_buscado, camino):
                return True
        camino.pop()
        return False


# ==========================================
# 2. SERVIDOR SOCKET (Construcción nodo a nodo)
# ==========================================
HOST = '127.0.0.1'
PORT = 65432

def servidor_socket():
    bst = ArbolBinarioBusqueda()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        
        with conn:
            # Recibir los 30 números uno a uno enviados por el cliente
            for i in range(30):
                data = conn.recv(1024).decode('utf-8').strip()
                if data:
                    num = int(data)
                    bst.insertar(num)
                    # Confirmación de recepción e inserción al cliente
                    conn.sendall(f"OK_NODO_{i+1}".encode('utf-8'))

            # Recibir el número de nodo a buscar
            nodo_a_buscar = int(conn.recv(1024).decode('utf-8').strip())

            # Construir la respuesta final con las operaciones sobre el Árbol
            inorden = " ".join(map(str, bst.recorrido_inorden()))
            dos_hijos = " ".join(map(str, bst.nodos_con_dos_hijos()))
            un_hijo_par = " ".join(map(str, bst.nodos_con_un_hijo_par()))
            suma_hijos = " ".join([str(suma) for _, suma in bst.suma_de_hijos()])
            
            camino = bst.buscar_camino(nodo_a_buscar)
            camino_str = " ".join(map(str, camino)) if camino else "El nodo no existe"

            respuesta_final = (
                f"\n===========================================\n"
                f"       RESPUESTA DEL SERVIDOR (ABB)        \n"
                f"===========================================\n"
                f"Recorrido en orden:\n{inorden}\n\n"
                f"Nodos con 2 hijos:\n{dos_hijos}\n\n"
                f"Nodos con 1 hijo par:\n{un_hijo_par}\n\n"
                f"Suma de sus hijos:\n{suma_hijos}\n\n"
                f"El camino para el nodo {nodo_a_buscar} es: {camino_str}\n"
                f"==========================================="
            )
            
            conn.sendall(respuesta_final.encode('utf-8'))


# ==========================================
# 3. CLIENTE SOCKET (Solicita los 30 números por teclado)
# ==========================================
def cliente_socket():
    time.sleep(0.5)  # Breve pausa para asegurar el inicio del servidor
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        print("=== ACTIVIDAD EVALUATIVA EJE 4: CLIENTE - SERVIDOR ===")
        print("Ingrese 30 números enteros de 2 cifras (entre 10 y 99) uno por uno:\n")

        numeros_ingresados = []

        # Bucle para pedir manualmente los 30 números al usuario
        i = 1
        while i <= 30:
            entrada = input(f"Digite el número {i} de 30: ").strip()
            
            # Validación: verificar que sea un número entero de 2 cifras
            if entrada.isdigit() and 10 <= int(entrada) <= 99:
                num = int(entrada)
                s.sendall(str(num).encode('utf-8'))
                
                # Esperar confirmación del servidor antes de pedir el siguiente
                s.recv(1024)
                numeros_ingresados.append(num)
                i += 1
            else:
                print(" -> Error: Debe ingresar un número entero de exactamente 2 cifras (10 a 99). Intente de nuevo.\n")

        print("\n¡Los 30 números fueron enviados correctamente!")
        
        # Bucle para solicitar el nodo que desea buscar
        while True:
            nodo_input = input("\nDigite el nodo que desea buscar en el árbol: ").strip()
            if nodo_input.isdigit():
                nodo_a_buscar = int(nodo_input)
                s.sendall(str(nodo_a_buscar).encode('utf-8'))
                break
            else:
                print(" -> Error: Ingrese un valor numérico válido.")

        # Recibir y mostrar el reporte final del servidor
        respuesta = s.recv(4096).decode('utf-8')
        print(respuesta)


# ==========================================
# EJECUCIÓN CONCURRENTE
# ==========================================
hilo_servidor = threading.Thread(target=servidor_socket)
hilo_servidor.start()

cliente_socket()
hilo_servidor.join()