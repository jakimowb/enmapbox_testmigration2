# -*- coding: utf-8 -*-

import numpy as np

# Beispieldatensatz
myarr = np.array([[0, 1,   2,   3,   4,   5],
                  [0, 10,  20,  30,  40,  50],
                  [0, 100, 200, 300, 400, 500]])  # Shape = (3, 6)

nrows, ncols = myarr.shape



def beispiel1(): ##### Grundrechenarten (Beispiel: Verdoppelung)
    # Standard:
    myresult_a = np.zeros(shape=(nrows, ncols))
    for row in range(nrows):
        for col in range(ncols):
            myresult_a[row, col] = myarr[row, col] * 2

    # Vectorized:
    myresult_b = myarr * 2

    return np.alltrue(myresult_a == myresult_b)  # Sind die Arrays identisch?


def beispiel2():  ##### Conditions (am Beispiel: Verdoppelung aller Zahlen, die glatt durch 8 teilbar sind)
    # Standard:
    myresult_a = np.zeros(shape=(nrows, ncols))
    for row in range(nrows):
        for col in range(ncols):
            if myarr[row, col] % 8 == 0:
                myresult_a[row, col] = myarr[row, col] * 2
            else:
                myresult_a[row, col] = myarr[row, col]

    # Vectorized:
    myresult_b = np.where(myarr % 8 == 0, myarr * 2, myarr)   # np.where(wenn, dann, sonst)

    return np.alltrue(myresult_a == myresult_b)

def beispiel3():  ##### Multiplikation von Arrays (z.B. Soil-Spektrum * psoil)

    # Standard: "Skalarprodukt", also Array * Variable
    soil_bright = np.array([0.1, 0.2, 0.1, 0.4, 0.4, 0.5, 0.5, 0.7, 0.5, 0.3])  # len: 10
    soil_dark = np.array([0.1, 0.1, 0.1, 0.3, 0.4, 0.4, 0.4, 0.6, 0.4, 0.2])  # len: 10
    psoil = [0.7, 0.5, 0.6, 0.8, 0.2]  # 5 Aufrufe von PROSAIL, jeweils mit anderem psoil

    soil_a = np.zeros(shape=(len(soil_bright), len(psoil)))
    for i in range(len(psoil)):  # Berechne jeden Soil einzeln in einer Schleife
        soil_a[:, i] = soil_bright * psoil[i] + soil_dark * (1 - psoil[i])

    # Vectorized: "Kreuzprodukt", engl. "Outer Product", numpy.outer
    psoil = np.array([0.7, 0.5, 0.6, 0.8, 0.2])  # 5 PROSAIL-Berechnungen auf einmal, d.h. 5 Parameter für psoil
    soil_b = np.outer(soil_bright, psoil) + np.outer(soil_dark, (1 - psoil))  # Shape von soil_b: (10, 5)
    # geht auch mit Division, Power, ...

    # Vectorized mithilfe von Numpy's Broadcasting:
    psoil = np.array([0.7, 0.5, 0.6, 0.8, 0.2])  # shape: (5,) -> 1D

    try:
        soil_c = soil_bright * psoil + soil_dark * (1 - psoil)
    except ValueError as e:
        print("Beispiel 3, Ansatz 1:  Geht leider nicht! Python sagt: '{}'".format(str(e)))

    # Lösung:
    psoil = psoil[:, np.newaxis]  # shape: (5, 1) -> 2D

    # Jetzt ist eine normale Multiplikation möglich: Numpy versteht, welche Dimension es mit welcher multiplizieren muss
    soil_c = soil_bright * psoil + soil_dark * (1 - psoil)  # shape (5, 10)
    soil_c = soil_c.T  # Transponieren, damit shape wieder (10, 5)
    return np.alltrue((soil_a == soil_b) & (soil_a == soil_c))

def beispiel4():  ##### Weitere Späße  mit Numpy über Auswahl von Axis
                  # Bilden von Mittelwerten (oder Median, oder Summen, ...) entlang der Zeilen

    # Standard:
    myresult_a1 = np.zeros(shape=nrows)
    myresult_a2 = np.zeros(shape=ncols)
    for row in range(nrows):
        myresult_a1[row] = np.mean(myarr[row, :])
    for col in range(ncols):
        myresult_a2[col] = np.mean(myarr[:, col])

    # Vectorized:
    myresult_b1 = np.mean(myarr, axis=1)
    myresult_b2 = np.mean(myarr, axis=0)

    return np.alltrue(myresult_a1 == myresult_b1) & np.alltrue((myresult_a2 == myresult_b2))

print("Beispiel 1: ", beispiel1(), "\n")
print("Beispiel 2: ", beispiel2(), "\n")
print("Beispiel 3, Ansatz 2: ", beispiel3(), "\n")
print("Beispiel 4: ", beispiel4())
