"""Motor D'Hondt para el Congreso (LOREG art. 163): umbral 3% de votos válidos (incluye blanco) por circunscripción."""
import numpy as np
def dhondt(votes, seats, valid=None, threshold=0.03, eligible=None):
    """votes: array (P,) ; devuelve escaños (P,). Desempate: más votos totales (LOREG)."""
    v=np.asarray(votes,float).copy()
    if valid is None: valid=v.sum()
    ok = v >= threshold*valid
    if eligible is not None: ok &= eligible
    v[~ok]=0
    s=np.zeros(len(v),int)
    for _ in range(seats):
        q=v/(s+1)
        i=np.lexsort((-v,-q))[0]  # max cociente, desempate por votos
        s[i]+=1
    return s
def dhondt_batch(V, seats, valid, threshold=0.03, eligible=None):
    """V: (N,P) simulaciones -> (N,P) escaños. Vectorizado."""
    V=np.asarray(V,float).copy(); N,P=V.shape
    ok = V >= threshold*np.asarray(valid).reshape(-1,1)
    if eligible is not None: ok &= eligible[None,:]
    V[~ok]=0
    S=np.zeros((N,P),int); r=np.arange(N)
    for _ in range(seats):
        q=V/(S+1)
        S[r,q.argmax(1)]+=1
    return S
