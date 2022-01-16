import random
import spade
from spade.behaviour import *
from spade.message import Message
import time
import ast

n = 8
broj_mina = 8
brojevi_u_poljima = [[0 for y in range(n)] for x in range(n)]
vrijednosti_mina = [[' ' for y in range(n)] for x in range(n)]
posjecene = []
generirane=[]
class AgentIgrac(spade.agent.Agent):
    class OdaberiPozicije(CyclicBehaviour):
        async def run(self):
            msg=await self.receive(timeout=1000)
            if msg:	
                odabrane=ast.literal_eval(msg.body)
                odabrane.extend(generirane)        
                duplikat=True
                while duplikat:
                    r=random.randint(0,7)
                    s=random.randint(0,7)
                    if [r,s] not in odabrane:
                        duplikat=False
                        print(f"Agent Igrac: Odabirem redak {r+1} i stupac {s+1}!")
                        novaPozicija=str(r+1)+" "+str(s+1)
                        generirane.append([r,s])
                await self.saljiOdgovor(novaPozicija)                     
                if msg.body=='kill':
                    self.kill(0)          
        async def saljiOdgovor(self,poz):
            msg=Message(
                to="lmiroic1@rec.foi.hr",
                body=poz)
            await self.send(msg)
    async def setup(self):
        print("AgentIgrac: Spreman sam!")
        odaberiPozicije=self.OdaberiPozicije()
        self.add_behaviour(odaberiPozicije)
        
class AgentGenerator(spade.agent.Agent):
    adresaAgentIgrac="lmiroic@rec.foi.h"
    class PostaviIgru(OneShotBehaviour):
        async def run(self):
            await self.postavi_mine()
            await self.postavi_vrijednosti()
        async def postavi_mine(self):
            global brojevi_u_poljima
            global broj_mina
            global n         
            brojac = 0
            while brojac < broj_mina:         
                br = random.randint(0, n*n-1)         
                r = br // n
                s = br % n         
                if brojevi_u_poljima[r][s] != -1:
                    brojac = brojac + 1
                    brojevi_u_poljima[r][s] = -1
        async def postavi_vrijednosti(self): 
            global brojevi_u_poljima
            global n         
            for r in range(n):
                for s in range(n):         
                    if brojevi_u_poljima[r][s] == -1:
                        continue         
                    if r > 0 and brojevi_u_poljima[r-1][s] == -1:
                        brojevi_u_poljima[r][s] = brojevi_u_poljima[r][s] + 1  
                    if r < n-1  and brojevi_u_poljima[r+1][s] == -1:
                        brojevi_u_poljima[r][s] = brojevi_u_poljima[r][s] + 1
                    if s > 0 and brojevi_u_poljima[r][s-1] == -1:
                        brojevi_u_poljima[r][s] = brojevi_u_poljima[r][s] + 1
                    if s < n-1 and brojevi_u_poljima[r][s+1] == -1:
                        brojevi_u_poljima[r][s] = brojevi_u_poljima[r][s] + 1  
                    if r > 0 and s > 0 and brojevi_u_poljima[r-1][s-1] == -1:
                        brojevi_u_poljima[r][s] = brojevi_u_poljima[r][s] + 1
                    if r > 0 and s < n-1 and brojevi_u_poljima[r-1][s+1] == -1:
                        brojevi_u_poljima[r][s] = brojevi_u_poljima[r][s] + 1
                    if r < n-1 and s > 0 and brojevi_u_poljima[r+1][s-1] == -1:
                        brojevi_u_poljima[r][s] = brojevi_u_poljima[r][s] + 1
                    if r < n-1 and s < n-1 and brojevi_u_poljima[r+1][s+1] == -1:
                        brojevi_u_poljima[r][s] = brojevi_u_poljima[r][s] + 1
       
    class IgrajIgru(CyclicBehaviour):
        async def run(self):
            time.sleep(1)
            gotovo=False
            await self.ispis_igre()
            unos=await self.saljiZahtjevAgentuIgrac()
            pom=unos.split(" ",1)
            r = int(pom[0])-1
            s = int(pom[1])-1
            if brojevi_u_poljima[r][s] == -1:
                vrijednosti_mina[r][s] = 'M'
                await self.ispis_mina()
                await self.ispis_igre()
                print("Agent Generator: Igra je gotova, stao si na MINU!!!")
                gotovo = True
                
            elif brojevi_u_poljima[r][s] == 0:
                vrijednosti_mina[r][s] = '0'
                await self.provjeri_susjede(r, s)
            else:   
                vrijednosti_mina[r][s] = brojevi_u_poljima[r][s]
            if(gotovo==True):
                msg = spade.message.Message(
                    to="lmiroic1@rec.foi.hr",
                    body="kill")
                await self.send(msg) 
                self.kill(0) 
            if(await self.provjera_igre()):
                await self.ispis_mina()
                await self.ispis_igre()
                print("Agent Generator: Bravo, nema vise slobodnih polja, pobijedio si!!!")
                gotovo = True
            if(gotovo==True):
                msg = spade.message.Message(
                    to="lmiroic1@rec.foi.hr",
                    body="kill")
                await self.send(msg) 
                self.kill(0)      
            
        async def saljiZahtjevAgentuIgrac(self):
            msg=Message(
                to="lmiroic@rec.foi.hr",
                body=f"{posjecene}"
                )
            await self.send(msg)
            msg=await self.receive(timeout=1000)
            if msg:
                pozicija=msg.body
            return pozicija
        async def ispis_igre(self):
            global vrijednosti_mina
            global n
            print()
            print("\t-----------------MINOLOVAC-----------------")
            print()
            st = "   "
            for i in range(n):
                st = st + "     " + str(i + 1)
            print(st)   
            for r in range(n):
                st = "     "
                if r == 0:
                    for s in range(n):
                        st = st + "______" 
                    print(st)       
                st = "     "
                for s in range(n):
                    st = st + "|     "
                print(st + "|")                 
                st = "  " + str(r + 1) + "  "
                for s in range(n):
                    st = st + "|  " + str(vrijednosti_mina[r][s]) + "  "
                print(st + "|")          
                st = "     "
                for s in range(n):
                    st = st + "|_____"
                print(st + '|')         
            print()
        
        async def provjeri_susjede(self,r, s):     
            global vrijednosti_mina
            global brojevi_u_poljima
            global posjecene      
            if [r,s] not in posjecene:         
                posjecene.append([r,s])         
                if brojevi_u_poljima[r][s] == 0:         
                    vrijednosti_mina[r][s] = brojevi_u_poljima[r][s]         
                    if r > 0:
                        await self.provjeri_susjede(r-1, s)
                    if r < n-1:
                        await self.provjeri_susjede(r+1, s)
                    if s > 0:
                        await self.provjeri_susjede(r, s-1)
                    if s < n-1:
                        await self.provjeri_susjede(r, s+1)    
                    if r > 0 and s > 0:
                        await self.provjeri_susjede(r-1, s-1)
                    if r > 0 and s < n-1:
                        await self.provjeri_susjede(r-1, s+1)
                    if r < n-1 and s > 0:
                        await self.provjeri_susjede(r+1, s-1)
                    if r < n-1 and s < n-1:
                        await self.provjeri_susjede(r+1, s+1)                     
                if brojevi_u_poljima[r][s] != 0:
                        vrijednosti_mina[r][s] = brojevi_u_poljima[r][s]
        async def provjera_igre(self):
            global vrijednosti_mina
            global n
            global broj_mina         
            brojac = 0         
            for r in range(n):
                for s in range(n):         
                    if vrijednosti_mina[r][s] != ' ':
                        brojac = brojac + 1                     
            if brojac == n * n - broj_mina:
                return True
            else:
                return False
        async def ispis_mina(self):
            global vrijednosti_mina
            global brojevi_u_poljima
            global n         
            for r in range(n):
                for s in range(n):
                    if brojevi_u_poljima[r][s] == -1:
                        vrijednosti_mina[r][s] = 'M'
    async def setup(self):
        print("AgentGenerator: Spreman sam")
        postaviIgru=self.PostaviIgru()
        self.add_behaviour(postaviIgru)
        igrajIgru = self.IgrajIgru()
        self.add_behaviour(igrajIgru)

if __name__ == '__main__':
    agentIgrac = AgentIgrac("lmiroic@rec.foi.hr", "lmiroic1")

    generator = AgentGenerator("lmiroic1@rec.foi.hr", "lmiroic2")
    agentIgrac.start()
    time.sleep(1)
    generator.start()
    while(True):
        try:
            time.sleep(1000)
        except KeyboardInterrupt:
            generator.stop()
            agentIgrac.stop()
            spade.quit_spade()
            print("Izlaz iz programa!")
            break
