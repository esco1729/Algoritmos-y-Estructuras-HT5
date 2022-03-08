# HDT 5 
#Grupo 8



import simpy as sp
import numpy as np
import random

random.seed(10) # fijar el inicio de random

No_procesos = 200    
intervalo = 1      #intervalo de llegada de los procesos
instr_procesador = 3            #Velocidad de operacion del procesador en ops/ciclo

#Recursos
env = sp.Environment() 
RAM = sp.Container(env, init = 100, capacity = 100) #incializando cola RAM 
procesador = sp.Resource(env, capacity = 2) #incializando cola procesador (ready)
IO = sp.Resource(env, capacity = 1)         #inciailizando cola waiting 



mediciones = []



def request_proceso(env,name, ram_req, No_ops, instr_procesador, mediciones, entrada):         #Funcion recursiva para circular procesos entre procesador, waiting y terminated
    
    with  procesador.request() as req: #poner en una funcion
        
        print('{} en cola para efectuar {} operaciones en momento: {}'.format(name, No_ops, env.now ))
        
        yield req
        
        No_ops = No_ops - instr_procesador
        
        decision = random.randint(1,2)
        
        print('{} efectuando {} operaciones en momento: {}'.format(name, instr_procesador, env.now))
        yield env.timeout(1)
        
        if No_ops <= 0:
            
            with RAM.put(ram_req) as put:
                
                print('{} ha terminado de efectuar todas sus operaciones y devuelve {} bytes a RAM en momento: {}'.format(name, ram_req, env.now))
                mediciones.append(env.now-entrada)
                yield put
            
            
        elif decision == 1:
            
            with IO.request() as wait:      #enviando a waiting para IO
                
                print('{} ingresando a la cola de IO (waiting) en momento {}'.format(name, env.now))
                yield wait
                print('{} iniciando operaciones de IO durante 15 unidades de tiempo en momento: {}'.format(name, env.now) )
                yield env.timeout(15)
                print('{} regresando a la cola de espera para efectuar operaciones (ready) en momento: {} con {} operaciones pendientes'.format(name, env.now, No_ops))
                env.process(request_proceso(env, name,  ram_req, No_ops, instr_procesador, mediciones, entrada))     #enviando a ready
                
        elif decision == 2: #enviando directamente a ready
            
            print('{} regresando directamente a cola para efectuar operaciones (ready) en momento: {} con {} operaciones pendientes'.format(name, env.now, No_ops))
            env.process(request_proceso(env, name, ram_req, No_ops, instr_procesador, mediciones, entrada))  






def proceso(env, name, ram_req, RAM, No_ops, procesador, instr_procesador, IO):
    
    
    #incialiando tiempo de ejecucion del proceso
    
    #conseguir RAM
    entrada = env.now
    with RAM.get(ram_req) as get:
        
        print('Tratando de asignar {} bytes de RAM a {} en momento {}'.format(ram_req, name, env.now))
        print('RAM disponible: {} --- momento: {}'.format(  RAM.level, env.now))
        
        yield get
        
        print('procesos esperando RAM: {} --- momento: {}'.format( len(RAM.get_queue), env.now))
        yield env.timeout(1)
        
        
    env.process(request_proceso(env, name, ram_req, No_ops, instr_procesador, mediciones, entrada))
    
                



def process_generator(env):
    for i in range(No_procesos):
         env.process(proceso( env, 'proceso {}'.format(i+1), random.randint(1,10), RAM, random.randint(1,10), procesador, instr_procesador, IO))
         t_llegada = random.expovariate(1.0/ intervalo) #creacion de procesos
         yield env.timeout(t_llegada)
         
proc_gen = env.process(process_generator(env))


env.run(until = 10000)

tiempo_total = sum(mediciones)
tiempo_prom = tiempo_total/No_procesos      #calculando tiempo promedio por programa
des_std = np.std(mediciones)

print('El tiempo promedio de ejecucion por proceso fue de: ', tiempo_prom)
print('La desviación std es de: ', des_std)






